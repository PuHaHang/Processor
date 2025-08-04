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
        OpenAIRefiner(),
    ]

    @ExceptionHandler(
        exception_type=ExceptionType.REFINING_ERROR,
        severity=ExceptionSeverity.HIGH,
        reraise=True,
        log_level="error",
        handler_name="refiner_process_handler"
    )
    @RetryOnException(
        max_retries=2,
        retry_delay=2.0,
        backoff_factor=2.0,
        exception_types=[ConnectionError, TimeoutError],
        reraise_on_failure=True
    )
    def process(self, payload: Payload, opt: dict = {}) -> Payload:
        strategy = self._get_context(payload)
        if strategy is None:
            raise ProcessingException(
                message=f"지원되는 정제기를 찾을 수 없습니다: {payload.data_type.name}",
                processor_name="refiner"
            )
        return strategy.process(payload, opt)

    @ValidationExceptionHandler(reraise=False, default_return=False)
    def is_supported(self, payload: Payload) -> bool:
        return self._get_context(payload) is not None

    @ExceptionHandler(
        exception_type=ExceptionType.REFINING_ERROR,
        severity=ExceptionSeverity.MEDIUM,
        reraise=False,
        default_return=None,
        log_level="warning",
        handler_name="refiner_context_handler"
    )
    def _get_context(self, payload: Payload) -> RefinerStrategy | None:
        for strategy in self.strategies:
            if strategy.is_supported(payload):
                return strategy
        return None
    
    def get_processor_type(self) -> ProcessorType:
        return self.processor_type