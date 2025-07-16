"""
예외 처리 시스템 테스트를 위한 공통 설정 및 fixture

이 모듈은 예외 처리 시스템의 모든 테스트에서 사용되는 공통 설정과
fixture들을 정의합니다.
"""

import pytest
import logging
import os
import asyncio
from unittest.mock import Mock, MagicMock
from typing import Dict, Any, List

# 테스트 환경 설정
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    테스트 환경 자동 설정 fixture
    
    모든 테스트 실행 전에 자동으로 실행되어 환경을 설정합니다.
    """
    # 테스트 환경변수 설정
    os.environ["TESTING"] = "true"
    os.environ["LOG_LEVEL"] = "DEBUG"
    
    # 로깅 레벨 설정
    logging.basicConfig(level=logging.DEBUG)
    
    # 예외 처리 시스템 초기화
    try:
        from src.common.exception import initialize_exception_system
        initialize_exception_system(log_level="DEBUG", register_defaults=True)
    except ImportError:
        pass  # 예외 시스템이 없는 경우 무시
    
    yield
    
    # 정리 작업
    if "TESTING" in os.environ:
        del os.environ["TESTING"]
    if "LOG_LEVEL" in os.environ:
        del os.environ["LOG_LEVEL"]


@pytest.fixture(scope="session")
def test_config():
    """
    테스트 세션 전체에서 사용할 설정을 제공하는 fixture
    
    Returns:
        dict: 테스트 설정 정보
    """
    return {
        "test_db_url": "sqlite:///:memory:",
        "api_base_url": "https://api.test.com",
        "timeout": 30,
        "retry_count": 3,
        "log_level": "DEBUG",
        "mock_external_services": True
    }


@pytest.fixture
def mock_logger():
    """
    로깅 Mock 객체를 제공하는 fixture
    
    Returns:
        Mock: 로거 Mock 객체
    """
    logger_mock = Mock()
    logger_mock.info = Mock()
    logger_mock.error = Mock()
    logger_mock.warning = Mock()
    logger_mock.debug = Mock()
    logger_mock.critical = Mock()
    return logger_mock


@pytest.fixture
def mock_exception_manager():
    """
    예외 관리자 Mock 객체를 제공하는 fixture
    
    Returns:
        Mock: 예외 관리자 Mock 객체
    """
    exception_manager_mock = Mock()
    
    # handle_exception 메서드가 원본 예외를 반환하도록 설정
    async def mock_handle_exception(exception, context=None, handler_name=None):
        return exception
    
    exception_manager_mock.handle_exception = Mock(side_effect=mock_handle_exception)
    return exception_manager_mock


@pytest.fixture
def sample_user_data():
    """
    사용자 데이터 샘플을 제공하는 fixture
    
    Returns:
        dict: 사용자 데이터
    """
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "name": "테스트 사용자",
        "age": 30,
        "created_at": "2024-01-01T00:00:00Z",
        "is_active": True,
        "permissions": ["read", "write"]
    }


@pytest.fixture
def sample_database_data():
    """
    데이터베이스 테스트용 샘플 데이터를 제공하는 fixture
    
    Returns:
        list: 데이터베이스 레코드 리스트
    """
    return [
        {"id": 1, "name": "Record 1", "value": 100},
        {"id": 2, "name": "Record 2", "value": 200},
        {"id": 3, "name": "Record 3", "value": 300}
    ]


@pytest.fixture
def sample_validation_data():
    """
    유효성 검증용 샘플 데이터를 제공하는 fixture
    
    Returns:
        dict: 유효성 검증 테스트 데이터
    """
    return {
        "valid_data": {
            "name": "유효한 이름",
            "email": "valid@example.com",
            "age": 25,
            "phone": "010-1234-5678"
        },
        "invalid_data": {
            "name": "",  # 빈 이름
            "email": "invalid-email",  # 잘못된 이메일 형식
            "age": -5,  # 음수 나이
            "phone": "123"  # 잘못된 전화번호 형식
        }
    }


@pytest.fixture
def mock_external_service():
    """
    외부 서비스 Mock 객체를 제공하는 fixture
    
    Returns:
        Mock: 외부 서비스 Mock 객체
    """
    service_mock = Mock()
    
    # 성공 응답
    service_mock.call_api.return_value = {
        "status": "success",
        "data": {"result": "mocked_data"},
        "timestamp": "2024-01-01T00:00:00Z"
    }
    
    # 비동기 메서드
    async def mock_async_call():
        return {
            "status": "success",
            "data": {"result": "async_mocked_data"}
        }
    
    service_mock.async_call = Mock(side_effect=mock_async_call)
    
    return service_mock


@pytest.fixture
def mock_database_connection():
    """
    데이터베이스 연결 Mock 객체를 제공하는 fixture
    
    Returns:
        Mock: 데이터베이스 연결 Mock 객체
    """
    db_mock = Mock()
    
    # 쿼리 메서드들
    db_mock.execute.return_value = {"rows_affected": 1}
    db_mock.fetchall.return_value = [{"id": 1, "name": "test"}]
    db_mock.fetchone.return_value = {"id": 1, "name": "test"}
    
    # 트랜잭션 메서드들
    db_mock.begin_transaction = Mock()
    db_mock.commit = Mock()
    db_mock.rollback = Mock()
    
    return db_mock


@pytest.fixture
def event_loop():
    """
    테스트용 이벤트 루프를 제공하는 fixture
    
    Returns:
        asyncio.AbstractEventLoop: 테스트용 이벤트 루프
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def failure_simulator():
    """
    실패 시뮬레이터 클래스를 제공하는 fixture
    
    Returns:
        class: 실패 시뮬레이터 클래스
    """
    class FailureSimulator:
        def __init__(self):
            self.call_count = 0
            self.failure_rate = 0.5
            self.max_failures = 3
        
        def simulate_failure(self, exception_type=Exception, message="시뮬레이션된 실패"):
            """실패를 시뮬레이션하는 메서드"""
            self.call_count += 1
            if self.call_count <= self.max_failures:
                raise exception_type(message)
            return f"성공 (시도 {self.call_count}회)"
        
        def reset(self):
            """시뮬레이터 상태 리셋"""
            self.call_count = 0
        
        def set_failure_rate(self, rate: float):
            """실패율 설정"""
            self.failure_rate = rate
        
        def set_max_failures(self, max_failures: int):
            """최대 실패 횟수 설정"""
            self.max_failures = max_failures
    
    return FailureSimulator


