"""
예외 처리 패키지

이 패키지는 시스템 전체의 예외 처리를 위한 통합 솔루션을 제공합니다.
커스텀 예외 클래스, 데코레이터, 예외 관리자 등을 포함합니다.

주요 구성 요소:
- exception_types: 예외 타입과 상태 코드 정의
- custom_exceptions: 커스텀 예외 클래스들
- exception_manager: 예외 관리자 (싱글톤)
- decorators: 예외 처리 데코레이터들

사용법:
    # 기본 예외 처리 데코레이터
    @exception_handler(
        exception_type=ExceptionType.DATABASE_ERROR,
        severity=ExceptionSeverity.HIGH
    )
    def database_operation():
        pass
    
    # 재시도 데코레이터
    @retry_on_exception(max_retries=3, retry_delay=1.0)
    def external_api_call():
        pass
    
    # 커스텀 예외 발생
    raise ValidationException(
        message="유효하지 않은 입력입니다",
        field_name="email",
        validation_rule="email_format"
    )
    
    # 예외 관리자 사용
    from src.common.exception import exception_manager
    
    try:
        # 위험한 작업
        pass
    except Exception as e:
        await exception_manager.handle_exception(e)
"""

# 예외 타입과 상태 코드
from .exception_types import (
    ExceptionType,
    ExceptionSeverity,
    ExceptionStatus,
    ExceptionContext,
    create_exception_context,
    EXCEPTION_DEFAULTS
)

# 커스텀 예외 클래스들
from .custom_exceptions import (
    BaseCustomException,
    ValidationException,
    DatabaseException,
    BusinessLogicException,
    ExternalServiceException,
    AuthenticationException,
    AuthorizationException,
    ProcessingException,
    FCMException,
    ValkeyException,
    # 팩토리 함수들
    create_validation_exception,
    create_database_exception,
    create_business_logic_exception,
    create_external_service_exception,
    wrap_exception
)

# 예외 관리자
from .exception_manager import (
    ExceptionManager,
    ExceptionRecord,
    exception_manager,
    get_exception_manager,
    handle_exception,
    register_exception_handler,
    resolve_exception
)

# 클래스 기반 데코레이터들
from .class_decorators import (
    ExceptionHandler,
    RetryOnException,
    DatabaseExceptionHandler,
    ValidationExceptionHandler,
    CircuitBreaker,
    SuppressExceptions,
    # 편의 함수들
    create_exception_handler,
    create_retry_handler,
    create_database_handler,
    create_validation_handler,
    create_circuit_breaker,
    create_suppression_handler
)

# 패키지 메타데이터
__version__ = "1.0.0"
__author__ = "PuHaHang Development Team"
__email__ = "dev@puhahang.com"
__description__ = "통합 예외 처리 시스템"

# 편의 함수들
def setup_exception_logging(log_level: str = "INFO") -> None:
    """
    예외 로깅 설정
    
    Args:
        log_level: 로그 레벨 ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
    """
    import logging
    
    # 예외 관련 로거 설정
    loggers = [
        'exception.low',
        'exception.medium', 
        'exception.high',
        'exception.critical',
        'src.common.exception'
    ]
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, log_level.upper()))
        
        # 핸들러가 없으면 기본 핸들러 추가
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)


def get_exception_metrics() -> dict:
    """
    예외 메트릭 조회
    
    Returns:
        dict: 예외 메트릭 정보
    """
    return exception_manager.get_metrics()


def clear_exception_history(days: int = 7) -> int:
    """
    예외 기록 정리
    
    Args:
        days: 보관 기간 (일)
    
    Returns:
        int: 삭제된 기록 수
    """
    return exception_manager.clear_old_records(days)


