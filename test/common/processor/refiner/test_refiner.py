"""
Refiner 메인 클래스 테스트 모듈

이 모듈은 Refiner 클래스의 핵심 기능을 검증하는 단위 테스트를 제공합니다.
전략 선택, 정제 수행 등의 기본적인 기능을 테스트합니다.
"""

import os
import pytest
import sys
from unittest.mock import Mock, patch

# 테스트용 환경변수 설정
os.environ['MODEL_PATH'] = 'test/resources/models'
os.environ['GEMINI_API_KEY'] = 'test-gemini-key'
os.environ['OPENAI_API_KEY'] = 'test-openai-key'

# 모델 및 API 관련 모듈들을 mock으로 처리
sys.modules['google.generativeai'] = Mock()
sys.modules['openai'] = Mock()
sys.modules['onnx'] = Mock()
sys.modules['onnxruntime'] = Mock()
sys.modules['transformers'] = Mock()

# Mock 객체들 설정
mock_gemini_client = Mock()
mock_openai_client = Mock()

# LLM 클라이언트들을 mock으로 처리
with patch.multiple(
    'src.common.processor.refiner.strategies.gemini_refiner',
    GeminiClient=Mock(return_value=mock_gemini_client)
), patch.multiple(
    'src.common.processor.refiner.strategies.openai_refiner',
    OpenAIClient=Mock(return_value=mock_openai_client)
):
    from src.common.processor.refiner import Refiner
    from src.common.processor.refiner.strategies import GeminiRefiner, OpenAIRefiner
    from src.common.processor.types import DataType, Payload, PayloadStatus


