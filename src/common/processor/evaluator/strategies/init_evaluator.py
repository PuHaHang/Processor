

from ...types import Payload
from ..evaluator_strategy import EvaluatorStrategy


class InitEvaluator(EvaluatorStrategy):
    available_processors: list = [None]


    def evaluate(self, payload: Payload) -> bool:
        return super()._evaluate(str(payload.__str__))
    
    def is_supported(self, payload: Payload) -> bool:
        return type(payload.get_processor()) in self.available_processors
