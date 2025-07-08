
from ...formatter.strategies.youtube_formatter import YoutubeFormatter
from ...formatter.formatter_strategy import FormatterStrategy
from ...types import Payload
from ...downloader.strategies.yt_dlp_downloader import YtDlpDownloader

from ..evaluator_strategy import EvaluatorStrategy

class YtDlpEvaluator (EvaluatorStrategy):
    available_processors: list[type] = [YtDlpDownloader]
    formatters: list[FormatterStrategy] = [
        YoutubeFormatter(),
    ]

    target_keys: list[str] = [
        'title',
        "description",
    ]

    def is_supported(self, payload: Payload) -> bool:
        return payload.get_processor() in self.available_processors

    def evaluate(self, payload: Payload) -> bool:
        if payload.get_metadata():
            target = {}
            for key in self.target_keys:
                if key in payload.get_metadata():
                    target[key] = payload.get_metadata()[key]
            return super()._evaluate(target)
        return False
