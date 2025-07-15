"""
클래스 기반 예외 처리 데코레이터 모듈

이 모듈은 클래스 기반 예외 처리 데코레이터들을 제공합니다.
함수형 데코레이터와 달리 상태를 유지할 수 있고 더 복잡한 로직을 구현할 수 있습니다.
"""

import asyncio
import logging
import inspect
from typing import (
    Any, Callable, Coroutine, Optional, Union, Type, List, Dict, 
    Awaitable, TypeVar, Tuple, Generic, overload
)
from functools import wraps
from datetime import datetime
from collections import defaultdict

from .exception_types import (
    ExceptionType,
    ExceptionSeverity,
    ExceptionStatus,
    ExceptionContext,
    create_exception_context
)
from .custom_exceptions import (
    BaseCustomException,
    ValidationException,
    DatabaseException,
    BusinessLogicException,
    ExternalServiceException,
    ProcessingException,
    wrap_exception
)
from .exception_manager import exception_manager

# 로거 설정
logger = logging.getLogger(__name__)

# 타입 변수
F = TypeVar('F', bound=Callable[..., Any])
T = TypeVar('T')

class ExceptionHandler:
    """
    기본 예외 처리 클래스 데코레이터
    
    모든 다른 예외 처리 데코레이터의 베이스 클래스입니다.
    
    사용법:
        @ExceptionHandler(
            exception_type=ExceptionType.DATABASE_ERROR,
            severity=ExceptionSeverity.HIGH,
            reraise=False,
            default_return=[]
        )
        def get_users():
            # 데이터베이스 조회 로직
            pass
    """
    
    def __init__(
        self,
        exception_type: ExceptionType = ExceptionType.UNKNOWN,
        severity: Optional[ExceptionSeverity] = None,
        reraise: bool = True,
        default_return: Any = None,
        log_level: Optional[str] = None,
        handler_name: Optional[str] = None
    ):
        """
        데코레이터 초기화
        
        Args:
            exception_type: 예외 타입
            severity: 심각도
            reraise: 예외 재발생 여부
            default_return: 예외 발생 시 반환할 기본값
            log_level: 로그 레벨
            handler_name: 핸들러 이름
        """
        self.exception_type = exception_type
        self.severity = severity
        self.reraise = reraise
        self.default_return = default_return
        self.log_level = log_level
        self.handler_name = handler_name

    def handle_exception(self, func: Callable, exception: Exception, *args, **kwargs) -> Any:
        """
        예외를 처리하는 기본 메서드
        
        하위 클래스에서 오버라이드하여 특별한 예외 처리 로직을 구현할 수 있습니다.
        
        Args:
            func: 예외가 발생한 함수
            exception: 발생한 예외
            *args: 함수 호출 시 사용된 인수
            **kwargs: 함수 호출 시 사용된 키워드 인수
            
        Returns:
            처리된 예외 또는 기본값
        """
        # 기본 예외 처리 로직
        context = create_exception_context(
            exception_type=self.exception_type,
            severity=self.severity,
            module=func.__module__,
            function=func.__name__
        )
        
        return context, exception

    async def handle_exception_async(self, func: Callable, exception: Exception, *args, **kwargs) -> Any:
        """
        비동기 예외를 처리하는 기본 메서드
        
        Args:
            func: 예외가 발생한 함수
            exception: 발생한 예외
            *args: 함수 호출 시 사용된 인수
            **kwargs: 함수 호출 시 사용된 키워드 인수
            
        Returns:
            처리된 예외 또는 기본값
        """
        context, processed_exception = self.handle_exception(func, exception, *args, **kwargs)
        
        # 예외 처리
        custom_exception = await exception_manager.handle_exception(
            processed_exception,
            context=context,
            handler_name=self.handler_name or f"{func.__name__}_handler"
        )
        
        return custom_exception

    def __call__(self, func: F) -> F:
        """함수를 래핑하여 예외 처리"""
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # 예외 처리
                custom_exception = await self.handle_exception_async(func, e, *args, **kwargs)
                
                # 커스텀 로깅
                if self.log_level:
                    log_func = getattr(logger, self.log_level.lower(), logger.error)
                    log_func(f"함수 {func.__name__}에서 예외 발생: {custom_exception}")
                
                # 재발생 또는 기본값 반환
                if self.reraise:
                    raise custom_exception
                else:
                    return self.default_return
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 예외 처리
                context, processed_exception = self.handle_exception(func, e, *args, **kwargs)
                
                # 예외 처리 (비동기)
                custom_exception = asyncio.create_task(
                    exception_manager.handle_exception(
                        processed_exception,
                        context=context,
                        handler_name=self.handler_name or f"{func.__name__}_handler"
                    )
                )
                
                # 커스텀 로깅
                if self.log_level:
                    log_func = getattr(logger, self.log_level.lower(), logger.error)
                    log_func(f"함수 {func.__name__}에서 예외 발생: {e}")
                
                # 재발생 또는 기본값 반환
                if self.reraise:
                    raise processed_exception
                else:
                    return self.default_return
        
        # 비동기 함수 여부에 따라 적절한 래퍼 반환
        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        else:
            return sync_wrapper  # type: ignore


