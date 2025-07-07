from ..types import Payload
from .strategies import AudioConverter
from ..processor import Processor
from ..processor_type import ProcessorType
from .converter_strategy import ConverterStrategy


class Converter (Processor):
    processor_type: ProcessorType = ProcessorType.CONVERTER
    strategies: list[ConverterStrategy] = [
        AudioConverter(),
    ]


    def process(self, payload: Payload, opt: dict = {}) -> Payload:
        strategy = self._get_context(payload)
        return strategy.process(payload, opt)

    def is_supported(self, payload: Payload) -> bool:
        return self._get_context(payload).is_supported(payload)

    def _get_context(self, payload: Payload) -> ConverterStrategy:
        for strategy in self.strategies:
            if strategy.is_supported(payload):
                return strategy
        raise ValueError(f"No converter strategy found for payload: {payload}")