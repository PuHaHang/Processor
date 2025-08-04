"""
예외 타입과 상태 코드 정의 모듈

이 모듈은 시스템에서 사용되는 예외 타입과 상태 코드를 정의합니다.
커스텀 예외 클래스와 함께 사용되어 일관된 예외 처리를 제공합니다.
"""

from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


class ExceptionType(Enum):
    """
    예외 타입 분류
    
    시스템에서 발생할 수 있는 예외를 카테고리별로 분류합니다.
    """
    def __new__(cls, description: str) -> "ExceptionType":
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj
    
    def __init__(self, description: str) -> None:
        self.description = description
    
    def __str__(self) -> int:
        return self.value
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.value}"
    
    # 일반 예외
    UNKNOWN = ("unknown")
    SYSTEM_ERROR = ("system_error")
    SUPPRESSED = ("suppressed")
    
    # 데이터베이스 관련
    DATABASE_ERROR = ("database_error")
    CONNECTION_ERROR = ("connection_error")
    TRANSACTION_ERROR = ("transaction_error")
    
    # 유효성 검증
    VALIDATION_ERROR = ("validation_error")
    INVALID_INPUT = ("invalid_input")
    MISSING_REQUIRED_FIELD = ("missing_required_field")
    
    # 비즈니스 로직
    BUSINESS_LOGIC_ERROR = ("business_logic_error")
    PERMISSION_DENIED = ("permission_denied")
    RESOURCE_NOT_FOUND = ("resource_not_found")
    DUPLICATE_RESOURCE = ("duplicate_resource")
    
    # 외부 서비스
    EXTERNAL_SERVICE_ERROR = ("external_service_error")
    API_ERROR = ("api_error")
    NETWORK_ERROR = ("network_error")
    TIMEOUT_ERROR = ("timeout_error")
    
    # 인증/인가
    AUTHENTICATION_ERROR = ("authentication_error")
    AUTHORIZATION_ERROR = ("authorization_error")
    TOKEN_EXPIRED = ("token_expired")
    
    # 파일/데이터 처리
    FILE_ERROR = ("file_error")
    PROCESSING_ERROR = ("processing_error")
    CONVERSION_ERROR = ("conversion_error")
    
    # 미디어 처리
    AUDIO_PROCESSING_ERROR = ("audio_processing_error")
    VIDEO_PROCESSING_ERROR = ("video_processing_error") 
    TRANSCRIPTION_ERROR = ("transcription_error")
    
    # 데이터 파싱/변환
    JSON_PARSING_ERROR = ("json_parsing_error")
    URL_PARSING_ERROR = ("url_parsing_error")
    METADATA_EXTRACTION_ERROR = ("metadata_extraction_error")
    
    # 파이프라인/모델
    PIPELINE_ERROR = ("pipeline_error")
    MODEL_LOADING_ERROR = ("model_loading_error")
    REFINING_ERROR = ("refining_error")
    CONTENT_FILTERING_ERROR = ("content_filtering_error")
    
    # FCM 관련
    FCM_ERROR = ("fcm_error")
    FCM_INVALID_TOKEN = ("fcm_invalid_token")
    FCM_QUOTA_EXCEEDED = ("fcm_quota_exceeded")
    
    # Valkey 관련
    VALKEY_ERROR = ("valkey_error")
    VALKEY_CONNECTION_ERROR = ("valkey_connection_error")
    VALKEY_TIMEOUT = ("valkey_timeout")


class ExceptionSeverity(Enum):
    """
    예외 심각도 레벨
    
    예외의 심각도를 분류하여 적절한 처리 방식을 결정합니다.
    """
    LOW = "low"           # 정보성 - 시스템 운영에 영향 없음
    MEDIUM = "medium"     # 주의 - 일부 기능 영향
    HIGH = "high"         # 경고 - 중요 기능 영향
    CRITICAL = "critical" # 치명적 - 시스템 전체 영향


class ExceptionStatus(Enum):
    """
    예외 처리 상태
    
    예외가 발생한 후 처리 상태를 추적합니다.
    """
    OCCURRED = "occurred"       # 발생
    HANDLING = "handling"       # 처리 중
    RESOLVED = "resolved"       # 해결됨
    RETRYING = "retrying"       # 재시도 중
    FAILED = "failed"           # 처리 실패
    ESCALATED = "escalated"     # 에스컬레이션됨


