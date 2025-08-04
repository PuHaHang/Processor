"""
커스텀 예외 클래스 정의 모듈

이 모듈은 시스템에서 사용되는 커스텀 예외 클래스들을 정의합니다.
각 예외 클래스는 예외 발생 시 상태 정보와 컨텍스트를 포함할 수 있습니다.
"""

import traceback
from typing import Optional, Dict, Any, Union
from datetime import datetime

from .exception_types import (
    ExceptionType,
    ExceptionSeverity,
    ExceptionStatus,
    ExceptionContext,
    create_exception_context
)


class BaseCustomException(Exception):
    """
    모든 커스텀 예외의 기본 클래스
    
    예외 발생 시 컨텍스트 정보와 상태를 포함할 수 있는 기본 기능을 제공합니다.
    """
    
    def __init__(
        self,
        message: str,
        exception_type: ExceptionType = ExceptionType.UNKNOWN,
        severity: Optional[ExceptionSeverity] = None,
        context: Optional[ExceptionContext] = None,
        original_exception: Optional[Exception] = None,
        **kwargs
    ):
        """
        커스텀 예외 초기화
        
        Args:
            message: 예외 메시지
            exception_type: 예외 타입
            severity: 심각도
            context: 예외 컨텍스트
            original_exception: 원본 예외
            **kwargs: 추가 컨텍스트 정보
        """
        super().__init__(message)
        self.message = message
        self.exception_type = exception_type
        self.original_exception = original_exception
        self.timestamp = datetime.now()
        
        # 컨텍스트 생성 또는 업데이트
        if context:
            self.context = context
        else:
            self.context = create_exception_context(
                exception_type=exception_type,
                severity=severity,
                **kwargs
            )
        
        # 추가 정보 저장
        if original_exception:
            self.context.add_detail('original_exception_type', type(original_exception).__name__)
            self.context.add_detail('original_exception_message', str(original_exception))
        
        # 스택 트레이스 저장
        self.stack_trace = traceback.format_exc()
        
    def get_context(self) -> ExceptionContext:
        """예외 컨텍스트 반환"""
        return self.context
    
    def get_severity(self) -> ExceptionSeverity:
        """예외 심각도 반환"""
        return self.context.severity
    
    def get_status(self) -> ExceptionStatus:
        """예외 상태 반환"""
        return self.context.status
    
    def add_context_detail(self, key: str, value: Any) -> None:
        """컨텍스트 상세 정보 추가"""
        self.context.add_detail(key, value)
    
    def add_context_tag(self, key: str, value: str) -> None:
        """컨텍스트 태그 추가"""
        self.context.add_tag(key, value)
    
    def update_status(self, status: ExceptionStatus) -> None:
        """예외 상태 업데이트"""
        self.context.status = status
    
    def to_dict(self) -> Dict[str, Any]:
        """예외 정보를 딕셔너리로 변환"""
        return {
            'message': self.message,
            'exception_type': self.exception_type.value,
            'severity': self.context.severity.value,
            'status': self.context.status.value,
            'timestamp': self.timestamp.isoformat(),
            'context': self.context.to_dict(),
            'stack_trace': self.stack_trace,
            'original_exception': {
                'type': type(self.original_exception).__name__,
                'message': str(self.original_exception)
            } if self.original_exception else None
        }
    
    def __str__(self) -> str:
        """문자열 표현"""
        return f"[{self.exception_type.value}] {self.message}"
    
    def __repr__(self) -> str:
        """객체 표현"""
        return f"{self.__class__.__name__}(type={self.exception_type.value}, message='{self.message}')"


class ValidationException(BaseCustomException):
    """
    유효성 검증 예외 클래스
    
    입력 데이터 검증 실패 시 발생하는 예외입니다.
    """
    
    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        field_value: Optional[Any] = None,
        validation_rule: Optional[str] = None,
        **kwargs
    ):
        """
        유효성 검증 예외 초기화
        
        Args:
            message: 예외 메시지
            field_name: 검증 실패한 필드명
            field_value: 검증 실패한 값
            validation_rule: 검증 규칙
            **kwargs: 추가 컨텍스트 정보
        """
        super().__init__(
            message=message,
            exception_type=ExceptionType.VALIDATION_ERROR,
            **kwargs
        )
        
        if field_name:
            self.add_context_detail('field_name', field_name)
        if field_value is not None:
            self.add_context_detail('field_value', field_value)
        if validation_rule:
            self.add_context_detail('validation_rule', validation_rule)


