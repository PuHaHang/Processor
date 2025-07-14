"""
Refiner 전략 인터페이스

이 모듈은 다양한 리파이너 전략들이 구현해야 하는
공통 인터페이스를 정의합니다.
"""

from abc import ABC, abstractmethod
from ..types import Payload


class RefinerStrategy(ABC):
    """
    리파이너 전략의 추상 기본 클래스
    
    모든 리파이너 전략은 이 클래스를 상속받아
    is_supported와 process 메소드를 구현해야 합니다.
    """
    
    @abstractmethod
    def is_supported(self, payload: Payload) -> bool:
        """
        주어진 페이로드가 이 전략에서 지원되는지 확인
        
        Args:
            payload: 검사할 페이로드
            
        Returns:
            bool: 지원 가능하면 True, 아니면 False
        """
        pass
    
    @abstractmethod
    def process(self, payload: Payload, opt: dict = {}) -> Payload:
        """
        페이로드를 정제(refine)하여 처리
        
        Args:
            payload: 처리할 페이로드
            opt: 처리 옵션
            
        Returns:
            Payload: 정제된 페이로드
        """
        pass
