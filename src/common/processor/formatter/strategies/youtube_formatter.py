"""
YouTube 포맷터 전략 모듈

이 모듈은 YouTube URL을 파싱하고 표준화하는 포맷터 전략을 제공합니다.
다양한 YouTube URL 형식을 지원하며, 비디오 ID 추출과 URL 생성을 담당합니다.
"""

import re
from urllib.parse import parse_qs, urlparse
import tldextract

from ..formatter_strategy import FormatterStrategy
from ....exception import (
    ExceptionHandler,
    ValidationExceptionHandler,
    ExceptionType,
    ExceptionSeverity,
    ValidationException
)


class YoutubeFormatter(FormatterStrategy):
    domain: str = "youtube.com"

    # YouTube URL 패턴 정의
    YOUTUBE_URL_PATTERN = re.compile(
        r"""^
        (?:https?://)?                # 프로토콜 (선택)
        (?:www\.|m\.)?                # www. 또는 m. (선택)
        (?:
            (?:youtube\.com/          # youtube.com/
                (?:
                    watch\?           # watch? (쿼리)
                    (?:.*&)?v=        # v= 파라미터 (중간에 다른 파라미터 허용)
                    (?P<id1>[a-zA-Z0-9_-]{11}) # 비디오 ID
                    (?:[&#].*)?       # 추가 파라미터 (선택)
                |
                    (?:embed|v|shorts)/ # embed/, v/, shorts/
                    (?P<id2>[a-zA-Z0-9_-]{11}) # 비디오 ID
                    (?:[/?&#].*)?     # 추가 파라미터 (선택)
                )
            )
        |
            youtu\.be/                # youtu.be/
            (?P<id3>[a-zA-Z0-9_-]{11}) # 비디오 ID
            (?:[/?&#].*)?             # 추가 파라미터 (선택)
        )
        $""",
        re.IGNORECASE | re.VERBOSE
    )

    YOUTUBE_URL_TEMPLATE = "https://www.youtube.com/watch?v=%s"

    @ExceptionHandler(
        exception_type=ExceptionType.URL_PARSING_ERROR,
        severity=ExceptionSeverity.LOW,
        reraise=True,
        log_level="info",
        handler_name="youtube_formatter_is_supported_handler"
    )
    def is_supported(self, data: str | dict) -> bool:
        """
        데이터가 YouTube URL인지 확인합니다.
        
        Args:
            data: 확인할 데이터 (문자열 또는 딕셔너리)
            
        Returns:
            bool: YouTube URL이면 True, 아니면 False
        """
        if isinstance(data, str):
            return self.YOUTUBE_URL_PATTERN.match(data) is not None
        elif isinstance(data, dict):
            return data.get("platform", "") == self.domain
        return False

    @ExceptionHandler(
        exception_type=ExceptionType.URL_PARSING_ERROR,
        severity=ExceptionSeverity.MEDIUM,
        reraise=True,
        log_level="warning",
        handler_name="youtube_formatter_parse_handler"
    )
    @ValidationExceptionHandler(reraise=True)
    def parse(self, string: str) -> dict:
        """
        YouTube URL을 파싱하여 구조화된 데이터로 변환합니다.
        
        Args:
            string: 파싱할 YouTube URL
            
        Returns:
            dict: 파싱된 YouTube URL 데이터
            
        Raises:
            ValidationException: 유효하지 않은 YouTube URL인 경우
        """
        # YOUTUBE_URL_PATTERN을 활용하여 파싱 및 검증 수행
        if not self.YOUTUBE_URL_PATTERN.match(string):
            raise ValidationException(
                message="유효하지 않은 YouTube URL 형식입니다",
                field_name="url",
                field_value=string,
                validation_rule="youtube_url_valid_format"
            )

        parsed_url = urlparse(string)
        path = parsed_url.path or ""
        netloc = parsed_url.netloc.lower().replace("www.", "")
        query = parse_qs(parsed_url.query)

        # youtu.be 단축 URL 처리
        if netloc == "youtu.be":
            video_id = path.lstrip("/").split("/")[0]
            if not video_id or len(video_id) != 11:
                raise ValidationException(
                    message="YouTube 단축 URL에 올바른 비디오 ID가 없습니다",
                    field_name="url",
                    field_value=string,
                    validation_rule="youtube_video_id_required"
                )
            return {
                "url": self.unparse({"v": [video_id]}),
                "platform": self.domain,
                "metadata": {
                    "is_shorts": False
                }
            }

        # /shorts 경로 처리
        if path.startswith("/shorts/"):
            video_id = path.split("/shorts/")[-1].split("/")[0]
            if not video_id or len(video_id) != 11:
                raise ValidationException(
                    message="YouTube Shorts URL에 올바른 비디오 ID가 없습니다",
                    field_name="url",
                    field_value=string,
                    validation_rule="youtube_shorts_video_id_required"
                )
            return {
                "url": self.unparse({"v": [video_id]}),
                "platform": self.domain,
                "metadata": {
                    "is_shorts": True
                }
            }

        # 일반 watch, embed, v 경로 처리
        video_id = None
        is_shorts = False

        # /watch 경로: 쿼리에서 v 추출
        if path.startswith("/watch"):
            v_list = query.get("v", [])
            if not v_list or not v_list[0]:
                raise ValidationException(
                    message="YouTube URL에 비디오 ID가 없습니다",
                    field_name="url",
                    field_value=string,
                    validation_rule="youtube_video_id_required"
                )
            if len(v_list) > 1:
                raise ValidationException(
                    message="YouTube URL에 중복된 비디오 ID가 있습니다",
                    field_name="url",
                    field_value=string,
                    validation_rule="youtube_single_video_id"
                )
            video_id = v_list[0]
        # /embed/ 또는 /v/ 경로: path에서 ID 추출
        elif path.startswith("/embed/") or path.startswith("/v/"):
            video_id = path.split("/")[-1]
        else:
            raise ValidationException(
                message="지원하지 않는 YouTube URL 경로입니다",
                field_name="url",
                field_value=string,
                validation_rule="youtube_unsupported_path"
            )

        if not video_id or len(video_id) != 11:
            raise ValidationException(
                message="YouTube URL에 올바른 비디오 ID가 없습니다",
                field_name="url",
                field_value=string,
                validation_rule="youtube_video_id_length"
            )

        return {
            "url": self.unparse({"v": [video_id]}),
            "platform": self.domain,
            "metadata": {
                "is_shorts": is_shorts
            }
        }

    @ExceptionHandler(
        exception_type=ExceptionType.URL_PARSING_ERROR,
        severity=ExceptionSeverity.MEDIUM,
        reraise=True,
        log_level="warning",
        handler_name="youtube_formatter_unparse_handler"
    )
    @ValidationExceptionHandler(reraise=True)
    def unparse(self, data: dict) -> str:
        """
        구조화된 데이터를 YouTube URL로 변환합니다.
        
        Args:
            data: 변환할 데이터 딕셔너리
            
        Returns:
            str: 생성된 YouTube URL
            
        Raises:
            ValidationException: 유효하지 않은 데이터인 경우
        """
        if "v" in data:
            if len(data["v"]) == 0:
                raise ValidationException(
                    message="YouTube 비디오 ID가 비어있습니다",
                    field_name="v",
                    field_value=data["v"],
                    validation_rule="youtube_video_id_not_empty"
                )
            elif len(data["v"]) > 1:
                raise ValidationException(
                    message="YouTube 비디오 ID가 여러 개입니다",
                    field_name="v",
                    field_value=data["v"],
                    validation_rule="youtube_single_video_id"
                )
            return self.YOUTUBE_URL_TEMPLATE % data["v"][0]
        elif "platform" in data and data["platform"] == self.domain:
            if "url" not in data:
                raise ValidationException(
                    message="YouTube URL 데이터에 url 필드가 없습니다",
                    field_name="url",
                    field_value=None,
                    validation_rule="youtube_url_required"
                )
            return data["url"]
        
        raise ValidationException(
            message="유효하지 않은 YouTube URL 데이터입니다",
            field_name="data",
            field_value=str(data),
            validation_rule="youtube_valid_data"
        )


        
