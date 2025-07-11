"""
Gemini 기반 레시피 정제 전략 모듈

이 모듈은 Google Gemini 모델을 사용하여 비디오, 오디오, 텍스트 데이터를
구조화된 레시피로 정제하는 전략을 구현합니다.
"""

import base64
import json
import logging
from typing import Tuple, Optional, Any

from ..refiner_strategy import RefinerStrategy
from ...types import DataType, Payload, PayloadStatus
from ....llm_client import GeminiClient
from ....prompt.recipe_refiner_prompt import RecipeRefinerPrompt


class GeminiRefiner(RefinerStrategy):
    """
    Gemini 모델을 사용한 레시피 정제 전략
    
    비디오, 오디오, 텍스트 데이터를 입력받아 Gemini 모델을 통해
    구조화된 레시피 텍스트로 정제합니다.
    
    Attributes:
        data_flow (Tuple[DataType, DataType]): 입력(GENERIC) → 출력(TEXT) 데이터 플로우
        available_input_ext (list[str]): 지원하는 입력 파일 확장자 목록
        available_output_ext (list[str]): 지원하는 출력 파일 확장자 목록
        default_output_ext (str): 기본 출력 파일 확장자
    """
    
    data_flow: Tuple[DataType, DataType] = (DataType.GENERIC, DataType.TEXT)
    available_input_ext: list[str] = ['.mp4', '.avi', '.mov', '.mp3', '.wav', '.txt', '.srt', '.vtt']
    available_output_ext: list[str] = ['.txt', '.md', '.json']
    default_output_ext: str = '.json'

    def __init__(self):
        """GeminiRefiner 초기화"""
        self._logger = logging.getLogger(__name__)
        self._client: Optional[GeminiClient] = None
        self._prompt_generator = RecipeRefinerPrompt()

    def process(self, payload: Payload, opt: dict = {}) -> Payload:
        """
        페이로드 데이터를 Gemini 모델을 통해 레시피로 정제합니다.
        
        Args:
            payload (Payload): 처리할 페이로드 데이터
            opt (dict, optional): 처리 옵션 (기본값: {})
        
        Returns:
            Payload: 정제된 레시피가 포함된 페이로드
            
        Raises:
            ValueError: 지원하지 않는 데이터 타입인 경우
            RuntimeError: Gemini 클라이언트 초기화 또는 API 호출 실패
        """
        try:
            # 입력 검증
            if not self.is_supported(payload):
                raise ValueError(f"지원하지 않는 데이터 타입입니다: {payload.data_type}")

            # Gemini 클라이언트 초기화
            client = self._get_gemini_client()
            
            # 데이터 타입에 따른 처리
            if payload.data_type == DataType.VIDEO:
                refined_content = self._process_video_data(client, payload)
            elif payload.data_type == DataType.AUDIO:
                refined_content = self._process_audio_data(client, payload)
            elif payload.data_type == DataType.TEXT:
                refined_content = self._process_text_data(client, payload)
            else:
                raise ValueError(f"처리할 수 없는 데이터 타입입니다: {payload.data_type}")

            # 결과 페이로드 생성
            result_payload = Payload(
                buffer=refined_content.encode('utf-8'),
                metadata={
                    **payload.metadata
                },
                data_type=DataType.TEXT,
                status=PayloadStatus.COMPLETED,
                processor=self.__class__
            )

            self._logger.info(f"레시피 정제 완료: {payload.data_type.name} → TEXT")
            return result_payload

        except Exception as e:
            self._logger.error(f"레시피 정제 중 오류 발생: {str(e)}")
            # 오류 상태의 페이로드 반환
            error_payload = Payload(
                buffer=f"레시피 정제 실패: {str(e)}".encode('utf-8'),
                metadata={
                    **payload.metadata,
                    'error': str(e),
                    'failed_processor': self.__class__.__name__
                },
                data_type=payload.data_type,
                status=PayloadStatus.ERROR,
                processor=self.__class__
            )
            return error_payload

    def is_supported(self, payload: Payload) -> bool:
        """
        페이로드가 이 정제기에서 지원되는지 확인합니다.
        
        Args:
            payload (Payload): 확인할 페이로드
            
        Returns:
            bool: 지원 여부 (VIDEO, AUDIO, TEXT 타입 지원)
        """
        supported_types = {DataType.VIDEO, DataType.AUDIO, DataType.TEXT}
        return payload.data_type in supported_types

    def _get_gemini_client(self) -> GeminiClient:
        """
        Gemini 클라이언트 인스턴스를 가져옵니다. (Singleton 패턴)
        
        Returns:
            GeminiClient: Gemini 클라이언트 인스턴스
            
        Raises:
            RuntimeError: 클라이언트 초기화 실패
        """
        try:
            if self._client is None:
                self._client = GeminiClient()
            return self._client
        except Exception as e:
            raise RuntimeError(f"Gemini 클라이언트 초기화 실패: {str(e)}")

    def _process_video_data(self, client: GeminiClient, payload: Payload) -> str:
        """
        비디오 데이터를 Gemini 모델을 통해 레시피로 정제합니다.
        
        Args:
            client (GeminiClient): Gemini 클라이언트
            payload (Payload): 비디오 데이터가 포함된 페이로드
            
        Returns:
            str: 정제된 레시피 텍스트
        """
        try:
            # 비디오 데이터를 base64로 인코딩
            video_b64 = base64.b64encode(payload.buffer).decode('utf-8')
            
            # 프롬프트 생성
            base_prompt = self._prompt_generator.get_video_recipe_prompt()
            context_prompt = self._prompt_generator.get_content_context_prompt(payload.metadata)
            full_prompt = context_prompt + base_prompt + self._prompt_generator.get_recipe_prompt_format()
            
            # Gemini API 호출
            response = self._call_gemini_with_video(client, video_b64, full_prompt)
            
            return self._extract_recipe_content(response)
            
        except Exception as e:
            self._logger.error(f"비디오 데이터 처리 중 오류: {str(e)}")
            raise RuntimeError(f"비디오 레시피 정제 실패: {str(e)}")

    def _process_audio_data(self, client: GeminiClient, payload: Payload) -> str:
        """
        오디오 데이터를 Gemini 모델을 통해 레시피로 정제합니다.
        
        Args:
            client (GeminiClient): Gemini 클라이언트
            payload (Payload): 오디오 데이터가 포함된 페이로드
            
        Returns:
            str: 정제된 레시피 텍스트
        """
        try:
            # 오디오 데이터를 base64로 인코딩
            audio_b64 = base64.b64encode(payload.buffer).decode('utf-8')
            
            # 프롬프트 생성
            base_prompt = self._prompt_generator.get_audio_recipe_prompt()
            context_prompt = self._prompt_generator.get_content_context_prompt(payload.metadata)
            full_prompt = context_prompt + base_prompt + self._prompt_generator.get_recipe_prompt_format()
            
            # Gemini API 호출
            response = self._call_gemini_with_audio(client, audio_b64, full_prompt)
            
            return self._extract_recipe_content(response)
            
        except Exception as e:
            self._logger.error(f"오디오 데이터 처리 중 오류: {str(e)}")
            raise RuntimeError(f"오디오 레시피 정제 실패: {str(e)}")

    def _process_text_data(self, client: GeminiClient, payload: Payload) -> str:
        """
        텍스트 데이터를 Gemini 모델을 통해 구조화된 레시피로 정제합니다.
        
        Args:
            client (GeminiClient): Gemini 클라이언트
            payload (Payload): 텍스트 데이터가 포함된 페이로드
            
        Returns:
            str: 정제된 레시피 텍스트
        """
        try:
            # 텍스트 데이터 추출
            text_content = payload.buffer.decode('utf-8')
            
            # 프롬프트 생성
            base_prompt = self._prompt_generator.get_text_recipe_prompt()
            context_prompt = self._prompt_generator.get_content_context_prompt(payload.metadata)
            full_prompt = context_prompt + base_prompt + f"\n\n**입력 텍스트:**\n{text_content}" + self._prompt_generator.get_recipe_prompt_format()
            
            # Gemini API 호출
            response = self._call_gemini_with_text(client, full_prompt)
            
            return self._extract_recipe_content(response)
            
        except Exception as e:
            self._logger.error(f"텍스트 데이터 처리 중 오류: {str(e)}")
            raise RuntimeError(f"텍스트 레시피 정제 실패: {str(e)}")

    def _call_gemini_with_video(self, client: GeminiClient, video_b64: str, prompt: str) -> str:
        """
        Gemini API를 통해 비디오와 함께 프롬프트를 전송합니다.
        
        Args:
            client (GeminiClient): Gemini 클라이언트
            video_b64 (str): Base64 인코딩된 비디오 데이터
            prompt (str): 프롬프트 텍스트
            
        Returns:
            str: API 응답 텍스트
        """
        try:
            # Gemini에 비디오와 텍스트 프롬프트 전송
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    {
                        'parts': [
                            {'text': prompt},
                            {
                                'inline_data': {
                                    'mime_type': 'video/mp4',
                                    'data': video_b64
                                }
                            }
                        ]
                    }
                ]
            )
            if response.text is None:
                raise RuntimeError("Gemini에서 빈 응답을 받았습니다")
            return response.text
        except Exception as e:
            raise RuntimeError(f"Gemini 비디오 API 호출 실패: {str(e)}")

    def _call_gemini_with_audio(self, client: GeminiClient, audio_b64: str, prompt: str) -> str:
        """
        Gemini API를 통해 오디오와 함께 프롬프트를 전송합니다.
        
        Args:
            client (GeminiClient): Gemini 클라이언트
            audio_b64 (str): Base64 인코딩된 오디오 데이터
            prompt (str): 프롬프트 텍스트
            
        Returns:
            str: API 응답 텍스트
        """
        try:
            # Gemini에 오디오와 텍스트 프롬프트 전송
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    {
                        'parts': [
                            {'text': prompt},
                            {
                                'inline_data': {
                                    'mime_type': 'audio/wav',
                                    'data': audio_b64
                                }
                            }
                        ]
                    }
                ]
            )
            if response.text is None:
                raise RuntimeError("Gemini에서 빈 응답을 받았습니다")
            return response.text
        except Exception as e:
            raise RuntimeError(f"Gemini 오디오 API 호출 실패: {str(e)}")

    def _call_gemini_with_text(self, client: GeminiClient, prompt: str) -> str:
        """
        Gemini API를 통해 텍스트 프롬프트를 전송합니다.
        
        Args:
            client (GeminiClient): Gemini 클라이언트
            prompt (str): 프롬프트 텍스트
            
        Returns:
            str: API 응답 텍스트
        """
        try:
            # Gemini에 텍스트 프롬프트 전송
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[{'parts': [{'text': prompt}]}]
            )
            if response.text is None:
                raise RuntimeError("Gemini에서 빈 응답을 받았습니다")
            return response.text
        except Exception as e:
            raise RuntimeError(f"Gemini 텍스트 API 호출 실패: {str(e)}")

    def _extract_recipe_content(self, response: str) -> str:
        """
        Gemini 응답에서 레시피 내용을 추출하고 후처리합니다.
        
        Args:
            response (str): Gemini API 응답
            
        Returns:
            str: 정제된 레시피 JSON 텍스트
        """
        try:
            # 응답이 비어있는 경우 처리
            if not response or not response.strip():
                return self._create_error_json("응답을 받을 수 없었습니다.")
            
            # JSON 블록 추출 (```json...``` 형태)
            json_content = self._extract_json_from_response(response)
            
            if json_content:
                # JSON 유효성 검증
                validated_json = self._validate_and_format_json(json_content)
                return validated_json
            else:
                # JSON 형태가 아닌 경우 기본 구조로 변환
                return self._convert_text_to_json(response)
            
        except Exception as e:
            self._logger.error(f"응답 추출 중 오류: {str(e)}")
            return self._create_error_json(f"오류가 발생했습니다: {str(e)}")

    def _extract_json_from_response(self, response: str) -> str:
        """
        응답에서 JSON 코드 블록을 추출합니다.
        
        Args:
            response (str): 원본 응답
            
        Returns:
            str: 추출된 JSON 문자열 (없으면 빈 문자열)
        """
        import re
        
        # ```json...``` 패턴 찾기
        json_pattern = r'```json\s*(.*?)\s*```'
        match = re.search(json_pattern, response, re.DOTALL | re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        
        # { ... } 패턴으로 JSON 찾기 (백틱 없는 경우)
        json_pattern = r'(\{.*\})'
        match = re.search(json_pattern, response, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        
        return ""

    def _validate_and_format_json(self, json_content: str) -> str:
        """
        JSON 내용을 검증하고 포맷팅합니다.
        
        Args:
            json_content (str): JSON 문자열
            
        Returns:
            str: 검증 및 포맷팅된 JSON 문자열
        """
        try:
            # JSON 파싱 시도
            parsed_json = json.loads(json_content)
            
            # 필수 필드 검증
            required_fields = ['title', 'ingredients', 'steps', 'estimated_time', 'difficulty', 'servings']
            for field in required_fields:
                if field not in parsed_json:
                    self._logger.warning(f"필수 필드 누락: {field}")
                    parsed_json[field] = self._get_default_value(field)
            
            # JSON 포맷팅하여 반환
            return json.dumps(parsed_json, ensure_ascii=False, indent=2)
            
        except json.JSONDecodeError as e:
            self._logger.error(f"JSON 파싱 오류: {str(e)}")
            return self._create_error_json(f"JSON 형식이 올바르지 않습니다: {str(e)}")

    def _convert_text_to_json(self, text: str) -> str:
        """
        일반 텍스트를 기본 JSON 구조로 변환합니다.
        
        Args:
            text (str): 일반 텍스트 응답
            
        Returns:
            str: JSON 형태로 변환된 텍스트
        """
        try:
            # 기본 JSON 구조 생성
            recipe_json = {
                "title": "추출된 레시피",
                "ingredients": [
                    {
                        "index": 1,
                        "name": "정보 부족",
                        "amount": "적당량"
                    }
                ],
                "steps": [
                    {
                        "step": 1,
                        "start_time": "00:00:00",
                        "end_time": "00:00:00",
                        "description": text.strip()[:500] + ("..." if len(text.strip()) > 500 else "")
                    }
                ],
                "estimated_time": "정보 없음",
                "difficulty": "정보 없음",
                "servings": "정보 없음"
            }
            
            return json.dumps(recipe_json, ensure_ascii=False, indent=2)
            
        except Exception as e:
            self._logger.error(f"텍스트 변환 중 오류: {str(e)}")
            return self._create_error_json("텍스트 변환 실패")

    def _create_error_json(self, error_message: str) -> str:
        """
        오류 정보를 포함한 기본 JSON을 생성합니다.
        
        Args:
            error_message (str): 오류 메시지
            
        Returns:
            str: 오류 정보가 포함된 JSON 문자열
        """
        error_json = {
            "title": "레시피 정제 실패",
            "ingredients": [
                {
                    "index": 1,
                    "name": "오류 발생",
                    "amount": "정보 없음"
                }
            ],
            "steps": [
                {
                    "step": 1,
                    "start_time": "00:00:00",
                    "end_time": "00:00:00",
                    "description": f"레시피 정제 중 오류가 발생했습니다: {error_message}"
                }
            ],
            "estimated_time": "정보 없음",
            "difficulty": "정보 없음",
            "servings": "정보 없음"
        }
        
        return json.dumps(error_json, ensure_ascii=False, indent=2)

    def _get_default_value(self, field: str) -> Any:
        """
        누락된 필드에 대한 기본값을 반환합니다.
        
        Args:
            field (str): 필드명
            
        Returns:
            Any: 해당 필드의 기본값
        """
        defaults = {
            "title": "정보 없음",
            "ingredients": [{"index": 1, "name": "정보 부족", "amount": "적당량"}],
            "steps": [{"step": 1, "start_time": "00:00:00", "end_time": "00:00:00", "description": "정보 부족"}],
            "estimated_time": "정보 없음",
            "difficulty": "정보 없음",
            "servings": "정보 없음"
        }
        
        return defaults.get(field, "정보 없음")

    