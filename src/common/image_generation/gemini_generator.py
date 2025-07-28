from io import BytesIO
from PIL import Image

from google.genai.types import GenerateContentConfig, Modality

from ..llm_client.gemini_client import GeminiClient

class GeminiGenerator:

    def __init__(self):
        self.client = GeminiClient()
    
    def generate_image(self, prompt: str) -> Image:
        response = self.client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=prompt,
            config=GenerateContentConfig(response_modalities=[Modality.TEXT, Modality.IMAGE]),
        )
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if part.inline_data:
                    image_data = part.inline_data.data
                    return Image.open(BytesIO(image_data))
        return None
    
    
    