from abc import ABC, abstractmethod
import os
from typing import Any

from ._models import ZeroShotClassifier
from ..types import Payload


class EvaluatorStrategy (ABC):
    available_processors: list[type]
    classifier = ZeroShotClassifier(
        os.getenv("ZEROSHOT_MODEL_NAME", "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7")
    )

    @abstractmethod
    def is_supported(self, payload: Payload) -> bool:
        pass

    @abstractmethod
    def evaluate(self, payload: Payload) -> bool:
        pass

    def get_available_processors(self) -> list[type]:
        return self.available_processors
    
    def _evaluate(self, sequence: str|dict[str, Any]) -> bool:
        return self.classifier.evaluate(sequence)