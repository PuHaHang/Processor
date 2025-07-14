"""
RefinerStrategy 인터페이스 테스트 모듈

이 모듈은 RefinerStrategy 추상 클래스의 인터페이스를 검증하는 단위 테스트를 제공합니다.
추상 메소드의 정의와 구현체에서의 인터페이스 준수를 테스트합니다.
"""

import pytest
from abc import ABC
from unittest.mock import Mock

from src.common.processor.refiner.refiner_strategy import RefinerStrategy
from src.common.processor.types import DataType, Payload, PayloadStatus


class TestRefinerStrategy:
    """
    RefinerStrategy 인터페이스에 대한 테스트 모음
    
    추상 클래스의 구조와 메소드 시그니처를 검증합니다.
    """
    
    def test_refiner_strategy_is_abstract_class(self):
        """
        RefinerStrategy가 추상 클래스인지 테스트
        """
        assert issubclass(RefinerStrategy, ABC)
        
        # 추상 클래스는 직접 인스턴스화할 수 없음
        with pytest.raises(TypeError):
            RefinerStrategy()
    
    
    def test_refiner_strategy_has_required_abstract_methods(self):
        """
        RefinerStrategy가 필요한 추상 메소드들을 가지고 있는지 테스트
        """
        # 추상 메소드 확인
        abstract_methods = RefinerStrategy.__abstractmethods__
        assert 'is_supported' in abstract_methods
        assert 'process' in abstract_methods
        assert len(abstract_methods) == 2
    
    
    def test_concrete_implementation_must_implement_abstract_methods(self):
        """
        구체적인 구현체가 추상 메소드들을 구현해야 하는지 테스트
        """
        # is_supported만 구현한 불완전한 클래스
        class IncompleteRefiner(RefinerStrategy):
            def is_supported(self, payload: Payload) -> bool:
                return True
            # process 메소드 누락
        
        # 불완전한 구현체는 인스턴스화할 수 없음
        with pytest.raises(TypeError):
            IncompleteRefiner()
    
    
    def test_concrete_implementation_with_all_methods(self):
        """
        모든 추상 메소드를 구현한 구체적인 구현체 테스트
        """
        # 완전한 구현체
        class ConcreteRefiner(RefinerStrategy):
            def is_supported(self, payload: Payload) -> bool:
                return payload.data_type == DataType.TEXT
            
            def process(self, payload: Payload, opt: dict = {}) -> Payload:
                return payload
        
        # 완전한 구현체는 인스턴스화 가능
        refiner = ConcreteRefiner()
        assert isinstance(refiner, RefinerStrategy)
        assert isinstance(refiner, ConcreteRefiner)
    
    
    def test_is_supported_method_signature(self):
        """
        is_supported 메소드의 시그니처 테스트
        """
        class TestRefiner(RefinerStrategy):
            def is_supported(self, payload: Payload) -> bool:
                return True
            
            def process(self, payload: Payload, opt: dict = {}) -> Payload:
                return payload
        
        refiner = TestRefiner()
        
        # 테스트 페이로드 생성
        payload = Payload(
            buffer=b"test",
            metadata={},
            data_type=DataType.TEXT,
            status=PayloadStatus.COMPLETED,
            processor=None
        )
        
        # 메소드 호출 및 반환 타입 확인
        result = refiner.is_supported(payload)
        assert isinstance(result, bool)
    
    
    def test_process_method_signature(self):
        """
        process 메소드의 시그니처 테스트
        """
        class TestRefiner(RefinerStrategy):
            def is_supported(self, payload: Payload) -> bool:
                return True
            
            def process(self, payload: Payload, opt: dict = {}) -> Payload:
                # 기본 구현: 원본 페이로드에 처리 정보 추가
                return Payload(
                    buffer=payload.buffer,
                    metadata={
                        **payload.metadata,
                        "processed": True,
                        "refiner": "test"
                    },
                    data_type=payload.data_type,
                    status=PayloadStatus.COMPLETED,
                    processor=payload.processor
                )
        
        refiner = TestRefiner()
        
        # 테스트 페이로드 생성
        payload = Payload(
            buffer=b"test content",
            metadata={"original": True},
            data_type=DataType.TEXT,
            status=PayloadStatus.COMPLETED,
            processor=None
        )
        
        # 옵션 없이 호출
        result1 = refiner.process(payload)
        assert isinstance(result1, Payload)
        assert result1.metadata["processed"] == True
        assert result1.metadata["original"] == True
        
        # 옵션과 함께 호출
        options = {"test_option": "test_value"}
        result2 = refiner.process(payload, options)
        assert isinstance(result2, Payload)
    
    
    def test_method_documentation(self):
        """
        RefinerStrategy 메소드들의 문서화 테스트
        """
        # is_supported 메소드 문서 확인
        is_supported_doc = RefinerStrategy.is_supported.__doc__
        assert is_supported_doc is not None
        assert "payload" in is_supported_doc.lower()
        assert "bool" in is_supported_doc.lower()
        
        # process 메소드 문서 확인
        process_doc = RefinerStrategy.process.__doc__
        assert process_doc is not None
        assert "payload" in process_doc.lower()
        assert "opt" in process_doc.lower()


