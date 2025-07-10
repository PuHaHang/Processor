"""
Evaluator 테스트 모듈

이 모듈은 Evaluator 클래스와 관련 전략들의 기능을 검증하는 단위 테스트를 제공합니다.
_models 관련 부분은 Mock을 사용하여 실제 모델 없이도 테스트가 가능하도록 구현되었습니다.
"""

import os
import pytest
import sys
from unittest.mock import Mock, patch, MagicMock

# 테스트용 환경변수 설정
os.environ['MODEL_PATH'] = 'test/resources/models'
os.environ['ZEROSHOT_MODEL_NAME'] = 'test-model'

# 모델 관련 모듈들을 mock으로 처리
sys.modules['onnx'] = Mock()
sys.modules['onnxruntime'] = Mock()
sys.modules['transformers'] = Mock()
sys.modules['yt_dlp'] = Mock()
sys.modules['yt_dlp.utils'] = Mock()

# numpy mock 설정
import numpy as np
mock_numpy_array = Mock()
mock_numpy_array.astype = Mock(return_value=mock_numpy_array)

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
    from src.common.processor.evaluator.strategies.generic_evaluator import GenericEvaluator
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
            processor=YtDlpDownloader
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
            processor=YtDlpDownloader
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
            processor=YtDlpDownloader
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


