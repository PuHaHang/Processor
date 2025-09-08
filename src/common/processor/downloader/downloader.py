from ..types import Payload
from .strategies import YtDlpDownloader
from ..processor import Processor
from .downloader_strategy import DownloaderStrategy
from ..processor_type import ProcessorType

# 예외 핸들러 import
from ...exception import (
    ExceptionHandler,
    RetryOnException,
    ValidationExceptionHandler,
    ExceptionType,
    ExceptionSeverity,
    ExternalServiceException
)


class Downloader (Processor):
    processor_type: ProcessorType = ProcessorType.DOWNLOADER
    strategies: list[DownloaderStrategy] = [
        YtDlpDownloader(),
    ]

    @ExceptionHandler(
        exception_type=ExceptionType.EXTERNAL_SERVICE_ERROR,
        severity=ExceptionSeverity.HIGH,
        reraise=True,
        log_level="error",
        handler_name="downloader_process_handler"
    )
    @RetryOnException(
        max_retries=3,
        retry_delay=2.0,
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
        exception_type=ExceptionType.EXTERNAL_SERVICE_ERROR,
        severity=ExceptionSeverity.MEDIUM,
        reraise=True,
        log_level="warning",
        handler_name="downloader_context_handler"
    )
    def _get_context(self, payload: Payload) -> DownloaderStrategy:
        for strategy in self.strategies:
            if strategy.is_supported(payload):
                return strategy
        raise ExternalServiceException(
            message=f"지원되는 다운로더를 찾을 수 없습니다: {payload.data_type.name}",
            service_name="downloader",
            endpoint=str(payload.buffer[:100] if payload.buffer else "None")
        )