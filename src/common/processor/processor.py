"""
프로세서 기본 클래스 모듈

이 모듈은 모든 프로세서가 상속받아야 하는 추상 기본 클래스를 정의합니다.
"""

from abc import ABC, abstractmethod
from typing import Tuple

from .types import Payload
from .types import DataType
from .processor_type import ProcessorType


class Processor (ABC):
    """
    모든 프로세서의 기본 추상 클래스
    
    이 클래스는 데이터 처리 파이프라인에서 사용되는 모든 프로세서가
    구현해야 하는 공통 인터페이스를 정의합니다.
    
    Attributes:
        data_flow (Tuple[DataType, DataType]): 입력 → 출력 데이터 타입
        processor_type (ProcessorType): 프로세서의 타입
        available_input_ext (list[str]): 지원하는 입력 파일 확장자 목록
        available_output_ext (list[str]): 지원하는 출력 파일 확장자 목록
        default_output_ext (str): 기본 출력 파일 확장자
    """
    data_flow: Tuple[DataType, DataType]
    processor_type: ProcessorType
    available_input_ext: list[str]
    available_output_ext: list[str]
    default_output_ext: str
    next_processor: 'Processor'

    @abstractmethod
    def process(self, payload: Payload, opt: dict = {}) -> Payload:
        """
        버퍼 데이터를 처리하는 추상 메소드
        
        Args:
            payload (Payload): 처리할 버퍼 데이터
            opt (dict, optional): 처리 옵션
        
        Returns:
            Payload: 처리된 버퍼 데이터
        """
        ...


    @abstractmethod
    def is_supported(self, payload: Payload) -> bool:
        """
        버퍼 데이터가 이 프로세서에서 지원되는지 확인하는 추상 메소드
        
        Args:
            payload (Payload): 확인할 버퍼 데이터
        
        Returns:
            bool: 지원 여부
        """
        ...


    def set_next_processor(self, processor: 'Processor') -> 'Processor':
        """
        다음 프로세서를 설정합니다.
        
        Args:
            processor (Processor): 설정할 다음 프로세서
        """
        self.next_processor = processor
        return processor


    def get_data_flow(self) -> Tuple[DataType, DataType]:
        """
        프로세서의 데이터 플로우를 반환합니다.
        
        Returns:
            Tuple[DataType, DataType]: (입력 타입, 출력 타입)
        """
        return self.data_flow


    def get_processor_type(self) -> ProcessorType:
        """
        프로세서의 타입을 반환합니다.
        
        Returns:
            ProcessorType: 프로세서 타입
        """
        return self.processor_type


    def get_available_input_ext(self) -> list[str]:
        """
        지원하는 입력 파일 확장자 목록을 반환합니다.
        
        Returns:
            list[str]: 입력 확장자 목록
        """
        return self.available_input_ext


    def get_available_output_ext(self) -> list[str]:
        """
        지원하는 출력 파일 확장자 목록을 반환합니다.
        
        Returns:
            list[str]: 출력 확장자 목록
        """
        return self.available_output_ext


    def get_default_output_ext(self) -> str:
        """
        기본 출력 파일 확장자를 반환합니다.
        
        Returns:
            str: 기본 출력 확장자
        """
        return self.default_output_ext
