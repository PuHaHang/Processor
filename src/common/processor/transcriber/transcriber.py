from ..types import Payload
from .strategies import OpenAITranscriber, GoogleTranscriber
from ..processor import Processor
from ..processor_type import ProcessorType
from .transcriber_strategy import TranscriberStrategy

# 예외 핸들러 import
from ...exception import (
    ExceptionHandler,
    RetryOnException,
    ValidationExceptionHandler,
    ExceptionType,
    ExceptionSeverity,
    ExternalServiceException
)


class Transcriber (Processor):
    
    processor_type: ProcessorType = ProcessorType.TRANSCRIBER

    strategies: list[TranscriberStrategy] = [
        OpenAITranscriber(),
        GoogleTranscriber(),
    ]

    @ExceptionHandler(
        exception_type=ExceptionType.TRANSCRIPTION_ERROR,
        severity=ExceptionSeverity.HIGH,
        reraise=True,
        log_level="error",
        handler_name="transcriber_process_handler"
    )
    @RetryOnException(
        max_retries=2,
        retry_delay=1.0,
        backoff_factor=2.0,
        exception_types=[ConnectionError, TimeoutError],
        reraise_on_failure=True
    )
    def process(self, payload: Payload, opt: dict = {}) -> Payload:
        strategy = self._get_context(payload)
        return strategy.process(payload, opt)

    @ValidationExceptionHandler(reraise=True)
    def is_supported(self, payload: Payload) -> bool:
        return self._get_context(payload).is_supported(payload)

    @ExceptionHandler(
        exception_type=ExceptionType.TRANSCRIPTION_ERROR,
        severity=ExceptionSeverity.MEDIUM,
        reraise=True,
        log_level="warning",
        handler_name="transcriber_context_handler"
    )
    def _get_context(self, payload: Payload) -> TranscriberStrategy:
        for strategy in self.strategies:
            if strategy.is_supported(payload):
                return strategy
        raise ExternalServiceException(
            message=f"지원되는 전사기를 찾을 수 없습니다: {payload.data_type.name}",
            service_name="transcriber"
        )
