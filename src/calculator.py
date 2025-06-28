"""
간단한 계산기 클래스
"""


class Calculator:
    """기본적인 수학 연산을 수행하는 계산기 클래스"""
    
    def add(self, a: float, b: float) -> float:
        """두 수를 더합니다"""
        return a + b
    
    def subtract(self, a: float, b: float) -> float:
        """첫 번째 수에서 두 번째 수를 뺍니다"""
        return a - b
    
    def multiply(self, a: float, b: float) -> float:
        """두 수를 곱합니다"""
        return a * b
    
    def divide(self, a: float, b: float) -> float:
        """첫 번째 수를 두 번째 수로 나눕니다"""
        if b == 0:
            raise ValueError("0으로 나눌 수 없습니다")
        return a / b
    
    def power(self, base: float, exponent: float) -> float:
        """거듭제곱을 계산합니다"""
        return base ** exponent 