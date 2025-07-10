from abc import ABC, abstractmethod
import os
from typing import Any

from ._models import Classifier, ZeroShotClassifier
from ..types import Payload


class EvaluatorStrategy (ABC):
    # 이 전략이 지원하는 프로세서 타입들을 저장
    available_processors: list[type]
    
    # 모든 평가 전략이 공유하는 Zero-shot 분류기
    # 환경변수에서 모델명을 가져오거나 기본 모델 사용
    classifier: Classifier = ZeroShotClassifier(
        os.getenv("ZEROSHOT_MODEL_NAME", "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7")
    )

    @abstractmethod
    def is_supported(self, payload: Payload) -> bool:
        # 주어진 페이로드가 이 전략에서 지원되는지 확인하는 추상 메소드
        # 하위 클래스에서 반드시 구현해야 함
        pass

    @abstractmethod
    def evaluate(self, payload: Payload) -> bool:
        # 실제 평가를 수행하는 추상 메소드
        # 하위 클래스에서 반드시 구현해야 함
        pass

    def get_available_processors(self) -> list[type]:
        # 이 전략이 지원하는 프로세서 타입들을 반환
        return self.available_processors
    
    def _evaluate(self, sequence: str|dict[str, Any]) -> bool:
        # 공통 분류기를 사용한 평가 수행
        # 문자열이나 딕셔너리 형태의 데이터를 받아서 레시피 관련 여부를 판단
        return self.classifier.evaluate(sequence)