class TestRefiner:
    """
    Refiner 클래스에 대한 테스트 모음
    
    리파이너의 초기화, 전략 선택, 정제 수행 등의
    모든 기능을 테스트합니다.
    """
    
    @pytest.fixture
    def refiner(self):
        """
        테스트용 Refiner 인스턴스를 제공하는 fixture
        
        Returns:
            Refiner: 테스트용 리파이너 인스턴스
        """
        return Refiner()
    
    
    @pytest.fixture
    def mock_text_payload(self):
        """
        텍스트 타입 Payload를 제공하는 fixture
        
        Returns:
            Payload: 테스트용 텍스트 페이로드
        """
        return Payload(
            buffer="김치찌개 만드는 방법을 알려드립니다. 재료는 김치, 돼지고기, 두부가 필요합니다.".encode('utf-8'),
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
        비디오 타입 Payload를 제공하는 fixture (Gemini 지원)
        
        Returns:
            Payload: 테스트용 비디오 페이로드
        """
        return Payload(
            buffer=b"fake_video_data",
            metadata={
                "title": "요리 영상",
                "duration": 300
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
            buffer=b"binary_data",
            metadata={},
            data_type=DataType.AUDIO,  # 현재는 AUDIO를 지원하지 않음
            status=PayloadStatus.COMPLETED,
            processor=None
        )
    
    
    @pytest.mark.unit
    def test_refiner_initialization(self, refiner):
        """
        Refiner 초기화 테스트
        
        Args:
            refiner: Refiner 인스턴스
        """
        assert isinstance(refiner, Refiner)
        assert len(refiner.strategies) == 2
        assert any(isinstance(strategy, GeminiRefiner) for strategy in refiner.strategies)
        assert any(isinstance(strategy, OpenAIRefiner) for strategy in refiner.strategies)
        
        # Gemini가 첫 번째 전략인지 확인 (우선순위)
        assert isinstance(refiner.strategies[0], GeminiRefiner)
        assert isinstance(refiner.strategies[1], OpenAIRefiner)
    
    
    @pytest.mark.unit
    @patch('src.common.processor.refiner.strategies.gemini_refiner.GeminiRefiner.process')
    def test_process_with_gemini_supported_payload(self, mock_process, refiner, mock_video_payload):
        """
        Gemini가 지원하는 페이로드에 대한 정제 테스트
        
        Args:
            mock_process: GeminiRefiner.process Mock
            refiner: Refiner 인스턴스
            mock_video_payload: 비디오 페이로드
        """
        # Mock 설정
        refined_payload = Payload(
            buffer="정제된 레시피 내용".encode('utf-8'),
            metadata={
                **mock_video_payload.metadata,
                "refiner": "gemini",
                "refined": True
            },
            data_type=DataType.TEXT,
            status=PayloadStatus.COMPLETED,
            processor=mock_video_payload.processor
        )
        mock_process.return_value = refined_payload
        
        # 테스트 실행
        result = refiner.process(mock_video_payload)
        
        # 검증
        assert result.metadata["refiner"] == "gemini"
        assert result.metadata["refined"] == True
        mock_process.assert_called_once_with(mock_video_payload, {})
    
    
    @pytest.mark.unit
    @patch('src.common.processor.refiner.strategies.openai_refiner.OpenAIRefiner.process')
    @patch('src.common.processor.refiner.strategies.gemini_refiner.GeminiRefiner.is_supported')
    def test_process_with_openai_supported_payload(self, mock_gemini_supported, mock_process, refiner, mock_text_payload):
        """
        OpenAI가 지원하는 페이로드에 대한 정제 테스트 (Gemini 미지원 시)
        
        Args:
            mock_gemini_supported: GeminiRefiner.is_supported Mock
            mock_process: OpenAIRefiner.process Mock
            refiner: Refiner 인스턴스
            mock_text_payload: 텍스트 페이로드
        """
        # Mock 설정 - Gemini는 지원하지 않음
        mock_gemini_supported.return_value = False
        
        refined_payload = Payload(
            buffer="정제된 텍스트 내용".encode('utf-8'),
            metadata={
                **mock_text_payload.metadata,
                "refiner": "openai",
                "refined": True
            },
            data_type=DataType.TEXT,
            status=PayloadStatus.COMPLETED,
            processor=mock_text_payload.processor
        )
        mock_process.return_value = refined_payload
        
        # 테스트 실행
        result = refiner.process(mock_text_payload)
        
        # 검증
        assert result.metadata["refiner"] == "openai"
        assert result.metadata["refined"] == True
        mock_process.assert_called_once_with(mock_text_payload, {})
    
    
    # @pytest.mark.unit
    # def test_process_with_unsupported_payload(self, refiner, mock_unsupported_payload):
    #     """
    #     지원되지 않는 페이로드에 대한 정제 시 예외 테스트
        
    #     Args:
    #         refiner: Refiner 인스턴스
    #         mock_unsupported_payload: 지원되지 않는 페이로드
    #     """
    #     with pytest.raises(ValueError) as exc_info:
    #         refiner.process(mock_unsupported_payload)
        
    #     assert "No refiner strategy found for payload" in str(exc_info.value)
    
    
    @pytest.mark.unit
    @patch('src.common.processor.refiner.strategies.gemini_refiner.GeminiRefiner.is_supported')
    def test_is_supported_with_supported_payload(self, mock_is_supported, refiner, mock_text_payload):
        """
        지원되는 페이로드에 대한 지원 여부 테스트
        
        Args:
            mock_is_supported: GeminiRefiner.is_supported Mock
            refiner: Refiner 인스턴스
            mock_text_payload: 텍스트 페이로드
        """
        # Mock 설정
        mock_is_supported.return_value = True
        
        # 테스트 실행
        result = refiner.is_supported(mock_text_payload)
        
        # 검증
        assert result == True
    
    @pytest.mark.unit
    @patch('src.common.processor.refiner.strategies.gemini_refiner.GeminiRefiner.is_supported')
    def test_get_context_with_supported_payload(self, mock_is_supported, refiner, mock_text_payload):
        """
        지원되는 페이로드에 대한 전략 선택 테스트
        
        Args:
            mock_is_supported: GeminiRefiner.is_supported Mock
            refiner: Refiner 인스턴스
            mock_text_payload: 텍스트 페이로드
        """
        # Mock 설정
        mock_is_supported.return_value = True
        
        # 테스트 실행
        strategy = refiner._get_context(mock_text_payload)
        
        # 검증
        assert strategy is not None
        assert isinstance(strategy, GeminiRefiner)
    
    # @pytest.mark.unit
    # @patch('src.common.processor.refiner.strategies.openai_refiner.OpenAIRefiner.process')
    # def test_process_with_options(self, mock_process, refiner, mock_text_payload):
    #     """
    #     옵션과 함께 정제 처리 테스트
        
    #     Args:
    #         mock_process: OpenAIRefiner.process Mock
    #         refiner: Refiner 인스턴스
    #         mock_text_payload: 텍스트 페이로드
    #     """
    #     # Mock 설정
    #     refined_payload = Payload(
    #         buffer="정제된 내용".encode('utf-8'),
    #         metadata={
    #             **mock_text_payload.metadata,
    #             "refiner": "openai",
    #             "refined": True
    #         },
    #         data_type=DataType.TEXT,
    #         status=PayloadStatus.COMPLETED,
    #         processor=mock_text_payload.processor
    #     )
    #     mock_process.return_value = refined_payload
        
    #     # 테스트 옵션
    #     options = {
    #         "remove_extra_spaces": True,
    #         "fix_grammar": True,
    #         "model": "gpt-4"
    #     }
        
    #     # 테스트 실행
    #     result = refiner.process(mock_text_payload, options)
        
    #     # 검증
    #     mock_process.assert_called_once_with(mock_text_payload, options)
    #     assert result.metadata["refined"] == True 