class DatabaseException(BaseCustomException):
    """
    데이터베이스 관련 예외 클래스
    
    데이터베이스 연결, 쿼리 실행, 트랜잭션 처리 등에서 발생하는 예외입니다.
    """
    
    def __init__(
        self,
        message: str,
        query: Optional[str] = None,
        table_name: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        """
        데이터베이스 예외 초기화
        
        Args:
            message: 예외 메시지
            query: 실행한 쿼리
            table_name: 테이블명
            operation: 실행한 작업
            **kwargs: 추가 컨텍스트 정보
        """
        super().__init__(
            message=message,
            exception_type=ExceptionType.DATABASE_ERROR,
            **kwargs
        )
        
        if query:
            self.add_context_detail('query', query)
        if table_name:
            self.add_context_detail('table_name', table_name)
        if operation:
            self.add_context_detail('operation', operation)


class BusinessLogicException(BaseCustomException):
    """
    비즈니스 로직 예외 클래스
    
    비즈니스 규칙 위반 시 발생하는 예외입니다.
    """
    
    def __init__(
        self,
        message: str,
        rule_name: Optional[str] = None,
        entity_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        **kwargs
    ):
        """
        비즈니스 로직 예외 초기화
        
        Args:
            message: 예외 메시지
            rule_name: 위반된 규칙명
            entity_id: 관련 엔티티 ID
            entity_type: 관련 엔티티 타입
            **kwargs: 추가 컨텍스트 정보
        """
        super().__init__(
            message=message,
            exception_type=ExceptionType.BUSINESS_LOGIC_ERROR,
            **kwargs
        )
        
        if rule_name:
            self.add_context_detail('rule_name', rule_name)
        if entity_id:
            self.add_context_detail('entity_id', entity_id)
        if entity_type:
            self.add_context_detail('entity_type', entity_type)


class ExternalServiceException(BaseCustomException):
    """
    외부 서비스 연동 예외 클래스
    
    외부 API 호출, 네트워크 통신 등에서 발생하는 예외입니다.
    """
    
    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        endpoint: Optional[str] = None,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        외부 서비스 예외 초기화
        
        Args:
            message: 예외 메시지
            service_name: 서비스명
            endpoint: 호출한 엔드포인트
            status_code: HTTP 상태 코드
            response_data: 응답 데이터
            **kwargs: 추가 컨텍스트 정보
        """
        super().__init__(
            message=message,
            exception_type=ExceptionType.EXTERNAL_SERVICE_ERROR,
            **kwargs
        )
        
        if service_name:
            self.add_context_detail('service_name', service_name)
        if endpoint:
            self.add_context_detail('endpoint', endpoint)
        if status_code:
            self.add_context_detail('status_code', status_code)
        if response_data:
            self.add_context_detail('response_data', response_data)


class AuthenticationException(BaseCustomException):
    """
    인증 예외 클래스
    
    사용자 인증 실패 시 발생하는 예외입니다.
    """
    
    def __init__(
        self,
        message: str,
        user_id: Optional[str] = None,
        auth_method: Optional[str] = None,
        **kwargs
    ):
        """
        인증 예외 초기화
        
        Args:
            message: 예외 메시지
            user_id: 사용자 ID
            auth_method: 인증 방법
            **kwargs: 추가 컨텍스트 정보
        """
        super().__init__(
            message=message,
            exception_type=ExceptionType.AUTHENTICATION_ERROR,
            **kwargs
        )
        
        if user_id:
            self.add_context_detail('user_id', user_id)
        if auth_method:
            self.add_context_detail('auth_method', auth_method)


class AuthorizationException(BaseCustomException):
    """
    인가 예외 클래스
    
    사용자 권한 부족 시 발생하는 예외입니다.
    """
    
    def __init__(
        self,
        message: str,
        user_id: Optional[str] = None,
        required_permission: Optional[str] = None,
        resource_id: Optional[str] = None,
        **kwargs
    ):
        """
        인가 예외 초기화
        
        Args:
            message: 예외 메시지
            user_id: 사용자 ID
            required_permission: 필요한 권한
            resource_id: 리소스 ID
            **kwargs: 추가 컨텍스트 정보
        """
        super().__init__(
            message=message,
            exception_type=ExceptionType.AUTHORIZATION_ERROR,
            **kwargs
        )
        
        if user_id:
            self.add_context_detail('user_id', user_id)
        if required_permission:
            self.add_context_detail('required_permission', required_permission)
        if resource_id:
            self.add_context_detail('resource_id', resource_id)


class ProcessingException(BaseCustomException):
    """
    데이터 처리 예외 클래스
    
    파일 처리, 데이터 변환 등에서 발생하는 예외입니다.
    """
    
    def __init__(
        self,
        message: str,
        processor_name: Optional[str] = None,
        input_data_type: Optional[str] = None,
        expected_output_type: Optional[str] = None,
        **kwargs
    ):
        """
        처리 예외 초기화
        
        Args:
            message: 예외 메시지
            processor_name: 프로세서명
            input_data_type: 입력 데이터 타입
            expected_output_type: 예상 출력 타입
            **kwargs: 추가 컨텍스트 정보
        """
        super().__init__(
            message=message,
            exception_type=ExceptionType.PROCESSING_ERROR,
            **kwargs
        )
        
        if processor_name:
            self.add_context_detail('processor_name', processor_name)
        if input_data_type:
            self.add_context_detail('input_data_type', input_data_type)
        if expected_output_type:
            self.add_context_detail('expected_output_type', expected_output_type)


class FCMException(BaseCustomException):
    """
    FCM 관련 예외 클래스
    
    Firebase Cloud Messaging 관련 예외입니다.
    """
    
    def __init__(
        self,
        message: str,
        fcm_token: Optional[str] = None,
        notification_id: Optional[str] = None,
        **kwargs
    ):
        """
        FCM 예외 초기화
        
        Args:
            message: 예외 메시지
            fcm_token: FCM 토큰
            notification_id: 알림 ID
            **kwargs: 추가 컨텍스트 정보
        """
        super().__init__(
            message=message,
            exception_type=ExceptionType.FCM_ERROR,
            **kwargs
        )
        
        if fcm_token:
            self.add_context_detail('fcm_token', fcm_token)
        if notification_id:
            self.add_context_detail('notification_id', notification_id)


class ValkeyException(BaseCustomException):
    """
    Valkey 관련 예외 클래스
    
    AWS Valkey 관련 예외입니다.
    """
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        key: Optional[str] = None,
        **kwargs
    ):
        """
        Valkey 예외 초기화
        
        Args:
            message: 예외 메시지
            operation: 실행한 작업
            key: 관련 키
            **kwargs: 추가 컨텍스트 정보
        """
        super().__init__(
            message=message,
            exception_type=ExceptionType.VALKEY_ERROR,
            **kwargs
        )
        
        if operation:
            self.add_context_detail('operation', operation)
        if key:
            self.add_context_detail('key', key)


# 예외 팩토리 함수들
def create_validation_exception(
    message: str,
    field_name: Optional[str] = None,
    field_value: Optional[Any] = None,
    validation_rule: Optional[str] = None
) -> ValidationException:
    """유효성 검증 예외 생성"""
    return ValidationException(
        message=message,
        field_name=field_name,
        field_value=field_value,
        validation_rule=validation_rule
    )


def create_database_exception(
    message: str,
    query: Optional[str] = None,
    table_name: Optional[str] = None,
    operation: Optional[str] = None,
    original_exception: Optional[Exception] = None
) -> DatabaseException:
    """데이터베이스 예외 생성"""
    return DatabaseException(
        message=message,
        query=query,
        table_name=table_name,
        operation=operation,
        original_exception=original_exception
    )


def create_business_logic_exception(
    message: str,
    rule_name: Optional[str] = None,
    entity_id: Optional[str] = None,
    entity_type: Optional[str] = None
) -> BusinessLogicException:
    """비즈니스 로직 예외 생성"""
    return BusinessLogicException(
        message=message,
        rule_name=rule_name,
        entity_id=entity_id,
        entity_type=entity_type
    )


def create_external_service_exception(
    message: str,
    service_name: Optional[str] = None,
    endpoint: Optional[str] = None,
    status_code: Optional[int] = None,
    response_data: Optional[Dict[str, Any]] = None
) -> ExternalServiceException:
    """외부 서비스 예외 생성"""
    return ExternalServiceException(
        message=message,
        service_name=service_name,
        endpoint=endpoint,
        status_code=status_code,
        response_data=response_data
    )


def wrap_exception(
    exception: Union[Exception, None],
    message: Optional[str] = None,
    exception_type: ExceptionType = ExceptionType.UNKNOWN,
    **kwargs
) -> BaseCustomException:
    """
    일반 예외를 커스텀 예외로 래핑
    
    Args:
        exception: 원본 예외
        message: 커스텀 메시지 (None이면 원본 메시지 사용)
        exception_type: 예외 타입
        **kwargs: 추가 컨텍스트 정보
    
    Returns:
        BaseCustomException: 래핑된 커스텀 예외
    """
    return BaseCustomException(
        message=message or str(exception),
        exception_type=exception_type,
        original_exception=exception,
        **kwargs
    ) 