
from typing import Optional

from .formatter_strategy import FormatterStrategy
from .strategies import YoutubeFormatter, UrlFormatter


class Formatter:
    strategies: list[FormatterStrategy] = [
        YoutubeFormatter(),
        UrlFormatter(),
    ]


    def parse(self, data: str, referer: Optional[type] = None) -> dict:
        strategy = self._get_context(data, referer)
        return strategy.parse(data)


    def unparse(self, data: dict, referer: Optional[type] = None) -> str:
        strategy = self._get_context(data, referer)
        return strategy.unparse(data)


    def _get_context(self, data: str | dict, referer: Optional[type] = None) -> FormatterStrategy:
        for strategy in self.strategies:
            if strategy.is_supported(data):
                return strategy
        raise ValueError(f"No formatter found for data: {data}")


