"""
유틸리티 함수들
"""
import os
from typing import List, Dict, Any


def is_even(number: int) -> bool:
    """숫자가 짝수인지 확인합니다"""
    return number % 2 == 0


def get_environment_variable(key: str, default: str = "") -> str:
    """환경변수 값을 가져옵니다"""
    return os.getenv(key, default)


def filter_positive_numbers(numbers: List[float]) -> List[float]:
    """양수만 필터링합니다"""
    return [num for num in numbers if num > 0]


def create_user_profile(name: str, age: int, **kwargs) -> Dict[str, Any]:
    """사용자 프로필을 생성합니다"""
    profile = {
        "name": name,
        "age": age,
        "is_adult": age >= 18
    }
    profile.update(kwargs)
    return profile 