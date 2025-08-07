"""
YouTube-DL 다운로더 모듈

이 모듈은 yt-dlp 라이브러리를 사용하여 YouTube 등의 플랫폼에서
오디오 스트림을 다운로드하는 다운로더를 제공합니다.
"""

import io
import os, sys
from typing import Any, Tuple

from yt_dlp.utils import DownloadError

from ...types import DataType
from ..downloader_strategy import DownloaderStrategy

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
from yt_dlp import YoutubeDL

from ...types import Payload, PayloadStatus
from ...formatter import Formatter

# 예외 핸들러 import
from ....exception import (
    ExceptionHandler,
    RetryOnException,
    CircuitBreaker,
    ValidationExceptionHandler,
    ExceptionType,
    ExceptionSeverity,
    ExternalServiceException,
    ValidationException
)


class YtDlpDownloader (DownloaderStrategy):
    """
    yt-dlp를 사용하는 YouTube 다운로더
    
    YouTube URL에서 오디오 스트림을 추출하여 다운로드합니다.
    yt-dlp 라이브러리를 통해 실제 스트리밍 URL을 가져온 후
    requests를 사용하여 오디오 데이터를 다운로드합니다.
    
    Attributes:
        data_flow (Tuple[DataType, DataType]): URL → AUDIO로 데이터 타입 변환
        available_input_ext (list[str]): 지원하는 입력 확장자 ('none')
        available_output_ext (list[str]): 지원하는 출력 확장자 ('webm')
        default_output_ext (str): 기본 출력 확장자 ('webm')
        YOUTUBE_URL_PATTERN (re.Pattern): YouTube URL 패턴 정규표현식
        YOUTUBE_STREAM_URL (str): YouTube 스트림 URL 템플릿
    """
    data_flow: Tuple[DataType, DataType] = (DataType.URL, DataType.AUDIO)
    available_input_ext: list[str] = ["none"]
    available_output_ext: list[str] = ["webm"]
    default_output_ext: str = "webm"

    metadata_keys_to_get: dict[str, Any] = {
        'id': None,
        'title': None,
        'description': None,
        'duration': None,
        'thumbnail': None,
        'channel': None,
        'channel_url': None,
        'formats': {
            'ext': None,
        },
        'webpage_url': None,
        'playable_in_embed': None,
        'subtitles': None,
        'uploader': None,
        'uploader_id': None,
        'uploader_url': None,
        'upload_date': None,
        'fulltitle': None,
    }
    cookie_file_path: str = "/tmp/cookies.txt"
    
    @ExceptionHandler(
        exception_type=ExceptionType.EXTERNAL_SERVICE_ERROR,
        severity=ExceptionSeverity.HIGH,
        reraise=True,
        log_level="error",
        handler_name="yt_dlp_process_handler"
    )
    @RetryOnException(
        max_retries=3,
        retry_delay=2.0,
        backoff_factor=2.0,
        exception_types=[ConnectionError, TimeoutError, DownloadError, requests.exceptions.RequestException],
        reraise_on_failure=True
    )
    @CircuitBreaker(
        failure_threshold=5,
        recovery_timeout=60,
        expected_exception=ConnectionError
    )
    def process(self, payload: Payload, opt: dict = {}) -> Payload:
        """
        URL에서 오디오를 다운로드하여 버퍼 데이터로 변환합니다.
        
        Args:
            payload (Payload): 처리할 URL 버퍼 데이터
            opt (dict, optional): 처리 옵션
        
        Returns:
            Payload: 다운로드된 오디오 데이터가 포함된 버퍼 데이터
            
        Raises:
            ValueError: 지원되지 않는 URL 형식인 경우
        """
        formatter = Formatter()

        buffer_data = payload.get_buffer().decode('utf-8')

        # URL에서 비디오 ID와 플랫폼 추출
        reference = formatter.parse(buffer_data)
        if not reference:
            raise ValidationException(
                message="유효하지 않은 URL 형식입니다",
                field_name="url",
                field_value=buffer_data,
                validation_rule="url_format"
            )

        # 실제 스트리밍 URL 추출
        stream_url = self._extract_stream_url(formatter.unparse(reference))

        return Payload(
            buffer=self._download_stream(stream_url).getvalue(),
            metadata=self._extract_metadata(formatter.unparse(reference)) | {
                "reference": reference,
            },
            data_type=DataType.AUDIO,
            status=PayloadStatus.COMPLETED,
            processor=self
        )


    @ValidationExceptionHandler(reraise=False, default_return=False)
    def is_supported(self, payload: Payload) -> bool:
        """
        버퍼 데이터가 이 다운로더에서 지원되는지 확인합니다.
        
        Args:
            payload (Payload): 확인할 버퍼 데이터
        
        Returns:
            bool: URL 타입이고 파싱 가능한 경우 True
        """
        return self.data_flow[0] == payload.data_type and \
            self._is_supported(payload.get_buffer().decode('utf-8'))


    @ExceptionHandler(
        exception_type=ExceptionType.NETWORK_ERROR,
        severity=ExceptionSeverity.MEDIUM,
        reraise=True,
        log_level="warning",
        handler_name="stream_download_handler"
    )
    @RetryOnException(
        max_retries=2,
        retry_delay=1.0,
        backoff_factor=2.0,
        exception_types=[requests.exceptions.RequestException, ConnectionError, TimeoutError]
    )
    def _download_stream(self, stream_url: str) -> io.BytesIO:
        """
        스트림 URL에서 오디오 데이터를 다운로드합니다.
        
        Args:
            stream_url (str): 다운로드할 스트림 URL
        
        Returns:
            io.BytesIO: 다운로드된 오디오 데이터
        """
        return self._perform_stream_download(stream_url)

    @ExceptionHandler(
        exception_type=ExceptionType.NETWORK_ERROR,
        severity=ExceptionSeverity.MEDIUM,
        reraise=True,
        log_level="error",
        handler_name="stream_download_core_handler"
    )
    def _perform_stream_download(self, stream_url: str) -> io.BytesIO:
        """
        실제 스트림 다운로드를 수행하는 내부 메소드
        
        Args:
            stream_url (str): 다운로드할 스트림 URL
        
        Returns:
            io.BytesIO: 다운로드된 오디오 데이터
        """
        # HTTP 스트리밍으로 데이터 다운로드
        with requests.get(stream_url, stream=True, timeout=30) as response:
            response.raise_for_status()
            return io.BytesIO(response.content)


    @ExceptionHandler(
        exception_type=ExceptionType.METADATA_EXTRACTION_ERROR,
        severity=ExceptionSeverity.MEDIUM,
        reraise=True,
        log_level="info",
        handler_name="metadata_extraction_handler"
    )
    @RetryOnException(
        max_retries=2,
        retry_delay=1.0,
        exception_types=[DownloadError, ConnectionError]
    )
    def _extract_metadata(self, video_url: str) -> dict:
        """
        비디오 URL에서 메타데이터를 추출합니다.
        
        Args:
            video_url (str): 메타데이터를 추출할 비디오 URL
        
        Returns:
            dict: 추출된 메타데이터 (제목, 설명, 길이 등)
        """
        return self._perform_metadata_extraction(video_url)

    @ExceptionHandler(
        exception_type=ExceptionType.METADATA_EXTRACTION_ERROR,
        severity=ExceptionSeverity.MEDIUM,
        reraise=True,
        log_level="error",
        handler_name="metadata_extraction_core_handler"
    )
    def _perform_metadata_extraction(self, video_url: str) -> dict:
        """
        실제 메타데이터 추출을 수행하는 내부 메소드
        
        Args:
            video_url (str): 메타데이터를 추출할 비디오 URL
        
        Returns:
            dict: 추출된 메타데이터
        """
        # yt-dlp 옵션 설정 (다운로드 없이 정보만 추출)
        ydl_opts = {
            'quiet': True,
            'skip_download': True,   # 다운로드 생략 (중요)
            'no_warnings': True,
            'noplaylist': True,
            'cookies': self.cookie_file_path,
            'geo_bypass': True,
            'no_check_certificate': True,
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.youtube.com/',
                'Origin': 'https://www.youtube.com',
            }
        }
        with YoutubeDL(ydl_opts) as ydl:
            # 비디오 정보 추출
            info = ydl.extract_info(video_url, download=False)
            if info is None:
                return {}
            return self._get_metadata_by_keys(info)

    @ExceptionHandler(
        exception_type=ExceptionType.EXTERNAL_SERVICE_ERROR,
        severity=ExceptionSeverity.HIGH,
        reraise=True,
        log_level="error",
        handler_name="stream_url_extraction_handler"
    )
    @RetryOnException(
        max_retries=3,
        retry_delay=2.0,
        backoff_factor=2.0,
        exception_types=[DownloadError, ConnectionError]
    )
    def _extract_stream_url(self, url: str) -> str:
        """
        비디오 URL에서 실제 오디오 스트림 URL을 추출합니다.
        
        Args:
            url (str): 스트림 URL을 추출할 URL
        
        Returns:
            str: 실제 오디오 스트리밍 URL
            
        Raises:
            ValueError: 스트림 URL을 찾을 수 없는 경우
        """
        return self._perform_stream_url_extraction(url)

    @ExceptionHandler(
        exception_type=ExceptionType.EXTERNAL_SERVICE_ERROR,
        severity=ExceptionSeverity.HIGH,
        reraise=True,
        log_level="error",
        handler_name="stream_url_extraction_core_handler"
    )
    def _perform_stream_url_extraction(self, url: str) -> str:
        """
        실제 스트림 URL 추출을 수행하는 내부 메소드
        
        Args:
            url (str): 스트림 URL을 추출할 URL
        
        Returns:
            str: 실제 오디오 스트리밍 URL
        """
        # yt-dlp 옵션 설정 (최고 품질 오디오 선택)
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '-',  # output template, 필요 없음 (파이썬 API 사용)
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'cookies': self.cookie_file_path,
            'geo_bypass': True,
            'no_check_certificate': True,
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.youtube.com/',
                'Origin': 'https://www.youtube.com',
            }
        }
        with YoutubeDL(ydl_opts) as ydl:
            # 비디오 정보 추출하여 실제 스트림 URL 획득
            info = ydl.extract_info(url, download=False)
            if info is None or not isinstance(info, dict) or 'url' not in info:
                raise ExternalServiceException(
                    message=f"스트림 URL을 추출할 수 없습니다",
                    service_name="yt-dlp",
                    endpoint=url
                )
            return info['url']  # 실제 오디오-only 스트리밍 URL
    
    @ValidationExceptionHandler(reraise=False, default_return=False)
    def _is_supported(self, url: str) -> bool:
        return self._perform_support_check(url)

    @ExceptionHandler(
        exception_type=ExceptionType.EXTERNAL_SERVICE_ERROR,
        severity=ExceptionSeverity.LOW,
        reraise=False,
        default_return=False,
        log_level="debug",
        handler_name="support_check_handler"
    )
    def _perform_support_check(self, url: str) -> bool:
        """
        실제 지원 여부 확인을 수행하는 내부 메소드
        
        Args:
            url (str): 확인할 URL
            
        Returns:
            bool: 지원 여부
        """
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'simulate': True,
            'cookies': self.cookie_file_path,
            'geo_bypass': True,
            'no_check_certificate': True,
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.youtube.com/',
                'Origin': 'https://www.youtube.com',
            }
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=False)
        return True
    
    def _get_metadata_by_keys(self, info: dict, keys: dict[str, Any] = metadata_keys_to_get) -> dict:
        result = {}
        for key, value in keys.items():
            if value is None and key in info:
                if isinstance(info[key], list):
                    result[key] = []
                    for item in info[key]:
                        if isinstance(item, dict):
                            result[key].append(self._get_metadata_by_keys(item, value))
                        else:
                            result[key].append(item)
                else:
                    result[key] = info[key]
                continue
            if isinstance(value, dict):
                result[key] = self._get_metadata_by_keys(info[key], value)
            else:
                pass
        return result
