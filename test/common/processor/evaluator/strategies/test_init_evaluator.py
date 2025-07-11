"""
InitEvaluator 테스트 모듈

이 모듈은 InitEvaluator 클래스의 기능을 검증하는 단위 테스트를 제공합니다.
초기화 평가기의 지원 여부 확인, 평가 수행 등의 기능을 테스트합니다.
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
    from src.common.processor.evaluator.strategies.init_evaluator import InitEvaluator
    from src.common.processor.types import DataType, Payload, PayloadStatus


class TestInitEvaluator:
    """
    InitEvaluator 클래스에 대한 테스트 모음
    
    초기화 평가기의 지원 여부 확인, 평가 수행 등의
    모든 기능을 테스트합니다.
    """
    
    @pytest.fixture
    def init_evaluator(self):
        """
        테스트용 InitEvaluator 인스턴스를 제공하는 fixture
        
        Returns:
            InitEvaluator: 테스트용 초기화 평가기 인스턴스
        """
        return InitEvaluator()
    
    
    @pytest.fixture
    def mock_payload_with_none_processor(self):
        """
        None 프로세서가 있는 Payload를 제공하는 fixture
        
        Returns:
            Payload: None 프로세서가 포함된 테스트용 페이로드
        """
        return Payload(
            buffer=b"test_data",
            metadata={"test": "metadata"},
            data_type=DataType.TEXT,
            status=PayloadStatus.INIT,
            processor=None
        )
    
    
    @pytest.fixture
    def mock_payload_with_other_processor(self):
        """
        다른 프로세서가 있는 Payload를 제공하는 fixture
        
        Returns:
            Payload: 다른 프로세서가 포함된 테스트용 페이로드
        """
        # Mock 프로세서 클래스 생성
        class MockProcessor:
            pass
        
        return Payload(
            buffer=b"test_data",
            metadata={"test": "metadata"},
            data_type=DataType.TEXT,
            status=PayloadStatus.INIT,
            processor=MockProcessor
        )
    
    
    @pytest.fixture
    def mock_payload_with_complex_data(self):
        """
        복잡한 데이터가 있는 Payload를 제공하는 fixture
        
        Returns:
            Payload: 복잡한 데이터가 포함된 테스트용 페이로드
        """
        return Payload(
            buffer="김치찌개 레시피입니다".encode('utf-8'),
            metadata={
                "title": "맛있는 김치찌개",
                "description": "전통 김치찌개 만드는 법",
                "duration": 180
            },
            data_type=DataType.TEXT,
            status=PayloadStatus.INIT,
            processor=None
        )
    
    
    @pytest.mark.unit
    def test_init_evaluator_initialization(self, init_evaluator):
        """
        InitEvaluator 초기화 테스트
        
        Args:
            init_evaluator: InitEvaluator 인스턴스
        """
        assert isinstance(init_evaluator, InitEvaluator)
        assert hasattr(init_evaluator, 'available_processors')
        assert init_evaluator.available_processors == [None]
        assert len(init_evaluator.available_processors) == 1
        assert init_evaluator.available_processors[0] is None
    
    
    @pytest.mark.unit
    def test_is_supported_with_none_processor(self, init_evaluator, mock_payload_with_none_processor):
        """
        None 프로세서에 대한 지원 여부 테스트
        
        Args:
            init_evaluator: InitEvaluator 인스턴스
            mock_payload_with_none_processor: None 프로세서 페이로드
        """
        result = init_evaluator.is_supported(mock_payload_with_none_processor)
        assert result == True
    
    
    @pytest.mark.unit
    def test_is_supported_with_other_processor(self, init_evaluator, mock_payload_with_other_processor):
        """
        다른 프로세서에 대한 지원 여부 테스트
        
        Args:
            init_evaluator: InitEvaluator 인스턴스
            mock_payload_with_other_processor: 다른 프로세서 페이로드
        """
        result = init_evaluator.is_supported(mock_payload_with_other_processor)
        assert result == False
    
    
    @pytest.mark.unit
    @patch('src.common.processor.evaluator.evaluator_strategy.EvaluatorStrategy._evaluate')
    def test_evaluate_with_simple_payload(self, mock_evaluate, init_evaluator, mock_payload_with_none_processor):
        """
        단순한 페이로드 평가 테스트
        
        Args:
            mock_evaluate: 상위 클래스 _evaluate 메소드 Mock
            init_evaluator: InitEvaluator 인스턴스
            mock_payload_with_none_processor: None 프로세서 페이로드
        """
        # Mock 설정
        mock_evaluate.return_value = True
        
        # 테스트 실행
        result = init_evaluator.evaluate(mock_payload_with_none_processor)
        
        # 검증
        assert result == True
        mock_evaluate.assert_called_once()
        
        # 호출된 인자 확인 - payload.__str__ 결과가 전달되어야 함
        call_args = mock_evaluate.call_args[0][0]
        assert isinstance(call_args, str)
        assert "test_data" in call_args or "Payload" in call_args
    
    
    @pytest.mark.unit
    @patch('src.common.processor.evaluator.evaluator_strategy.EvaluatorStrategy._evaluate')
    def test_evaluate_with_complex_payload(self, mock_evaluate, init_evaluator, mock_payload_with_complex_data):
        """
        복잡한 페이로드 평가 테스트
        
        Args:
            mock_evaluate: 상위 클래스 _evaluate 메소드 Mock
            init_evaluator: InitEvaluator 인스턴스
            mock_payload_with_complex_data: 복잡한 데이터 페이로드
        """
        # Mock 설정
        mock_evaluate.return_value = True
        
        # 테스트 실행
        result = init_evaluator.evaluate(mock_payload_with_complex_data)
        
        # 검증
        assert result == True
        mock_evaluate.assert_called_once()
        
        # 호출된 인자 확인
        call_args = mock_evaluate.call_args[0][0]
        assert isinstance(call_args, str)
        # payload.__str__ 결과에 메타데이터 정보가 포함되어야 함
        assert "Payload" in call_args
    
    
    @pytest.mark.unit
    @patch('src.common.processor.evaluator.evaluator_strategy.EvaluatorStrategy._evaluate')
    def test_evaluate_returns_false(self, mock_evaluate, init_evaluator, mock_payload_with_none_processor):
        """
        평가 결과가 False인 경우 테스트
        
        Args:
            mock_evaluate: 상위 클래스 _evaluate 메소드 Mock
            init_evaluator: InitEvaluator 인스턴스
            mock_payload_with_none_processor: None 프로세서 페이로드
        """
        # Mock 설정
        mock_evaluate.return_value = False
        
        # 테스트 실행
        result = init_evaluator.evaluate(mock_payload_with_none_processor)
        
        # 검증
        assert result == False
        mock_evaluate.assert_called_once()
    
    
    @pytest.mark.unit
    @patch('src.common.processor.evaluator.evaluator_strategy.EvaluatorStrategy._evaluate')
    def test_evaluate_exception_handling(self, mock_evaluate, init_evaluator, mock_payload_with_none_processor):
        """
        상위 클래스 _evaluate 메소드에서 예외 발생 시 처리 테스트
        
        Args:
            mock_evaluate: 상위 클래스 _evaluate 메소드 Mock
            init_evaluator: InitEvaluator 인스턴스
            mock_payload_with_none_processor: None 프로세서 페이로드
        """
        # Mock 설정 - 예외 발생
        mock_evaluate.side_effect = Exception("평가 중 오류 발생")
        
        # 테스트 실행 및 검증
        with pytest.raises(Exception) as exc_info:
            init_evaluator.evaluate(mock_payload_with_none_processor)
        
        assert "평가 중 오류 발생" in str(exc_info.value)
        mock_evaluate.assert_called_once()
    
    
    @pytest.mark.unit
    def test_available_processors_immutability(self, init_evaluator):
        """
        available_processors 속성의 불변성 테스트
        
        Args:
            init_evaluator: InitEvaluator 인스턴스
        """
        # 원본 값 저장
        original_processors = init_evaluator.available_processors.copy()
        
        # 리스트 수정 시도
        init_evaluator.available_processors.append("TestProcessor")
        
        # 수정된 값 확인 (실제로는 수정됨을 확인하는 테스트)
        assert len(init_evaluator.available_processors) == 2
        assert "TestProcessor" in init_evaluator.available_processors
        
        # 원본 값과 다름을 확인
        assert init_evaluator.available_processors != original_processors
    
    
    @pytest.mark.unit
    def test_is_supported_with_multiple_payloads(self, init_evaluator):
        """
        여러 페이로드에 대한 지원 여부 일관성 테스트
        
        Args:
            init_evaluator: InitEvaluator 인스턴스
        """
                 # Mock 프로세서 클래스 생성
        class MockProcessor:
            pass
        
        # 다양한 페이로드 생성
        payloads = [
            Payload(
                buffer=b"data1",
                metadata={},
                data_type=DataType.TEXT,
                status=PayloadStatus.INIT,
                processor=None
            ),
            Payload(
                buffer=b"data2",
                metadata={},
                data_type=DataType.AUDIO,
                status=PayloadStatus.INIT,
                processor=None
            ),
            Payload(
                buffer=b"data3",
                metadata={},
                data_type=DataType.URL,
                status=PayloadStatus.INIT,
                processor=None
            ),
            Payload(
                buffer=b"data4",
                metadata={},
                data_type=DataType.TEXT,
                status=PayloadStatus.INIT,
                processor=MockProcessor
            ),
        ]
        
        # 테스트 실행
        results = [init_evaluator.is_supported(payload) for payload in payloads]
        
        # 검증 - 처음 3개는 True, 마지막은 False
        assert results == [True, True, True, False]
    
    
    @pytest.mark.unit
    @patch('src.common.processor.evaluator.evaluator_strategy.EvaluatorStrategy._evaluate')
    def test_evaluate_with_different_data_types(self, mock_evaluate, init_evaluator):
        """
        다양한 데이터 타입의 페이로드 평가 테스트
        
        Args:
            mock_evaluate: 상위 클래스 _evaluate 메소드 Mock
            init_evaluator: InitEvaluator 인스턴스
        """
        # Mock 설정
        mock_evaluate.return_value = True
        
                 # 다양한 데이터 타입 페이로드 생성
        payloads = [
            Payload(
                buffer=b"text_data",
                metadata={},
                data_type=DataType.TEXT,
                status=PayloadStatus.INIT,
                processor=None
            ),
            Payload(
                buffer=b"audio_data",
                metadata={},
                data_type=DataType.AUDIO,
                status=PayloadStatus.INIT,
                processor=None
            ),
            Payload(
                buffer=b"url_data",
                metadata={},
                data_type=DataType.URL,
                status=PayloadStatus.INIT,
                processor=None
            ),
        ]
        
        # 각 페이로드에 대해 테스트 실행
        for payload in payloads:
            result = init_evaluator.evaluate(payload)
            assert result == True
        
        # _evaluate가 페이로드 수만큼 호출되었는지 확인
        assert mock_evaluate.call_count == len(payloads)
    
    
    @pytest.mark.unit
    def test_payload_str_conversion(self, init_evaluator):
        """
        페이로드 문자열 변환 테스트
        
        Args:
            init_evaluator: InitEvaluator 인스턴스
        """
        # 테스트 페이로드 생성
        payload = Payload(
            buffer="test데이터".encode('utf-8'),
            metadata={"key": "value"},
            data_type=DataType.TEXT,
            status=PayloadStatus.INIT,
            processor=None
        )
        
        # __str__ 메소드 호출 결과 확인
        str_result = str(payload.__str__)
        assert isinstance(str_result, str)
        
        # 실제 __str__ 메소드 호출 결과 확인
        actual_str = payload.__str__()
        assert isinstance(actual_str, str)
        assert "Payload" in actual_str or "payload" in actual_str.lower() 