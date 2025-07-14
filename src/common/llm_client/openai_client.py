from openai import OpenAI

from .client import LLMClient


# Singleton Pattern
class OpenAIClient (OpenAI, LLMClient):
    _instance = None
    def __new__ (cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
