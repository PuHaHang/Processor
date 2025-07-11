"""
Evaluator 메인 클래스 테스트 모듈

이 모듈은 Evaluator 클래스의 핵심 기능을 검증하는 단위 테스트를 제공합니다.
전략 선택, 평가 수행 등의 기본적인 기능을 테스트합니다.
"""

import os
import pytest
import sys
from unittest.mock import Mock, patch

# 테스트용 환경변수 설정
os.environ['MODEL_PATH'] = 'test/resources/models'
os.environ['ZEROSHOT_MODEL_NAME'] = 'test-model'

# 모델 관련 모듈들을 mock으로 처리
sys.modules['onnx'] = Mock()
sys.modules['onnxruntime'] = Mock()
sys.modules['transformers'] = Mock()
sys.modules['yt_dlp'] = Mock()
sys.modules['yt_dlp.utils'] = Mock()

# Mock 객체들 설정
mock_yt_dlp = Mock()
mock_yt_dlp.utils.DownloadError = Exception
sys.modules['yt_dlp'].utils = mock_yt_dlp.utils

# 모델 파일 검증 함수들을 mock으로 처리
mock_validate_model = Mock()
mock_load_tokenizer = Mock(return_value=Mock())
mock_load_session = Mock(return_value=Mock())

# ZeroShotClassifier의 메소드들을 패치
with patch.multiple(
    'src.common.processor.evaluator._models.zero_shot_classifier.ZeroShotClassifier',
    _validate_model=mock_validate_model,
    _load_tokenizer=mock_load_tokenizer,
    _load_session=mock_load_session
):
    from src.common.processor.evaluator import Evaluator
    from src.common.processor.evaluator.strategies import YtDlpEvaluator
    from src.common.processor.types import DataType, Payload, PayloadStatus
    from src.common.processor.downloader.strategies.yt_dlp_downloader import YtDlpDownloader


class TestEvaluator:
    """
    Evaluator 클래스에 대한 테스트 모음
    
    평가기의 초기화, 전략 선택, 평가 수행 등의
    모든 기능을 테스트합니다.
    """
    
    @pytest.fixture
    def evaluator(self):
        """
        테스트용 Evaluator 인스턴스를 제공하는 fixture
        
        Returns:
            Evaluator: 테스트용 평가기 인스턴스
        """
        return Evaluator()
    
    
    @pytest.fixture
    def mock_payload_yt_dlp(self):
        """
        YtDlpDownloader로 처리된 Payload를 제공하는 fixture
        
        Returns:
            Payload: 테스트용 페이로드
        """
        return Payload(
            buffer=b"audio_data",
            metadata={
                "title": "요리 레시피 - 김치찌개 만들기",
                "description": "맛있는 김치찌개를 만드는 방법을 알려드립니다",
                "reference": {"platform": "youtube.com", "v": ["test123"]}
            },
            data_type=DataType.AUDIO,
            status=PayloadStatus.COMPLETED,
            processor=YtDlpDownloader
        )
    
    
    @pytest.fixture
    def mock_payload_unsupported(self):
        """
        지원되지 않는 프로세서로 처리된 Payload를 제공하는 fixture
        
        Returns:
            Payload: 테스트용 페이로드
        """
        return Payload(
            buffer=b"text_data",
            metadata={},
            data_type=DataType.TEXT,
            status=PayloadStatus.COMPLETED,
            processor=None
        )
    
    
    @pytest.mark.unit
    def test_evaluator_initialization(self, evaluator):
        """
        Evaluator 초기화 테스트
        
        Args:
            evaluator: Evaluator 인스턴스
        """
        assert isinstance(evaluator, Evaluator)
        assert len(evaluator.strategies) > 0
        assert any(isinstance(strategy, YtDlpEvaluator) for strategy in evaluator.strategies)
    
    
    @pytest.mark.unit
    @patch('src.common.processor.evaluator.strategies.yt_dlp_evaluator.YtDlpEvaluator.evaluate')
    def test_evaluate_supported_payload(self, mock_evaluate, evaluator, mock_payload_yt_dlp):
        """
        지원되는 페이로드에 대한 평가 테스트
        
        Args:
            mock_evaluate: YtDlpEvaluator.evaluate Mock
            evaluator: Evaluator 인스턴스
            mock_payload_yt_dlp: YtDlp로 처리된 페이로드
        """
        # Mock 설정
        mock_evaluate.return_value = True
        
        # 테스트 실행
        result = evaluator.evaluate(mock_payload_yt_dlp)
        
        # 검증
        assert result == True
        mock_evaluate.assert_called_once_with(mock_payload_yt_dlp)
    
    
    def test_evaluate_unsupported_payload(self, evaluator, mock_payload_unsupported):
        """
        지원되지 않는 페이로드에 대한 평가 테스트 (기본값 True 반환)
        
        Args:
            evaluator: Evaluator 인스턴스
            mock_payload_unsupported: 지원되지 않는 페이로드
        """
        result = evaluator.evaluate(mock_payload_unsupported)
        assert result == True
    
    
    def test_get_context_with_supported_payload(self, evaluator, mock_payload_yt_dlp):
        """
        지원되는 페이로드에 대한 전략 선택 테스트
        
        Args:
            evaluator: Evaluator 인스턴스
            mock_payload_yt_dlp: 지원되는 페이로드
        """
        strategy = evaluator._get_context(mock_payload_yt_dlp)
        assert strategy is not None
        assert isinstance(strategy, YtDlpEvaluator)
    
    
    def test_get_context_with_unsupported_payload(self, evaluator, mock_payload_unsupported):
        """
        지원되지 않는 페이로드에 대한 전략 선택 테스트
        
        Args:
            evaluator: Evaluator 인스턴스
            mock_payload_unsupported: 지원되지 않는 페이로드
        """
        strategy = evaluator._get_context(mock_payload_unsupported)
        assert strategy is None 