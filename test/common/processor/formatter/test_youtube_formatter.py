"""
YouTube 포맷터 테스트 모듈

이 모듈은 YoutubeFormatter 클래스의 기능을 검증하는 단위 테스트를 제공합니다.
"""

import pytest
from src.common.processor.formatter.strategies import YoutubeFormatter
from src.common.exception import ValidationException


class TestYoutubeFormatter:
    """
    YoutubeFormatter 클래스에 대한 테스트 모음
    """
    
    @pytest.fixture
    def formatter(self):
        """
        테스트용 YoutubeFormatter 인스턴스를 제공하는 fixture
        """
        return YoutubeFormatter()
    
    
    @pytest.mark.parametrize("url, expected", [
        # 표준 YouTube URL
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", True),
        ("https://youtube.com/watch?v=dQw4w9WgXcQ", True),
        ("http://www.youtube.com/watch?v=dQw4w9WgXcQ", True),
        ("www.youtube.com/watch?v=dQw4w9WgXcQ", True),
        ("youtube.com/watch?v=dQw4w9WgXcQ", True),
        
        # 단축 URL (youtu.be)
        ("https://youtu.be/dQw4w9WgXcQ", True),
        ("http://youtu.be/dQw4w9WgXcQ", True),
        ("youtu.be/dQw4w9WgXcQ", True),
        
        # 모바일 URL
        ("https://m.youtube.com/watch?v=dQw4w9WgXcQ", True),
        ("http://m.youtube.com/watch?v=dQw4w9WgXcQ", True),
        ("m.youtube.com/watch?v=dQw4w9WgXcQ", True),
        
        # 쇼츠 URL
        ("https://www.youtube.com/shorts/dQw4w9WgXcQ", True),
        ("https://youtube.com/shorts/dQw4w9WgXcQ", True),
        
        # 다른 형태의 URL
        ("https://www.youtube.com/embed/dQw4w9WgXcQ", True),
        ("https://www.youtube.com/v/dQw4w9WgXcQ", True),
        
        # 추가 매개변수가 있는 URL
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=100", True),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLExample", True),
        
        # 유효하지 않은 URL
        ("https://www.google.com", False),
        ("https://www.youtube.com/watch", False),
        ("https://www.youtube.com/watch?v=", False),
        ("https://www.youtube.com/watch?v=invalid", False),  # 11자가 아님
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ123", False),  # 11자를 초과
        ("https://vimeo.com/123456789", False),
        ("not_a_url", False),
    ])
    def test_is_supported(self, formatter, url, expected):
        """
        다양한 URL에 대한 지원 여부 테스트
        """
        assert formatter.is_supported(url) == expected
    
    
    @pytest.mark.parametrize("data, expected", [
        ({"platform": "youtube.com"}, True),
        ({"platform": "youtube.com", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}, True),
        ({"platform": "other.com"}, False),
        ({"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}, False),  # platform 없음
        ({}, False),
    ])
    def test_is_supported_dict(self, formatter, data, expected):
        """
        딕셔너리 데이터에 대한 지원 여부 테스트
        """
        assert formatter.is_supported(data) == expected
    
    
    @pytest.mark.parametrize("url, expected_id", [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://m.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/v/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=100", "dQw4w9WgXcQ"),
    ])
    def test_parse_valid_urls(self, formatter, url, expected_id):
        """
        유효한 YouTube URL 파싱 테스트
        """
        result = formatter.parse(url)
        
        assert result["platform"] == "youtube.com"
        assert result["url"] == f"https://www.youtube.com/watch?v={expected_id}"
        assert "metadata" in result
        assert "is_shorts" in result["metadata"]
    
    
    @pytest.mark.parametrize("url", [
        "https://www.youtube.com/watch",  # v 파라미터 없음
        "https://www.youtube.com/watch?v=",  # 빈 v 파라미터
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ&v=another_id",  # 여러 v 파라미터
        "https://www.youtube.com/watch?list=PLExample",  # v 파라미터 없음
    ])
    def test_parse_invalid_youtube_urls(self, formatter, url):
        """
        유효하지 않은 YouTube URL 파싱 테스트
        
        Args:
            formatter: YoutubeFormatter 인스턴스
            url: 유효하지 않은 YouTube URL
        """
        with pytest.raises(ValidationException) as exc_info:
            formatter.parse(url)
        
        assert "YouTube URL" in str(exc_info.value)
    
    
    @pytest.mark.parametrize("data, expected", [
        ({"v": ["dQw4w9WgXcQ"]}, "https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
        ({"platform": "youtube.com", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}, "https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
    ])
    def test_unparse_valid_data(self, formatter, data, expected):
        """
        유효한 데이터 언파싱 테스트
        """
        result = formatter.unparse(data)
        assert result == expected
    
    
    @pytest.mark.parametrize("data", [
        {},  # v 키 없음
        {"v": []},  # 빈 v 배열
        {"v": ["id1", "id2"]},  # 여러 v 값
        {"platform": "youtube.com"},  # url 키 없음
    ])
    def test_unparse_invalid_data(self, formatter, data):
        """
        유효하지 않은 데이터 언파싱 테스트
        
        Args:
            formatter: YoutubeFormatter 인스턴스
            data: 유효하지 않은 데이터
        """
        with pytest.raises(ValidationException) as exc_info:
            formatter.unparse(data)
        
        assert "YouTube" in str(exc_info.value)
    
    
    def test_shorts_url_parsing(self, formatter):
        """
        쇼츠 URL 파싱 테스트
        """
        result = formatter.parse("https://www.youtube.com/shorts/dQw4w9WgXcQ")
        
        assert result["platform"] == "youtube.com"
        assert result["url"] == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert result["metadata"]["is_shorts"] == True
    
    
    def test_regular_url_parsing(self, formatter):
        """
        일반 URL 파싱 테스트
        """
        result = formatter.parse("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        
        assert result["platform"] == "youtube.com"
        assert result["url"] == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert result["metadata"]["is_shorts"] == False
    
    
    def test_youtu_be_url_parsing(self, formatter):
        """
        youtu.be URL 파싱 테스트
        """
        result = formatter.parse("https://youtu.be/dQw4w9WgXcQ")
        
        assert result["platform"] == "youtube.com"
        assert result["url"] == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert result["metadata"]["is_shorts"] == False