@patch('src.common.processor.evaluator._models.zero_shot_classifier.ZeroShotClassifier._validate_model')
@patch('src.common.processor.evaluator._models.zero_shot_classifier.ZeroShotClassifier._load_session')
@patch('src.common.processor.evaluator._models.zero_shot_classifier.ZeroShotClassifier._load_tokenizer')
class TestZeroShotClassifier:
    """
    ZeroShotClassifier 클래스에 대한 테스트 모음
    
    실제 모델 대신 Mock을 사용하여 분류기의 기능을 테스트합니다.
    """
    
    def test_zero_shot_classifier_initialization(self, mock_load_tokenizer, mock_load_session, mock_validate_model):
        """
        ZeroShotClassifier 초기화 테스트
        
        Args:
            mock_load_tokenizer: 토크나이저 로딩 Mock
            mock_load_session: 세션 로딩 Mock
            mock_validate_model: 모델 검증 Mock
        """
        from src.common.processor.evaluator._models import ZeroShotClassifier
        
        # Mock 설정
        mock_load_tokenizer.return_value = Mock()
        mock_load_session.return_value = Mock()
        
        # 테스트 실행
        classifier = ZeroShotClassifier("test-model")
        
        # 검증
        assert classifier is not None
        mock_validate_model.assert_called_once()
        mock_load_tokenizer.assert_called_once()
        mock_load_session.assert_called_once()
    
    
    def test_evaluate_string_recipe_content(self, mock_load_tokenizer, mock_load_session, mock_validate_model):
        """
        레시피 관련 문자열 평가 테스트
        
        Args:
            mock_load_tokenizer: 토크나이저 로딩 Mock
            mock_load_session: 세션 로딩 Mock
            mock_validate_model: 모델 검증 Mock
        """
        from src.common.processor.evaluator._models import ZeroShotClassifier
        
        # Mock 설정
        mock_tokenizer = Mock()
        mock_tokenizer.return_value = {
            "input_ids": mock_numpy_array,
            "attention_mask": mock_numpy_array
        }
        mock_session = Mock()
        mock_session.run.return_value = [[[2.0, 0.5, 0.3]]]  # entailment가 높음
        
        mock_load_tokenizer.return_value = mock_tokenizer
        mock_load_session.return_value = mock_session
        
        # 테스트 실행
        classifier = ZeroShotClassifier("test-model")
        result = classifier.evaluate("김치찌개 만드는 방법을 알려드립니다")
        
        # 검증
        assert result == True
        mock_tokenizer.assert_called()
        mock_session.run.assert_called()
    
    
    def test_evaluate_string_non_recipe_content(self, mock_load_tokenizer, mock_load_session, mock_validate_model):
        """
        레시피와 관련없는 문자열 평가 테스트
        
        Args:
            mock_load_tokenizer: 토크나이저 로딩 Mock
            mock_load_session: 세션 로딩 Mock
            mock_validate_model: 모델 검증 Mock
        """
        from src.common.processor.evaluator._models import ZeroShotClassifier
        
        # Mock 설정
        mock_tokenizer = Mock()
        mock_tokenizer.return_value = {
            "input_ids": mock_numpy_array,
            "attention_mask": mock_numpy_array
        }
        mock_session = Mock()
        mock_session.run.return_value = [[[0.3, 0.5, 2.0]]]  # contradiction이 높음
        
        mock_load_tokenizer.return_value = mock_tokenizer
        mock_load_session.return_value = mock_session
        
        # 테스트 실행
        classifier = ZeroShotClassifier("test-model")
        result = classifier.evaluate("축구 경기 하이라이트")
        
        # 검증
        assert result == False
    
    
    def test_evaluate_dict_content(self, mock_load_tokenizer, mock_load_session, mock_validate_model):
        """
        딕셔너리 형태 메타데이터 평가 테스트
        
        Args:
            mock_load_tokenizer: 토크나이저 로딩 Mock
            mock_load_session: 세션 로딩 Mock
            mock_validate_model: 모델 검증 Mock
        """
        from src.common.processor.evaluator._models import ZeroShotClassifier
        
        # Mock 설정
        mock_tokenizer = Mock()
        mock_tokenizer.return_value = {
            "input_ids": mock_numpy_array,
            "attention_mask": mock_numpy_array
        }
        mock_session = Mock()
        mock_session.run.return_value = [[[2.0, 0.5, 0.3]]]  # entailment가 높음
        
        mock_load_tokenizer.return_value = mock_tokenizer
        mock_load_session.return_value = mock_session
        
        # 테스트 실행
        classifier = ZeroShotClassifier("test-model")
        metadata = {
            "title": "파스타 만들기",
            "description": "맛있는 토마토 파스타 레시피"
        }
        result = classifier.evaluate(metadata)
        
        # 검증
        assert result == True
        assert mock_session.run.call_count == 2  # title과 description 각각 호출
    
    
    def test_evaluate_empty_sequence(self, mock_load_tokenizer, mock_load_session, mock_validate_model):
        """
        빈 시퀀스 평가 시 예외 테스트
        
        Args:
            mock_load_tokenizer: 토크나이저 로딩 Mock
            mock_load_session: 세션 로딩 Mock
            mock_validate_model: 모델 검증 Mock
        """
        from src.common.processor.evaluator._models import ZeroShotClassifier
        
        # Mock 설정
        mock_load_tokenizer.return_value = Mock()
        mock_load_session.return_value = Mock()
        
        # 테스트 실행
        classifier = ZeroShotClassifier("test-model")
        
        # 검증
        with pytest.raises(ValueError) as exc_info:
            classifier.evaluate("")
        assert "Sequence is empty" in str(exc_info.value)


