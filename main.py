"""
메인 실행 파일
"""
from src.calculator import Calculator
from src.utils import is_even, filter_positive_numbers, create_user_profile


def main():
    """메인 함수"""
    print("=== 계산기 테스트 ===")
    calc = Calculator()
    
    print(f"2 + 3 = {calc.add(2, 3)}")
    print(f"10 - 4 = {calc.subtract(10, 4)}")
    print(f"5 * 6 = {calc.multiply(5, 6)}")
    print(f"15 / 3 = {calc.divide(15, 3)}")
    print(f"2^8 = {calc.power(2, 8)}")
    
    print("\n=== 유틸리티 함수 테스트 ===")
    numbers = [-3, -1, 0, 1, 2, 5, -2]
    print(f"원본 숫자들: {numbers}")
    print(f"양수만 필터링: {filter_positive_numbers(numbers)}")
    
    print(f"4는 짝수? {is_even(4)}")
    print(f"7은 짝수? {is_even(7)}")
    
    profile = create_user_profile("김개발", 28, job="소프트웨어 엔지니어")
    print(f"\n사용자 프로필: {profile}")


if __name__ == "__main__":
    main() 