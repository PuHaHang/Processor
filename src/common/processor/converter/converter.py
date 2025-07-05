from ..data_structure.buffer_dto import BufferDto
from .strategies import AudioConverter
from ..processor import Processor
from ..processor_type import ProcessorType
from .converter_strategy import ConverterStrategy


class Converter (Processor):
    processor_type: ProcessorType = ProcessorType.CONVERTER
    strategies: list[ConverterStrategy] = [
        AudioConverter(),
    ]


    def process(self, buffer_dto: BufferDto, opt: dict = {}) -> BufferDto:
        strategy = self._get_context(buffer_dto)
        return strategy.process(buffer_dto, opt)

    def is_supported(self, buffer_dto: BufferDto) -> bool:
        return self._get_context(buffer_dto).is_supported(buffer_dto)

    def _get_context(self, buffer_dto: BufferDto) -> ConverterStrategy:
        for strategy in self.strategies:
            if strategy.is_supported(buffer_dto):
                return strategy
        raise ValueError(f"No converter strategy found for buffer_dto: {buffer_dto}")