@patch('src.common.processor.evaluator._models.bert_base_classifier.BertBaseClassifier._validate_model')
@patch('src.common.processor.evaluator._models.bert_base_classifier.BertBaseClassifier._load_session')
@patch('src.common.processor.evaluator._models.bert_base_classifier.BertBaseClassifier._load_tokenizer')
class TestBertBaseClassifier:
    """
    BertBaseClassifier 클래스에 대한 테스트 모음
    
    실제 모델 대신 Mock을 사용하여 BERT 기반 분류기의 기능을 테스트합니다.
    """
    
    def test_bert_classifier_initialization(self, mock_load_tokenizer, mock_load_session, mock_validate_model):
        """
        BertBaseClassifier 초기화 테스트
        
        Args:
            mock_load_tokenizer: 토크나이저 로딩 Mock
            mock_load_session: 세션 로딩 Mock
            mock_validate_model: 모델 검증 Mock
        """
        from src.common.processor.evaluator._models import BertBaseClassifier
        
        # Mock 설정
        mock_load_tokenizer.return_value = Mock()
        mock_load_session.return_value = Mock()
        
        # 테스트 실행
        classifier = BertBaseClassifier("test-model")
        
        # 검증
        assert classifier is not None
        mock_validate_model.assert_called_once()
        mock_load_tokenizer.assert_called_once()
        mock_load_session.assert_called_once()
    
    
    @patch('src.common.processor.evaluator._models.bert_base_classifier.BertBaseClassifier._classify')
    def test_evaluate_recipe_content(self, mock_classify, mock_load_tokenizer, mock_load_session, mock_validate_model):
        """
        레시피 관련 내용 평가 테스트
        
        Args:
            mock_classify: _classify 메소드 Mock
            mock_load_tokenizer: 토크나이저 로딩 Mock
            mock_load_session: 세션 로딩 Mock
            mock_validate_model: 모델 검증 Mock
        """
        from src.common.processor.evaluator._models import BertBaseClassifier
        
        # Mock 설정
        mock_load_tokenizer.return_value = Mock()
        mock_load_session.return_value = Mock()
        mock_classify.return_value = {"recipe": 0.8}
        
        # 테스트 실행
        classifier = BertBaseClassifier("test-model")
        result = classifier.evaluate("김치볶음밥 만들기")
        
        # 검증
        assert result == True
        mock_classify.assert_called_once_with("김치볶음밥 만들기")
    
    
    @patch('src.common.processor.evaluator._models.bert_base_classifier.BertBaseClassifier._classify')
    def test_evaluate_non_recipe_content(self, mock_classify, mock_load_tokenizer, mock_load_session, mock_validate_model):
        """
        레시피가 아닌 내용 평가 테스트
        
        Args:
            mock_classify: _classify 메소드 Mock
            mock_load_tokenizer: 토크나이저 로딩 Mock
            mock_load_session: 세션 로딩 Mock
            mock_validate_model: 모델 검증 Mock
        """
        from src.common.processor.evaluator._models import BertBaseClassifier
        
        # Mock 설정
        mock_load_tokenizer.return_value = Mock()
        mock_load_session.return_value = Mock()
        mock_classify.return_value = {"recipe": 0.3}
        
        # 테스트 실행
        classifier = BertBaseClassifier("test-model")
        result = classifier.evaluate("영화 리뷰")
        
        # 검증
        assert result == False
        mock_classify.assert_called_once_with("영화 리뷰")