def register_default_handlers() -> None:
    """기본 예외 핸들러들을 등록합니다."""
    
    def database_error_handler(exception: BaseCustomException) -> None:
        """데이터베이스 오류 핸들러"""
        if exception.get_severity() == ExceptionSeverity.CRITICAL:
            # 중요한 데이터베이스 오류는 알림 시스템으로 전송
            print(f"🚨 [CRITICAL DB ERROR] {exception.message}")
    
    def external_service_error_handler(exception: BaseCustomException) -> None:
        """외부 서비스 오류 핸들러"""
        if exception.context.retry_count >= 3:
            # 재시도 횟수 초과 시 알림
            print(f"⚠️ [SERVICE ERROR] {exception.message} (재시도 {exception.context.retry_count}회)")
    
    def validation_error_handler(exception: BaseCustomException) -> None:
        """유효성 검증 오류 핸들러"""
        # 유효성 검증 오류는 사용자에게 친화적인 메시지로 변환
        print(f"ℹ️ [VALIDATION ERROR] {exception.message}")
    
    # 핸들러 등록
    register_exception_handler(ExceptionType.DATABASE_ERROR, database_error_handler)
    register_exception_handler(ExceptionType.EXTERNAL_SERVICE_ERROR, external_service_error_handler)
    register_exception_handler(ExceptionType.VALIDATION_ERROR, validation_error_handler)


# 자동 초기화
def initialize_exception_system(
    log_level: str = "INFO",
    register_defaults: bool = True
) -> None:
    """
    예외 시스템 초기화
    
    Args:
        log_level: 로그 레벨
        register_defaults: 기본 핸들러 등록 여부
    """
    setup_exception_logging(log_level)
    
    if register_defaults:
        register_default_handlers()
    
    print("🎯 예외 처리 시스템이 초기화되었습니다.")


# 컨텍스트 관리자들
class exception_context:
    """
    예외 컨텍스트 관리자
    
    사용법:
        with exception_context(
            exception_type=ExceptionType.DATABASE_ERROR,
            severity=ExceptionSeverity.HIGH,
            user_id="user123"
        ):
            # 예외 발생 가능한 코드
            pass
    """
    
    def __init__(
        self,
        exception_type: ExceptionType = ExceptionType.UNKNOWN,
        severity: ExceptionSeverity = ExceptionSeverity.MEDIUM,
        **kwargs
    ):
        self.exception_type = exception_type
        self.severity = severity
        self.context_kwargs = kwargs
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # 예외 발생 시 자동 처리
            context = create_exception_context(
                exception_type=self.exception_type,
                severity=self.severity,
                **self.context_kwargs
            )
            
            import asyncio
            asyncio.create_task(
                exception_manager.handle_exception(
                    exc_val,
                    context=context
                )
            )
        
        return False  # 예외 전파


# 패키지 레벨 익스포트
__all__ = [
    # 타입과 상태
    'ExceptionType',
    'ExceptionSeverity', 
    'ExceptionStatus',
    'ExceptionContext',
    'create_exception_context',
    'EXCEPTION_DEFAULTS',
    
    # 커스텀 예외
    'BaseCustomException',
    'ValidationException',
    'DatabaseException',
    'BusinessLogicException',
    'ExternalServiceException',
    'AuthenticationException',
    'AuthorizationException',
    'ProcessingException',
    'FCMException',
    'ValkeyException',
    
    # 팩토리 함수
    'create_validation_exception',
    'create_database_exception',
    'create_business_logic_exception',
    'create_external_service_exception',
    'wrap_exception',
    
    # 예외 관리자
    'ExceptionManager',
    'ExceptionRecord',
    'exception_manager',
    'get_exception_manager',
    'handle_exception',
    'register_exception_handler',
    'resolve_exception',
    
    # 데코레이터
    # 클래스 기반 데코레이터
    'ExceptionHandler',
    'RetryOnException',
    'DatabaseExceptionHandler',
    'ValidationExceptionHandler',
    'CircuitBreaker',
    'SuppressExceptions',
    'create_exception_handler',
    'create_retry_handler',
    'create_database_handler',
    'create_validation_handler',
    'create_circuit_breaker',
    'create_suppression_handler',
    
    # 편의 함수
    'setup_exception_logging',
    'get_exception_metrics',
    'clear_exception_history',
    'register_default_handlers',
    'initialize_exception_system',
    'exception_context',
]

# 패키지 임포트 시 자동 초기화 (선택사항)
# initialize_exception_system()
