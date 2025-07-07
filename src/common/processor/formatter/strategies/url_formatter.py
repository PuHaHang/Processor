import re
from urllib.parse import urlparse

from ..formatter_strategy import FormatterStrategy


class UrlFormatter(FormatterStrategy):
    
    URL_PATTERN = re.compile(
        r"^(https?://)?" +
        r"(www\.)?" +
        r"([a-zA-Z0-9.-]+)" +
        r"(\.[a-zA-Z]{2,})" +
        r"(:\d+)?" +
        r"(/[a-zA-Z0-9.-/]*)?" +
        r"(\?[a-zA-Z0-9.-/=]*)?$"
    )


    def is_supported(self, data: str | dict) -> bool:
        if isinstance(data, str):
            return self.URL_PATTERN.match(data) is not None
        elif isinstance(data, dict):
            return data.get("url", "") is not None
        return False

    def parse(self, data: str) -> dict:
        parsed_url = urlparse(data)
        return {
            "url": data,
            "platform": self.get_domain(data),
            "metadata": {
                "scheme": parsed_url.scheme,
                "netloc": parsed_url.netloc,
                "path": parsed_url.path,
                "params": parsed_url.params,
                "query": parsed_url.query,
                "fragment": parsed_url.fragment,
            }
        }

    def unparse(self, data: dict) -> str:
        return data.get("url", "")