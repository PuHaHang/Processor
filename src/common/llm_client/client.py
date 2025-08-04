

from abc import ABC, abstractmethod


class LLMClient (ABC):
    _instance = None


    def get_client(self):
        if self._instance is None:
            self._instance = self.__new__(self.__class__)
        return self._instance