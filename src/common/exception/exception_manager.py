"""
예외 관리자 모듈

이 모듈은 시스템 전체의 예외 처리를 관리하고 로깅하는 ExceptionManager 클래스를 제공합니다.
예외 발생 시 적절한 로깅, 알림, 재시도 등의 처리를 수행합니다.
"""

import logging
import asyncio
from typing import Optional, Dict, Any, List, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from contextlib import contextmanager
from functools import wraps

from .exception_types import (
    ExceptionType,
    ExceptionSeverity,
    ExceptionStatus,
    ExceptionContext,
    create_exception_context
)
from .custom_exceptions import BaseCustomException, wrap_exception

# 로거 설정
logger = logging.getLogger(__name__)


@dataclass
class ExceptionRecord:
    """예외 기록 데이터 클래스"""
    exception: BaseCustomException
    timestamp: datetime
    handler_name: Optional[str] = None
    resolved: bool = False
    resolution_timestamp: Optional[datetime] = None
    resolution_details: Optional[str] = None


class ExceptionManager:
    """
    예외 관리자 클래스
    
    시스템 전체의 예외 처리를 관리하고 로깅합니다.
    싱글톤 패턴으로 구현되어 전역적으로 사용할 수 있습니다.
    """
    
    _instance = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ExceptionManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._exception_records: Dict[str, ExceptionRecord] = {}
            self._handlers: Dict[ExceptionType, List[Callable]] = {}
            self._severity_loggers: Dict[ExceptionSeverity, logging.Logger] = {
                ExceptionSeverity.LOW: logging.getLogger('exception.low'),
                ExceptionSeverity.MEDIUM: logging.getLogger('exception.medium'),
                ExceptionSeverity.HIGH: logging.getLogger('exception.high'),
                ExceptionSeverity.CRITICAL: logging.getLogger('exception.critical')
            }
            self._metrics: Dict[str, Any] = {
                'total_exceptions': 0,
                'exceptions_by_type': {},
                'exceptions_by_severity': {},
                'resolution_times': [],
                'retry_counts': []
            }
            self._initialized = True
    
    async def handle_exception(
        self,
        exception: Union[Exception, BaseCustomException],
        context: Optional[ExceptionContext] = None,
        handler_name: Optional[str] = None,
        auto_retry: bool = True,
        notify_handlers: bool = True
    ) -> BaseCustomException:
        """
        예외 처리 및 관리
        
        Args:
            exception: 처리할 예외
            context: 예외 컨텍스트
            handler_name: 처리기 이름
            auto_retry: 자동 재시도 여부
            notify_handlers: 핸들러 알림 여부
        
        Returns:
            BaseCustomException: 처리된 커스텀 예외
        """
        async with self._lock:
            # 커스텀 예외로 변환
            if isinstance(exception, BaseCustomException):
                custom_exception = exception
            else:
                custom_exception = wrap_exception(
                    exception,
                    exception_type=self._determine_exception_type(exception)
                )
            
            # 컨텍스트 업데이트
            if context:
                custom_exception.context = context
            
            # 예외 기록 생성
            record_id = self._generate_record_id()
            record = ExceptionRecord(
                exception=custom_exception,
                timestamp=datetime.now(),
                handler_name=handler_name
            )
            self._exception_records[record_id] = record
            
            # 메트릭 업데이트
            self._update_metrics(custom_exception)
            
            # 로깅
            self._log_exception(custom_exception, record_id)
            
            # 핸들러 알림
            if notify_handlers:
                await self._notify_handlers(custom_exception)
            
            # 자동 재시도
            if auto_retry and custom_exception.context.can_retry():
                await self._schedule_retry(custom_exception)
            
            return custom_exception
    
    def register_handler(
        self,
        exception_type: ExceptionType,
        handler: Callable[[BaseCustomException], None]
    ) -> None:
        """
        예외 타입별 핸들러 등록
        
        Args:
            exception_type: 예외 타입
            handler: 핸들러 함수
        """
        if exception_type not in self._handlers:
            self._handlers[exception_type] = []
        self._handlers[exception_type].append(handler)
    
    def unregister_handler(
        self,
        exception_type: ExceptionType,
        handler: Callable[[BaseCustomException], None]
    ) -> None:
        """
        예외 타입별 핸들러 해제
        
        Args:
            exception_type: 예외 타입
            handler: 핸들러 함수
        """
        if exception_type in self._handlers:
            try:
                self._handlers[exception_type].remove(handler)
            except ValueError:
                pass
    
    def resolve_exception(
        self,
        record_id: str,
        resolution_details: Optional[str] = None
    ) -> bool:
        """
        예외 해결 표시
        
        Args:
            record_id: 기록 ID
            resolution_details: 해결 상세 정보
        
        Returns:
            bool: 해결 성공 여부
        """
        if record_id in self._exception_records:
            record = self._exception_records[record_id]
            record.resolved = True
            record.resolution_timestamp = datetime.now()
            record.resolution_details = resolution_details
            record.exception.context.mark_resolved()
            
            # 해결 시간 메트릭 업데이트
            resolution_time = (record.resolution_timestamp - record.timestamp).total_seconds()
            self._metrics['resolution_times'].append(resolution_time)
            
            logger.info(f"예외 해결됨: {record_id}, 해결 시간: {resolution_time:.2f}초")
            return True
        
        return False
    
    def get_exception_record(self, record_id: str) -> Optional[ExceptionRecord]:
        """예외 기록 조회"""
        return self._exception_records.get(record_id)
    
    def get_recent_exceptions(
        self,
        hours: int = 24,
        severity: Optional[ExceptionSeverity] = None,
        exception_type: Optional[ExceptionType] = None
    ) -> List[ExceptionRecord]:
        """
        최근 예외 기록 조회
        
        Args:
            hours: 조회 시간 범위 (시간)
            severity: 심각도 필터
            exception_type: 예외 타입 필터
        
        Returns:
            List[ExceptionRecord]: 예외 기록 목록
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        filtered_records = []
        for record in self._exception_records.values():
            if record.timestamp < cutoff_time:
                continue
            
            if severity and record.exception.get_severity() != severity:
                continue
            
            if exception_type and record.exception.exception_type != exception_type:
                continue
            
            filtered_records.append(record)
        
        return sorted(filtered_records, key=lambda x: x.timestamp, reverse=True)
    
    def get_metrics(self) -> Dict[str, Any]:
        """메트릭 정보 조회"""
        metrics = self._metrics.copy()
        
        # 평균 해결 시간 계산
        if self._metrics['resolution_times']:
            metrics['average_resolution_time'] = sum(self._metrics['resolution_times']) / len(self._metrics['resolution_times'])
        else:
            metrics['average_resolution_time'] = 0
        
        # 평균 재시도 횟수 계산
        if self._metrics['retry_counts']:
            metrics['average_retry_count'] = sum(self._metrics['retry_counts']) / len(self._metrics['retry_counts'])
        else:
            metrics['average_retry_count'] = 0
        
        return metrics
    
    def clear_old_records(self, days: int = 7) -> int:
        """
        오래된 기록 삭제
        
        Args:
            days: 보관 기간 (일)
        
        Returns:
            int: 삭제된 기록 수
        """
        cutoff_time = datetime.now() - timedelta(days=days)
        
        to_remove = []
        for record_id, record in self._exception_records.items():
            if record.timestamp < cutoff_time:
                to_remove.append(record_id)
        
        for record_id in to_remove:
            del self._exception_records[record_id]
        
        logger.info(f"오래된 예외 기록 {len(to_remove)}개 삭제됨")
        return len(to_remove)
    
    @contextmanager
    def exception_context(
        self,
        exception_type: ExceptionType = ExceptionType.UNKNOWN,
        severity: Optional[ExceptionSeverity] = None,
        **context_kwargs
    ):
        """
        예외 컨텍스트 관리자
        
        사용법:
            with exception_manager.exception_context(
                exception_type=ExceptionType.DATABASE_ERROR,
                severity=ExceptionSeverity.HIGH,
                user_id="user123"
            ):
                # 예외 발생 가능한 코드
                pass
        """
        context = create_exception_context(
            exception_type=exception_type,
            severity=severity,
            **context_kwargs
        )
        
        try:
            yield context
        except Exception as e:
            # 예외 발생 시 자동으로 처리
            asyncio.create_task(self.handle_exception(e, context=context))
            raise
    
    def _determine_exception_type(self, exception: Exception) -> ExceptionType:
        """예외 타입 자동 결정"""
        exception_name = type(exception).__name__.lower()
        
        # 데이터베이스 관련 예외
        if any(keyword in exception_name for keyword in ['sql', 'database', 'connection']):
            return ExceptionType.DATABASE_ERROR
        
        # 네트워크 관련 예외
        if any(keyword in exception_name for keyword in ['network', 'connection', 'timeout']):
            return ExceptionType.NETWORK_ERROR
        
        # 유효성 검증 예외
        if any(keyword in exception_name for keyword in ['validation', 'value']):
            return ExceptionType.VALIDATION_ERROR
        
        # 파일 관련 예외
        if any(keyword in exception_name for keyword in ['file', 'io']):
            return ExceptionType.FILE_ERROR
        
        # 인증 관련 예외
        if any(keyword in exception_name for keyword in ['auth', 'permission']):
            return ExceptionType.AUTHENTICATION_ERROR
        
        return ExceptionType.UNKNOWN
    
    def _generate_record_id(self) -> str:
        """기록 ID 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"exc_{timestamp}"
    
    def _update_metrics(self, exception: BaseCustomException) -> None:
        """메트릭 업데이트"""
        self._metrics['total_exceptions'] += 1
        
        # 타입별 집계
        exception_type = exception.exception_type.value
        if exception_type not in self._metrics['exceptions_by_type']:
            self._metrics['exceptions_by_type'][exception_type] = 0
        self._metrics['exceptions_by_type'][exception_type] += 1
        
        # 심각도별 집계
        severity = exception.get_severity().value
        if severity not in self._metrics['exceptions_by_severity']:
            self._metrics['exceptions_by_severity'][severity] = 0
        self._metrics['exceptions_by_severity'][severity] += 1
        
        # 재시도 횟수 기록
        if exception.context.retry_count > 0:
            self._metrics['retry_counts'].append(exception.context.retry_count)
    
    def _log_exception(self, exception: BaseCustomException, record_id: str) -> None:
        """예외 로깅"""
        severity = exception.get_severity()
        logger_instance = self._severity_loggers[severity]
        
        log_message = f"[{record_id}] {exception.exception_type.value}: {exception.message}"
        
        # 컨텍스트 정보 추가
        if exception.context.details:
            log_message += f" | 상세: {exception.context.details}"
        
        # 심각도에 따른 로그 레벨 결정
        if severity == ExceptionSeverity.CRITICAL:
            logger_instance.critical(log_message)
        elif severity == ExceptionSeverity.HIGH:
            logger_instance.error(log_message)
        elif severity == ExceptionSeverity.MEDIUM:
            logger_instance.warning(log_message)
        else:
            logger_instance.info(log_message)
    
    async def _notify_handlers(self, exception: BaseCustomException) -> None:
        """핸들러 알림"""
        handlers = self._handlers.get(exception.exception_type, [])
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(exception)
                else:
                    handler(exception)
            except Exception as e:
                logger.error(f"핸들러 실행 중 오류 발생: {e}")
    
    async def _schedule_retry(self, exception: BaseCustomException) -> None:
        """재시도 스케줄링"""
        if not exception.context.can_retry():
            return
        
        # 재시도 지연 시간 (지수 백오프)
        delay = 2 ** exception.context.retry_count
        
        logger.info(f"재시도 스케줄링: {delay}초 후 재시도")
        
        # 실제 재시도 로직은 데코레이터에서 처리
        # 여기서는 상태만 업데이트
        exception.context.increment_retry()


# 전역 예외 관리자 인스턴스
exception_manager = ExceptionManager()


def get_exception_manager() -> ExceptionManager:
    """전역 예외 관리자 인스턴스 반환"""
    return exception_manager


# 편의 함수들
async def handle_exception(
    exception: Union[Exception, BaseCustomException],
    context: Optional[ExceptionContext] = None,
    handler_name: Optional[str] = None
) -> BaseCustomException:
    """예외 처리 편의 함수"""
    return await exception_manager.handle_exception(
        exception,
        context=context,
        handler_name=handler_name
    )


def register_exception_handler(
    exception_type: ExceptionType,
    handler: Callable[[BaseCustomException], None]
) -> None:
    """예외 핸들러 등록 편의 함수"""
    exception_manager.register_handler(exception_type, handler)


def resolve_exception(record_id: str, resolution_details: Optional[str] = None) -> bool:
    """예외 해결 편의 함수"""
    return exception_manager.resolve_exception(record_id, resolution_details) 