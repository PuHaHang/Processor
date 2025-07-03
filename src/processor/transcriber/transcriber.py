"""
전사기 기본 클래스 모듈

이 모듈은 오디오를 텍스트로 변환하는 모든 전사기가 상속받는 추상 기본 클래스를 정의합니다.
"""

from abc import ABC

from src.processor.processor import Processor
from src.processor.processor_type import ProcessorType

class Transcriber (Processor, ABC):
    """
    오디오 전사를 수행하는 프로세서의 기본 추상 클래스
    
    오디오 데이터를 텍스트로 변환하는 음성 인식 프로세서들이
    상속받는 기본 클래스입니다.
    
    Attributes:
        processor_type (ProcessorType): 전사기 타입으로 고정
    """
    processor_type: ProcessorType = ProcessorType.TRANSCRIBER