"""
utils 모듈에 대한 테스트
"""
import os
import pytest
from unittest.mock import patch
from src.utils import (
    is_even, 
    get_environment_variable, 
    filter_positive_numbers, 
    create_user_profile
)


class TestUtils:
    """Utils 함수들에 대한 테스트"""
    
    @pytest.mark.unit
    @pytest.mark.parametrize("number,expected", [
        (2, True),
        (3, False),
        (0, True),
        (-2, True),
        (-3, False),
        (100, True),
        (101, False)
    ])
    def test_is_even(self, number, expected):
        """짝수 판별 함수 테스트"""
        assert is_even(number) == expected
    
    @pytest.mark.unit
    def test_get_environment_variable_existing(self):
        """존재하는 환경변수 테스트"""
        with patch.dict(os.environ, {'TEST_VAR': 'test_value'}):
            assert get_environment_variable('TEST_VAR') == 'test_value'
    
    @pytest.mark.unit
    def test_get_environment_variable_non_existing(self):
        """존재하지 않는 환경변수 테스트"""
        assert get_environment_variable('NON_EXISTING_VAR') == ""
    
    @pytest.mark.unit
    def test_get_environment_variable_with_default(self):
        """기본값이 있는 환경변수 테스트"""
        assert get_environment_variable('NON_EXISTING_VAR', 'default') == 'default'
    
    @pytest.mark.unit
    def test_filter_positive_numbers(self):
        """양수 필터링 테스트"""
        numbers = [-3, -1, 0, 1, 2, 5, -2]
        expected = [1, 2, 5]
        assert filter_positive_numbers(numbers) == expected
        
        # 빈 리스트 테스트
        assert filter_positive_numbers([]) == []
        
        # 모두 음수인 경우
        assert filter_positive_numbers([-1, -2, -3]) == []
        
        # 모두 양수인 경우
        assert filter_positive_numbers([1, 2, 3]) == [1, 2, 3]
    
    @pytest.mark.unit
    def test_create_user_profile_basic(self):
        """기본 사용자 프로필 생성 테스트"""
        profile = create_user_profile("김철수", 25)
        expected = {
            "name": "김철수",
            "age": 25,
            "is_adult": True
        }
        assert profile == expected
    
    @pytest.mark.unit
    def test_create_user_profile_minor(self):
        """미성년자 프로필 생성 테스트"""
        profile = create_user_profile("김영희", 16)
        assert profile["is_adult"] is False
    
    @pytest.mark.unit
    def test_create_user_profile_with_kwargs(self):
        """추가 정보가 있는 사용자 프로필 생성 테스트"""
        profile = create_user_profile(
            "이민수", 30, 
            job="개발자", 
            city="서울",
            hobbies=["독서", "영화감상"]
        )
        
        assert profile["name"] == "이민수"
        assert profile["age"] == 30
        assert profile["is_adult"] is True
        assert profile["job"] == "개발자"
        assert profile["city"] == "서울"
        assert profile["hobbies"] == ["독서", "영화감상"] 