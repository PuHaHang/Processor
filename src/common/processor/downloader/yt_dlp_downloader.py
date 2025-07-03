"""
YouTube-DL 다운로더 모듈

이 모듈은 yt-dlp 라이브러리를 사용하여 YouTube 등의 플랫폼에서
오디오 스트림을 다운로드하는 다운로더를 제공합니다.
"""

import io
import re
import os, sys
from typing import Tuple

from src.common.processor.data_type import DataType
from src.common.processor.downloader.downloader import Downloader

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
from yt_dlp import YoutubeDL

from src.common.processor.data_structure.buffer_dto import BufferDto
from src.common.processor.data_structure.buffer_status import BufferStatus


class YtDlpDownloader (Downloader):
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

    # YouTube URL 패턴 정의
    YOUTUBE_URL_PATTERN = re.compile(
        "^(https?://)?" +                          # 프로토콜 (선택사항)
        "(www\\.)?" +                              # www (선택사항)  
        "(youtube\\.com/" +                        # youtube.com/
            "(watch\\?v=|embed/|v/|shorts/)" +     # 경로 타입들
        "|youtu\\.be/" +                           # 또는 youtu.be/
        "|m\\.youtube\\.com/watch\\?v=)" +         # 또는 모바일
        "([a-zA-Z0-9_-]{11})" +                    # 비디오 ID (11자리)
        "(\\?.*)?$"
    );

    # YouTube 스트림 URL 템플릿
    YOUTUBE_STREAM_URL = "https://www.youtube.com/watch?v=%s"
    
    
    def process(self, buffer_dto: BufferDto, opt: dict = {}) -> BufferDto:
        """
        URL에서 오디오를 다운로드하여 버퍼 데이터로 변환합니다.
        
        Args:
            buffer_dto (BufferDto): 처리할 URL 버퍼 데이터
            opt (dict, optional): 처리 옵션
        
        Returns:
            BufferDto: 다운로드된 오디오 데이터가 포함된 버퍼 데이터
            
        Raises:
            ValueError: 지원되지 않는 URL 형식인 경우
        """
        # URL에서 비디오 ID와 플랫폼 추출
        video_id, platform = self._parse_video_id(buffer_dto.get_buffer_string())

        # 비디오 URL 생성
        video_url = self._get_video_url(video_id, platform)
        # 실제 스트리밍 URL 추출
        stream_url = self._extract_stream_url(video_url)

        return BufferDto(
            buffer=self._download_stream(stream_url).getvalue(),
            metadata={
                **self._extract_metadata(video_url),
                "referrer": {
                    "video_id": video_id,
                    "platform": platform
                }
            },
            data_type=DataType.AUDIO,
            status=BufferStatus.COMPLETED
        )


    def is_supported(self, buffer_dto: BufferDto) -> bool:
        """
        버퍼 데이터가 이 다운로더에서 지원되는지 확인합니다.
        
        Args:
            buffer_dto (BufferDto): 확인할 버퍼 데이터
        
        Returns:
            bool: URL 타입이고 파싱 가능한 경우 True
        """
        return self.data_flow[0] == buffer_dto.data_type \
            and self._parse_video_id(buffer_dto.get_buffer_string()) is not None


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

    
    def _parse_video_id(self, video_url: str) -> tuple[str, str]:
        """
        비디오 URL에서 비디오 ID와 플랫폼을 추출합니다.
        
        Args:
            video_url (str): 파싱할 비디오 URL
        
        Returns:
            tuple[str, str]: (비디오 ID, 플랫폼)
            
        Raises:
            ValueError: 유효하지 않은 URL 형식인 경우
        """
        # YouTube URL 패턴 매칭
        matched = self.YOUTUBE_URL_PATTERN.fullmatch(video_url)
        if matched and matched.group(5):
            return matched.group(5), "youtube"
        raise ValueError(f"Invalid video url: {video_url}")


    def _get_video_url(self, video_id: str, platform: str) -> str:
        """
        비디오 ID와 플랫폼으로부터 표준 비디오 URL을 생성합니다.
        
        Args:
            video_id (str): 비디오 ID
            platform (str): 플랫폼 이름
        
        Returns:
            str: 표준 비디오 URL
            
        Raises:
            ValueError: 지원되지 않는 플랫폼인 경우
        """
        match platform:
            case "youtube":
                return self.YOUTUBE_STREAM_URL % video_id
            case _:
                raise ValueError(f"Unsupported platform: {platform}")


    def _extract_stream_url(self, video_url: str) -> str:
        """
        비디오 URL에서 실제 오디오 스트림 URL을 추출합니다.
        
        Args:
            video_url (str): 스트림 URL을 추출할 비디오 URL
        
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
            info = ydl.extract_info(video_url, download=False)
            if info is None or not isinstance(info, dict) or 'url' not in info:
                raise ValueError(f"Could not extract stream URL from {video_url}")
            return info['url']  # 실제 오디오-only 스트리밍 URL