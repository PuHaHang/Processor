

import re

from urllib.parse import parse_qs, urlparse
import tldextract

from ..formatter_strategy import FormatterStrategy


class YoutubeFormatter(FormatterStrategy):
    domain: str = "youtube.com"

    # YouTube URL 패턴 정의
    YOUTUBE_URL_PATTERN = re.compile(
        "^(https?://)?" +                          # 프로토콜 (선택사항)
        "(www\\.)?" +                              # www (선택사항)  
        "(" +
            "youtube\\.com/" +                     # youtube.com/
                "(watch\\?v=|embed/|v/|shorts/)" + # 경로 타입들
            "|youtu\\.be/" +                       # 또는 youtu.be/
            "|m\\.youtube\\.com/watch\\?v=" +      # 또는 모바일
        ")" +
        "([a-zA-Z0-9_-]{11})" +                    # 비디오 ID (11자리)
        "(&.*|\\?.*)?$"                            # 추가 쿼리 매개변수 (선택사항)
    );

    YOUTUBE_URL_TEMPLATE = "https://www.youtube.com/watch?v=%s"


    def is_supported(self, data: str | dict) -> bool:
        if isinstance(data, str):
            return self.YOUTUBE_URL_PATTERN.match(data) is not None
        elif isinstance(data, dict):
            return data.get("platform", "") == self.domain
        return False

    def parse(self, string: str) -> dict:
        parsed_url = urlparse(string)
        query = parse_qs(parsed_url.query)
        if parsed_url.netloc == "youtu.be":
            return {
                "url": self.unparse({"v": [parsed_url.path.split("/")[-1]]}),
                "platform": self.domain,
                "metadata": {
                    "is_shorts": False
                }
            }

        if parsed_url.path.startswith("/shorts/"):
            return {
                "url": self.unparse({"v": [parsed_url.path.split("/")[-1]]}),
                "platform": self.domain,
                "metadata": {
                    "is_shorts": True
                }
            }
        
        if "v" not in query:
            raise ValueError("Invalid YouTube URL")
        elif len(query["v"]) > 1:
            raise ValueError("Invalid YouTube URL")

        return {
            "url": self.unparse(query),
            "platform": self.domain,
            "metadata": {
                "is_shorts": False,
            }
        }

    def unparse(self, data: dict) -> str:
        if "v" in data:
            if len(data["v"]) == 0:
                raise ValueError("Invalid YouTube URL")
            elif len(data["v"]) > 1:
                raise ValueError("Invalid YouTube URL")
            return self.YOUTUBE_URL_TEMPLATE % data["v"][0]
        elif "platform" in data and data["platform"] == self.domain:
            if "url" not in data:
                raise ValueError("Invalid YouTube URL")
            return data["url"]
        
        raise ValueError("Invalid YouTube URL")


        
