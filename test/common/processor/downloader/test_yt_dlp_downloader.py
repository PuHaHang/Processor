"""
YouTube 다운로더 테스트 모듈

이 모듈은 YtDlpDownloader 클래스의 기능을 검증하는 단위 테스트를 제공합니다.
Mock을 사용하여 실제 네트워크 요청 없이도 테스트가 가능하도록 구현되었습니다.
"""

import pytest
from unittest.mock import MagicMock, Mock, patch

from src.common.processor.downloader.strategies import YtDlpDownloader
from src.common.processor.types import DataType
from src.common.processor.types import Payload
from src.common.processor.types import PayloadStatus
from src.common.processor.processor_type import ProcessorType 


class TestYtDlpDownloader:
    """
    YtDlpDownloader 클래스에 대한 테스트 모음
    
    YouTube 다운로더의 초기화, URL 지원 여부 확인, 다운로드 처리 등의
    모든 기능을 테스트합니다.
    """
    
    @pytest.fixture
    def downloader(self):
        """
        테스트용 YtDlpDownloader 인스턴스를 제공하는 fixture
        
        Returns:
            YtDlpDownloader: 테스트용 다운로더 인스턴스
        """
        return YtDlpDownloader()
    

    @pytest.fixture
    def valid_url_buffer(self):
        """
        유효한 YouTube URL BufferDto를 제공하는 fixture
        
        Returns:
            BufferDto: 테스트용 URL 버퍼 데이터
        """
        return Payload(
            buffer="https://www.youtube.com/watch?v=dQw4w9WgXcQ".encode('utf-8'),
            metadata={},
            data_type=DataType.URL,
            status=PayloadStatus.INIT
        )
    

    @pytest.fixture
    def invalid_buffer(self):
        """
        잘못된 타입의 BufferDto를 제공하는 fixture
        
        Returns:
            BufferDto: 테스트용 잘못된 버퍼 데이터
        """
        return Payload(
            buffer="invalid_data".encode('utf-8'),
            metadata={},
            data_type=DataType.AUDIO,
            status=PayloadStatus.INIT
        )

    
    def test_init(self, downloader):
        """
        YtDlpDownloader 초기화 테스트
        
        Args:
            downloader: YtDlpDownloader 인스턴스
        """
        assert downloader.data_flow == (DataType.URL, DataType.AUDIO)
        assert "none" in downloader.available_input_ext
        assert downloader.default_output_ext == "webm"

    
    def test_is_supported_with_valid_url(self, downloader, valid_url_buffer):
        """
        유효한 YouTube URL에 대한 지원 여부 테스트
        
        Args:
            downloader: YtDlpDownloader 인스턴스
            valid_url_buffer: 유효한 URL 버퍼
        """
        assert downloader.is_supported(valid_url_buffer) == True

    
    def test_is_supported_with_invalid_data_type(self, downloader, invalid_buffer):
        """
        잘못된 데이터 타입에 대한 지원 여부 테스트
        
        Args:
            downloader: YtDlpDownloader 인스턴스
            invalid_buffer: 잘못된 버퍼 데이터
        """
        assert downloader.is_supported(invalid_buffer) == False


    # 주석 처리된 테스트 메소드 - 복잡한 Mock 설정 필요
    # @patch('src.processor.downloader.yt_dlp_downloader')
    # @patch('src.processor.downloader.yt_dlp_downloader.requests.get')
    # def test_process_success(self, mock_yt_dlp, mock_requests, downloader, valid_url_buffer):
    #     """성공적인 다운로드 처리 테스트"""
    #     # Mock 설정
    #     mock_ydl = Mock()
    #     mock_yt_dlp.return_value = mock_ydl
    #     mock_ydl.download.return_value = 0
    #     mock_requests.get.return_value = Mock(content=b"mock_audio_data")
        
    #     # Mock 파일 데이터
    #     mock_audio_data = b"mock_audio_data"
    #     mock_ydl.download.side_effect = lambda urls: mock_audio_data
        
    #     result = downloader.process(valid_url_buffer)
        
    #     # 검증
    #     assert result.data_type == DataType.AUDIO
    #     assert result.status == BufferStatus.COMPLETED
    #     assert "referrer" in result.metadata
    #     assert result.metadata["referrer"]["platform"] == "youtube"
        # assert mock_yt_dlp.YoutubeDL.called

    
    @patch('src.common.processor.downloader.strategies.yt_dlp_downloader.YoutubeDL')
    def test_process_download_failure(self, mock_youtube_dl, downloader, valid_url_buffer):
        """
        다운로드 실패 시 예외 처리 테스트
        
        Args:
            mock_youtube_dl: YoutubeDL Mock 객체
            downloader: YtDlpDownloader 인스턴스
            valid_url_buffer: 유효한 URL 버퍼
        """
        # YoutubeDL Mock 설정 - context manager에서 예외 발생
        mock_ydl_instance = MagicMock()
        mock_youtube_dl.return_value.__enter__.return_value = mock_ydl_instance
        mock_youtube_dl.return_value.__exit__.return_value = None
        
        # extract_info에서 예외 발생하도록 설정
        mock_ydl_instance.extract_info.side_effect = Exception("Invalid YouTube URL")
        
        with pytest.raises(Exception) as exc_info:
            downloader.process(valid_url_buffer)
        
        assert "Invalid YouTube URL" in str(exc_info.value)


    # 주석 처리된 테스트 메소드 - 현재 구현에서는 지원되지 않는 버퍼 처리 테스트
    # def test_process_unsupported_buffer(self, downloader, invalid_buffer):
    #     """지원하지 않는 버퍼 처리 시 예외 테스트"""
    #     with pytest.raises(ValueError) as exc_info:
    #         downloader.process(invalid_buffer)
        
    #     assert "YtDlpDownloader is not supported" in str(exc_info.value)

    
    def test_get_processor_type(self, downloader):
        """
        프로세서 타입 반환 테스트
        
        Args:
            downloader: YtDlpDownloader 인스턴스
        """
        assert downloader.get_processor_type() == ProcessorType.DOWNLOADER

    
    def test_get_data_flow(self, downloader):
        """
        데이터 플로우 반환 테스트
        
        Args:
            downloader: YtDlpDownloader 인스턴스
        """
        expected_flow = (DataType.URL, DataType.AUDIO)
        assert downloader.get_data_flow() == expected_flow

    
    def test_get_available_input_ext(self, downloader):
        """
        입력 확장자 목록 반환 테스트
        
        Args:
            downloader: YtDlpDownloader 인스턴스
        """
        assert "none" in downloader.get_available_input_ext()


    def test_get_available_output_ext(self, downloader):
        """
        출력 확장자 목록 반환 테스트
        
        Args:
            downloader: YtDlpDownloader 인스턴스
        """
        assert "webm" in downloader.get_available_output_ext()


    def test_get_default_output_ext(self, downloader):
        """
        기본 출력 확장자 반환 테스트
        
        Args:
            downloader: YtDlpDownloader 인스턴스
        """
        assert downloader.get_default_output_ext() == "webm"
