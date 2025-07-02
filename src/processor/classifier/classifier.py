"""
분류기 기본 클래스 모듈

이 모듈은 데이터 분류를 수행하는 모든 분류기가 상속받는 추상 기본 클래스를 정의합니다.
"""

from abc import ABC

from src.processor.processor import Processor
from src.processor.processor_type import ProcessorType

class Classifier (Processor, ABC):
    """
    데이터 분류를 수행하는 프로세서의 기본 추상 클래스
    
    입력 데이터를 분석하여 적절한 카테고리나 타입으로 분류하는
    프로세서들이 상속받는 기본 클래스입니다.
    
    Attributes:
        processor_type (ProcessorType): 분류기 타입으로 고정
    """
    processor_type: ProcessorType = ProcessorType.CLASSIFIER
