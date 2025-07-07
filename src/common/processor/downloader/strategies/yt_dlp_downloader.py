"""
YouTube-DL 다운로더 모듈

이 모듈은 yt-dlp 라이브러리를 사용하여 YouTube 등의 플랫폼에서
오디오 스트림을 다운로드하는 다운로더를 제공합니다.
"""

import io
import os, sys
from typing import Tuple

from yt_dlp.utils import DownloadError

from ...types import DataType
from ..downloader_strategy import DownloaderStrategy

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
from yt_dlp import YoutubeDL

from ...types import Payload, PayloadStatus
from ...formatter import Formatter


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

        # URL에서 비디오 ID와 플랫폼 추출
        reference = formatter.parse(payload.get_buffer_string())
        if not reference:
            raise ValueError(f"Invalid reference: {payload.get_buffer_string()}")

        # 실제 스트리밍 URL 추출
        stream_url = self._extract_stream_url(formatter.unparse(reference))

        return Payload(
            buffer=self._download_stream(stream_url).getvalue(),
            metadata={
                "reference": reference,
            },
            data_type=DataType.AUDIO,
            status=PayloadStatus.COMPLETED
        )


    def is_supported(self, payload: Payload) -> bool:
        """
        버퍼 데이터가 이 다운로더에서 지원되는지 확인합니다.
        
        Args:
            payload (Payload): 확인할 버퍼 데이터
        
        Returns:
            bool: URL 타입이고 파싱 가능한 경우 True
        """
        return self.data_flow[0] == payload.data_type and \
            self._is_supported(payload.get_buffer_string())


    def _download_stream(self, stream_url: str) -> io.BytesIO:
        """
        스트림 URL에서 오디오 데이터를 다운로드합니다.
        
        Args:
            stream_url (str): 다운로드할 스트림 URL
        
        Returns:
            io.BytesIO: 다운로드된 오디오 데이터
        """
        # HTTP 스트리밍으로 데이터 다운로드
        with requests.get(stream_url, stream=True) as response:
            return io.BytesIO(response.content)


    def _extract_metadata(self, video_url: str) -> dict:
        """
        비디오 URL에서 메타데이터를 추출합니다.
        
        Args:
            video_url (str): 메타데이터를 추출할 비디오 URL
        
        Returns:
            dict: 추출된 메타데이터 (제목, 설명, 길이 등)
        """
        # yt-dlp 옵션 설정 (다운로드 없이 정보만 추출)
        ydl_opts = {
            'quiet': True,
            'skip_download': True,   # 다운로드 생략 (중요)
            'no_warnings': True,
            'noplaylist': True
        }
        with YoutubeDL(ydl_opts) as ydl:
            # 비디오 정보 추출
            info = ydl.extract_info(video_url, download=False)
            if info is None:
                return {}
            try:
                # 실제 스트림 URL은 메타데이터에서 제거
                if 'url' in info:
                    del info['url']
            except (KeyError, TypeError):
                pass
            return info if isinstance(info, dict) else {}


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
        # yt-dlp 옵션 설정 (최고 품질 오디오 선택)
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '-',  # output template, 필요 없음 (파이썬 API 사용)
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True
        }
        with YoutubeDL(ydl_opts) as ydl:
            # 비디오 정보 추출하여 실제 스트림 URL 획득
            info = ydl.extract_info(url, download=False)
            if info is None or not isinstance(info, dict) or 'url' not in info:
                raise ValueError(f"Could not extract stream URL from {url}")
            return info['url']  # 실제 오디오-only 스트리밍 URL
    
    def _is_supported(self, url: str) -> bool:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'simulate': True
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(url, download=False)
            return True
        except DownloadError:
            return False
        except Exception:
            return False