"""
Processor 패키지

이 패키지는 데이터 처리 파이프라인을 위한 다양한 프로세서들을 제공합니다.
URL에서 미디어 다운로드, 형식 변환, 음성 인식, 데이터 정제 등의 기능을 포함합니다.
"""

# 주요 프로세서들 import
from .agent import Agent
from .processor import Processor
from .processor_type import ProcessorType

# 구체적인 프로세서들
from .downloader import Downloader
from .converter import Converter
from .transcriber import Transcriber
from .refiner import Refiner
from .evaluator import Evaluator
from .formatter import Formatter

# 타입들
from .types import DataType, Payload, PayloadStatus

# 예외 시스템 초기화
from ..exception import initialize_exception_system

# 패키지 로드 시 예외 시스템 자동 초기화
try:
    initialize_exception_system(
        log_level="INFO",
        register_defaults=True
    )
except Exception as e:
    # 초기화 실패 시에도 패키지는 로드되어야 함
    print(f"⚠️ 예외 시스템 초기화 실패: {e}")

# 패키지 메타데이터
__version__ = "1.0.0"
__author__ = "PuHaHang Development Team"
__description__ = "데이터 처리 파이프라인 프로세서 패키지"

# 패키지 레벨 익스포트
__all__ = [
    # 핵심 클래스
    'Agent',
    'Processor',
    'ProcessorType',
    
    # 프로세서들
    'Downloader',
    'Converter', 
    'Transcriber',
    'Refiner',
    'Evaluator',
    'Formatter',
    
    # 타입들
    'DataType',
    'Payload',
    'PayloadStatus',
]
