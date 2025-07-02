"""
URL 분류기 모듈

이 모듈은 입력된 URL을 분석하여 플랫폼(YouTube, Twitter 등)을 식별하고
비디오 ID를 추출하는 분류기를 제공합니다.
"""

import re
from typing import Dict, Tuple

from src.processor.classifier.classifier import Classifier
from src.processor.data_structure.buffer_dto import BufferDto
from src.processor.data_structure.buffer_status import BufferStatus
from src.processor.data_type import DataType

class UrlClassifier (Classifier):
    """
    URL을 분석하여 플랫폼과 비디오 ID를 추출하는 분류기
    
    YouTube, Twitter 등의 URL을 정규표현식으로 분석하여
    플랫폼 정보와 비디오 ID를 추출합니다.
    
    Attributes:
        data_flow (Tuple[DataType, DataType]): TEXT → URL로 데이터 타입 변환
        available_input_ext (list[str]): 지원하는 입력 확장자 ('text')
        available_output_ext (list[str]): 지원하는 출력 확장자 ('url')
        default_output_ext (str): 기본 출력 확장자 ('url')
        patterns (dict): 플랫폼별 URL 패턴 정규표현식
        match_sequence (dict): 정규표현식 매칭 그룹 순서 정의
    """
    data_flow: Tuple[DataType, DataType] = (DataType.TEXT, DataType.URL)
    available_input_ext: list[str] = ["text"]
    available_output_ext: list[str] = ["url"]
    default_output_ext: str = "url"

    # 플랫폼별 URL 패턴 정의
    patterns = {
        "youtube": re.compile(
            "^(https?://)?" +                          # 프로토콜 (선택사항)
            "(www\\.)?" +                              # www (선택사항)  
            "(youtube\\.com/" +                        # youtube.com/
                "(watch\\?v=|embed/|v/|shorts/)" +     # 경로 타입들
            "|youtu\\.be/" +                           # 또는 youtu.be/
            "|m\\.youtube\\.com/watch\\?v=)" +         # 또는 모바일
            "([a-zA-Z0-9_-]{11})" +                    # 비디오 ID (11자리)
            "(\\?.*)?$"
        ),
        "twitter": re.compile(
            "^(https?://)?" +                          # 프로토콜 (선택사항)
            "(www\\.)?" +                              # www (선택사항)  
            "(twitter\\.com/)" +                        # twitter.com/
            "([a-zA-Z0-9_-]{11})" +                    # 비디오 ID (11자리)
            "(\\?.*)?$"
        ),
        "unknown": re.compile(
            "^(https?://)?" +                          # 프로토콜 (선택사항)
            "(www\\.)?" +                              # www (선택사항)  
            "(.*)" +                                    # 모든 문자열
            "(\\?.*)?$"
        )
    }

    # 정규표현식 매칭 그룹 순서 정의
    match_sequence = {
        "youtube": {
            "protocol": 1,      # 프로토콜 그룹
            "www": 2,          # www 그룹
            "host": 3,         # 호스트 그룹
            "type": 4,         # URL 타입 그룹
            "video_id": 5,     # 비디오 ID 그룹
            "query_string": 6  # 쿼리 스트링 그룹
        },
        "twitter": {
            "protocol": 1,      # 프로토콜 그룹
            "www": 2,          # www 그룹
            "host": 3,         # 호스트 그룹
            "video_id": 4,     # 비디오 ID 그룹
            "query_string": 5  # 쿼리 스트링 그룹
        },
        "unknown": {
            "protocol": 1,      # 프로토콜 그룹
            "www": 2,          # www 그룹
            "host": 3,         # 호스트 그룹
            "query_string": 4  # 쿼리 스트링 그룹
        }
    }


    def process(self, buffer_dto: BufferDto, opt: dict = {}) -> BufferDto:
        """
        URL을 분류하여 플랫폼 정보와 비디오 ID를 추출합니다.
        
        Args:
            buffer_dto (BufferDto): 처리할 버퍼 데이터 (URL 텍스트)
            opt (dict, optional): 처리 옵션
        
        Returns:
            BufferDto: 분류된 URL 정보가 포함된 버퍼 데이터
        """
        return BufferDto(
            buffer=buffer_dto.buffer,
            metadata={
                "referrer": self._classify_url(buffer_dto.buffer.decode("utf-8")),
            },
            status=BufferStatus.COMPLETED,
            data_type=DataType.URL
        )


    def is_supported(self, buffer_dto: BufferDto) -> bool:
        """
        버퍼 데이터가 이 분류기에서 지원되는지 확인합니다.
        
        Args:
            buffer_dto (BufferDto): 확인할 버퍼 데이터
        
        Returns:
            bool: TEXT 타입인 경우 True, 그렇지 않으면 False
        """
        return buffer_dto.data_type == self.data_flow[0]


    def _classify_url(self, url: str) -> dict | None:
        """
        URL을 분석하여 플랫폼과 비디오 ID를 추출합니다.
        
        Args:
            url (str): 분석할 URL 문자열
        
        Returns:
            dict | None: 플랫폼과 비디오 ID 정보, 매칭되지 않으면 None
        """
        # 각 플랫폼 패턴과 매칭 시도
        for platform, pattern in self.patterns.items():
            if (matched := pattern.match(url)):
                return {
                    "platform": platform,
                    "video_id": matched.group(self.match_sequence[platform]["video_id"])
                }
        return None