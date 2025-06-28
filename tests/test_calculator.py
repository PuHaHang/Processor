"""
Calculator 클래스에 대한 테스트
"""
import pytest
from src.calculator import Calculator


class TestCalculator:
    """Calculator 클래스 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.calculator = Calculator()
    
    @pytest.mark.unit
    def test_add(self):
        """덧셈 테스트"""
        assert self.calculator.add(2, 3) == 5
        assert self.calculator.add(-1, 1) == 0
        assert self.calculator.add(0, 0) == 0
        assert self.calculator.add(1.5, 2.5) == 4.0
    
    @pytest.mark.unit
    def test_subtract(self):
        """뺄셈 테스트"""
        assert self.calculator.subtract(5, 3) == 2
        assert self.calculator.subtract(1, 1) == 0
        assert self.calculator.subtract(-1, -1) == 0
        assert self.calculator.subtract(1.5, 0.5) == 1.0
    
    @pytest.mark.unit
    def test_multiply(self):
        """곱셈 테스트"""
        assert self.calculator.multiply(2, 3) == 6
        assert self.calculator.multiply(-2, 3) == -6
        assert self.calculator.multiply(0, 5) == 0
        assert self.calculator.multiply(1.5, 2) == 3.0
    
    @pytest.mark.unit
    def test_divide(self):
        """나눗셈 테스트"""
        assert self.calculator.divide(6, 2) == 3
        assert self.calculator.divide(5, 2) == 2.5
        assert self.calculator.divide(-6, 2) == -3
    
    @pytest.mark.unit
    def test_divide_by_zero(self):
        """0으로 나누기 오류 테스트"""
        with pytest.raises(ValueError, match="0으로 나눌 수 없습니다"):
            self.calculator.divide(5, 0)
    
    @pytest.mark.unit
    def test_power(self):
        """거듭제곱 테스트"""
        assert self.calculator.power(2, 3) == 8
        assert self.calculator.power(5, 0) == 1
        assert self.calculator.power(2, -1) == 0.5
        assert self.calculator.power(9, 0.5) == 3.0 