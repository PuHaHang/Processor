"""
클래스 기반 예외 처리 데코레이터 테스트 모듈

이 모듈은 클래스 기반 예외 처리 데코레이터들의 모든 기능을 검증하는 단위 테스트를 제공합니다.
ExceptionHandler, RetryOnException, DatabaseExceptionHandler, ValidationExceptionHandler,
CircuitBreaker, SuppressExceptions 등의 데코레이터를 포괄적으로 테스트합니다.
"""

import pytest
import asyncio
import random
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import List, Dict, Any, Optional

from src.common.exception.class_decorators import (
    ExceptionHandler,
    RetryOnException,
    DatabaseExceptionHandler,
    ValidationExceptionHandler,
    CircuitBreaker,
    SuppressExceptions,
    create_exception_handler,
    create_retry_handler,
    create_database_handler,
    create_validation_handler,
    create_circuit_breaker,
    create_suppression_handler
)
from src.common.exception.exception_types import (
    ExceptionType,
    ExceptionSeverity
)
from src.common.exception.custom_exceptions import (
    ValidationException,
    DatabaseException,
    ExternalServiceException
)


class TestExceptionHandler:
    """
    ExceptionHandler 클래스에 대한 테스트 모음
    
    기본 예외 처리 기능의 초기화, 예외 처리, 상속 구조 등을
    체계적으로 테스트합니다.
    """
    
    @pytest.fixture
    def exception_handler(self):
        """
        기본 ExceptionHandler 인스턴스를 제공하는 fixture
        
        Returns:
            ExceptionHandler: 테스트용 예외 처리기 인스턴스
        """
        return ExceptionHandler(
            exception_type=ExceptionType.UNKNOWN,
            severity=ExceptionSeverity.MEDIUM,
            reraise=True,
            default_return=None,
            log_level="error",
            handler_name="test_handler"
        )
    
    @pytest.fixture
    def no_reraise_handler(self):
        """
        예외를 재발생시키지 않는 ExceptionHandler 인스턴스 fixture
        
        Returns:
            ExceptionHandler: 재발생하지 않는 예외 처리기 인스턴스
        """
        return ExceptionHandler(
            exception_type=ExceptionType.SYSTEM_ERROR,
            severity=ExceptionSeverity.HIGH,
            reraise=False,
            default_return="default_value",
            log_level="warning"
        )
    
    @pytest.mark.unit
    def test_exception_handler_initialization(self, exception_handler):
        """
        ExceptionHandler 초기화 테스트
        
        Args:
            exception_handler: ExceptionHandler 인스턴스
        """
        assert isinstance(exception_handler, ExceptionHandler)
        assert exception_handler.exception_type == ExceptionType.UNKNOWN
        assert exception_handler.severity == ExceptionSeverity.MEDIUM
        assert exception_handler.reraise is True
        assert exception_handler.default_return is None
        assert exception_handler.log_level == "error"
        assert exception_handler.handler_name == "test_handler"
    
    @pytest.mark.unit
    def test_handle_exception_basic(self, exception_handler):
        """
        기본 예외 처리 메서드 테스트
        
        Args:
            exception_handler: ExceptionHandler 인스턴스
        """
        def test_func():
            """테스트 함수"""
            pass
        
        test_exception = ValueError("테스트 예외")
        
        # 예외 처리 실행
        context, processed_exception = exception_handler.handle_exception(
            test_func, test_exception
        )
        
        # 검증
        assert context.exception_type == ExceptionType.UNKNOWN
        assert context.severity == ExceptionSeverity.MEDIUM
        assert context.module == test_func.__module__
        assert context.function == test_func.__name__
        assert processed_exception == test_exception
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_handle_exception_async(self, exception_handler):
        """
        비동기 예외 처리 메서드 테스트
        
        Args:
            exception_handler: ExceptionHandler 인스턴스
        """
        async def test_async_func():
            """테스트 비동기 함수"""
            pass
        
        test_exception = ValueError("테스트 예외")
        
        # 비동기 예외 처리 실행
        custom_exception = await exception_handler.handle_exception_async(
            test_async_func, test_exception
        )
        
        # 검증
        assert custom_exception is not None
        # exception_manager가 처리한 예외인지 확인
        assert hasattr(custom_exception, 'original_exception')
        assert str(test_exception) in str(custom_exception)
    
    @pytest.mark.unit
    def test_decorator_with_successful_function(self, exception_handler):
        """
        성공하는 함수에 데코레이터 적용 테스트
        
        Args:
            exception_handler: ExceptionHandler 인스턴스
        """
        @exception_handler
        def successful_function():
            """성공하는 테스트 함수"""
            return "success"
        
        result = successful_function()
        assert result == "success"
    
    @pytest.mark.unit
    def test_decorator_with_exception_reraise(self, exception_handler):
        """
        예외 발생 시 재발생 테스트
        
        Args:
            exception_handler: ExceptionHandler 인스턴스
        """
        @exception_handler
        def failing_function():
            """실패하는 테스트 함수"""
            raise ValueError("테스트 예외")
        
        # 예외가 재발생되는지 확인
        with pytest.raises(Exception):
            failing_function()
    
    @pytest.mark.unit
    def test_decorator_with_exception_no_reraise(self, no_reraise_handler):
        """
        예외 발생 시 기본값 반환 테스트
        
        Args:
            no_reraise_handler: 재발생하지 않는 예외 처리기 인스턴스
        """
        @no_reraise_handler
        def failing_function():
            """실패하는 테스트 함수"""
            raise ValueError("테스트 예외")
        
        result = failing_function()
        assert result == "default_value"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_decorator_with_async_function(self, exception_handler):
        """
        비동기 함수에 데코레이터 적용 테스트
        
        Args:
            exception_handler: ExceptionHandler 인스턴스
        """
        @exception_handler
        async def async_successful_function():
            """성공하는 비동기 테스트 함수"""
            return "async_success"
        
        result = await async_successful_function()
        assert result == "async_success"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_decorator_with_async_exception(self, no_reraise_handler):
        """
        비동기 함수 예외 처리 테스트
        
        Args:
            no_reraise_handler: 재발생하지 않는 예외 처리기 인스턴스
        """
        @no_reraise_handler
        async def async_failing_function():
            """실패하는 비동기 테스트 함수"""
            raise ValueError("비동기 테스트 예외")
        
        result = await async_failing_function()
        assert result == "default_value"