class RetryOnException(ExceptionHandler):
    """
    예외 발생 시 재시도하는 클래스 데코레이터
    
    ExceptionHandler를 상속받아 재시도 기능을 추가합니다.
    
    사용법:
        @RetryOnException(
            max_retries=3,
            retry_delay=1.0,
            backoff_factor=2.0,
            exception_types=[ConnectionError, TimeoutError]
        )
        def call_external_api():
            # 외부 API 호출 로직
            pass
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        backoff_factor: float = 2.0,
        exception_types: Optional[List[Type[Exception]]] = None,
        reraise_on_failure: bool = True,
        **kwargs
    ):
        """
        데코레이터 초기화
        
        Args:
            max_retries: 최대 재시도 횟수
            retry_delay: 초기 재시도 지연 시간 (초)
            backoff_factor: 지연 시간 증가 배수
            exception_types: 재시도할 예외 타입 목록
            reraise_on_failure: 최종 실패 시 예외 재발생 여부
            **kwargs: 부모 클래스 인수
        """
        super().__init__(
            exception_type=kwargs.get('exception_type', ExceptionType.EXTERNAL_SERVICE_ERROR),
            severity=kwargs.get('severity', ExceptionSeverity.MEDIUM),
            reraise=reraise_on_failure,
            **kwargs
        )
        
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.backoff_factor = backoff_factor
        self.exception_types = exception_types or []
        self.reraise_on_failure = reraise_on_failure
    
    def handle_exception(self, func: Callable, exception: Exception, *args, **kwargs) -> Any:
        """재시도 로직이 포함된 예외 처리"""
        # 재시도 대상 예외인지 확인
        if self.exception_types and not any(isinstance(exception, exc_type) for exc_type in self.exception_types):
            return super().handle_exception(func, exception, *args, **kwargs)
        
        # 부모 클래스의 예외 처리 로직 호출
        return super().handle_exception(func, exception, *args, **kwargs)
    
    def __call__(self, func: F) -> F:
        """함수를 래핑하여 재시도 로직 적용"""
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(self.max_retries + 1):
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    last_exception = e
                    
                    # 재시도 대상 예외인지 확인
                    if self.exception_types and not any(isinstance(e, exc_type) for exc_type in self.exception_types):
                        break
                    
                    # 마지막 시도인 경우
                    if attempt == self.max_retries:
                        break
                    
                    # 재시도 지연
                    delay = self.retry_delay * (self.backoff_factor ** attempt)
                    logger.warning(f"함수 {func.__name__} 재시도 {attempt + 1}/{self.max_retries} (지연: {delay:.2f}초): {e}")
                    await asyncio.sleep(delay)
            
            # 최종 예외 처리
            if last_exception:
                custom_exception = await self.handle_exception_async(func, last_exception, *args, **kwargs)
                
                if self.reraise_on_failure:
                    raise custom_exception
                else:
                    return self.default_return
            
            return self.default_return
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(self.max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    last_exception = e
                    
                    # 재시도 대상 예외인지 확인
                    if self.exception_types and not any(isinstance(e, exc_type) for exc_type in self.exception_types):
                        break
                    
                    # 마지막 시도인 경우
                    if attempt == self.max_retries:
                        break

                    # 재시도 지연
                    delay = self.retry_delay * (self.backoff_factor ** attempt)
                    logger.warning(f"함수 {func.__name__} 재시도 {attempt + 1}/{self.max_retries} (지연: {delay:.2f}초): {e}")
                    import time
                    time.sleep(delay)
            
            # 최종 예외 처리
            if last_exception:
                if self.reraise_on_failure:
                    raise last_exception
                else:
                    return self.default_return
            
            return self.default_return
        
        # 비동기 함수 여부에 따라 적절한 래퍼 반환
        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        else:
            return sync_wrapper  # type: ignore
    

class DatabaseExceptionHandler(ExceptionHandler):
    """
    데이터베이스 예외 처리 클래스 데코레이터
    
    ExceptionHandler를 상속받아 데이터베이스 관련 예외 처리를 추가합니다.
    
    사용법:
        @DatabaseExceptionHandler(reraise=False, default_return=[])
        def get_users_from_db():
            # 데이터베이스 조회 로직
            pass
    """
    
    def __init__(
        self,
        reraise: bool = True,
        default_return: Any = None,
        log_queries: bool = True,
        track_performance: bool = True,
        **kwargs
    ):
        """
        데코레이터 초기화
        
        Args:
            reraise: 예외 재발생 여부
            default_return: 예외 발생 시 반환할 기본값
            log_queries: 쿼리 로깅 여부
            track_performance: 성능 추적 여부
            **kwargs: 부모 클래스 인수
        """
        super().__init__(
            exception_type=kwargs.get('exception_type', ExceptionType.DATABASE_ERROR),
            severity=kwargs.get('severity', ExceptionSeverity.HIGH),
            reraise=reraise,
            default_return=default_return,
            **kwargs
        )
        
        self.log_queries = log_queries
        self.track_performance = track_performance
    
    def handle_exception(self, func: Callable, exception: Exception, *args, **kwargs) -> Any:
        """데이터베이스 예외 처리 로직"""
        # 데이터베이스 예외 생성
        db_exception = DatabaseException(
            message=f"데이터베이스 작업 실패: {str(exception)}",
            operation=func.__name__,
            original_exception=exception
        )
        
        # 쿼리 정보 추가 (가능한 경우)
        if self.log_queries and hasattr(exception, 'message'):
            db_exception.add_context_detail('query', str(exception))
        
        # 부모 클래스의 컨텍스트 생성
        context = create_exception_context(
            exception_type=self.exception_type,
            severity=self.severity,
            module=func.__module__,
            function=func.__name__
        )
        
        return context, db_exception
        
    def __call__(self, func: F) -> F:
        """함수를 래핑하여 데이터베이스 예외 처리"""
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = datetime.now() if self.track_performance else None
            
            try:
                result = await func(*args, **kwargs)
                
                # 성능 추적
                if self.track_performance and start_time:
                    duration = (datetime.now() - start_time).total_seconds()
                    logger.info(f"데이터베이스 작업 성공 ({func.__name__}): {duration:.3f}초")
                
                return result
                
            except Exception as e:
                # 실패한 쿼리 기록
                if self.track_performance and start_time:
                    duration = (datetime.now() - start_time).total_seconds()
                    logger.warning(f"데이터베이스 작업 실패 ({func.__name__}): {duration:.3f}초")
                
                # 예외 처리
                custom_exception = await self.handle_exception_async(func, e, *args, **kwargs)
                
                if self.reraise:
                    raise custom_exception
                else:
                    return self.default_return
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = datetime.now() if self.track_performance else None
            
            try:
                result = func(*args, **kwargs)
                
                # 성능 추적
                if self.track_performance and start_time:
                    duration = (datetime.now() - start_time).total_seconds()
                    logger.info(f"데이터베이스 작업 성공 ({func.__name__}): {duration:.3f}초")
                
                return result
                
            except Exception as e:
                # 실패한 쿼리 기록
                if self.track_performance and start_time:
                    duration = (datetime.now() - start_time).total_seconds()
                    logger.warning(f"데이터베이스 작업 실패 ({func.__name__}): {duration:.3f}초")
                
                # 예외 처리
                context, db_exception = self.handle_exception(func, e, *args, **kwargs)
                
                # 예외 처리 (비동기)
                asyncio.create_task(
                    exception_manager.handle_exception(
                        db_exception,
                        context=context,
                        handler_name=self.handler_name or f"{func.__name__}_db_handler"
                    )
                )
                
                if self.reraise:
                    raise db_exception
                else:
                    return self.default_return
        
        # 비동기 함수 여부에 따라 적절한 래퍼 반환
        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        else:
            return sync_wrapper  # type: ignore
    

class ValidationExceptionHandler(ExceptionHandler):
    """
    유효성 검증 예외 처리 클래스 데코레이터
    
    ExceptionHandler를 상속받아 유효성 검증 관련 예외 처리를 추가합니다.
    
    사용법:
        @ValidationExceptionHandler(reraise=True, collect_errors=True)
        def validate_user_input(data):
            # 유효성 검증 로직
            pass
    """
    
    def __init__(
        self,
        reraise: bool = True,
        default_return: Any = None,
        collect_errors: bool = False,
        **kwargs
    ):
        """
        데코레이터 초기화
        
        Args:
            reraise: 예외 재발생 여부
            default_return: 예외 발생 시 반환할 기본값
            collect_errors: 오류 수집 여부
            **kwargs: 부모 클래스 인수
        """
        super().__init__(
            exception_type=kwargs.get('exception_type', ExceptionType.VALIDATION_ERROR),
            severity=kwargs.get('severity', ExceptionSeverity.MEDIUM),
            reraise=reraise,
            default_return=default_return,
            **kwargs
        )
        
        self.collect_errors = collect_errors
        
        # 오류 수집
        self.validation_errors = []
    
    def handle_exception(self, func: Callable, exception: Exception, *args, **kwargs) -> Any:
        """유효성 검증 예외 처리 로직"""
        # 유효성 검증 예외 생성
        validation_exception = ValidationException(
            message=f"유효성 검증 실패: {str(exception)}",
            original_exception=exception
        )
        
        # 오류 수집
        if self.collect_errors:
            error_info = {
                'function': func.__name__,
                'error': str(exception),
                'timestamp': datetime.now(),
                'args': args,
                'kwargs': kwargs
            }
            self.validation_errors.append(error_info)
        
        # 부모 클래스의 컨텍스트 생성
        context = create_exception_context(
            exception_type=self.exception_type,
            severity=self.severity,
            module=func.__module__,
            function=func.__name__
        )
        
        return context, validation_exception
    
    def __call__(self, func: F) -> F:
        """함수를 래핑하여 유효성 검증 예외 처리"""
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # 예외 처리
                custom_exception = await self.handle_exception_async(func, e, *args, **kwargs)
                
                if self.reraise:
                    raise custom_exception
                else:
                    return self.default_return
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 예외 처리
                context, validation_exception = self.handle_exception(func, e, *args, **kwargs)
                
                # 예외 처리 (비동기)
                asyncio.create_task(
                    exception_manager.handle_exception(
                        validation_exception,
                        context=context,
                        handler_name=self.handler_name or f"{func.__name__}_validation_handler"
                    )
                )
                
                if self.reraise:
                    raise validation_exception
                else:
                    return self.default_return
        
        # 비동기 함수 여부에 따라 적절한 래퍼 반환
        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        else:
            return sync_wrapper  # type: ignore
    



class CircuitBreaker(ExceptionHandler):
    """
    서킷 브레이커 패턴 클래스 데코레이터
    
    ExceptionHandler를 상속받아 서킷 브레이커 패턴을 추가합니다.
    
    사용법:
        @CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=30,
            expected_exception=ConnectionError
        )
        def unreliable_service_call():
            # 불안정한 서비스 호출
            pass
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: Type[Exception] = Exception,
        monitor_performance: bool = True,
        **kwargs
    ):
        """
        데코레이터 초기화
        
        Args:
            failure_threshold: 실패 임계값
            recovery_timeout: 복구 대기 시간 (초)
            expected_exception: 감지할 예외 타입
            monitor_performance: 성능 모니터링 여부
            **kwargs: 부모 클래스 인수
        """
        super().__init__(
            exception_type=kwargs.get('exception_type', ExceptionType.EXTERNAL_SERVICE_ERROR),
            severity=kwargs.get('severity', ExceptionSeverity.HIGH),
            **kwargs
        )
        
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.monitor_performance = monitor_performance
        
        # 서킷 브레이커 상태
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        
        # 성능 모니터링
        self.success_count = 0
    
    def handle_exception(self, func: Callable, exception: Exception, *args, **kwargs) -> Any:
        """서킷 브레이커 예외 처리 로직"""
        if isinstance(exception, self.expected_exception):
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            # 실패 임계값 초과 시 OPEN 상태로 전환
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
                self._log_state_transition('OPEN')
                logger.error(f"서킷 브레이커 OPEN 상태로 전환: {func.__name__} (실패 {self.failure_count}회)")
        
        # 부모 클래스의 예외 처리
        return super().handle_exception(func, exception, *args, **kwargs)
    
    def __call__(self, func: F) -> F:
        """함수를 래핑하여 서킷 브레이커 패턴 적용"""
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            current_time = datetime.now()
            
            # OPEN 상태에서 복구 시간 확인
            if self.state == 'OPEN':
                if self.last_failure_time and (current_time - self.last_failure_time).total_seconds() > self.recovery_timeout:
                    self.state = 'HALF_OPEN'
                    self._log_state_transition('HALF_OPEN')
                    logger.info(f"서킷 브레이커 HALF_OPEN 상태로 전환: {func.__name__}")
                else:
                    raise ExternalServiceException(
                        message="서킷 브레이커 OPEN 상태: 서비스 호출이 차단되었습니다",
                        service_name=func.__name__
                    )
            
            start_time = datetime.now() if self.monitor_performance else None
            
            try:
                result = await func(*args, **kwargs)
                
                # 성공 처리
                if self.state == 'HALF_OPEN':
                    self.state = 'CLOSED'
                    self.failure_count = 0
                    self._log_state_transition('CLOSED')
                    logger.info(f"서킷 브레이커 CLOSED 상태로 전환: {func.__name__}")
                
                self.success_count += 1
                
                # 성능 모니터링
                if self.monitor_performance and start_time:
                    duration = (datetime.now() - start_time).total_seconds()
                    logger.info(f"서킷 브레이커 성공 ({func.__name__}): {duration:.3f}초")
                
                return result
                
            except self.expected_exception as e:
                # 예외 처리
                custom_exception = await self.handle_exception_async(func, e, *args, **kwargs)
                raise custom_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            current_time = datetime.now()
            
            # OPEN 상태에서 복구 시간 확인
            if self.state == 'OPEN':
                if self.last_failure_time and (current_time - self.last_failure_time).total_seconds() > self.recovery_timeout:
                    self.state = 'HALF_OPEN'
                    self._log_state_transition('HALF_OPEN')
                    logger.info(f"서킷 브레이커 HALF_OPEN 상태로 전환: {func.__name__}")
                else:
                    raise ExternalServiceException(
                        message="서킷 브레이커 OPEN 상태: 서비스 호출이 차단되었습니다",
                        service_name=func.__name__
                    )
            
            start_time = datetime.now() if self.monitor_performance else None
            
            try:
                result = func(*args, **kwargs)
                
                # 성공 처리
                if self.state == 'HALF_OPEN':
                    self.state = 'CLOSED'
                    self.failure_count = 0
                    self._log_state_transition('CLOSED')
                    logger.info(f"서킷 브레이커 CLOSED 상태로 전환: {func.__name__}")
                
                self.success_count += 1
                
                # 성능 모니터링
                if self.monitor_performance and start_time:
                    duration = (datetime.now() - start_time).total_seconds()
                    logger.info(f"서킷 브레이커 성공 ({func.__name__}): {duration:.3f}초")
                
                return result
                
            except self.expected_exception as e:
                # 예외 처리
                context, processed_exception = self.handle_exception(func, e, *args, **kwargs)
                raise processed_exception
        
        # 비동기 함수 여부에 따라 적절한 래퍼 반환
        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        else:
            return sync_wrapper  # type: ignore
    
    def _log_state_transition(self, new_state: str) -> None:
        """상태 전환 로그"""
        if self.monitor_performance:
            logger.info(f"서킷 브레이커 상태 변경: {self.state} -> {new_state}")

    
    def reset(self) -> None:
        """서킷 브레이커 상태 초기화"""
        self.state = 'CLOSED'
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None


