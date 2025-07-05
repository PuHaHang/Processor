from ..data_structure.buffer_dto import BufferDto
from .strategies import YtDlpDownloader
from ..processor import Processor
from .downloader_strategy import DownloaderStrategy
from ..processor_type import ProcessorType


class Downloader (Processor):
    processor_type: ProcessorType = ProcessorType.DOWNLOADER
    strategies: list[DownloaderStrategy] = [
        YtDlpDownloader(),
    ]


    def process(self, buffer_dto: BufferDto, opt: dict = {}) -> BufferDto:
        strategy = self._get_context(buffer_dto)
        return strategy.process(buffer_dto, opt)

    def is_supported(self, buffer_dto: BufferDto) -> bool:
        return self._get_context(buffer_dto).is_supported(buffer_dto)

    def _get_context(self, buffer_dto: BufferDto) -> DownloaderStrategy:
        for strategy in self.strategies:
            if strategy.is_supported(buffer_dto):
                return strategy
        raise ValueError(f"No supported downloader found for buffer_dto: {buffer_dto}")