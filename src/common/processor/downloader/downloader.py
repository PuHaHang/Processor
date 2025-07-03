"""
다운로더 기본 클래스 모듈

이 모듈은 URL에서 미디어 파일을 다운로드하는 모든 다운로더가 상속받는 추상 기본 클래스를 정의합니다.
"""

from abc import ABC

from src.common.processor.processor import Processor
from src.common.processor.processor_type import ProcessorType


class Downloader (Processor, ABC):
    """
    미디어 다운로드를 수행하는 프로세서의 기본 추상 클래스
    
    URL에서 비디오, 오디오 등의 미디어 파일을 다운로드하는
    프로세서들이 상속받는 기본 클래스입니다.
    
    Attributes:
        processor_type (ProcessorType): 다운로더 타입으로 고정
    """
    processor_type: ProcessorType = ProcessorType.DOWNLOADER

