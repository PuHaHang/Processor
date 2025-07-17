"""
URL 포맷터 전략 모듈

이 모듈은 일반적인 URL을 파싱하고 표준화하는 포맷터 전략을 제공합니다.
HTTP/HTTPS URL의 구성 요소를 분석하고 메타데이터를 추출합니다.
"""

import re
from urllib.parse import urlparse

from ..formatter_strategy import FormatterStrategy
from ....exception import (
    ExceptionHandler,
    ValidationExceptionHandler,
    ExceptionType,
    ExceptionSeverity,
    ValidationException
)


class UrlFormatter(FormatterStrategy):
    
    URL_PATTERN = re.compile(
        r"^(https?://)?"                # http:// 또는 https:// (옵션)
        r"(www\.)?"                     # www. (옵션)
        r"([a-zA-Z0-9.-]+)"             # 도메인(서브도메인 포함)
        r"(\.[a-zA-Z]{2,})"             # TLD (.com, .net 등)
        r"(:\d+)?"                      # 포트 (옵션)
        r"(/[a-zA-Z0-9._~!$&'()*+,;=:@%-]*)*"  # 경로 (대시, 언더스코어, 퍼센트 등 허용, 0개 이상)
        r"(\?[a-zA-Z0-9._~!$&'()*+,;=:@%/-]*)?" # 쿼리 (옵션, 여러 파라미터 허용)
        r"(#[a-zA-Z0-9._~!$&'()*+,;=:@%/-]*)?$" # 프래그먼트 (옵션)
    )

    @ExceptionHandler(
        exception_type=ExceptionType.URL_PARSING_ERROR,
        severity=ExceptionSeverity.LOW,
        reraise=True,
        log_level="info",
        handler_name="url_formatter_is_supported_handler"
    )
    def is_supported(self, data: str | dict) -> bool:
        """
        데이터가 일반적인 URL인지 확인합니다.
        
        Args:
            data: 확인할 데이터 (문자열 또는 딕셔너리)
            
        Returns:
            bool: 유효한 URL이면 True, 아니면 False
        """
        if isinstance(data, str):
            return self.URL_PATTERN.match(data) is not None
        elif isinstance(data, dict):
            return not(not data.get("url", "")) and self.URL_PATTERN.match(data.get("url", "")) is not None
        return False

    @ExceptionHandler(
        exception_type=ExceptionType.URL_PARSING_ERROR,
        severity=ExceptionSeverity.MEDIUM,
        reraise=True,
        log_level="warning",
        handler_name="url_formatter_parse_handler"
    )
    @ValidationExceptionHandler(reraise=True)
    def parse(self, data: str) -> dict:
        """
        URL을 파싱하여 구조화된 데이터로 변환합니다.
        
        Args:
            data: 파싱할 URL 문자열
            
        Returns:
            dict: 파싱된 URL 데이터
            
        Raises:
            ValidationException: 유효하지 않은 URL인 경우
        """
        if not data or not isinstance(data, str):
            raise ValidationException(
                message="URL이 비어있거나 유효하지 않습니다",
                field_name="data",
                field_value=data,
                validation_rule="url_not_empty"
            )
        
        if not self.URL_PATTERN.match(data):
            raise ValidationException(
                message="유효하지 않은 URL 형식입니다",
                field_name="data",
                field_value=data,
                validation_rule="url_valid_format"
            )
        
        parsed_url = urlparse(data)
        
        if not parsed_url.netloc:
            raise ValidationException(
                message="URL에 호스트 정보가 없습니다",
                field_name="data",
                field_value=data,
                validation_rule="url_host_required"
            )
        
        return {
            "url": data,
            "platform": self.get_domain(data),
            "metadata": {
                "scheme": parsed_url.scheme,
                "netloc": parsed_url.netloc,
                "path": parsed_url.path,
                "params": parsed_url.params,
                "query": parsed_url.query,
                "fragment": parsed_url.fragment,
            }
        }

    @ExceptionHandler(
        exception_type=ExceptionType.URL_PARSING_ERROR,
        severity=ExceptionSeverity.MEDIUM,
        reraise=True,
        log_level="warning",
        handler_name="url_formatter_unparse_handler"
    )
    @ValidationExceptionHandler(reraise=True)
    def unparse(self, data: dict) -> str:
        """
        구조화된 데이터를 URL로 변환합니다.
        
        Args:
            data: 변환할 데이터 딕셔너리
            
        Returns:
            str: 생성된 URL
            
        Raises:
            ValidationException: 유효하지 않은 데이터인 경우
        """
        if not isinstance(data, dict):
            raise ValidationException(
                message="URL 데이터가 딕셔너리가 아닙니다",
                field_name="data",
                field_value=str(data),
                validation_rule="url_data_dict_required"
            )
        
        url = data.get("url", "")
        if not url:
            raise ValidationException(
                message="URL 데이터에 url 필드가 없습니다",
                field_name="url",
                field_value=url,
                validation_rule="url_field_required"
            )
        
        return url