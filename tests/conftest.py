"""
pytest 설정 및 픽스처 정의
"""
import pytest
import sys
import os

# src 디렉토리를 Python path에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


@pytest.fixture
def sample_numbers():
    """테스트용 샘플 숫자 리스트"""
    return [1, 2, 3, 4, 5, -1, -2, 0]


@pytest.fixture
def sample_user_data():
    """테스트용 사용자 데이터"""
    return {
        "name": "테스트 사용자",
        "age": 30,
        "email": "test@example.com"
    } 