class TestRetryOnException:
    """
    RetryOnException 클래스에 대한 테스트 모음
    
    재시도 로직의 정상 동작, 백오프 알고리즘, 예외 타입 필터링 등을
    체계적으로 테스트합니다.
    """
    
    @pytest.fixture
    def retry_handler(self):
        """
        재시도 핸들러 인스턴스를 제공하는 fixture
        
        Returns:
            RetryOnException: 재시도 핸들러 인스턴스
        """
        return RetryOnException(
            max_retries=3,
            retry_delay=0.1,
            backoff_factor=2.0,
            exception_types=[ConnectionError, TimeoutError],
            reraise_on_failure=True
        )
    
    @pytest.fixture
    def no_reraise_retry_handler(self):
        """
        재시도 실패 시 예외를 재발생시키지 않는 핸들러 fixture
        
        Returns:
            RetryOnException: 재발생하지 않는 재시도 핸들러 인스턴스
        """
        return RetryOnException(
            max_retries=2,
            retry_delay=0.05,
            backoff_factor=1.5,
            exception_types=[ConnectionError],
            reraise_on_failure=False
        )
    
    @pytest.mark.unit
    def test_retry_handler_initialization(self, retry_handler):
        """
        RetryOnException 초기화 테스트
        
        Args:
            retry_handler: RetryOnException 인스턴스
        """
        assert isinstance(retry_handler, RetryOnException)
        assert retry_handler.max_retries == 3
        assert retry_handler.retry_delay == 0.1
        assert retry_handler.backoff_factor == 2.0
        assert retry_handler.exception_types == [ConnectionError, TimeoutError]
        assert retry_handler.reraise_on_failure is True
    
    @pytest.mark.unit
    def test_retry_handler_inheritance(self, retry_handler):
        """
        ExceptionHandler 상속 테스트
        
        Args:
            retry_handler: RetryOnException 인스턴스
        """
        assert isinstance(retry_handler, ExceptionHandler)
        assert retry_handler.exception_type == ExceptionType.EXTERNAL_SERVICE_ERROR
        assert retry_handler.severity == ExceptionSeverity.MEDIUM
    
    @pytest.mark.unit
    def test_successful_function_no_retry(self, retry_handler):
        """
        성공하는 함수는 재시도하지 않음 테스트
        
        Args:
            retry_handler: RetryOnException 인스턴스
        """
        call_count = 0
        
        @retry_handler
        def successful_function():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = successful_function()
        
        assert result == "success"
        assert call_count == 1
    
    @pytest.mark.unit
    def test_retry_on_target_exception(self, retry_handler):
        """
        대상 예외 발생 시 재시도 테스트
        
        Args:
            retry_handler: RetryOnException 인스턴스
        """
        call_count = 0
        
        @retry_handler
        def failing_then_success_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("연결 실패")
            return "success"
        
        result = failing_then_success_function()
        
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.unit
    def test_retry_failure_reraise(self, retry_handler):
        """
        재시도 실패 시 예외 재발생 테스트
        
        Args:
            retry_handler: RetryOnException 인스턴스
        """
        call_count = 0
        
        @retry_handler
        def always_failing_function():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("연결 실패")
        
        with pytest.raises(Exception):
            always_failing_function()
        
        assert call_count == 4  # 초기 시도 + 3번 재시도
    
    @pytest.mark.unit
    def test_retry_failure_no_reraise(self, no_reraise_retry_handler):
        """
        재시도 실패 시 기본값 반환 테스트
        
        Args:
            no_reraise_retry_handler: 재발생하지 않는 재시도 핸들러 인스턴스
        """
        call_count = 0
        
        @no_reraise_retry_handler
        def always_failing_function():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("연결 실패")
        
        result = always_failing_function()
        
        assert result == no_reraise_retry_handler.default_return
        assert call_count == 3  # 초기 시도 + 2번 재시도
    
    @pytest.mark.unit
    def test_non_target_exception_no_retry(self, retry_handler):
        """
        대상이 아닌 예외 발생 시 재시도하지 않음 테스트
        
        Args:
            retry_handler: RetryOnException 인스턴스
        """
        call_count = 0
        
        @retry_handler
        def non_target_exception_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("값 오류")
        
        with pytest.raises(ValueError):
            non_target_exception_function()
        
        assert call_count == 1  # 재시도하지 않음
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_async_retry_success(self, retry_handler):
        """
        비동기 함수 재시도 성공 테스트
        
        Args:
            retry_handler: RetryOnException 인스턴스
        """
        call_count = 0
        
        @retry_handler
        async def async_failing_then_success():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("연결 실패")
            return "async_success"
        
        result = await async_failing_then_success()
        
        assert result == "async_success"
        assert call_count == 2


