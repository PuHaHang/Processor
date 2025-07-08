

from ..types import Payload

from .evaluator_strategy import EvaluatorStrategy
from .strategies.yt_dlp_evaluator import YtDlpEvaluator


class Evaluator:
    strategies: list[EvaluatorStrategy] = [
        YtDlpEvaluator(),
    ]


    def evaluate(self, payload: Payload) -> bool:
        strategy = self._get_context(payload)
        if not strategy:
            return True
        return strategy.evaluate(payload)
    
    def _get_context(self, payload: Payload) -> EvaluatorStrategy|None:
        for strategy in self.strategies:
            if strategy.is_supported(payload):
                return strategy
        return None