@pytest.fixture
def performance_monitor():
    """
    성능 모니터링 도구를 제공하는 fixture
    
    Returns:
        class: 성능 모니터링 클래스
    """
    import time
    from typing import Dict, List
    
    class PerformanceMonitor:
        def __init__(self):
            self.records: List[Dict[str, Any]] = []
        
        def start_timer(self, operation_name: str):
            """타이머 시작"""
            return {
                "operation": operation_name,
                "start_time": time.time()
            }
        
        def end_timer(self, timer_info: Dict[str, Any]):
            """타이머 종료 및 기록"""
            end_time = time.time()
            duration = end_time - timer_info["start_time"]
            
            record = {
                "operation": timer_info["operation"],
                "duration": duration,
                "start_time": timer_info["start_time"],
                "end_time": end_time
            }
            
            self.records.append(record)
            return record
        
        def get_average_duration(self, operation_name: str) -> float:
            """특정 작업의 평균 수행 시간 반환"""
            matching_records = [r for r in self.records if r["operation"] == operation_name]
            if not matching_records:
                return 0.0
            
            total_duration = sum(r["duration"] for r in matching_records)
            return total_duration / len(matching_records)
        
        def get_total_calls(self, operation_name: str) -> int:
            """특정 작업의 총 호출 횟수 반환"""
            return len([r for r in self.records if r["operation"] == operation_name])
        
        def reset(self):
            """모니터링 기록 초기화"""
            self.records.clear()
    
    return PerformanceMonitor()


# 마킹 정의
def pytest_configure(config):
    """pytest 설정 및 커스텀 마킹 정의"""
    config.addinivalue_line(
        "markers", "unit: 단위 테스트 마킹"
    )
    config.addinivalue_line(
        "markers", "integration: 통합 테스트 마킹"
    )
    config.addinivalue_line(
        "markers", "slow: 실행 시간이 긴 테스트 마킹"
    )
    config.addinivalue_line(
        "markers", "external: 외부 의존성이 있는 테스트 마킹"
    )
    config.addinivalue_line(
        "markers", "asyncio: 비동기 테스트 마킹"
    )
    config.addinivalue_line(
        "markers", "performance: 성능 테스트 마킹"
    )


# 테스트 결과 후처리
@pytest.fixture(autouse=True)
def test_cleanup():
    """
    각 테스트 후 자동 정리 fixture
    
    각 테스트 실행 후 자동으로 실행되어 상태를 정리합니다.
    """
    yield
    
    # 테스트 후 정리 작업
    # 예: 임시 파일 삭제, 캐시 정리, 상태 초기화 등
    pass


# 테스트 실행 전 검증
def pytest_runtest_setup(item):
    """
    테스트 실행 전 검증
    
    Args:
        item: 테스트 아이템
    """
    # 필요한 마킹이 있는지 확인
    if hasattr(item, 'pytestmark'):
        # 예: 특정 환경에서만 실행되는 테스트 확인
        pass


# 테스트 실행 후 검증
def pytest_runtest_teardown(item):
    """
    테스트 실행 후 검증
    
    Args:
        item: 테스트 아이템
    """
    # 테스트 후 상태 검증
    pass 