class TestRefinerStrategyUsage:
    """
    RefinerStrategy 인터페이스의 실제 사용 패턴 테스트
    """
    
    @pytest.fixture
    def mock_refiner_strategy(self):
        """
        테스트용 RefinerStrategy 구현체를 제공하는 fixture
        """
        class MockRefinerStrategy(RefinerStrategy):
            def __init__(self):
                self.call_history = []
            
            def is_supported(self, payload: Payload) -> bool:
                self.call_history.append(('is_supported', payload))
                return payload.data_type == DataType.TEXT
            
            def process(self, payload: Payload, opt: dict = {}) -> Payload:
                self.call_history.append(('process', payload, opt))
                return Payload(
                    buffer=f"processed: {payload.buffer.decode()}".encode(),
                    metadata={
                        **payload.metadata,
                        "processed_by": "mock_refiner"
                    },
                    data_type=payload.data_type,
                    status=PayloadStatus.COMPLETED,
                    processor=payload.processor
                )
        
        return MockRefinerStrategy()
    
    
    def test_strategy_pattern_usage(self, mock_refiner_strategy):
        """
        Strategy 패턴에서의 RefinerStrategy 사용 테스트
        """
        # 테스트 페이로드들
        text_payload = Payload(
            buffer="Hello world".encode(),
            metadata={"type": "greeting"},
            data_type=DataType.TEXT,
            status=PayloadStatus.COMPLETED,
            processor=None
        )
        
        audio_payload = Payload(
            buffer=b"audio_data",
            metadata={"duration": 120},
            data_type=DataType.AUDIO,
            status=PayloadStatus.COMPLETED,
            processor=None
        )
        
        # 지원 여부 확인
        assert mock_refiner_strategy.is_supported(text_payload) == True
        assert mock_refiner_strategy.is_supported(audio_payload) == False
        
        # 지원되는 페이로드 처리
        result = mock_refiner_strategy.process(text_payload, {"option": "value"})
        
        # 결과 검증
        assert result.metadata["processed_by"] == "mock_refiner"
        assert "processed: Hello world" in result.buffer.decode()
        
        # 호출 이력 확인
        assert len(mock_refiner_strategy.call_history) == 3
        assert mock_refiner_strategy.call_history[0][0] == 'is_supported'
        assert mock_refiner_strategy.call_history[1][0] == 'is_supported'
        assert mock_refiner_strategy.call_history[2][0] == 'process'
    
    
    def test_error_handling_in_implementation(self):
        """
        구현체에서의 에러 처리 테스트
        """
        class ErrorProneRefiner(RefinerStrategy):
            def is_supported(self, payload: Payload) -> bool:
                if payload.buffer is None:
                    raise ValueError("Buffer cannot be None")
                return True
            
            def process(self, payload: Payload, opt: dict = {}) -> Payload:
                if not self.is_supported(payload):
                    raise ValueError("Payload not supported")
                
                if opt.get("should_fail", False):
                    raise RuntimeError("Processing failed")
                
                return payload
        
        refiner = ErrorProneRefiner()
        
        # 정상 페이로드
        valid_payload = Payload(
            buffer=b"test",
            metadata={},
            data_type=DataType.TEXT,
            status=PayloadStatus.COMPLETED,
            processor=None
        )
        
        # 옵션에 의한 실패
        with pytest.raises(RuntimeError, match="Processing failed"):
            refiner.process(valid_payload, {"should_fail": True})
        
        # 정상 처리
        result = refiner.process(valid_payload, {"should_fail": False})
        assert result == valid_payload 