class TestDatabaseExceptionHandler:
    """
    DatabaseExceptionHandler 클래스에 대한 테스트 모음
    
    데이터베이스 관련 예외 처리, 성능 추적, 쿼리 로깅 등을
    체계적으로 테스트합니다.
    """
    
    @pytest.fixture
    def db_handler(self):
        """
        데이터베이스 예외 핸들러 인스턴스를 제공하는 fixture
        
        Returns:
            DatabaseExceptionHandler: 데이터베이스 예외 처리기 인스턴스
        """
        return DatabaseExceptionHandler(
            reraise=True,
            default_return=[],
            log_queries=True,
            track_performance=True
        )
    
    @pytest.fixture
    def no_reraise_db_handler(self):
        """
        예외를 재발생시키지 않는 데이터베이스 핸들러 fixture
        
        Returns:
            DatabaseExceptionHandler: 재발생하지 않는 데이터베이스 예외 처리기 인스턴스
        """
        return DatabaseExceptionHandler(
            reraise=False,
            default_return=[],
            log_queries=False,
            track_performance=False
        )
    
    @pytest.mark.unit
    def test_db_handler_initialization(self, db_handler):
        """
        DatabaseExceptionHandler 초기화 테스트
        
        Args:
            db_handler: DatabaseExceptionHandler 인스턴스
        """
        assert isinstance(db_handler, DatabaseExceptionHandler)
        assert isinstance(db_handler, ExceptionHandler)
        assert db_handler.reraise is True
        assert db_handler.default_return == []
        assert db_handler.log_queries is True
        assert db_handler.track_performance is True
        assert db_handler.exception_type == ExceptionType.DATABASE_ERROR
        assert db_handler.severity == ExceptionSeverity.HIGH
    
    @pytest.mark.unit
    def test_handle_database_exception(self, db_handler):
        """
        데이터베이스 예외 처리 로직 테스트
        
        Args:
            db_handler: DatabaseExceptionHandler 인스턴스
        """
        def test_db_function():
            """테스트 데이터베이스 함수"""
            pass
        
        original_exception = Exception("데이터베이스 오류")
        
        # 예외 처리 실행
        context, db_exception = db_handler.handle_exception(
            test_db_function, original_exception
        )
        
        # 검증
        assert isinstance(db_exception, DatabaseException)
        assert "데이터베이스 작업 실패" in db_exception.message
        assert db_exception.original_exception == original_exception
        assert context.exception_type == ExceptionType.DATABASE_ERROR
        assert context.severity == ExceptionSeverity.HIGH
    
    @pytest.mark.unit
    def test_successful_db_operation(self, db_handler):
        """
        성공하는 데이터베이스 작업 테스트
        
        Args:
            db_handler: DatabaseExceptionHandler 인스턴스
        """
        @db_handler
        def successful_db_query():
            """성공하는 데이터베이스 쿼리"""
            return [{"id": 1, "name": "test"}]
        
        result = successful_db_query()
        
        assert result == [{"id": 1, "name": "test"}]
    
    @pytest.mark.unit
    def test_db_exception_reraise(self, db_handler):
        """
        데이터베이스 예외 재발생 테스트
        
        Args:
            db_handler: DatabaseExceptionHandler 인스턴스
        """
        @db_handler
        def failing_db_query():
            """실패하는 데이터베이스 쿼리"""
            raise Exception("데이터베이스 연결 실패")
        
        with pytest.raises(DatabaseException):
            failing_db_query()
    
    @pytest.mark.unit
    def test_db_exception_no_reraise(self, no_reraise_db_handler):
        """
        데이터베이스 예외 발생 시 기본값 반환 테스트
        
        Args:
            no_reraise_db_handler: 재발생하지 않는 데이터베이스 예외 처리기 인스턴스
        """
        @no_reraise_db_handler
        def failing_db_query():
            """실패하는 데이터베이스 쿼리"""
            raise Exception("데이터베이스 연결 실패")
        
        result = failing_db_query()
        
        assert result == []
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_async_db_operation(self, db_handler):
        """
        비동기 데이터베이스 작업 테스트
        
        Args:
            db_handler: DatabaseExceptionHandler 인스턴스
        """
        @db_handler
        async def async_db_query():
            """비동기 데이터베이스 쿼리"""
            return [{"id": 1, "name": "async_test"}]
        
        result = await async_db_query()
        
        assert result == [{"id": 1, "name": "async_test"}]
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_async_db_exception(self, no_reraise_db_handler):
        """
        비동기 데이터베이스 예외 처리 테스트
        
        Args:
            no_reraise_db_handler: 재발생하지 않는 데이터베이스 예외 처리기 인스턴스
        """
        @no_reraise_db_handler
        async def async_failing_db_query():
            """실패하는 비동기 데이터베이스 쿼리"""
            raise Exception("비동기 데이터베이스 연결 실패")
        
        result = await async_failing_db_query()
        
        assert result == []


