"""
YtDlpEvaluator 테스트 모듈

이 모듈은 YtDlpEvaluator 클래스의 기능을 검증하는 단위 테스트를 제공합니다.
YtDlpDownloader 결과를 평가하는 기능을 테스트합니다.
"""

import os
import pytest
import sys
from unittest.mock import Mock, patch

# 환경변수와 모듈 Mock 설정
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
    from src.common.processor.evaluator.strategies.yt_dlp_evaluator import YtDlpEvaluator
    from src.common.processor.types import DataType, Payload, PayloadStatus
    from src.common.processor.downloader.strategies.yt_dlp_downloader import YtDlpDownloader
    from src.common.exception import ValidationException


class TestYtDlpEvaluator:
    """
    YtDlpEvaluator 클래스에 대한 테스트 모음
    
    YouTube 다운로더 전용 평가기의 지원 여부 확인, 평가 수행 등의
    모든 기능을 테스트합니다.
    """
    
    @pytest.fixture
    def yt_dlp_evaluator(self):
        """
        테스트용 YtDlpEvaluator 인스턴스를 제공하는 fixture
        
        Returns:
            YtDlpEvaluator: 테스트용 평가기 인스턴스
        """
        return YtDlpEvaluator()
    
    
    @pytest.fixture
    def mock_payload_with_metadata(self):
        """
        메타데이터가 있는 Payload를 제공하는 fixture
        
        Returns:
            Payload: 메타데이터가 포함된 테스트용 페이로드
        """
        return Payload(
            buffer=b"audio_data",
            metadata={
                "title": "맛있는 파스타 만들기",
                "description": "집에서 쉽게 만들 수 있는 크림파스타 레시피",
                "duration": 300.5,
                "reference": {"platform": "youtube.com", "v": ["abc123"]}
            },
            data_type=DataType.AUDIO,
            status=PayloadStatus.COMPLETED,
            processor=YtDlpDownloader()
        )
    
    
    @pytest.fixture
    def mock_payload_without_metadata(self):
        """
        메타데이터가 없는 Payload를 제공하는 fixture
        
        Returns:
            Payload: 메타데이터가 없는 테스트용 페이로드
        """
        return Payload(
            buffer=b"audio_data",
            metadata={},
            data_type=DataType.AUDIO,
            status=PayloadStatus.COMPLETED,
            processor=YtDlpDownloader()
        )
    
    
    def test_yt_dlp_evaluator_initialization(self, yt_dlp_evaluator):
        """
        YtDlpEvaluator 초기화 테스트
        
        Args:
            yt_dlp_evaluator: YtDlpEvaluator 인스턴스
        """
        assert isinstance(yt_dlp_evaluator, YtDlpEvaluator)
        assert YtDlpDownloader in yt_dlp_evaluator.available_processors
        assert "title" in yt_dlp_evaluator.target_keys
        assert "description" in yt_dlp_evaluator.target_keys
    
    
    def test_is_supported_with_yt_dlp_processor(self, yt_dlp_evaluator, mock_payload_with_metadata):
        """
        YtDlpDownloader로 처리된 페이로드 지원 여부 테스트
        
        Args:
            yt_dlp_evaluator: YtDlpEvaluator 인스턴스
            mock_payload_with_metadata: YtDlp로 처리된 페이로드
        """
        assert yt_dlp_evaluator.is_supported(mock_payload_with_metadata) == True
    
    
    def test_is_supported_with_other_processor(self, yt_dlp_evaluator):
        """
        다른 프로세서로 처리된 페이로드 지원 여부 테스트
        
        Args:
            yt_dlp_evaluator: YtDlpEvaluator 인스턴스
        """
        payload = Payload(
            buffer=b"data",
            metadata={},
            data_type=DataType.TEXT,
            status=PayloadStatus.COMPLETED,
            processor=None  # 다른 프로세서
        )
        assert yt_dlp_evaluator.is_supported(payload) == False
    
    
    @patch('src.common.processor.evaluator.evaluator_strategy.EvaluatorStrategy._evaluate')
    def test_evaluate_with_metadata(self, mock_evaluate, yt_dlp_evaluator, mock_payload_with_metadata):
        """
        메타데이터가 있는 페이로드 평가 테스트
        
        Args:
            mock_evaluate: _evaluate 메소드 Mock
            yt_dlp_evaluator: YtDlpEvaluator 인스턴스
            mock_payload_with_metadata: 메타데이터가 있는 페이로드
        """
        # Mock 설정
        mock_evaluate.return_value = True
        
        # 테스트 실행
        result = yt_dlp_evaluator.evaluate(mock_payload_with_metadata)
        
        # 검증
        assert result == True
        mock_evaluate.assert_called_once()
        
        # 호출된 인자 확인
        call_args = mock_evaluate.call_args[0][0]
        assert "title" in call_args
        assert "description" in call_args
        assert call_args["title"] == "맛있는 파스타 만들기"
        assert call_args["description"] == "집에서 쉽게 만들 수 있는 크림파스타 레시피"
    
    
    def test_evaluate_without_metadata(self, yt_dlp_evaluator, mock_payload_without_metadata):
        """
        메타데이터가 없는 페이로드 평가 테스트
        
        Args:
            yt_dlp_evaluator: YtDlpEvaluator 인스턴스
            mock_payload_without_metadata: 메타데이터가 없는 페이로드
        """
        result = yt_dlp_evaluator.evaluate(mock_payload_without_metadata)
        assert result == False
    
    
    @patch('src.common.processor.evaluator.evaluator_strategy.EvaluatorStrategy._evaluate')
    def test_evaluate_with_partial_metadata(self, mock_evaluate, yt_dlp_evaluator):
        """
        일부 메타데이터만 있는 페이로드 평가 테스트
        
        Args:
            mock_evaluate: _evaluate 메소드 Mock
            yt_dlp_evaluator: YtDlpEvaluator 인스턴스
        """
        # Mock 설정
        mock_evaluate.return_value = False
        
        # 일부 메타데이터만 있는 페이로드
        payload = Payload(
            buffer=b"audio_data",
            metadata={
                "title": "게임 플레이 영상",
                "other_field": "should_be_ignored"
            },
            data_type=DataType.AUDIO,
            status=PayloadStatus.COMPLETED,
            processor=YtDlpDownloader()
        )
        
        # 테스트 실행
        result = yt_dlp_evaluator.evaluate(payload)
        
        # 검증
        assert result == False
        mock_evaluate.assert_called_once()
        
        # 호출된 인자 확인 - title만 포함되어야 함
        call_args = mock_evaluate.call_args[0][0]
        assert "title" in call_args
        assert "description" not in call_args
        assert "other_field" not in call_args
        assert call_args["title"] == "게임 플레이 영상" 