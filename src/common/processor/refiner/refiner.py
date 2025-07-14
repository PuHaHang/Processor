from ..types import Payload
from .strategies import GeminiRefiner, OpenAIRefiner
from ..processor import Processor
from ..processor_type import ProcessorType
from .refiner_strategy import RefinerStrategy


class Refiner(Processor):
    processor_type: ProcessorType = ProcessorType.REFINER
    strategies: list[RefinerStrategy] = [
        GeminiRefiner(),
        OpenAIRefiner(),
    ]

    def process(self, payload: Payload, opt: dict = {}) -> Payload:
        strategy = self._get_context(payload)
        if strategy is None:
            raise ValueError(f"No refiner strategy found for payload: {payload}")
        return strategy.process(payload, opt)

    def is_supported(self, payload: Payload) -> bool:
        return self._get_context(payload) is not None

    def _get_context(self, payload: Payload) -> RefinerStrategy | None:
        for strategy in self.strategies:
            if strategy.is_supported(payload):
                return strategy
        return None