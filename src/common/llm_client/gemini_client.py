from google import genai

from .client import LLMClient


class GeminiClient (genai.Client, LLMClient):
    _instance = None
    def __new__ (cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        
        
        
        
        
        
        