@dataclass
class ExceptionContext:
    """
    예외 발생 맥락 정보
    
    예외가 발생한 상황과 관련된 메타데이터를 포함합니다.
    """
    # 기본 정보
    exception_type: ExceptionType
    severity: ExceptionSeverity
    status: ExceptionStatus = ExceptionStatus.OCCURRED
    
    # 메타데이터
    module: Optional[str] = None
    function: Optional[str] = None
    line_number: Optional[int] = None
    
    # 추가 정보
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    
    # 상세 정보
    details: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)
    
    # 재시도 정보
    retry_count: int = 0
    max_retries: int = 3
    
    def add_detail(self, key: str, value: Any) -> None:
        """상세 정보 추가"""
        self.details[key] = value
    
    def add_tag(self, key: str, value: str) -> None:
        """태그 추가"""
        self.tags[key] = value
    
    def increment_retry(self) -> None:
        """재시도 횟수 증가"""
        self.retry_count += 1
        self.status = ExceptionStatus.RETRYING
    
    def can_retry(self) -> bool:
        """재시도 가능 여부 확인"""
        return self.retry_count < self.max_retries
    
    def mark_resolved(self) -> None:
        """해결됨으로 표시"""
        self.status = ExceptionStatus.RESOLVED
    
    def mark_failed(self) -> None:
        """실패로 표시"""
        self.status = ExceptionStatus.FAILED
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'exception_type': self.exception_type.value,
            'severity': self.severity.value,
            'status': self.status.value,
            'module': self.module,
            'function': self.function,
            'line_number': self.line_number,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'request_id': self.request_id,
            'details': self.details,
            'tags': self.tags,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries
        }


