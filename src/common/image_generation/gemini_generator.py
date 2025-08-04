from io import BytesIO
from PIL import Image
import logfire

from google.genai.types import GenerateContentConfig, Modality

from ..llm_client.gemini_client import GeminiClient

class GeminiGenerator:

    def __init__(self):
        self.client = GeminiClient()
    
    def generate_image(self, prompt: str) -> Image:
        logfire.info('Gemini 이미지 생성 시작 {prompt}', prompt=prompt[:50] + '...' if len(prompt) > 50 else prompt)
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-preview-image-generation",
                contents=prompt,
                config=GenerateContentConfig(response_modalities=[Modality.TEXT, Modality.IMAGE]),
            )
            
            for candidate in response.candidates:
                for part in candidate.content.parts:
                    if part.inline_data:
                        image_data = part.inline_data.data
                        logfire.info('Gemini 이미지 생성 성공 {prompt}', prompt=prompt[:50] + '...' if len(prompt) > 50 else prompt)
                        return Image.open(BytesIO(image_data))
            
            logfire.warn('Gemini 이미지 생성 실패 - 이미지 데이터 없음 {prompt}', prompt=prompt[:50] + '...' if len(prompt) > 50 else prompt)
            return None
            
        except Exception as e:
            logfire.error('Gemini 이미지 생성 중 오류 발생 {error}, prompt: {prompt}', error=str(e), prompt=prompt[:50] + '...' if len(prompt) > 50 else prompt)
            raise
    
    
    