class TestValidationExceptionHandler:
    """
    ValidationExceptionHandler 클래스에 대한 테스트 모음
    
    유효성 검증 예외 처리, 오류 수집, 검증 로직 등을
    체계적으로 테스트합니다.
    """
    
    @pytest.fixture
    def validation_handler(self):
        """
        유효성 검증 핸들러 인스턴스를 제공하는 fixture
        
        Returns:
            ValidationExceptionHandler: 유효성 검증 예외 처리기 인스턴스
        """
        return ValidationExceptionHandler(
            reraise=True,
            default_return=False,
            collect_errors=True
        )
    
    @pytest.fixture
    def no_collect_validation_handler(self):
        """
        오류 수집하지 않는 유효성 검증 핸들러 fixture
        
        Returns:
            ValidationExceptionHandler: 오류 수집하지 않는 유효성 검증 예외 처리기 인스턴스
        """
        return ValidationExceptionHandler(
            reraise=False,
            default_return=False,
            collect_errors=False
        )
    
    @pytest.mark.unit
    def test_validation_handler_initialization(self, validation_handler):
        """
        ValidationExceptionHandler 초기화 테스트
        
        Args:
            validation_handler: ValidationExceptionHandler 인스턴스
        """
        assert isinstance(validation_handler, ValidationExceptionHandler)
        assert isinstance(validation_handler, ExceptionHandler)
        assert validation_handler.reraise is True
        assert validation_handler.default_return is False
        assert validation_handler.collect_errors is True
        assert validation_handler.exception_type == ExceptionType.VALIDATION_ERROR
        assert validation_handler.severity == ExceptionSeverity.MEDIUM
        assert validation_handler.validation_errors == []
    
    @pytest.mark.unit
    def test_handle_validation_exception(self, validation_handler):
        """
        유효성 검증 예외 처리 로직 테스트
        
        Args:
            validation_handler: ValidationExceptionHandler 인스턴스
        """
        def test_validation_function():
            """테스트 유효성 검증 함수"""
            pass
        
        original_exception = ValueError("유효하지 않은 값")
        
        # 예외 처리 실행
        context, validation_exception = validation_handler.handle_exception(
            test_validation_function, original_exception, "test_arg", test_kwarg="test_value"
        )
        
        # 검증
        assert isinstance(validation_exception, ValidationException)
        assert "유효성 검증 실패" in validation_exception.message
        assert validation_exception.original_exception == original_exception
        assert context.exception_type == ExceptionType.VALIDATION_ERROR
        assert context.severity == ExceptionSeverity.MEDIUM
        
        # 오류 수집 확인
        assert len(validation_handler.validation_errors) == 1
        error_info = validation_handler.validation_errors[0]
        assert error_info['function'] == "test_validation_function"
        assert error_info['error'] == str(original_exception)
        assert error_info['args'] == ("test_arg",)
        assert error_info['kwargs'] == {"test_kwarg": "test_value"}
        assert 'timestamp' in error_info
    
    @pytest.mark.unit
    def test_successful_validation(self, validation_handler):
        """
        성공하는 유효성 검증 테스트
        
        Args:
            validation_handler: ValidationExceptionHandler 인스턴스
        """
        @validation_handler
        def successful_validation():
            """성공하는 유효성 검증"""
            return True
        
        result = successful_validation()
        
        assert result is True
        assert len(validation_handler.validation_errors) == 0
    
    @pytest.mark.unit
    def test_validation_exception_reraise(self, validation_handler):
        """
        유효성 검증 예외 재발생 테스트
        
        Args:
            validation_handler: ValidationExceptionHandler 인스턴스
        """
        @validation_handler
        def failing_validation():
            """실패하는 유효성 검증"""
            raise ValueError("유효하지 않은 데이터")
        
        with pytest.raises(ValidationException):
            failing_validation()
        
        assert len(validation_handler.validation_errors) == 1
    
    @pytest.mark.unit
    def test_validation_exception_no_reraise(self, no_collect_validation_handler):
        """
        유효성 검증 예외 발생 시 기본값 반환 테스트
        
        Args:
            no_collect_validation_handler: 오류 수집하지 않는 유효성 검증 예외 처리기 인스턴스
        """
        @no_collect_validation_handler
        def failing_validation():
            """실패하는 유효성 검증"""
            raise ValueError("유효하지 않은 데이터")
        
        result = failing_validation()
        
        assert result is False
        assert len(no_collect_validation_handler.validation_errors) == 0
    
    @pytest.mark.unit
    def test_validation_error_collection(self, validation_handler):
        """
        유효성 검증 오류 수집 테스트
        
        Args:
            validation_handler: ValidationExceptionHandler 인스턴스
        """
        @validation_handler
        def multiple_validation_calls():
            """여러 번 호출되는 유효성 검증"""
            raise ValueError("유효성 검증 실패")
        
        # 여러 번 호출
        for i in range(3):
            try:
                multiple_validation_calls()
            except ValidationException:
                pass
        
        # 오류 수집 확인
        assert len(validation_handler.validation_errors) == 3
        for error_info in validation_handler.validation_errors:
            assert error_info['function'] == "multiple_validation_calls"
            assert error_info['error'] == "유효성 검증 실패"