class SuppressExceptions(ExceptionHandler):
    """
    예외 억제 클래스 데코레이터
    
    ExceptionHandler를 상속받아 예외 억제 기능을 추가합니다.
    
    사용법:
        @SuppressExceptions(
            exception_types=[FileNotFoundError, PermissionError],
            default_return=None,
            log_suppressed=True
        )
        def optional_file_operation():
            # 파일 작업 (실패해도 괜찮음)
            pass
    """
    
    def __init__(
        self,
        exception_types: Optional[List[Type[Exception]]] = None,
        default_return: Any = None,
        log_suppressed: bool = True,
        track_suppressed: bool = True,
        **kwargs
    ):
        """
        데코레이터 초기화
        
        Args:
            exception_types: 억제할 예외 타입 목록
            default_return: 기본 반환값
            log_suppressed: 억제된 예외 로깅 여부
            track_suppressed: 억제된 예외 추적 여부
            **kwargs: 부모 클래스 인수
        """
        super().__init__(
            exception_type=kwargs.get('exception_type', ExceptionType.SUPPRESSED),
            severity=kwargs.get('severity', ExceptionSeverity.LOW),
            reraise=False,
            default_return=default_return,
            **kwargs
        )
        
        self.exception_types = exception_types
        self.log_suppressed = log_suppressed
        self.track_suppressed = track_suppressed
        
        # 억제된 예외 추적
        self.suppressed_exceptions = []
    
    def handle_exception(self, func: Callable, exception: Exception, *args, **kwargs) -> Any:
        """예외 억제 처리 로직"""
        # 억제할 예외인지 확인
        if self.exception_types is None or any(isinstance(exception, exc_type) for exc_type in self.exception_types):
            if self.log_suppressed:
                logger.info(f"예외 억제됨 ({func.__name__}): {exception}")
            
            if self.track_suppressed:
                self.suppressed_exceptions.append({
                    'exception': exception,
                    'exception_type': type(exception).__name__,
                    'message': str(exception),
                    'function': func.__name__,
                    'timestamp': datetime.now()
                })
            
            # 부모 클래스의 컨텍스트 생성 (억제된 예외용)
            context = create_exception_context(
                exception_type=self.exception_type,
                severity=self.severity,
                module=func.__module__,
                function=func.__name__
            )
            
            return context, exception
        else:
            # 억제하지 않는 예외는 부모 클래스에서 처리
            return super().handle_exception(func, exception, *args, **kwargs)
    
    def __call__(self, func: F) -> F:
        """함수를 래핑하여 예외 억제"""
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # 예외 처리
                context, processed_exception = self.handle_exception(func, e, *args, **kwargs)
                
                # 억제할 예외인지 확인
                if self.exception_types is None or any(isinstance(e, exc_type) for exc_type in self.exception_types):
                    return self.default_return
                else:
                    # 억제하지 않는 예외는 재발생
                    raise processed_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 예외 처리
                context, processed_exception = self.handle_exception(func, e, *args, **kwargs)
                
                # 억제할 예외인지 확인
                if self.exception_types is None or any(isinstance(e, exc_type) for exc_type in self.exception_types):
                    return self.default_return
                else:
                    # 억제하지 않는 예외는 재발생
                    raise processed_exception
        
        # 비동기 함수 여부에 따라 적절한 래퍼 반환
        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        else:
            return sync_wrapper  # type: ignore


# 편의 함수들
def create_exception_handler(**kwargs) -> ExceptionHandler:
    """예외 핸들러 생성 편의 함수"""
    return ExceptionHandler(**kwargs)


def create_retry_handler(**kwargs) -> RetryOnException:
    """재시도 핸들러 생성 편의 함수"""
    return RetryOnException(**kwargs)


def create_database_handler(**kwargs) -> DatabaseExceptionHandler:
    """데이터베이스 핸들러 생성 편의 함수"""
    return DatabaseExceptionHandler(**kwargs)


def create_validation_handler(**kwargs) -> ValidationExceptionHandler:
    """유효성 검증 핸들러 생성 편의 함수"""
    return ValidationExceptionHandler(**kwargs)


def create_circuit_breaker(**kwargs) -> CircuitBreaker:
    """서킷 브레이커 생성 편의 함수"""
    return CircuitBreaker(**kwargs)


def create_suppression_handler(**kwargs) -> SuppressExceptions:
    """예외 억제 핸들러 생성 편의 함수"""
    return SuppressExceptions(**kwargs)