# 예외 타입별 기본 설정
EXCEPTION_DEFAULTS: Dict[ExceptionType, Dict[str, Any]] = {
    ExceptionType.UNKNOWN: {
        'severity': ExceptionSeverity.MEDIUM,
        'max_retries': 0
    },
    ExceptionType.SYSTEM_ERROR: {
        'severity': ExceptionSeverity.CRITICAL,
        'max_retries': 1
    },
    ExceptionType.DATABASE_ERROR: {
        'severity': ExceptionSeverity.HIGH,
        'max_retries': 3
    },
    ExceptionType.CONNECTION_ERROR: {
        'severity': ExceptionSeverity.HIGH,
        'max_retries': 3
    },
    ExceptionType.TRANSACTION_ERROR: {
        'severity': ExceptionSeverity.HIGH,
        'max_retries': 2
    },
    ExceptionType.VALIDATION_ERROR: {
        'severity': ExceptionSeverity.LOW,
        'max_retries': 0
    },
    ExceptionType.INVALID_INPUT: {
        'severity': ExceptionSeverity.LOW,
        'max_retries': 0
    },
    ExceptionType.MISSING_REQUIRED_FIELD: {
        'severity': ExceptionSeverity.LOW,
        'max_retries': 0
    },
    ExceptionType.BUSINESS_LOGIC_ERROR: {
        'severity': ExceptionSeverity.MEDIUM,
        'max_retries': 1
    },
    ExceptionType.PERMISSION_DENIED: {
        'severity': ExceptionSeverity.MEDIUM,
        'max_retries': 0
    },
    ExceptionType.RESOURCE_NOT_FOUND: {
        'severity': ExceptionSeverity.LOW,
        'max_retries': 0
    },
    ExceptionType.DUPLICATE_RESOURCE: {
        'severity': ExceptionSeverity.LOW,
        'max_retries': 0
    },
    ExceptionType.EXTERNAL_SERVICE_ERROR: {
        'severity': ExceptionSeverity.MEDIUM,
        'max_retries': 3
    },
    ExceptionType.API_ERROR: {
        'severity': ExceptionSeverity.MEDIUM,
        'max_retries': 2
    },
    ExceptionType.NETWORK_ERROR: {
        'severity': ExceptionSeverity.HIGH,
        'max_retries': 3
    },
    ExceptionType.TIMEOUT_ERROR: {
        'severity': ExceptionSeverity.MEDIUM,
        'max_retries': 2
    },
    ExceptionType.AUTHENTICATION_ERROR: {
        'severity': ExceptionSeverity.MEDIUM,
        'max_retries': 1
    },
    ExceptionType.AUTHORIZATION_ERROR: {
        'severity': ExceptionSeverity.MEDIUM,
        'max_retries': 0
    },
    ExceptionType.TOKEN_EXPIRED: {
        'severity': ExceptionSeverity.LOW,
        'max_retries': 0
    },
    ExceptionType.FILE_ERROR: {
        'severity': ExceptionSeverity.MEDIUM,
        'max_retries': 2
    },
    ExceptionType.PROCESSING_ERROR: {
        'severity': ExceptionSeverity.MEDIUM,
        'max_retries': 2
    },
    ExceptionType.CONVERSION_ERROR: {
        'severity': ExceptionSeverity.MEDIUM,
        'max_retries': 1
    },
    ExceptionType.AUDIO_PROCESSING_ERROR: {
        'severity': ExceptionSeverity.MEDIUM,
        'max_retries': 2
    },
    ExceptionType.VIDEO_PROCESSING_ERROR: {
        'severity': ExceptionSeverity.MEDIUM,
        'max_retries': 2
    },
    ExceptionType.TRANSCRIPTION_ERROR: {
        'severity': ExceptionSeverity.MEDIUM,
        'max_retries': 3
    },
    ExceptionType.JSON_PARSING_ERROR: {
        'severity': ExceptionSeverity.LOW,
        'max_retries': 1
    },
    ExceptionType.URL_PARSING_ERROR: {
        'severity': ExceptionSeverity.LOW,
        'max_retries': 0
    },
    ExceptionType.METADATA_EXTRACTION_ERROR: {
        'severity': ExceptionSeverity.LOW,
        'max_retries': 2
    },
    ExceptionType.PIPELINE_ERROR: {
        'severity': ExceptionSeverity.HIGH,
        'max_retries': 1
    },
    ExceptionType.MODEL_LOADING_ERROR: {
        'severity': ExceptionSeverity.HIGH,
        'max_retries': 2
    },
    ExceptionType.REFINING_ERROR: {
        'severity': ExceptionSeverity.MEDIUM,
        'max_retries': 2
    },
    ExceptionType.CONTENT_FILTERING_ERROR: {
        'severity': ExceptionSeverity.MEDIUM,
        'max_retries': 1
    },
    ExceptionType.FCM_ERROR: {
        'severity': ExceptionSeverity.MEDIUM,
        'max_retries': 2
    },
    ExceptionType.FCM_INVALID_TOKEN: {
        'severity': ExceptionSeverity.LOW,
        'max_retries': 0
    },
    ExceptionType.FCM_QUOTA_EXCEEDED: {
        'severity': ExceptionSeverity.HIGH,
        'max_retries': 0
    },
    ExceptionType.VALKEY_ERROR: {
        'severity': ExceptionSeverity.MEDIUM,
        'max_retries': 3
    },
    ExceptionType.VALKEY_CONNECTION_ERROR: {
        'severity': ExceptionSeverity.HIGH,
        'max_retries': 3
    },
    ExceptionType.VALKEY_TIMEOUT: {
        'severity': ExceptionSeverity.MEDIUM,
        'max_retries': 2
    },
    ExceptionType.SUPPRESSED: {
        'severity': ExceptionSeverity.LOW,
        'max_retries': 0
    }
}


def create_exception_context(
    exception_type: ExceptionType,
    severity: Optional[ExceptionSeverity] = None,
    max_retries: Optional[int] = None,
    **kwargs
) -> ExceptionContext:
    """
    예외 컨텍스트 생성 헬퍼 함수
    
    Args:
        exception_type: 예외 타입
        severity: 심각도 (None이면 기본값 사용)
        max_retries: 최대 재시도 횟수 (None이면 기본값 사용)
        **kwargs: 추가 컨텍스트 정보
    
    Returns:
        ExceptionContext: 생성된 예외 컨텍스트
    """
    defaults = EXCEPTION_DEFAULTS.get(exception_type, {})
    
    return ExceptionContext(
        exception_type=exception_type,
        severity=severity or defaults.get('severity', ExceptionSeverity.MEDIUM),
        max_retries=max_retries or defaults.get('max_retries', 3),
        **kwargs
    ) 