class TestCircuitBreaker:
    """
    CircuitBreaker 클래스에 대한 테스트 모음
    
    서킷 브레이커 패턴의 상태 변화, 임계값 관리, 복구 로직 등을
    체계적으로 테스트합니다.
    """
    
    @pytest.fixture
    def circuit_breaker(self):
        """
        서킷 브레이커 인스턴스를 제공하는 fixture
        
        Returns:
            CircuitBreaker: 서킷 브레이커 인스턴스
        """
        return CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=1,
            expected_exception=ConnectionError,
            monitor_performance=True
        )
    
    @pytest.fixture
    def fast_recovery_circuit_breaker(self):
        """
        빠른 복구 서킷 브레이커 fixture
        
        Returns:
            CircuitBreaker: 빠른 복구 서킷 브레이커 인스턴스
        """
        return CircuitBreaker(
            failure_threshold=1,
            recovery_timeout=0.1,
            expected_exception=ConnectionError,
            monitor_performance=False
        )
    
    @pytest.mark.unit
    def test_circuit_breaker_initialization(self, circuit_breaker):
        """
        CircuitBreaker 초기화 테스트
        
        Args:
            circuit_breaker: CircuitBreaker 인스턴스
        """
        assert isinstance(circuit_breaker, CircuitBreaker)
        assert isinstance(circuit_breaker, ExceptionHandler)
        assert circuit_breaker.failure_threshold == 2
        assert circuit_breaker.recovery_timeout == 1
        assert circuit_breaker.expected_exception == ConnectionError
        assert circuit_breaker.monitor_performance is True
        assert circuit_breaker.state == 'CLOSED'
        assert circuit_breaker.failure_count == 0
        assert circuit_breaker.success_count == 0
    
    @pytest.mark.unit
    def test_circuit_breaker_closed_state_success(self, circuit_breaker):
        """
        CLOSED 상태에서 성공 동작 테스트
        
        Args:
            circuit_breaker: CircuitBreaker 인스턴스
        """
        @circuit_breaker
        def successful_service():
            """성공하는 서비스"""
            return "success"
        
        result = successful_service()
        
        assert result == "success"
        assert circuit_breaker.state == 'CLOSED'
        assert circuit_breaker.failure_count == 0
        assert circuit_breaker.success_count == 1
    
    @pytest.mark.unit
    def test_circuit_breaker_open_state_transition(self, circuit_breaker):
        """
        CLOSED에서 OPEN 상태 전환 테스트
        
        Args:
            circuit_breaker: CircuitBreaker 인스턴스
        """
        @circuit_breaker
        def failing_service():
            """실패하는 서비스"""
            raise ConnectionError("서비스 연결 실패")
        
        # 실패 임계값까지 호출
        for i in range(circuit_breaker.failure_threshold):
            with pytest.raises(Exception):
                failing_service()
        
        # OPEN 상태로 전환 확인
        assert circuit_breaker.state == 'OPEN'
        assert circuit_breaker.failure_count == circuit_breaker.failure_threshold
        
        # OPEN 상태에서 추가 호출 시 즉시 차단
        with pytest.raises(ExternalServiceException) as exc_info:
            failing_service()
        
        assert "서킷 브레이커 OPEN 상태" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_circuit_breaker_half_open_transition(self, fast_recovery_circuit_breaker):
        """
        OPEN에서 HALF_OPEN 상태 전환 테스트
        
        Args:
            fast_recovery_circuit_breaker: 빠른 복구 서킷 브레이커 인스턴스
        """
        @fast_recovery_circuit_breaker
        def failing_then_success_service():
            """처음 실패 후 성공하는 서비스"""
            if fast_recovery_circuit_breaker.state == 'CLOSED':
                raise ConnectionError("서비스 연결 실패")
            return "success"
        
        # OPEN 상태로 전환
        with pytest.raises(Exception):
            failing_then_success_service()
        
        assert fast_recovery_circuit_breaker.state == 'OPEN'
        
        # 복구 시간 대기
        import time
        time.sleep(0.2)
        
        # HALF_OPEN 상태에서 성공하면 CLOSED로 전환
        result = failing_then_success_service()
        
        assert result == "success"
        assert fast_recovery_circuit_breaker.state == 'CLOSED'
        assert fast_recovery_circuit_breaker.failure_count == 0
    
    @pytest.mark.unit
    def test_circuit_breaker_non_target_exception(self, circuit_breaker):
        """
        대상이 아닌 예외 발생 시 서킷 브레이커 동작 테스트
        
        Args:
            circuit_breaker: CircuitBreaker 인스턴스
        """
        @circuit_breaker
        def non_target_exception_service():
            """대상이 아닌 예외를 발생시키는 서비스"""
            raise ValueError("값 오류")
        
        # 대상이 아닌 예외는 서킷 브레이커 상태에 영향을 주지 않음
        with pytest.raises(ValueError):
            non_target_exception_service()
        
        assert circuit_breaker.state == 'CLOSED'
        assert circuit_breaker.failure_count == 0
    
    @pytest.mark.unit
    def test_circuit_breaker_reset(self, circuit_breaker):
        """
        서킷 브레이커 리셋 테스트
        
        Args:
            circuit_breaker: CircuitBreaker 인스턴스
        """
        # 실패 상태로 만들기
        circuit_breaker.failure_count = 5
        circuit_breaker.success_count = 10
        circuit_breaker.state = 'OPEN'
        circuit_breaker.last_failure_time = datetime.now()
        
        # 리셋 실행
        circuit_breaker.reset()
        
        # 리셋 확인
        assert circuit_breaker.state == 'CLOSED'
        assert circuit_breaker.failure_count == 0
        assert circuit_breaker.success_count == 0
        assert circuit_breaker.last_failure_time is None


