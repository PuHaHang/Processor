from abc import ABC, abstractmethod
from typing import overload

import tldextract


class FormatterStrategy(ABC):

    @overload
    def is_supported(self, data: str) -> bool:
        ...


    @overload
    def is_supported(self, data: dict) -> bool:
        ...


    @abstractmethod
    def is_supported(self, data: str | dict) -> bool:
        ...


    @abstractmethod
    def unparse(self, data: dict) -> str:
        ...


    @abstractmethod
    def parse(self, string: str) -> dict:
        ...
    

    def get_domain(self, url: str) -> str:
        ext = tldextract.extract(url)
        return ext.domain + "." + ext.suffix