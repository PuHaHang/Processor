"""
변환기 기본 클래스 모듈

이 모듈은 미디어 파일 형식을 변환하는 모든 변환기가 상속받는 추상 기본 클래스를 정의합니다.
"""

from abc import ABC

from src.common.processor.processor import Processor
from src.common.processor.processor_type import ProcessorType


class Converter (Processor, ABC):
    """
    미디어 변환을 수행하는 프로세서의 기본 추상 클래스
    
    오디오, 비디오 등의 미디어 파일 형식을 다른 형식으로 변환하는
    프로세서들이 상속받는 기본 클래스입니다.
    
    Attributes:
        processor_type (ProcessorType): 변환기 타입으로 고정
    """
    processor_type: ProcessorType = ProcessorType.CONVERTER