class TestSuppressExceptions:
    """
    SuppressExceptions 클래스에 대한 테스트 모음
    
    예외 억제 기능, 예외 타입 필터링, 억제 통계 수집 등을
    체계적으로 테스트합니다.
    """
    
    @pytest.fixture
    def suppress_handler(self):
        """
        예외 억제 핸들러 인스턴스를 제공하는 fixture
        
        Returns:
            SuppressExceptions: 예외 억제 핸들러 인스턴스
        """
        return SuppressExceptions(
            exception_types=[FileNotFoundError, PermissionError],
            default_return=None,
            log_suppressed=True,
            track_suppressed=True
        )
    
    @pytest.fixture
    def suppress_all_handler(self):
        """
        모든 예외를 억제하는 핸들러 fixture
        
        Returns:
            SuppressExceptions: 모든 예외를 억제하는 핸들러 인스턴스
        """
        return SuppressExceptions(
            exception_types=None,  # 모든 예외 억제
            default_return="suppressed",
            log_suppressed=False,
            track_suppressed=False
        )
    
    @pytest.mark.unit
    def test_suppress_handler_initialization(self, suppress_handler):
        """
        SuppressExceptions 초기화 테스트
        
        Args:
            suppress_handler: SuppressExceptions 인스턴스
        """
        assert isinstance(suppress_handler, SuppressExceptions)
        assert isinstance(suppress_handler, ExceptionHandler)
        assert suppress_handler.exception_types == [FileNotFoundError, PermissionError]
        assert suppress_handler.default_return is None
        assert suppress_handler.log_suppressed is True
        assert suppress_handler.track_suppressed is True
        assert suppress_handler.exception_type == ExceptionType.SUPPRESSED
        assert suppress_handler.severity == ExceptionSeverity.LOW
        assert suppress_handler.suppressed_exceptions == []
    
    @pytest.mark.unit
    def test_successful_function_no_suppression(self, suppress_handler):
        """
        성공하는 함수는 억제하지 않음 테스트
        
        Args:
            suppress_handler: SuppressExceptions 인스턴스
        """
        @suppress_handler
        def successful_function():
            """성공하는 함수"""
            return "success"
        
        result = successful_function()
        
        assert result == "success"
        assert len(suppress_handler.suppressed_exceptions) == 0
    
    @pytest.mark.unit
    def test_suppress_target_exception(self, suppress_handler):
        """
        대상 예외 억제 테스트
        
        Args:
            suppress_handler: SuppressExceptions 인스턴스
        """
        @suppress_handler
        def file_operation():
            """파일 작업 함수"""
            raise FileNotFoundError("파일을 찾을 수 없습니다")
        
        result = file_operation()
        
        assert result is None  # default_return 값
        assert len(suppress_handler.suppressed_exceptions) == 1
        
        # 억제된 예외 정보 확인
        suppressed_info = suppress_handler.suppressed_exceptions[0]
        assert suppressed_info['exception_type'] == 'FileNotFoundError'
        assert suppressed_info['message'] == '파일을 찾을 수 없습니다'
        assert suppressed_info['function'] == 'file_operation'
        assert 'timestamp' in suppressed_info
    
    @pytest.mark.unit
    def test_suppress_multiple_target_exceptions(self, suppress_handler):
        """
        여러 대상 예외 억제 테스트
        
        Args:
            suppress_handler: SuppressExceptions 인스턴스
        """
        @suppress_handler
        def permission_operation():
            """권한 관련 작업 함수"""
            raise PermissionError("권한이 없습니다")
        
        result = permission_operation()
        
        assert result is None
        assert len(suppress_handler.suppressed_exceptions) == 1
        
        suppressed_info = suppress_handler.suppressed_exceptions[0]
        assert suppressed_info['exception_type'] == 'PermissionError'
        assert suppressed_info['message'] == '권한이 없습니다'
    
    @pytest.mark.unit
    def test_non_target_exception_not_suppressed(self, suppress_handler):
        """
        대상이 아닌 예외는 억제하지 않음 테스트
        
        Args:
            suppress_handler: SuppressExceptions 인스턴스
        """
        @suppress_handler
        def value_error_function():
            """값 오류 함수"""
            raise ValueError("값 오류")
        
        with pytest.raises(ValueError):
            value_error_function()
        
        assert len(suppress_handler.suppressed_exceptions) == 0
    
    @pytest.mark.unit
    def test_suppress_all_exceptions(self, suppress_all_handler):
        """
        모든 예외 억제 테스트
        
        Args:
            suppress_all_handler: 모든 예외를 억제하는 핸들러 인스턴스
        """
        @suppress_all_handler
        def any_exception_function():
            """임의 예외 함수"""
            raise ValueError("임의 예외")
        
        result = any_exception_function()
        
        assert result == "suppressed"
        assert len(suppress_all_handler.suppressed_exceptions) == 0  # track_suppressed=False
    
    @pytest.mark.unit
    def test_suppress_exception_tracking(self, suppress_handler):
        """
        억제된 예외 추적 테스트
        
        Args:
            suppress_handler: SuppressExceptions 인스턴스
        """
        @suppress_handler
        def multiple_exceptions():
            """여러 예외를 발생시키는 함수"""
            raise FileNotFoundError("파일 없음")
        
        # 여러 번 호출
        for i in range(3):
            multiple_exceptions()
        
        # 억제된 예외 추적 확인
        assert len(suppress_handler.suppressed_exceptions) == 3
        
        for suppressed_info in suppress_handler.suppressed_exceptions:
            assert suppressed_info['exception_type'] == 'FileNotFoundError'
            assert suppressed_info['message'] == '파일 없음'
            assert suppressed_info['function'] == 'multiple_exceptions'


