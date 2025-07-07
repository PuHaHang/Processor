from ..types import Payload
from .strategies import YtDlpDownloader
from ..processor import Processor
from .downloader_strategy import DownloaderStrategy
from ..processor_type import ProcessorType


class Downloader (Processor):
    processor_type: ProcessorType = ProcessorType.DOWNLOADER
    strategies: list[DownloaderStrategy] = [
        YtDlpDownloader(),
    ]


    def process(self, payload: Payload, opt: dict = {}) -> Payload:
        strategy = self._get_context(payload)
        return strategy.process(payload, opt)

    def is_supported(self, payload: Payload) -> bool:
        return self._get_context(payload).is_supported(payload)

    def _get_context(self, payload: Payload) -> DownloaderStrategy:
        for strategy in self.strategies:
            if strategy.is_supported(payload):
                return strategy
        raise ValueError(f"No supported downloader found for payload: {payload}")