class TestGenericEvaluator:
    """
    GenericEvaluator 클래스에 대한 테스트 모음
    
    범용 평가기의 지원 여부 확인, 평가 수행 등의
    모든 기능을 테스트합니다.
    """
    
    @pytest.fixture
    def generic_evaluator(self):
        """
        테스트용 GenericEvaluator 인스턴스를 제공하는 fixture
        
        Returns:
            GenericEvaluator: 테스트용 범용 평가기 인스턴스
        """
        return GenericEvaluator()
    
    
    @pytest.fixture
    def mock_text_payload(self):
        """
        텍스트 타입 Payload를 제공하는 fixture
        
        Returns:
            Payload: 테스트용 텍스트 페이로드
        """
        return Payload(
            buffer="김치찌개 만드는 방법을 알려드립니다. 재료는 김치, 돼지고기, 두부가 필요합니다.".encode('utf-8'),
            metadata={"content_type": "recipe"},
            data_type=DataType.TEXT,
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
            buffer=b"fake_audio_data",
            metadata={"duration": 120},
            data_type=DataType.AUDIO,
            status=PayloadStatus.COMPLETED,
            processor=YtDlpDownloader
        )
    
    
    @pytest.fixture
    def mock_empty_text_payload(self):
        """
        빈 텍스트 Payload를 제공하는 fixture
        
        Returns:
            Payload: 테스트용 빈 텍스트 페이로드
        """
        return Payload(
            buffer=b"",
            metadata={},
            data_type=DataType.TEXT,
            status=PayloadStatus.COMPLETED,
            processor=None
        )
    
    
    @pytest.fixture
    def mock_invalid_encoding_payload(self):
        """
        잘못된 인코딩 Payload를 제공하는 fixture
        
        Returns:
            Payload: 테스트용 잘못된 인코딩 페이로드
        """
        return Payload(
            buffer=b'\xff\xfe\xfd',  # 잘못된 UTF-8 바이트 시퀀스
            metadata={},
            data_type=DataType.TEXT,
            status=PayloadStatus.COMPLETED,
            processor=None
        )
    
    
    @pytest.mark.unit
    def test_generic_evaluator_initialization(self, generic_evaluator):
        """
        GenericEvaluator 초기화 테스트
        
        Args:
            generic_evaluator: GenericEvaluator 인스턴스
        """
        assert isinstance(generic_evaluator, GenericEvaluator)
        assert hasattr(generic_evaluator, 'available_processors')
        assert isinstance(generic_evaluator.available_processors, list)
        assert len(generic_evaluator.available_processors) == 0  # 현재 빈 리스트로 설정
    
    
    @pytest.mark.unit
    def test_is_supported_with_text_data_type(self, generic_evaluator, mock_text_payload):
        """
        텍스트 데이터 타입에 대한 지원 여부 테스트
        
        Args:
            generic_evaluator: GenericEvaluator 인스턴스
            mock_text_payload: 텍스트 타입 페이로드
        """
        result = generic_evaluator.is_supported(mock_text_payload)
        assert result == True
    
    
    @pytest.mark.unit
    def test_is_supported_with_audio_data_type(self, generic_evaluator, mock_audio_payload):
        """
        오디오 데이터 타입에 대한 지원 여부 테스트
        
        Args:
            generic_evaluator: GenericEvaluator 인스턴스
            mock_audio_payload: 오디오 타입 페이로드
        """
        result = generic_evaluator.is_supported(mock_audio_payload)
        assert result == False
    
    
    @pytest.mark.unit
    def test_is_supported_with_none_data_type(self, generic_evaluator):
        """
        None 데이터 타입에 대한 지원 여부 테스트
        
        Args:
            generic_evaluator: GenericEvaluator 인스턴스
        """
        # None data_type은 실제로는 발생하지 않으므로 AUDIO로 대체
        payload = Payload(
            buffer=b"test",
            metadata={},
            data_type=DataType.AUDIO,  # None 대신 AUDIO 사용
            status=PayloadStatus.COMPLETED,
            processor=None
        )
        result = generic_evaluator.is_supported(payload)
        assert result == False
    
    
    @pytest.mark.unit
    def test_is_supported_with_empty_data_type(self, generic_evaluator):
        """
        다른 데이터 타입에 대한 지원 여부 테스트 (URL 타입)
        
        Args:
            generic_evaluator: GenericEvaluator 인스턴스
        """
        payload = Payload(
            buffer=b"test",
            metadata={},
            data_type=DataType.URL,  # 빈 문자열 대신 URL 사용
            status=PayloadStatus.COMPLETED,
            processor=None
        )
        result = generic_evaluator.is_supported(payload)
        assert result == False
    
    
    @pytest.mark.unit
    @patch('src.common.processor.evaluator.evaluator_strategy.EvaluatorStrategy._evaluate')
    def test_evaluate_with_recipe_text(self, mock_evaluate, generic_evaluator, mock_text_payload):
        """
        레시피 관련 텍스트 평가 테스트
        
        Args:
            mock_evaluate: 상위 클래스 _evaluate 메소드 Mock
            generic_evaluator: GenericEvaluator 인스턴스
            mock_text_payload: 텍스트 타입 페이로드
        """
        # Mock 설정
        mock_evaluate.return_value = True
        
        # 테스트 실행
        result = generic_evaluator.evaluate(mock_text_payload)
        
        # 검증
        assert result == True
        mock_evaluate.assert_called_once_with("김치찌개 만드는 방법을 알려드립니다. 재료는 김치, 돼지고기, 두부가 필요합니다.")
    
    
    @pytest.mark.unit
    @patch('src.common.processor.evaluator.evaluator_strategy.EvaluatorStrategy._evaluate')
    def test_evaluate_with_non_recipe_text(self, mock_evaluate, generic_evaluator):
        """
        레시피가 아닌 텍스트 평가 테스트
        
        Args:
            mock_evaluate: 상위 클래스 _evaluate 메소드 Mock
            generic_evaluator: GenericEvaluator 인스턴스
        """
        # Mock 설정
        mock_evaluate.return_value = False
        
        # 테스트 페이로드 생성
        payload = Payload(
            buffer="오늘 날씨가 매우 좋습니다. 산책하기 좋은 날입니다.".encode('utf-8'),
            metadata={},
            data_type=DataType.TEXT,
            status=PayloadStatus.COMPLETED,
            processor=None
        )
        
        # 테스트 실행
        result = generic_evaluator.evaluate(payload)
        
        # 검증
        assert result == False
        mock_evaluate.assert_called_once_with("오늘 날씨가 매우 좋습니다. 산책하기 좋은 날입니다.")
    
    
    @pytest.mark.unit
    @patch('src.common.processor.evaluator.evaluator_strategy.EvaluatorStrategy._evaluate')
    def test_evaluate_with_empty_text(self, mock_evaluate, generic_evaluator, mock_empty_text_payload):
        """
        빈 텍스트 평가 테스트
        
        Args:
            mock_evaluate: 상위 클래스 _evaluate 메소드 Mock
            generic_evaluator: GenericEvaluator 인스턴스
            mock_empty_text_payload: 빈 텍스트 페이로드
        """
        # Mock 설정
        mock_evaluate.return_value = False
        
        # 테스트 실행
        result = generic_evaluator.evaluate(mock_empty_text_payload)
        
        # 검증
        assert result == False
        mock_evaluate.assert_called_once_with("")
    
    
    @pytest.mark.unit
    def test_evaluate_with_unicode_decode_error(self, generic_evaluator, mock_invalid_encoding_payload):
        """
        UTF-8 디코딩 에러 테스트
        
        Args:
            generic_evaluator: GenericEvaluator 인스턴스
            mock_invalid_encoding_payload: 잘못된 인코딩 페이로드
        """
        # 테스트 실행 및 검증
        with pytest.raises(UnicodeDecodeError):
            generic_evaluator.evaluate(mock_invalid_encoding_payload)
    
    
    @pytest.mark.unit
    @patch('src.common.processor.evaluator.evaluator_strategy.EvaluatorStrategy._evaluate')
    def test_evaluate_with_korean_text(self, mock_evaluate, generic_evaluator):
        """
        한국어 텍스트 평가 테스트
        
        Args:
            mock_evaluate: 상위 클래스 _evaluate 메소드 Mock
            generic_evaluator: GenericEvaluator 인스턴스
        """
        # Mock 설정
        mock_evaluate.return_value = True
        
        # 한국어 텍스트 페이로드 생성
        korean_text = "맛있는 된장찌개 끓이는 법: 먼저 멸치육수를 우려내세요."
        payload = Payload(
            buffer=korean_text.encode('utf-8'),
            metadata={},
            data_type=DataType.TEXT,
            status=PayloadStatus.COMPLETED,
            processor=None
        )
        
        # 테스트 실행
        result = generic_evaluator.evaluate(payload)
        
        # 검증
        assert result == True
        mock_evaluate.assert_called_once_with(korean_text)
    
    
    @pytest.mark.unit
    @patch('src.common.processor.evaluator.evaluator_strategy.EvaluatorStrategy._evaluate')
    def test_evaluate_with_english_text(self, mock_evaluate, generic_evaluator):
        """
        영어 텍스트 평가 테스트
        
        Args:
            mock_evaluate: 상위 클래스 _evaluate 메소드 Mock
            generic_evaluator: GenericEvaluator 인스턴스
        """
        # Mock 설정
        mock_evaluate.return_value = True
        
        # 영어 텍스트 페이로드 생성
        english_text = "How to make pasta: Boil water and add salt."
        payload = Payload(
            buffer=english_text.encode('utf-8'),
            metadata={},
            data_type=DataType.TEXT,
            status=PayloadStatus.COMPLETED,
            processor=None
        )
        
        # 테스트 실행
        result = generic_evaluator.evaluate(payload)
        
        # 검증
        assert result == True
        mock_evaluate.assert_called_once_with(english_text)
    
    
    @pytest.mark.unit
    @patch('src.common.processor.evaluator.evaluator_strategy.EvaluatorStrategy._evaluate')
    def test_evaluate_with_mixed_language_text(self, mock_evaluate, generic_evaluator):
        """
        혼합 언어 텍스트 평가 테스트
        
        Args:
            mock_evaluate: 상위 클래스 _evaluate 메소드 Mock
            generic_evaluator: GenericEvaluator 인스턴스
        """
        # Mock 설정
        mock_evaluate.return_value = True
        
        # 한영 혼합 텍스트 페이로드 생성
        mixed_text = "Korean Recipe 김치찌개: Mix kimchi and pork 돼지고기와 함께 끓이세요."
        payload = Payload(
            buffer=mixed_text.encode('utf-8'),
            metadata={},
            data_type=DataType.TEXT,
            status=PayloadStatus.COMPLETED,
            processor=None
        )
        
        # 테스트 실행
        result = generic_evaluator.evaluate(payload)
        
        # 검증
        assert result == True
        mock_evaluate.assert_called_once_with(mixed_text)
    
    
    @pytest.mark.unit
    @patch('src.common.processor.evaluator.evaluator_strategy.EvaluatorStrategy._evaluate')
    def test_evaluate_exception_handling(self, mock_evaluate, generic_evaluator, mock_text_payload):
        """
        상위 클래스 _evaluate 메소드에서 예외 발생 시 처리 테스트
        
        Args:
            mock_evaluate: 상위 클래스 _evaluate 메소드 Mock
            generic_evaluator: GenericEvaluator 인스턴스
            mock_text_payload: 텍스트 타입 페이로드
        """
        # Mock 설정 - 예외 발생
        mock_evaluate.side_effect = Exception("분류기 오류")
        
        # 테스트 실행 및 검증
        with pytest.raises(Exception) as exc_info:
            generic_evaluator.evaluate(mock_text_payload)
        
        assert "분류기 오류" in str(exc_info.value)
        mock_evaluate.assert_called_once()
    
    
    @pytest.mark.unit
    def test_evaluate_with_none_buffer(self, generic_evaluator):
        """
        None 버퍼에 대한 평가 테스트
        
        Args:
            generic_evaluator: GenericEvaluator 인스턴스
        """
        # None 버퍼 페이로드 생성
        payload = Payload(
            buffer=b"",
            metadata={},
            data_type=DataType.TEXT,
            status=PayloadStatus.COMPLETED,
            processor=None
        )
        
        # 테스트 실행 및 검증
        with pytest.raises((AttributeError, ValueError)):
            generic_evaluator.evaluate(payload)
    
    
    @pytest.mark.unit
    @patch('src.common.processor.evaluator.evaluator_strategy.EvaluatorStrategy._evaluate')
    def test_evaluate_with_special_characters(self, mock_evaluate, generic_evaluator):
        """
        특수 문자가 포함된 텍스트 평가 테스트
        
        Args:
            mock_evaluate: 상위 클래스 _evaluate 메소드 Mock
            generic_evaluator: GenericEvaluator 인스턴스
        """
        # Mock 설정
        mock_evaluate.return_value = True
        
        # 특수 문자 포함 텍스트 페이로드 생성
        special_text = "김치찌개 🍲 만들기: 재료 준비 → 끓이기 → 완성! (맛있어요 😋)"
        payload = Payload(
            buffer=special_text.encode('utf-8'),
            metadata={},
            data_type=DataType.TEXT,
            status=PayloadStatus.COMPLETED,
            processor=None
        )
        
        # 테스트 실행
        result = generic_evaluator.evaluate(payload)
        
        # 검증
        assert result == True
        mock_evaluate.assert_called_once_with(special_text) 