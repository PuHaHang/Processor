from ..types import Payload
from .strategies import GeminiRefiner, OpenAIRefiner
from ..processor import Processor
from ..processor_type import ProcessorType
from .refiner_strategy import RefinerStrategy

# 예외 핸들러 import
from ...exception import (
    ExceptionHandler,
    RetryOnException,
    ValidationExceptionHandler,
    ExceptionType,
    ExceptionSeverity,
    ProcessingException
)


class Refiner(Processor):
    processor_type: ProcessorType = ProcessorType.REFINER
    strategies: list[RefinerStrategy] = [
        GeminiRefiner(),
        # OpenAIRefiner(),
    ]

    def process(self, payload: Payload, opt: dict = {}) -> Payload:
        strategy = self._get_context(payload)
        if strategy is None:
            raise ProcessingException(
                message=f"지원되는 정제기를 찾을 수 없습니다: {payload.data_type.name}",
                processor_name="refiner"
            )
        return strategy.process(payload, opt)

    def is_supported(self, payload: Payload) -> bool:
        return self._get_context(payload) is not None

    def _get_context(self, payload: Payload) -> RefinerStrategy | None:
        for strategy in self.strategies:
            if strategy.is_supported(payload):
                return strategy
        return None
    
    def get_processor_type(self) -> ProcessorType:
        return self.processor_type