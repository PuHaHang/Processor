"""
YouTube 포맷터 테스트 모듈

이 모듈은 YoutubeFormatter 클래스의 기능을 검증하는 단위 테스트를 제공합니다.
YouTube URL 파싱, 지원 여부 확인, URL 재구성 등의 기능을 테스트합니다.
"""

import pytest
from src.common.processor.formatter.strategies.youtube_formatter import YoutubeFormatter


class TestYoutubeFormatter:
    """
    YoutubeFormatter 클래스에 대한 테스트 모음
    
    YouTube URL 처리, 파싱, 지원 여부 확인 등의
    모든 기능을 테스트합니다.
    """
    
    @pytest.fixture
    def formatter(self):
        """
        테스트용 YoutubeFormatter 인스턴스를 제공하는 fixture
        
        Returns:
            YoutubeFormatter: 테스트용 포맷터 인스턴스
        """
        return YoutubeFormatter()
    
    
    def test_domain_initialization(self, formatter):
        """
        YoutubeFormatter 도메인 초기화 테스트
        
        Args:
            formatter: YoutubeFormatter 인스턴스
        """
        assert formatter.domain == "youtube.com"
        assert formatter.YOUTUBE_URL_TEMPLATE == "https://www.youtube.com/watch?v=%s"
    
    
    @pytest.mark.parametrize("url", [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "http://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "https://www.youtube.com/v/dQw4w9WgXcQ",
        "https://www.youtube.com/shorts/dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30s",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLExample",
    ])
    def test_is_supported_with_valid_youtube_urls(self, formatter, url):
        """
        유효한 YouTube URL에 대한 지원 여부 테스트
        
        Args:
            formatter: YoutubeFormatter 인스턴스
            url: 테스트할 유효한 YouTube URL
        """
        assert formatter.is_supported(url) == True
    
    
    @pytest.mark.parametrize("url", [
        "https://vimeo.com/123456789",
        "https://www.dailymotion.com/video/x123456",
        "https://www.example.com/video",
        "not_a_url",
        "https://www.youtube.com/watch?v=invalid_id",  # 잘못된 ID 길이
        "https://www.youtube.com/watch?v=",  # 빈 ID
        "https://www.youtube.com/watch",  # v 파라미터 없음
        "",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ123",  # 너무 긴 ID
    ])
    def test_is_supported_with_invalid_urls(self, formatter, url):
        """
        무효한 URL에 대한 지원 여부 테스트
        
        Args:
            formatter: YoutubeFormatter 인스턴스
            url: 테스트할 무효한 URL
        """
        assert formatter.is_supported(url) == False
    
    
    @pytest.mark.parametrize("data", [
        {"platform": "youtube.com", "v": ["dQw4w9WgXcQ"]},
        {"platform": "youtube.com", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
    ])
    def test_is_supported_with_valid_dict_data(self, formatter, data):
        """
        유효한 dict 데이터에 대한 지원 여부 테스트
        
        Args:
            formatter: YoutubeFormatter 인스턴스
            data: 테스트할 유효한 dict 데이터
        """
        assert formatter.is_supported(data) == True
    
    
    @pytest.mark.parametrize("data", [
        {"platform": "vimeo.com", "v": ["123456789"]},
        {"platform": "dailymotion.com", "url": "https://www.dailymotion.com/video/x123456"},
        {"v": ["dQw4w9WgXcQ"]},  # platform 키 없음
        {},  # 빈 dict
        {"platform": ""},  # 빈 platform
    ])
    def test_is_supported_with_invalid_dict_data(self, formatter, data):
        """
        무효한 dict 데이터에 대한 지원 여부 테스트
        
        Args:
            formatter: YoutubeFormatter 인스턴스
            data: 테스트할 무효한 dict 데이터
        """
        assert formatter.is_supported(data) == False
    
    
    def test_is_supported_with_invalid_data_types(self, formatter):
        """
        잘못된 데이터 타입에 대한 지원 여부 테스트
        
        Args:
            formatter: YoutubeFormatter 인스턴스
        """
        assert formatter.is_supported(123) == False
        assert formatter.is_supported(None) == False
        assert formatter.is_supported([]) == False
        assert formatter.is_supported(True) == False
    
    
    @pytest.mark.parametrize("url, expected_result", [
        (
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "platform": "youtube.com",
                "metadata": {"is_shorts": False}
            }
        ),
        (
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30s",
            {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "platform": "youtube.com",
                "metadata": {"is_shorts": False}
            }
        ),
        (
            "https://youtu.be/dQw4w9WgXcQ",
            {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "platform": "youtube.com",
                "metadata": {"is_shorts": False}
            }
        ),
    ])
    def test_parse_regular_youtube_urls(self, formatter, url, expected_result):
        """
        일반 YouTube URL 파싱 테스트
        
        Args:
            formatter: YoutubeFormatter 인스턴스
            url: 파싱할 YouTube URL
            expected_result: 예상 결과
        """
        result = formatter.parse(url)
        assert result == expected_result
    
    
    @pytest.mark.parametrize("url, expected_result", [
        (
            "https://www.youtube.com/shorts/dQw4w9WgXcQ",
            {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "platform": "youtube.com",
                "metadata": {"is_shorts": True}
            }
        ),
        (
            "https://youtube.com/shorts/abcdefghijk",
            {
                "url": "https://www.youtube.com/watch?v=abcdefghijk",
                "platform": "youtube.com",
                "metadata": {"is_shorts": True}
            }
        ),
    ])
    def test_parse_youtube_shorts_urls(self, formatter, url, expected_result):
        """
        YouTube Shorts URL 파싱 테스트
        
        Args:
            formatter: YoutubeFormatter 인스턴스
            url: 파싱할 YouTube Shorts URL
            expected_result: 예상 결과
        """
        result = formatter.parse(url)
        assert result == expected_result
    
    
    @pytest.mark.parametrize("url", [
        "https://www.youtube.com/watch",  # v 파라미터 없음
        "https://www.youtube.com/watch?v=",  # 빈 v 파라미터
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ&v=another_id",  # 여러 v 파라미터
        "https://www.youtube.com/watch?list=PLExample",  # v 파라미터 없음
    ])
    def test_parse_invalid_youtube_urls(self, formatter, url):
        """
        무효한 YouTube URL 파싱 시 예외 테스트
        
        Args:
            formatter: YoutubeFormatter 인스턴스
            url: 파싱할 무효한 YouTube URL
        """
        with pytest.raises(ValueError) as exc_info:
            formatter.parse(url)
        assert "Invalid YouTube URL" in str(exc_info.value)
    
    
    @pytest.mark.parametrize("data, expected_url", [
        ({"v": ["dQw4w9WgXcQ"]}, "https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
        ({"v": ["abcdefghijk"]}, "https://www.youtube.com/watch?v=abcdefghijk"),
        ({"v": ["0123456789A"]}, "https://www.youtube.com/watch?v=0123456789A"),
    ])
    def test_unparse_valid_data(self, formatter, data, expected_url):
        """
        유효한 데이터를 URL로 변환 테스트
        
        Args:
            formatter: YoutubeFormatter 인스턴스
            data: 변환할 데이터
            expected_url: 예상 URL
        """
        result = formatter.unparse(data)
        assert result == expected_url
    
    
    @pytest.mark.parametrize("data", [
        {},  # v 키 없음
        {"v": []},  # 빈 v 배열
        {"v": ["id1", "id2"]},  # 여러 v 값
        {"other_key": "value"},  # v 키 없음
    ])
    def test_unparse_invalid_data(self, formatter, data):
        """
        무효한 데이터 변환 시 예외 테스트
        
        Args:
            formatter: YoutubeFormatter 인스턴스
            data: 변환할 무효한 데이터
        """
        with pytest.raises(ValueError) as exc_info:
            formatter.unparse(data)
        assert "Invalid YouTube URL" in str(exc_info.value)
    
    
    def test_parse_unparse_consistency(self, formatter):
        """
        parse와 unparse의 일관성 테스트
        
        Args:
            formatter: YoutubeFormatter 인스턴스
        """
        original_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        
        # parse 후 unparse 했을 때 동일한 URL이 나오는지 확인
        parsed_data = formatter.parse(original_url)
        
        # parse 결과에서 v 파라미터 추출
        parsed_url = parsed_data["url"]
        
        # 원본 URL과 파싱된 URL이 같은지 확인
        assert parsed_url == original_url
    
    
    def test_shorts_url_conversion(self, formatter):
        """
        Shorts URL의 일반 URL 변환 테스트
        
        Args:
            formatter: YoutubeFormatter 인스턴스
        """
        shorts_url = "https://www.youtube.com/shorts/dQw4w9WgXcQ"
        expected_regular_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        
        parsed_data = formatter.parse(shorts_url)
        
        # Shorts URL이 일반 URL로 변환되는지 확인
        assert parsed_data["url"] == expected_regular_url
        assert parsed_data["metadata"]["is_shorts"] == True
    
    
    def test_regex_pattern_coverage(self, formatter):
        """
        정규표현식 패턴 적용 범위 테스트
        
        Args:
            formatter: YoutubeFormatter 인스턴스
        """
        # 패턴이 올바르게 컴파일되었는지 확인
        assert formatter.YOUTUBE_URL_PATTERN is not None
        
        # 다양한 YouTube URL 형식이 매칭되는지 확인
        test_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "http://youtube.com/watch?v=dQw4w9WgXcQ",
            "www.youtube.com/watch?v=dQw4w9WgXcQ",
            "youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
        ]
        
        for url in test_urls:
            assert formatter.YOUTUBE_URL_PATTERN.match(url) is not None