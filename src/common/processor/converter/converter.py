from ..types import Payload
from .strategies import AudioConverter
from ..processor import Processor
from ..processor_type import ProcessorType
from .converter_strategy import ConverterStrategy

# 예외 핸들러 import
from ...exception import (
    ExceptionHandler,
    ValidationExceptionHandler,
    ExceptionType,
    ExceptionSeverity,
    ProcessingException
)


class Converter (Processor):
    processor_type: ProcessorType = ProcessorType.CONVERTER
    strategies: list[ConverterStrategy] = [
        AudioConverter(),
    ]

    @ExceptionHandler(
        exception_type=ExceptionType.AUDIO_PROCESSING_ERROR,
        severity=ExceptionSeverity.MEDIUM,
        reraise=True,
        log_level="warning",
        handler_name="converter_process_handler"
    )
    @ValidationExceptionHandler(reraise=True)
    def process(self, payload: Payload, opt: dict = {}) -> Payload:
        strategy = self._get_context(payload)
        return strategy.process(payload, opt)

    @ValidationExceptionHandler(reraise=True)
    def is_supported(self, payload: Payload) -> bool:
        return self._get_context(payload).is_supported(payload)

    @ExceptionHandler(
        exception_type=ExceptionType.AUDIO_PROCESSING_ERROR,
        severity=ExceptionSeverity.MEDIUM,
        reraise=True,
        log_level="warning",
        handler_name="converter_context_handler"
    )
    def _get_context(self, payload: Payload) -> ConverterStrategy:
        for strategy in self.strategies:
            if strategy.is_supported(payload):
                return strategy
        raise ProcessingException(
            message=f"지원되는 변환기를 찾을 수 없습니다: {payload.data_type.name}",
            processor_name="converter"
        )