class TestConvenienceFunctions:
    """
    편의 함수들에 대한 테스트 모음
    
    create_* 함수들의 정상 동작을 검증합니다.
    """
    
    @pytest.mark.unit
    def test_create_exception_handler(self):
        """
        create_exception_handler 함수 테스트
        """
        handler = create_exception_handler(
            exception_type=ExceptionType.SYSTEM_ERROR,
            severity=ExceptionSeverity.HIGH,
            reraise=False
        )
        
        assert isinstance(handler, ExceptionHandler)
        assert handler.exception_type == ExceptionType.SYSTEM_ERROR
        assert handler.severity == ExceptionSeverity.HIGH
        assert handler.reraise is False
    
    @pytest.mark.unit
    def test_create_retry_handler(self):
        """
        create_retry_handler 함수 테스트
        """
        handler = create_retry_handler(
            max_retries=5,
            retry_delay=0.2,
            backoff_factor=1.5
        )
        
        assert isinstance(handler, RetryOnException)
        assert handler.max_retries == 5
        assert handler.retry_delay == 0.2
        assert handler.backoff_factor == 1.5
    
    @pytest.mark.unit
    def test_create_database_handler(self):
        """
        create_database_handler 함수 테스트
        """
        handler = create_database_handler(
            reraise=False,
            default_return=[],
            log_queries=True
        )
        
        assert isinstance(handler, DatabaseExceptionHandler)
        assert handler.reraise is False
        assert handler.default_return == []
        assert handler.log_queries is True
    
    @pytest.mark.unit
    def test_create_validation_handler(self):
        """
        create_validation_handler 함수 테스트
        """
        handler = create_validation_handler(
            collect_errors=True,
            reraise=True
        )
        
        assert isinstance(handler, ValidationExceptionHandler)
        assert handler.collect_errors is True
        assert handler.reraise is True
    
    @pytest.mark.unit
    def test_create_circuit_breaker(self):
        """
        create_circuit_breaker 함수 테스트
        """
        handler = create_circuit_breaker(
            failure_threshold=3,
            recovery_timeout=30,
            expected_exception=ConnectionError
        )
        
        assert isinstance(handler, CircuitBreaker)
        assert handler.failure_threshold == 3
        assert handler.recovery_timeout == 30
        assert handler.expected_exception == ConnectionError
    
    @pytest.mark.unit
    def test_create_suppression_handler(self):
        """
        create_suppression_handler 함수 테스트
        """
        handler = create_suppression_handler(
            exception_types=[FileNotFoundError],
            default_return="suppressed",
            log_suppressed=True
        )
        
        assert isinstance(handler, SuppressExceptions)
        assert handler.exception_types == [FileNotFoundError]
        assert handler.default_return == "suppressed"
        assert handler.log_suppressed is True


