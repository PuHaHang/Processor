from ..processor_type import ProcessorType
from ..data_structure.buffer_dto import BufferDto
from ..processor import Processor
from .transcriber_strategy import TranscriberStrategy
from .strategies import OpenAITranscriber, GoogleTranscriber


class Transcriber (Processor):
    
    processor_type: ProcessorType = ProcessorType.TRANSCRIBER

    strategies: list[TranscriberStrategy] = [
        OpenAITranscriber(),
        GoogleTranscriber(),
    ]


    def process(self, buffer_dto: BufferDto, opt: dict = {}) -> BufferDto:
        strategy = self._get_context(buffer_dto)
        return strategy.process(buffer_dto, opt)

    def is_supported(self, buffer_dto: BufferDto) -> bool:
        return self._get_context(buffer_dto).is_supported(buffer_dto)

    def _get_context(self, buffer_dto: BufferDto) -> TranscriberStrategy:
        for strategy in self.strategies:
            if strategy.is_supported(buffer_dto):
                return strategy
        raise ValueError(f"No transcriber found for buffer_dto: {buffer_dto}")
