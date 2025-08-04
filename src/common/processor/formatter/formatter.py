"""
포맷터 모듈

이 모듈은 URL이나 데이터를 구조화된 형태로 변환하는 Formatter 클래스를 제공합니다.
"""

from typing import Optional

from .formatter_strategy import FormatterStrategy
from .strategies import YoutubeFormatter, UrlFormatter

# 예외 핸들러 import
from ...exception import (
    ExceptionHandler,
    ValidationExceptionHandler,
    ExceptionType,
    ExceptionSeverity,
    ValidationException
)


class Formatter:
    strategies: list[FormatterStrategy] = [
        YoutubeFormatter(),
        UrlFormatter(),
    ]

    @ExceptionHandler(
        exception_type=ExceptionType.URL_PARSING_ERROR,
        severity=ExceptionSeverity.MEDIUM,
        reraise=True,
        log_level="warning",
        handler_name="formatter_parse_handler"
    )
    @ValidationExceptionHandler(reraise=True)
    def parse(self, data: str, referer: Optional[type] = None) -> dict:
        strategy = self._get_context(data, referer)
        return strategy.parse(data)

    @ExceptionHandler(
        exception_type=ExceptionType.URL_PARSING_ERROR,
        severity=ExceptionSeverity.MEDIUM,
        reraise=True,
        log_level="warning",
        handler_name="formatter_unparse_handler"
    )
    @ValidationExceptionHandler(reraise=True)
    def unparse(self, data: dict, referer: Optional[type] = None) -> str:
        strategy = self._get_context(data, referer)
        return strategy.unparse(data)

    @ExceptionHandler(
        exception_type=ExceptionType.URL_PARSING_ERROR,
        severity=ExceptionSeverity.MEDIUM,
        reraise=True,
        log_level="warning",
        handler_name="formatter_context_handler"
    )
    def _get_context(self, data: str | dict, referer: Optional[type] = None) -> FormatterStrategy:
        for strategy in self.strategies:
            if strategy.is_supported(data):
                return strategy
        raise ValidationException(
            message=f"지원되는 포맷터를 찾을 수 없습니다: {type(data).__name__}",
            field_name="data_type",
            field_value=str(data)[:100] if isinstance(data, str) else str(type(data)),
            validation_rule="supported_format"
        )