class TestIntegrationScenarios:
    """
    통합 시나리오 테스트
    
    실제 사용 시나리오를 모방한 복합적인 테스트를 수행합니다.
    """
    
    @pytest.fixture
    def service_with_decorators(self):
        """
        데코레이터가 적용된 서비스 클래스 fixture
        
        Returns:
            객체: 데코레이터가 적용된 서비스 인스턴스
        """
        class TestService:
            def __init__(self):
                self.db_handler = DatabaseExceptionHandler(reraise=True, default_return=[])
                self.retry_handler = RetryOnException(max_retries=2, retry_delay=0.05)
                self.validation_handler = ValidationExceptionHandler(collect_errors=True)
                self.circuit_breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
                self.suppress_handler = SuppressExceptions(exception_types=[FileNotFoundError])
        
        return TestService()
    
    @pytest.mark.integration
    def test_database_with_retry_combination(self, service_with_decorators):
        """
        데이터베이스 핸들러와 재시도 핸들러 조합 테스트
        
        Args:
            service_with_decorators: 데코레이터가 적용된 서비스 인스턴스
        """
        call_count = 0
        
        def create_combined_function():
            @service_with_decorators.retry_handler
            @service_with_decorators.db_handler
            def db_operation_with_retry():
                nonlocal call_count
                call_count += 1
                if call_count < 3:
                    raise ConnectionError("데이터베이스 연결 실패")
                return [{"id": 1, "name": "test"}]
            
            return db_operation_with_retry
        
        combined_func = create_combined_function()
        result = combined_func()
        
        assert result == [{"id": 1, "name": "test"}]
        assert call_count == 3
    
    @pytest.mark.integration
    def test_validation_with_circuit_breaker_combination(self, service_with_decorators):
        """
        유효성 검증과 서킷 브레이커 조합 테스트
        
        Args:
            service_with_decorators: 데코레이터가 적용된 서비스 인스턴스
        """
        def create_combined_function():
            @service_with_decorators.circuit_breaker
            @service_with_decorators.validation_handler
            def validation_with_circuit_breaker():
                raise ConnectionError("외부 서비스 연결 실패")
            
            return validation_with_circuit_breaker
        
        combined_func = create_combined_function()
        
        # 서킷 브레이커 임계값까지 호출
        for i in range(service_with_decorators.circuit_breaker.failure_threshold):
            with pytest.raises(Exception):
                combined_func()
        
        # 서킷 브레이커 OPEN 상태 확인
        assert service_with_decorators.circuit_breaker.state == 'OPEN'
        
        # 추가 호출 시 서킷 브레이커에 의해 차단
        with pytest.raises(ExternalServiceException):
            combined_func()
    
    @pytest.mark.integration
    @pytest.mark.parametrize("exception_type,should_suppress", [
        (FileNotFoundError("파일 없음"), True),
        (PermissionError("권한 없음"), False),
        (ValueError("값 오류"), False),
    ])
    def test_suppression_with_various_exceptions(self, service_with_decorators, exception_type, should_suppress):
        """
        다양한 예외에 대한 억제 테스트
        
        Args:
            service_with_decorators: 데코레이터가 적용된 서비스 인스턴스
            exception_type: 테스트할 예외 타입
            should_suppress: 억제 여부
        """
        @service_with_decorators.suppress_handler
        def test_function():
            """테스트 함수"""
            raise exception_type
        
        if should_suppress:
            result = test_function()
            assert result is None
            assert len(service_with_decorators.suppress_handler.suppressed_exceptions) > 0
        else:
            with pytest.raises(type(exception_type)):
                test_function()
            
            # FileNotFoundError가 아닌 경우 suppressed_exceptions는 그대로
            if not isinstance(exception_type, FileNotFoundError):
                assert len(service_with_decorators.suppress_handler.suppressed_exceptions) == 0
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_performance_monitoring_integration(self, service_with_decorators):
        """
        성능 모니터링 통합 테스트
        
        Args:
            service_with_decorators: 데코레이터가 적용된 서비스 인스턴스
        """
        @service_with_decorators.db_handler
        def slow_database_operation():
            """느린 데이터베이스 작업"""
            import time
            time.sleep(0.1)
            return [{"id": 1, "data": "test"}]
        
        # 성능 추적이 활성화된 데이터베이스 핸들러 사용
        result = slow_database_operation()
        
        assert result == [{"id": 1, "data": "test"}]
        # 성능 모니터링 로그가 기록되었는지 확인 (실제 로그 시스템이 있다면) 