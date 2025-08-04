"""
OpenAI 기반 레시피 정제 전략 모듈

이 모듈은 OpenAI GPT 모델을 사용하여 텍스트 데이터를
구조화된 레시피로 정제하는 전략을 구현합니다.
"""

import base64
import json
import logging
from typing import Tuple, Optional, Any

from ..refiner_strategy import RefinerStrategy
from ...types import DataType, Payload, PayloadStatus
from ....llm_client import OpenAIClient
from ....prompt.recipe_refiner_prompt import RecipeRefinerPrompt

# 예외 핸들러 import
from ....exception import (
    ExceptionHandler,
    RetryOnException,
    ValidationExceptionHandler,
    ExceptionType,
    ExceptionSeverity,
    ExternalServiceException,
    ValidationException,
    ProcessingException
)


class OpenAIRefiner(RefinerStrategy):
    """
    OpenAI GPT 모델을 사용한 레시피 정제 전략
    
    주로 텍스트 데이터를 입력받아 OpenAI GPT 모델을 통해
    구조화된 레시피 텍스트로 정제합니다.
    
    주의: OpenAI는 비디오/오디오 직접 처리가 제한적이므로
    텍스트 기반 처리에 최적화되어 있습니다.
    
    Attributes:
        data_flow (Tuple[DataType, DataType]): 입력(GENERIC) → 출력(TEXT) 데이터 플로우
        available_input_ext (list[str]): 지원하는 입력 파일 확장자 목록
        available_output_ext (list[str]): 지원하는 출력 파일 확장자 목록
        default_output_ext (str): 기본 출력 파일 확장자
    """
    
    data_flow: Tuple[DataType, DataType] = (DataType.TEXT, DataType.TEXT)
    available_input_ext: list[str] = ['.txt', '.md']
    available_output_ext: list[str] = ['.txt', '.md', '.json']
    default_output_ext: str = '.json'

    def __init__(self):
        """OpenAIRefiner 초기화"""
        self._logger = logging.getLogger(__name__)
        self._client: Optional[OpenAIClient] = None
        self._prompt_generator = RecipeRefinerPrompt()

    @ExceptionHandler(
        exception_type=ExceptionType.REFINING_ERROR,
        severity=ExceptionSeverity.HIGH,
        reraise=True,
        log_level="error",
        handler_name="openai_refiner_process_handler"
    )
    @RetryOnException(
        max_retries=3,
        retry_delay=2.0,
        backoff_factor=2.0,
        exception_types=[ConnectionError, TimeoutError],
        reraise_on_failure=True
    )
    @ValidationExceptionHandler(reraise=True)
    def process(self, payload: Payload, opt: dict = {}) -> Payload:
        """
        페이로드 데이터를 OpenAI 모델을 통해 레시피로 정제합니다.
        
        Args:
            payload (Payload): 처리할 페이로드 데이터
            opt (dict, optional): 처리 옵션 (기본값: {})
        
        Returns:
            Payload: 정제된 레시피가 포함된 페이로드
            
        Raises:
            ValueError: 지원하지 않는 데이터 타입인 경우
            RuntimeError: OpenAI 클라이언트 초기화 또는 API 호출 실패
        """

        # 입력 검증
        if not self.is_supported(payload):
            raise ValidationException(
                message=f"지원하지 않는 데이터 타입입니다: {payload.data_type.name}",
                field_name="data_type",
                field_value=payload.data_type.name,
                validation_rule="supported_data_type"
            )
        
        # OpenAI 클라이언트 초기화
        client = self._get_openai_client()
        
        # 데이터 타입에 따른 처리
        if payload.data_type == DataType.TEXT:
            refined_content = self._process_text_data(client, payload)
        else:
            raise ValidationException(
                message=f"처리할 수 없는 데이터 타입입니다: {payload.data_type.name}",
                field_name="data_type",
                field_value=payload.data_type.name,
                validation_rule="processable_data_type"
            )

        if not refined_content:
            raise ValidationException(
                message="레시피 정제 실패: 잘못된 JSON 형식입니다.",
                field_name="refined_content",
                field_value=None,
                validation_rule="recipe_refining_error"
            )

        # 결과 페이로드 생성
        result_payload = Payload(
            buffer=refined_content.encode('utf-8'),
            metadata={
                **payload.metadata
            },
            data_type=DataType.TEXT,
            status=PayloadStatus.COMPLETED,
            processor=self
        )

        self._logger.info(f"레시피 정제 완료: {payload.data_type.name} → TEXT")
        return result_payload

    @ValidationExceptionHandler(reraise=False, default_return=False)
    def is_supported(self, payload: Payload) -> bool:
        """
        페이로드가 이 정제기에서 지원되는지 확인합니다.
        
        Args:
            payload (Payload): 확인할 페이로드
            
        Returns:
            bool: 지원 여부 (주로 TEXT 타입)
        """
        return payload.data_type == self.data_flow[0]

    @ExceptionHandler(
        exception_type=ExceptionType.MODEL_LOADING_ERROR,
        severity=ExceptionSeverity.CRITICAL,
        reraise=True,
        log_level="error",
        handler_name="openai_client_init_handler"
    )
    def _get_openai_client(self) -> OpenAIClient:
        """
        OpenAI 클라이언트 인스턴스를 가져옵니다. (Singleton 패턴)
        
        Returns:
            OpenAIClient: OpenAI 클라이언트 인스턴스
            
        Raises:
            RuntimeError: 클라이언트 초기화 실패
        """
        if self._client is None:
            self._client = OpenAIClient()
        return self._client

    @ExceptionHandler(
        exception_type=ExceptionType.REFINING_ERROR,
        severity=ExceptionSeverity.HIGH,
        reraise=True,
        log_level="error",
        handler_name="openai_text_processing_handler"
    )
    def _process_text_data(self, client: OpenAIClient, payload: Payload) -> str:
        """
        텍스트 데이터를 OpenAI 모델을 통해 구조화된 레시피로 정제합니다.
        
        Args:
            client (OpenAIClient): OpenAI 클라이언트
            payload (Payload): 텍스트 데이터가 포함된 페이로드
            
        Returns:
            str: 정제된 레시피 텍스트
        """
        # 텍스트 데이터 추출
        text_content = payload.buffer.decode('utf-8')
        
        # 프롬프트 생성
        base_prompt = self._prompt_generator.get_text_recipe_prompt()
        context_prompt = self._prompt_generator.get_content_context_prompt(payload.metadata)
        format_prompt = self._prompt_generator.get_recipe_prompt_format()
        full_prompt = context_prompt + base_prompt + f"\n\n**입력 텍스트:**\n{text_content}" + format_prompt
        
        # OpenAI API 호출
        response = self._call_openai_with_text(client, full_prompt)
        
        return self._extract_recipe_content(response)

    @ExceptionHandler(
        exception_type=ExceptionType.EXTERNAL_SERVICE_ERROR,
        severity=ExceptionSeverity.HIGH,
        reraise=True,
        log_level="error",
        handler_name="openai_text_api_handler"
    )
    def _call_openai_with_text(self, client: OpenAIClient, prompt: str) -> str:
        """
        OpenAI API를 통해 텍스트 프롬프트를 전송합니다.
        
        Args:
            client (OpenAIClient): OpenAI 클라이언트
            prompt (str): 프롬프트 텍스트
            
        Returns:
            str: API 응답 텍스트
        """
        # OpenAI Chat Completions API 호출
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 요리 전문가입니다. 제공된 정보를 바탕으로 정확하고 구조화된 레시피를 JSON 형태로 작성해주세요."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=4000
        )
        
        content = response.choices[0].message.content
        if content is None:
            raise RuntimeError("OpenAI에서 빈 응답을 받았습니다")
        return content

    @ExceptionHandler(
        exception_type=ExceptionType.JSON_PARSING_ERROR,
        severity=ExceptionSeverity.MEDIUM,
        reraise=False,
        default_return=None,
        log_level="warning",
        handler_name="openai_recipe_content_extraction_handler"
    )
    def _extract_recipe_content(self, response: str) -> str:
        """
        OpenAI 응답에서 레시피 내용을 추출하고 후처리합니다.
        
        Args:
            response (str): OpenAI API 응답
            
        Returns:
            str: 정제된 레시피 JSON 텍스트
        """
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

    @ExceptionHandler(
        exception_type=ExceptionType.JSON_PARSING_ERROR,
        severity=ExceptionSeverity.MEDIUM,
        reraise=False,
        default_return=None,
        log_level="warning",
        handler_name="openai_json_validation_handler"
    )
    def _validate_and_format_json(self, json_content: str) -> str:
        """
        JSON 내용을 검증하고 포맷팅합니다.
        
        Args:
            json_content (str): JSON 문자열
            
        Returns:
            str: 검증 및 포맷팅된 JSON 문자열
        """
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

    @ExceptionHandler(
        exception_type=ExceptionType.JSON_PARSING_ERROR,
        severity=ExceptionSeverity.MEDIUM,
        reraise=False,
        default_return=None,
        log_level="warning",
        handler_name="openai_text_to_json_conversion_handler"
    )
    def _convert_text_to_json(self, text: str) -> str:
        """
        일반 텍스트를 기본 JSON 구조로 변환합니다.
        
        Args:
            text (str): 일반 텍스트 응답
            
        Returns:
            str: JSON 형태로 변환된 텍스트
        """
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
                    "start_time": "0.0",
                    "end_time": "0.0",
                    "description": text.strip()[:500] + ("..." if len(text.strip()) > 500 else "")
                }
            ],
            "estimated_time": "정보 없음",
            "difficulty": "정보 없음",
            "servings": "정보 없음"
        }
        
        return json.dumps(recipe_json, ensure_ascii=False, indent=2)

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
                    "start_time": "0.0",
                    "end_time": "0.0",
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
            "steps": [{"step": 1, "start_time": "0.0", "end_time": "0.0", "description": "정보 부족"}],
            "estimated_time": "정보 없음",
            "difficulty": "정보 없음",
            "servings": "정보 없음"
        }
        
        return defaults.get(field, "정보 없음") 