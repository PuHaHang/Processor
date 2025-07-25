"""
버퍼 상태 정의 모듈

이 모듈은 프로세서 파이프라인에서 버퍼 데이터의 처리 상태를 나타내는 열거형을 정의합니다.
"""

from enum import Enum


class PayloadStatus (Enum):
    """
    버퍼 데이터의 처리 상태를 정의하는 열거형
    
    프로세서 파이프라인에서 각 단계별 처리 상태를 추적하기 위해 사용됩니다.
    """
    INIT = "INIT"                 # 초기 상태
    PROCESSING = "PROCESSING"     # 처리 중
    COMPLETED = "COMPLETED"       # 처리 완료
    FAILED = "FAILED"             # 처리 실패
    CANCELLED = "CANCELLED"       # 처리 취소