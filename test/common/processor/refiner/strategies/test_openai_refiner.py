"""
OpenAIRefiner 테스트 모듈

이 모듈은 OpenAIRefiner 클래스의 기능을 검증하는 단위 테스트를 제공합니다.
실제 OpenAI API 호출 대신 Mock을 사용하여 기능을 테스트합니다.
"""

import os
import pytest
import sys
from unittest.mock import Mock, patch, MagicMock

from src.common.exception import ValidationException, ProcessingException

# 테스트용 환경변수 설정
os.environ['OPENAI_API_KEY'] = 'test-openai-key'

# API 관련 모듈들을 mock으로 처리
sys.modules['openai'] = Mock()

# Mock 객체들 설정
mock_openai_client = Mock()
mock_prompt_generator = Mock()

# OpenAI 관련 의존성들을 mock으로 처리
with patch.multiple(
    'src.common.processor.refiner.strategies.openai_refiner',
    OpenAIClient=Mock(return_value=mock_openai_client),
    RecipeRefinerPrompt=Mock(return_value=mock_prompt_generator)
):
    from src.common.processor.refiner.strategies.openai_refiner import OpenAIRefiner
    from src.common.processor.types import DataType, Payload, PayloadStatus


class TestOpenAIRefiner:
    """
    OpenAIRefiner 클래스에 대한 테스트 모음
    
    OpenAI 기반 리파이너의 지원 여부 확인, 정제 수행 등의
    모든 기능을 테스트합니다.
    """
    
    @pytest.fixture
    def openai_refiner(self):
        """
        테스트용 OpenAIRefiner 인스턴스를 제공하는 fixture
        
        Returns:
            OpenAIRefiner: 테스트용 OpenAI 리파이너 인스턴스
        """
        return OpenAIRefiner()
    
    
    @pytest.fixture
    def mock_text_payload(self):
        """
        텍스트 타입 Payload를 제공하는 fixture
        
        Returns:
            Payload: 테스트용 텍스트 페이로드
        """
        return Payload(
            buffer="김치찌개 레시피를 소개합니다. 재료는 다음과 같습니다...".encode('utf-8'),
            metadata={
                "title": "김치찌개 만들기",
                "description": "맛있는 김치찌개 레시피",
                "source": "블로그"
            },
            data_type=DataType.TEXT,
            status=PayloadStatus.COMPLETED,
            processor=None
        )
    
    
    @pytest.fixture
    def mock_video_payload(self):
        """
        비디오 타입 Payload를 제공하는 fixture (OpenAI 미지원)
        
        Returns:
            Payload: 테스트용 비디오 페이로드
        """
        return Payload(
            buffer=b"fake_video_data",
            metadata={
                "title": "요리 영상",
                "duration": 240
            },
            data_type=DataType.VIDEO,
            status=PayloadStatus.COMPLETED,
            processor=None
        )
    
    
    @pytest.fixture
    def mock_unsupported_payload(self):
        """
        지원되지 않는 타입 Payload를 제공하는 fixture
        
        Returns:
            Payload: 테스트용 지원되지 않는 페이로드
        """
        return Payload(
            buffer=b"binary_audio_data",
            metadata={},
            data_type=DataType.AUDIO,
            status=PayloadStatus.COMPLETED,
            processor=None
        )
    
    
    @pytest.mark.unit
    def test_openai_refiner_initialization(self, openai_refiner):
        """
        OpenAIRefiner 초기화 테스트
        
        Args:
            openai_refiner: OpenAIRefiner 인스턴스
        """
        assert isinstance(openai_refiner, OpenAIRefiner)
        assert hasattr(openai_refiner, 'data_flow')
        assert hasattr(openai_refiner, 'available_input_ext')
        assert hasattr(openai_refiner, 'available_output_ext')
        assert hasattr(openai_refiner, 'default_output_ext')
        
        # OpenAI는 주로 텍스트 처리에 특화
        assert openai_refiner.data_flow == (DataType.TEXT, DataType.TEXT)
    
    
    @pytest.mark.unit
    def test_is_supported_with_text_payload(self, openai_refiner, mock_text_payload):
        """
        텍스트 페이로드에 대한 지원 여부 테스트
        
        Args:
            openai_refiner: OpenAIRefiner 인스턴스
            mock_text_payload: 텍스트 페이로드
        """
        result = openai_refiner.is_supported(mock_text_payload)
        assert result == True
    
    
    @pytest.mark.unit
    def test_is_supported_with_video_payload(self, openai_refiner, mock_video_payload):
        """
        비디오 페이로드에 대한 지원 여부 테스트 (OpenAI는 비디오 미지원)
        
        Args:
            openai_refiner: OpenAIRefiner 인스턴스
            mock_video_payload: 비디오 페이로드
        """
        result = openai_refiner.is_supported(mock_video_payload)
        assert result == False
    
    
    @pytest.mark.unit
    def test_is_supported_with_unsupported_payload(self, openai_refiner, mock_unsupported_payload):
        """
        지원되지 않는 페이로드에 대한 지원 여부 테스트
        
        Args:
            openai_refiner: OpenAIRefiner 인스턴스
            mock_unsupported_payload: 지원되지 않는 페이로드
        """
        result = openai_refiner.is_supported(mock_unsupported_payload)
        assert result == False
    
    
    @pytest.mark.unit
    @patch('src.common.processor.refiner.strategies.openai_refiner.OpenAIRefiner._process_text_data')
    @patch('src.common.processor.refiner.strategies.openai_refiner.OpenAIRefiner._get_openai_client')
    def test_process_text_payload_success(self, mock_get_client, mock_process_text, openai_refiner, mock_text_payload):
        """
        텍스트 페이로드 정제 성공 테스트
        
        Args:
            mock_get_client: OpenAI 클라이언트 Mock
            mock_process_text: 텍스트 처리 메소드 Mock
            openai_refiner: OpenAIRefiner 인스턴스
            mock_text_payload: 텍스트 페이로드
        """
        # Mock 설정
        mock_get_client.return_value = mock_openai_client
        mock_process_text.return_value = '''
        {
            "title": "정제된 김치찌개 레시피",
            "ingredients": [
                {"index": 1, "name": "김치", "amount": "2컵"},
                {"index": 2, "name": "돼지고기", "amount": "200g"}
            ],
            "steps": [
                {"step": 1, "start_time": "0.0", "end_time": "5.0", "description": "재료를 준비합니다"}
            ],
            "estimated_time": "30분",
            "difficulty": "쉬움",
            "servings": "2인분"
        }
        '''
        
        # 테스트 실행
        result = openai_refiner.process(mock_text_payload)
        
        # 검증
        assert result.status == PayloadStatus.COMPLETED
        assert result.data_type == DataType.TEXT
        assert "정제된 김치찌개 레시피" in result.buffer.decode('utf-8')
        mock_get_client.assert_called_once()
        mock_process_text.assert_called_once()
    
    
    @pytest.mark.unit
    def test_process_unsupported_payload_error(self, openai_refiner, mock_video_payload):
        """
        지원되지 않는 페이로드 정제 시 예외 테스트
        
        Args:
            openai_refiner: OpenAIRefiner 인스턴스
            mock_video_payload: 지원되지 않는 비디오 페이로드
        """
        with pytest.raises(ValidationException) as exc_info:
            openai_refiner.process(mock_video_payload)
        
        assert "지원하지 않는 데이터 타입입니다" in str(exc_info.value)
    
    
    @pytest.mark.unit
    @patch('src.common.processor.refiner.strategies.openai_refiner.OpenAIRefiner._get_openai_client')
    def test_process_with_client_error(self, mock_get_client, openai_refiner, mock_text_payload):
        """
        OpenAI 클라이언트 오류 시 에러 페이로드 반환 테스트
        
        Args:
            mock_get_client: OpenAI 클라이언트 Mock
            openai_refiner: OpenAIRefiner 인스턴스
            mock_text_payload: 텍스트 페이로드
        """
        # Mock 설정 - 클라이언트 초기화 실패
        mock_get_client.side_effect = ValidationException(
            message="OpenAI 클라이언트 초기화 실패",
            field_name="client",
            field_value=None,
            validation_rule="openai_client_init_error"
        )
        
        # 테스트 실행
        with pytest.raises(ValidationException) as exc_info:
            openai_refiner.process(mock_text_payload)
        
        assert "OpenAI 클라이언트 초기화 실패" in str(exc_info.value)
    
    
    @pytest.mark.unit
    @patch('src.common.processor.refiner.strategies.openai_refiner.OpenAIRefiner._call_openai_with_text')
    @patch('src.common.processor.refiner.strategies.openai_refiner.OpenAIRefiner._get_openai_client')
    def test_extract_recipe_content_with_json_response(self, mock_get_client, mock_call_openai, openai_refiner, mock_text_payload):
        """
        JSON 형태 응답에서 레시피 내용 추출 테스트
        
        Args:
            mock_get_client: OpenAI 클라이언트 Mock
            mock_call_openai: OpenAI API 호출 Mock
            openai_refiner: OpenAIRefiner 인스턴스
            mock_text_payload: 텍스트 페이로드
        """
        # Mock 설정
        mock_get_client.return_value = mock_openai_client
        mock_call_openai.return_value = '''
        ```json
        {
            "title": "김치찌개",
            "ingredients": [
                {"index": 1, "name": "김치", "amount": "2컵"},
                {"index": 2, "name": "물", "amount": "3컵"}
            ],
            "steps": [
                {"step": 1, "start_time": "0.0", "end_time": "2.0", "description": "김치를 볶습니다"}
            ],
            "estimated_time": "20분",
            "difficulty": "보통",
            "servings": "3인분"
        }
        ```
        '''
        
        # 테스트 실행
        result = openai_refiner.process(mock_text_payload)
        
        # 검증
        assert result.status == PayloadStatus.COMPLETED
        response_data = result.buffer.decode('utf-8')
        assert "김치찌개" in response_data
        assert "김치" in response_data
        assert "20분" in response_data
        assert "보통" in response_data
    
    
    @pytest.mark.unit
    @patch('src.common.processor.refiner.strategies.openai_refiner.OpenAIRefiner._call_openai_with_text')
    @patch('src.common.processor.refiner.strategies.openai_refiner.OpenAIRefiner._get_openai_client')
    def test_extract_recipe_content_with_invalid_json(self, mock_get_client, mock_call_openai, openai_refiner, mock_text_payload):
        """
        잘못된 JSON 응답 처리 테스트
        
        Args:
            mock_get_client: OpenAI 클라이언트 Mock
            mock_call_openai: OpenAI API 호출 Mock
            openai_refiner: OpenAIRefiner 인스턴스
            mock_text_payload: 텍스트 페이로드
        """
        # Mock 설정 - 잘못된 JSON 응답
        mock_get_client.return_value = mock_openai_client
        mock_call_openai.return_value = "김치찌개는 한국의 대표적인 음식입니다. JSON 형태가 아닌 텍스트입니다."
        
        # 테스트 실행
        result = openai_refiner.process(mock_text_payload)
        
        # 검증
        assert result.status == PayloadStatus.COMPLETED
        response_data = result.buffer.decode('utf-8')
        assert "추출된 레시피" in response_data  # 기본 구조로 변환됨
        assert "김치찌개는 한국의 대표적인 음식입니다" in response_data
    
    
    @pytest.mark.unit
    @patch('src.common.processor.refiner.strategies.openai_refiner.OpenAIRefiner._call_openai_with_text')
    @patch('src.common.processor.refiner.strategies.openai_refiner.OpenAIRefiner._get_openai_client')
    def test_extract_recipe_content_with_empty_response(self, mock_get_client, mock_call_openai, openai_refiner, mock_text_payload):
        """
        빈 응답 처리 테스트
        
        Args:
            mock_get_client: OpenAI 클라이언트 Mock
            mock_call_openai: OpenAI API 호출 Mock
            openai_refiner: OpenAIRefiner 인스턴스
            mock_text_payload: 텍스트 페이로드
        """
        # Mock 설정 - 빈 응답
        mock_get_client.return_value = mock_openai_client
        mock_call_openai.return_value = ""
        
        # 테스트 실행
        result = openai_refiner.process(mock_text_payload)
        
        # 검증
        assert result.status == PayloadStatus.COMPLETED
        response_data = result.buffer.decode('utf-8')
        assert "레시피 정제 실패" in response_data  # 에러 JSON이 생성됨
        assert "응답을 받을 수 없었습니다" in response_data
    
    
    @pytest.mark.unit
    @patch('src.common.processor.refiner.strategies.openai_refiner.OpenAIRefiner._call_openai_with_text')
    @patch('src.common.processor.refiner.strategies.openai_refiner.OpenAIRefiner._get_openai_client')
    def test_process_with_api_call_failure(self, mock_get_client, mock_call_openai, openai_refiner, mock_text_payload):
        """
        OpenAI API 호출 실패 시 처리 테스트
        
        Args:
            mock_get_client: OpenAI 클라이언트 Mock
            mock_call_openai: OpenAI API 호출 Mock
            openai_refiner: OpenAIRefiner 인스턴스
            mock_text_payload: 텍스트 페이로드
        """
        # Mock 설정 - API 호출 실패
        mock_get_client.return_value = mock_openai_client
        mock_call_openai.side_effect = ValidationException(
            message="OpenAI API 호출 실패",
            field_name="api_call",
            field_value=None,
            validation_rule="openai_api_call_error"
        )
        
        # 테스트 실행
        with pytest.raises(ValidationException) as exc_info:
            openai_refiner.process(mock_text_payload)
        
        assert "OpenAI API 호출 실패" in str(exc_info.value)
    
    
    @pytest.mark.unit
    @patch('src.common.processor.refiner.strategies.openai_refiner.OpenAIRefiner._call_openai_with_text')
    @patch('src.common.processor.refiner.strategies.openai_refiner.OpenAIRefiner._get_openai_client')
    def test_validate_and_format_json_with_missing_fields(self, mock_get_client, mock_call_openai, openai_refiner, mock_text_payload):
        """
        필수 필드가 누락된 JSON 응답 처리 테스트
        
        Args:
            mock_get_client: OpenAI 클라이언트 Mock
            mock_call_openai: OpenAI API 호출 Mock
            openai_refiner: OpenAIRefiner 인스턴스
            mock_text_payload: 텍스트 페이로드
        """
        # Mock 설정 - 필수 필드 누락된 JSON
        mock_get_client.return_value = mock_openai_client
        mock_call_openai.return_value = '''
        ```json
        {
            "title": "김치찌개",
            "ingredients": [{"index": 1, "name": "김치", "amount": "2컵"}]
        }
        ```
        '''
        
        # 테스트 실행
        result = openai_refiner.process(mock_text_payload)
        
        # 검증
        assert result.status == PayloadStatus.COMPLETED
        response_data = result.buffer.decode('utf-8')
        
        # 누락된 필드들이 기본값으로 채워져야 함
        assert "김치찌개" in response_data
        assert "정보 없음" in response_data  # 기본값이 추가됨
    
    
    @pytest.mark.unit
    @patch('src.common.processor.refiner.strategies.openai_refiner.OpenAIRefiner._call_openai_with_text')
    @patch('src.common.processor.refiner.strategies.openai_refiner.OpenAIRefiner._get_openai_client')
    def test_process_with_malformed_json_raises_validation_exception(
        self, mock_get_client, mock_call_openai, openai_refiner, mock_text_payload
    ):
        """
        잘못된 JSON이 입력될 경우 ValidationException이 발생하는지 테스트합니다.

        Args:
            mock_get_client: OpenAI 클라이언트 Mock
            mock_call_openai: OpenAI API 호출 Mock
            openai_refiner: OpenAIRefiner 인스턴스
            mock_text_payload: 텍스트 페이로드
        """
        # Mock 설정 - 잘못된 JSON 반환
        mock_get_client.return_value = mock_openai_client
        mock_call_openai.return_value = '''
        ```json
        {
            "title": "김치찌개",
            "ingredients": [{"index": 1, "name": "김치", "amount": "2컵"},
            // 잘못된 JSON 형식 (쉼표 누락, 주석 포함)
        ```
        '''

        # 테스트 실행 및 예외 검증
        with pytest.raises(ValidationException) as exc_info:
            openai_refiner.process(mock_text_payload)

        # 예외 메시지 및 필드 검증
        assert "레시피 정제 실패" in str(exc_info.value)
        assert "잘못된 JSON 형식입니다." in str(exc_info.value)
    
    
    @pytest.mark.unit
    def test_data_flow_configuration(self, openai_refiner):
        """
        OpenAIRefiner의 데이터 플로우 설정 테스트
        
        Args:
            openai_refiner: OpenAIRefiner 인스턴스
        """
        # OpenAI는 텍스트 입력 → 텍스트 출력
        assert openai_refiner.data_flow[0] == DataType.TEXT
        assert openai_refiner.data_flow[1] == DataType.TEXT
        
        # 지원 확장자 확인
        assert '.txt' in openai_refiner.available_input_ext
        assert '.md' in openai_refiner.available_input_ext
        assert '.json' in openai_refiner.available_output_ext
        assert openai_refiner.default_output_ext == '.json' 