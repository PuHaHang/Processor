"""
GeminiRefiner 테스트 모듈

이 모듈은 GeminiRefiner 클래스의 기능을 검증하는 단위 테스트를 제공합니다.
실제 Gemini API 호출 대신 Mock을 사용하여 기능을 테스트합니다.
"""

import os
import pytest
import sys
from unittest.mock import Mock, patch, MagicMock

from src.common.exception import ValidationException, ProcessingException

# 테스트용 환경변수 설정
os.environ['GEMINI_API_KEY'] = 'test-gemini-key'

# API 관련 모듈들을 mock으로 처리
sys.modules['google.generativeai'] = Mock()

# Mock 객체들 설정
mock_gemini_client = Mock()
mock_prompt_generator = Mock()

# Gemini 관련 의존성들을 mock으로 처리
with patch.multiple(
    'src.common.processor.refiner.strategies.gemini_refiner',
    GeminiClient=Mock(return_value=mock_gemini_client),
    RecipeRefinerPrompt=Mock(return_value=mock_prompt_generator)
):
    from src.common.processor.refiner.strategies.gemini_refiner import GeminiRefiner
    from src.common.processor.types import DataType, Payload, PayloadStatus


class TestGeminiRefiner:
    """
    GeminiRefiner 클래스에 대한 테스트 모음
    
    Gemini 기반 리파이너의 지원 여부 확인, 정제 수행 등의
    모든 기능을 테스트합니다.
    """
    
    @pytest.fixture
    def gemini_refiner(self):
        """
        테스트용 GeminiRefiner 인스턴스를 제공하는 fixture
        
        Returns:
            GeminiRefiner: 테스트용 Gemini 리파이너 인스턴스
        """
        return GeminiRefiner()
    
    
    @pytest.fixture
    def mock_text_payload(self):
        """
        텍스트 타입 Payload를 제공하는 fixture
        
        Returns:
            Payload: 테스트용 텍스트 페이로드
        """
        return Payload(
            buffer="김치찌개 만드는 방법을 설명하겠습니다. 먼저 김치를 준비하고...".encode('utf-8'),
            metadata={
                "title": "김치찌개 레시피",
                "description": "전통 김치찌개 만드는 법"
            },
            data_type=DataType.TEXT,
            status=PayloadStatus.COMPLETED,
            processor=None
        )
    
    
    @pytest.fixture
    def mock_video_payload(self):
        """
        비디오 타입 Payload를 제공하는 fixture
        
        Returns:
            Payload: 테스트용 비디오 페이로드
        """
        return Payload(
            buffer=b"fake_video_binary_data",
            metadata={
                "title": "요리 비디오",
                "duration": 300,
                "format": "mp4"
            },
            data_type=DataType.VIDEO,
            status=PayloadStatus.COMPLETED,
            processor=None
        )
    
    
    @pytest.fixture
    def mock_audio_payload(self):
        """
        오디오 타입 Payload를 제공하는 fixture
        
        Returns:
            Payload: 테스트용 오디오 페이로드
        """
        return Payload(
            buffer=b"fake_audio_binary_data",
            metadata={
                "title": "요리 오디오",
                "duration": 180,
                "format": "wav"
            },
            data_type=DataType.AUDIO,
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
            buffer="https://example.com/recipe".encode('utf-8'),
            metadata={},
            data_type=DataType.URL,
            status=PayloadStatus.COMPLETED,
            processor=None
        )
    
    
    @pytest.mark.unit
    def test_gemini_refiner_initialization(self, gemini_refiner):
        """
        GeminiRefiner 초기화 테스트
        
        Args:
            gemini_refiner: GeminiRefiner 인스턴스
        """
        assert isinstance(gemini_refiner, GeminiRefiner)
        assert hasattr(gemini_refiner, 'data_flow')
        assert hasattr(gemini_refiner, 'available_input_ext')
        assert hasattr(gemini_refiner, 'available_output_ext')
        assert hasattr(gemini_refiner, 'default_output_ext')
    
    
    @pytest.mark.unit
    def test_is_supported_with_text_payload(self, gemini_refiner, mock_text_payload):
        """
        텍스트 페이로드에 대한 지원 여부 테스트
        
        Args:
            gemini_refiner: GeminiRefiner 인스턴스
            mock_text_payload: 텍스트 페이로드
        """
        result = gemini_refiner.is_supported(mock_text_payload)
        assert result == True
    
    
    @pytest.mark.unit
    def test_is_supported_with_video_payload(self, gemini_refiner, mock_video_payload):
        """
        비디오 페이로드에 대한 지원 여부 테스트
        
        Args:
            gemini_refiner: GeminiRefiner 인스턴스
            mock_video_payload: 비디오 페이로드
        """
        result = gemini_refiner.is_supported(mock_video_payload)
        assert result == True
    
    
    @pytest.mark.unit
    def test_is_supported_with_audio_payload(self, gemini_refiner, mock_audio_payload):
        """
        오디오 페이로드에 대한 지원 여부 테스트
        
        Args:
            gemini_refiner: GeminiRefiner 인스턴스
            mock_audio_payload: 오디오 페이로드
        """
        result = gemini_refiner.is_supported(mock_audio_payload)
        assert result == True
    
    
    @pytest.mark.unit
    def test_is_supported_with_unsupported_payload(self, gemini_refiner, mock_unsupported_payload):
        """
        지원되지 않는 페이로드에 대한 지원 여부 테스트
        
        Args:
            gemini_refiner: GeminiRefiner 인스턴스
            mock_unsupported_payload: 지원되지 않는 페이로드
        """
        result = gemini_refiner.is_supported(mock_unsupported_payload)
        assert result == False
    
    
    @pytest.mark.unit
    @patch('src.common.processor.refiner.strategies.gemini_refiner.GeminiRefiner._process_text_data')
    @patch('src.common.processor.refiner.strategies.gemini_refiner.GeminiRefiner._get_gemini_client')
    def test_process_text_payload_success(self, mock_get_client, mock_process_text, gemini_refiner, mock_text_payload):
        """
        텍스트 페이로드 정제 성공 테스트
        
        Args:
            mock_get_client: Gemini 클라이언트 Mock
            mock_process_text: 텍스트 처리 메소드 Mock
            gemini_refiner: GeminiRefiner 인스턴스
            mock_text_payload: 텍스트 페이로드
        """
        # Mock 설정
        mock_get_client.return_value = mock_gemini_client
        mock_process_text.return_value = '{"title": "정제된 김치찌개 레시피", "ingredients": [], "steps": []}'
        
        # 테스트 실행
        result = gemini_refiner.process(mock_text_payload)
        
        # 검증
        assert result.status == PayloadStatus.COMPLETED
        assert result.data_type == DataType.TEXT
        assert "정제된 김치찌개 레시피" in result.buffer.decode('utf-8')
        mock_get_client.assert_called_once()
        mock_process_text.assert_called_once()
    
    
    @pytest.mark.unit
    @patch('src.common.processor.refiner.strategies.gemini_refiner.GeminiRefiner._process_video_data')
    @patch('src.common.processor.refiner.strategies.gemini_refiner.GeminiRefiner._get_gemini_client')
    def test_process_video_payload_success(self, mock_get_client, mock_process_video, gemini_refiner, mock_video_payload):
        """
        비디오 페이로드 정제 성공 테스트
        
        Args:
            mock_get_client: Gemini 클라이언트 Mock
            mock_process_video: 비디오 처리 메소드 Mock
            gemini_refiner: GeminiRefiner 인스턴스
            mock_video_payload: 비디오 페이로드
        """
        # Mock 설정
        mock_get_client.return_value = mock_gemini_client
        mock_process_video.return_value = '{"title": "비디오에서 추출한 레시피", "ingredients": [], "steps": []}'
        
        # 테스트 실행
        result = gemini_refiner.process(mock_video_payload)
        
        # 검증
        assert result.status == PayloadStatus.COMPLETED
        assert result.data_type == DataType.TEXT
        assert "비디오에서 추출한 레시피" in result.buffer.decode('utf-8')
        mock_get_client.assert_called_once()
        mock_process_video.assert_called_once()
    
    
    @pytest.mark.unit
    @patch('src.common.processor.refiner.strategies.gemini_refiner.GeminiRefiner._process_audio_data')
    @patch('src.common.processor.refiner.strategies.gemini_refiner.GeminiRefiner._get_gemini_client')
    def test_process_audio_payload_success(self, mock_get_client, mock_process_audio, gemini_refiner, mock_audio_payload):
        """
        오디오 페이로드 정제 성공 테스트
        
        Args:
            mock_get_client: Gemini 클라이언트 Mock
            mock_process_audio: 오디오 처리 메소드 Mock
            gemini_refiner: GeminiRefiner 인스턴스
            mock_audio_payload: 오디오 페이로드
        """
        # Mock 설정
        mock_get_client.return_value = mock_gemini_client
        mock_process_audio.return_value = '{"title": "오디오에서 추출한 레시피", "ingredients": [], "steps": []}'
        
        # 테스트 실행
        result = gemini_refiner.process(mock_audio_payload)
        
        # 검증
        assert result.status == PayloadStatus.COMPLETED
        assert result.data_type == DataType.TEXT
        assert "오디오에서 추출한 레시피" in result.buffer.decode('utf-8')
        mock_get_client.assert_called_once()
        mock_process_audio.assert_called_once()
    
    
    @pytest.mark.unit
    def test_process_unsupported_payload_error(self, gemini_refiner, mock_unsupported_payload):
        """
        지원되지 않는 페이로드 정제 시 예외 테스트
        
        Args:
            gemini_refiner: GeminiRefiner 인스턴스
            mock_unsupported_payload: 지원되지 않는 페이로드
        """
        with pytest.raises(ValidationException) as exc_info:
            gemini_refiner.process(mock_unsupported_payload)
        
        assert "지원하지 않는 데이터 타입입니다" in str(exc_info.value)
    
    
    # @pytest.mark.unit
    # @patch('src.common.processor.refiner.strategies.gemini_refiner.GeminiRefiner._get_gemini_client')
    # def test_process_with_client_error(self, mock_get_client, gemini_refiner, mock_text_payload):
    #     """
    #     Gemini 클라이언트 오류 시 에러 페이로드 반환 테스트
        
    #     Args:
    #         mock_get_client: Gemini 클라이언트 Mock
    #         gemini_refiner: GeminiRefiner 인스턴스
    #         mock_text_payload: 텍스트 페이로드
    #     """
    #     # Mock 설정 - 클라이언트 초기화 실패
    #     mock_get_client.side_effect = RuntimeError("Gemini 클라이언트 초기화 실패")
        
    #     # 테스트 실행
    #     result = gemini_refiner.process(mock_text_payload)
        
    #     # 검증
    #     assert result.status == PayloadStatus.ERROR
    #     assert "error" in result.metadata
    #     assert "Gemini 클라이언트 초기화 실패" in result.metadata["error"]
    
    
    @pytest.mark.unit
    @patch('src.common.processor.refiner.strategies.gemini_refiner.GeminiRefiner._call_gemini_with_text')
    @patch('src.common.processor.refiner.strategies.gemini_refiner.GeminiRefiner._get_gemini_client')
    def test_extract_recipe_content_with_json_response(self, mock_get_client, mock_call_gemini, gemini_refiner, mock_text_payload):
        """
        JSON 형태 응답에서 레시피 내용 추출 테스트
        
        Args:
            mock_get_client: Gemini 클라이언트 Mock
            mock_call_gemini: Gemini API 호출 Mock
            gemini_refiner: GeminiRefiner 인스턴스
            mock_text_payload: 텍스트 페이로드
        """
        # Mock 설정
        mock_get_client.return_value = mock_gemini_client
        mock_call_gemini.return_value = '''
        ```json
        {
            "title": "김치찌개",
            "ingredients": [{"index": 1, "name": "김치", "amount": "1컵"}],
            "steps": [{"step": 1, "description": "김치를 볶는다"}],
            "estimated_time": "30분",
            "difficulty": "쉬움",
            "servings": "2인분"
        }
        ```
        '''
        
        # 테스트 실행
        result = gemini_refiner.process(mock_text_payload)
        
        # 검증
        assert result.status == PayloadStatus.COMPLETED
        response_data = result.buffer.decode('utf-8')
        assert "김치찌개" in response_data
        assert "김치" in response_data
        assert "30분" in response_data
    
    
    @pytest.mark.unit
    @patch('src.common.processor.refiner.strategies.gemini_refiner.GeminiRefiner._call_gemini_with_text')
    @patch('src.common.processor.refiner.strategies.gemini_refiner.GeminiRefiner._get_gemini_client')
    def test_extract_recipe_content_with_invalid_json(self, mock_get_client, mock_call_gemini, gemini_refiner, mock_text_payload):
        """
        잘못된 JSON 응답 처리 테스트
        
        Args:
            mock_get_client: Gemini 클라이언트 Mock
            mock_call_gemini: Gemini API 호출 Mock
            gemini_refiner: GeminiRefiner 인스턴스
            mock_text_payload: 텍스트 페이로드
        """
        # Mock 설정 - 잘못된 JSON 응답
        mock_get_client.return_value = mock_gemini_client
        mock_call_gemini.return_value = "이것은 일반 텍스트 응답입니다. JSON이 아닙니다."
        
        # 테스트 실행
        result = gemini_refiner.process(mock_text_payload)
        
        # 검증
        assert result.status == PayloadStatus.COMPLETED
        response_data = result.buffer.decode('utf-8')
        assert "추출된 레시피" in response_data  # 기본 구조로 변환됨
        assert "이것은 일반 텍스트 응답입니다" in response_data
    
    
    @pytest.mark.unit
    @patch('src.common.processor.refiner.strategies.gemini_refiner.GeminiRefiner._call_gemini_with_text')
    @patch('src.common.processor.refiner.strategies.gemini_refiner.GeminiRefiner._get_gemini_client')
    def test_extract_recipe_content_with_empty_response(self, mock_get_client, mock_call_gemini, gemini_refiner, mock_text_payload):
        """
        빈 응답 처리 테스트
        
        Args:
            mock_get_client: Gemini 클라이언트 Mock
            mock_call_gemini: Gemini API 호출 Mock
            gemini_refiner: GeminiRefiner 인스턴스
            mock_text_payload: 텍스트 페이로드
        """
        # Mock 설정 - 빈 응답
        mock_get_client.return_value = mock_gemini_client
        mock_call_gemini.return_value = ""
        
        # 테스트 실행
        result = gemini_refiner.process(mock_text_payload)
        
        # 검증
        assert result.status == PayloadStatus.COMPLETED
        response_data = result.buffer.decode('utf-8')
        assert "레시피 정제 실패" in response_data  # 에러 JSON이 생성됨
        assert "응답을 받을 수 없었습니다" in response_data 