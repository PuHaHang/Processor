"""
URL 포맷터 테스트 모듈

이 모듈은 UrlFormatter 클래스의 기능을 검증하는 단위 테스트를 제공합니다.
"""

import pytest
from src.common.processor.formatter.strategies import UrlFormatter
from src.common.exception import ValidationException


class TestUrlFormatter:
    """
    UrlFormatter 클래스에 대한 테스트 모음
    """
    
    @pytest.fixture
    def formatter(self):
        """
        테스트용 UrlFormatter 인스턴스를 제공하는 fixture
        """
        return UrlFormatter()
    
    
    @pytest.mark.parametrize("url, expected", [
        # 표준 HTTP/HTTPS URL
        ("https://www.example.com", True),
        ("http://www.example.com", True),
        ("https://example.com", True),
        ("http://example.com", True),
        ("www.example.com", True),
        ("example.com", True),
        
        # 포트 번호가 있는 URL
        ("https://www.example.com:8080", True),
        ("http://example.com:3000", True),
        
        # 경로가 있는 URL
        ("https://www.example.com/path", True),
        ("https://www.example.com/path/to/resource", True),
        ("https://www.example.com/path-with-dash", True),
        ("https://www.example.com/path_with_underscore", True),
        
        # 쿼리 파라미터가 있는 URL
        ("https://www.example.com?query=value", True),
        ("https://www.example.com/path?query=value", True),
        ("https://www.example.com?query=value&another=param", True),
        
        # 서브도메인이 있는 URL
        ("https://subdomain.example.com", True),
        ("https://sub.domain.example.com", True),
        
        # 유효하지 않은 URL
        ("not_a_url", False),
        ("ftp://example.com", False),  # FTP 프로토콜
        ("https://", False),  # 도메인 없음
        ("example", False),  # TLD 없음
        ("", False),  # 빈 문자열
        ("https://example.c", False),  # 너무 짧은 TLD
    ])
    def test_is_supported_string(self, formatter, url, expected):
        """
        문자열 URL에 대한 지원 여부 테스트
        """
        assert formatter.is_supported(url) == expected
    
    
    @pytest.mark.parametrize("data, expected", [
        ({"url": "https://www.example.com"}, True),
        ({"url": "http://example.com"}, True),
        ({"url": ""}, False),
        ({"platform": "example.com"}, False),  # url 키 없음
        ({}, False),  # 빈 딕셔너리
    ])
    def test_is_supported_dict(self, formatter, data, expected):
        """
        딕셔너리 데이터에 대한 지원 여부 테스트
        """
        assert formatter.is_supported(data) == expected
    
    
    @pytest.mark.parametrize("url, expected_platform", [
        ("https://www.example.com", "example.com"),
        ("https://subdomain.example.com", "example.com"),
        ("https://www.google.com", "google.com"),
        ("https://github.com", "github.com"),
        ("https://www.stackoverflow.com", "stackoverflow.com"),
    ])
    def test_parse_valid_urls(self, formatter, url, expected_platform):
        """
        유효한 URL 파싱 테스트
        """
        result = formatter.parse(url)
        
        assert result["url"] == url
        assert result["platform"] == expected_platform
        assert "metadata" in result
        assert "scheme" in result["metadata"]
        assert "netloc" in result["metadata"]
        assert "path" in result["metadata"]
        assert "query" in result["metadata"]
    
    
    @pytest.mark.parametrize("url", [
        "",  # 빈 문자열
        "not_a_url",  # 유효하지 않은 형식
        "ftp://example.com",  # 지원하지 않는 프로토콜
        "https://",  # 호스트 없음
        123,  # 문자열이 아님
        None,  # None 값
    ])
    def test_parse_invalid_urls(self, formatter, url):
        """
        유효하지 않은 URL 파싱 테스트
        """
        with pytest.raises(ValidationException) as exc_info:
            formatter.parse(url)
        
        assert "URL" in str(exc_info.value)
    
    
    @pytest.mark.parametrize("data, expected", [
        ({"url": "https://www.example.com"}, "https://www.example.com"),
        ({"url": "http://example.com"}, "http://example.com"),
        ({"url": "https://subdomain.example.com/path"}, "https://subdomain.example.com/path"),
    ])
    def test_unparse_valid_data(self, formatter, data, expected):
        """
        유효한 데이터 언파싱 테스트
        """
        result = formatter.unparse(data)
        assert result == expected
    
    
    @pytest.mark.parametrize("data", [
        {},  # url 키 없음
        {"platform": "example.com"},  # url 키 없음
        {"url": ""},  # 빈 url
        "not_a_dict",  # 딕셔너리가 아님
        None,  # None 값
    ])
    def test_unparse_invalid_data(self, formatter, data):
        """
        유효하지 않은 데이터 언파싱 테스트
        """
        with pytest.raises(ValidationException) as exc_info:
            formatter.unparse(data)
        
        assert "URL" in str(exc_info.value)
    
    
    def test_parse_with_all_url_components(self, formatter):
        """
        모든 URL 구성 요소를 포함한 파싱 테스트
        """
        url = "https://subdomain.example.com:8080/path/to/resource?query=value&param=123#fragment"
        result = formatter.parse(url)
        
        assert result["url"] == url
        assert result["platform"] == "example.com"
        assert result["metadata"]["scheme"] == "https"
        assert result["metadata"]["netloc"] == "subdomain.example.com:8080"
        assert result["metadata"]["path"] == "/path/to/resource"
        assert result["metadata"]["query"] == "query=value&param=123"
        assert result["metadata"]["fragment"] == "fragment"
    
    
    def test_parse_unparse_consistency(self, formatter):
        """
        parse와 unparse의 일관성 테스트
        """
        original_url = "https://www.example.com/path?query=value"
        
        # parse 후 unparse 했을 때 동일한 URL이 나오는지 확인
        parsed_data = formatter.parse(original_url)
        unparsed_url = formatter.unparse(parsed_data)
        
        assert unparsed_url == original_url
    
    
    def test_is_supported_with_various_data_types(self, formatter):
        """
        다양한 데이터 타입에 대한 지원 여부 테스트
        """
        # 지원하지 않는 데이터 타입들
        assert formatter.is_supported(123) == False
        assert formatter.is_supported(None) == False
        assert formatter.is_supported([]) == False
        assert formatter.is_supported(True) == False
        assert formatter.is_supported(set()) == False 