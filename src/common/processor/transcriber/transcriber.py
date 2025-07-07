from ..processor_type import ProcessorType
from ..types import Payload
from ..processor import Processor
from .transcriber_strategy import TranscriberStrategy
from .strategies import OpenAITranscriber, GoogleTranscriber


class Transcriber (Processor):
    
    processor_type: ProcessorType = ProcessorType.TRANSCRIBER

    strategies: list[TranscriberStrategy] = [
        OpenAITranscriber(),
        GoogleTranscriber(),
    ]


    def process(self, payload: Payload, opt: dict = {}) -> Payload:
        strategy = self._get_context(payload)
        return strategy.process(payload, opt)

    def is_supported(self, payload: Payload) -> bool:
        return self._get_context(payload).is_supported(payload)

    def _get_context(self, payload: Payload) -> TranscriberStrategy:
        for strategy in self.strategies:
            if strategy.is_supported(payload):
                return strategy
        raise ValueError(f"No transcriber found for payload: {payload}")
