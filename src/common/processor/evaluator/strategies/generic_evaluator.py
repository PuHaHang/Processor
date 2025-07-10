
"""
범용 평가기 모듈
==============

이 모듈은 텍스트 타입의 페이로드에 대해 범용적으로 사용할 수 있는 평가기를 제공합니다.
상위 EvaluatorStrategy 클래스를 상속받아 Zero-shot 분류기를 통한 레시피 관련 여부를 판단합니다.

주요 구성 요소:
    - GenericEvaluator: 범용 평가기 클래스

아키텍처:
    입력 페이로드 → 지원 여부 확인 → 텍스트 추출 → Zero-shot 분류 → 평가 결과 반환

주요 사용 사례:
    - 텍스트 데이터의 레시피 관련 여부 판단
    - 범용적인 컨텐츠 분류 및 평가
    - 다양한 프로세서에서 생성된 텍스트 데이터 검증

의존성:
    - EvaluatorStrategy: 평가 전략 기본 클래스
    - Payload: 데이터 전송 객체

사용 예시:
    >>> evaluator = GenericEvaluator()
    >>> payload = Payload(buffer=b"recipe text", data_type="text", ...)
    >>> result = evaluator.evaluate(payload)
    >>> print(result)  # True or False

성능 특성:
    - 단순한 텍스트 기반 평가로 빠른 처리 속도
    - Zero-shot 분류기를 통한 정확한 분류
    - 메모리 효율적인 구조

제한사항:
    - 텍스트 타입 데이터만 지원
    - 단일 텍스트 문자열만 처리 가능
    - 긴 텍스트에 대한 청킹 처리 미지원

TODO:
    - 다양한 데이터 타입 지원 확장
    - 긴 텍스트 청킹 처리 기능 추가
    - 배치 처리 지원

작성자: 개발팀
최종 수정일: 2024-01-15
버전: 1.0.0
"""

from src.common.processor.evaluator.evaluator_strategy import EvaluatorStrategy
from src.common.processor.types.payload import Payload


class GenericEvaluator(EvaluatorStrategy):
    """
    범용 평가기 클래스
    ---------------
    
    텍스트 타입의 페이로드에 대해 범용적으로 사용할 수 있는 평가기입니다.
    
    이 클래스는 상위 EvaluatorStrategy 클래스를 상속받아 Zero-shot 분류기를 통한 
    레시피 관련 여부를 판단하는 기능을 제공합니다. 단순하고 효율적인 구조로 설계되어 
    빠른 텍스트 분류 작업에 적합합니다.
    
    주요 책임:
        - 텍스트 타입 페이로드 지원 여부 확인
        - 페이로드에서 텍스트 데이터 추출
        - Zero-shot 분류기를 통한 레시피 관련 여부 평가
        - 표준화된 평가 결과 반환
    
    설계 특징:
        - 상속을 통한 공통 인터페이스 제공
        - 단일 책임 원칙 적용 (텍스트 분류만 담당)
        - 의존성 주입을 통한 분류기 활용
        - 간단하고 직관적인 API 제공
    
    주요 메소드:
        - is_supported(payload): 페이로드 지원 여부 확인
        - evaluate(payload): 실제 평가 수행
    
    사용 예시:
        >>> evaluator = GenericEvaluator()
        >>> payload = Payload(buffer=b"김치찌개 만들기", data_type="text", ...)
        >>> 
        >>> # 지원 여부 확인
        >>> if evaluator.is_supported(payload):
        ...     result = evaluator.evaluate(payload)
        ...     print(f"레시피 관련 여부: {result}")
        >>> 
        >>> # 결과: 레시피 관련 여부: True
    
    제한사항:
        - 텍스트 타입(data_type="text")만 지원
        - UTF-8 인코딩된 바이트 데이터만 처리
        - 단일 텍스트 문자열만 처리 (배치 처리 미지원)
        - 긴 텍스트에 대한 청킹 처리 미지원
    
    성능 고려사항:
        - 텍스트 디코딩 오버헤드 최소화
        - 상위 클래스의 분류기 재사용으로 메모리 효율성 확보
        - 단순한 로직으로 빠른 처리 속도
    
    확장성:
        - 다양한 데이터 타입 지원을 위한 확장 가능
        - 청킹 처리 기능 추가 가능
        - 배치 처리 지원 확장 가능
    
    참고사항:
        - 상위 클래스 EvaluatorStrategy의 classifier 속성 사용
        - Zero-shot 분류기 모델은 환경변수에서 설정 가능
        - 스레드 안전성은 상위 클래스 구현에 의존
    """
    
    # 지원하는 프로세서 타입 목록 (현재 빈 리스트로 모든 프로세서 지원)
    available_processors: list[type] = []

    def is_supported(self, payload: Payload) -> bool:
        """
        페이로드가 이 평가기에서 지원되는지 확인합니다.
        
        텍스트 타입 데이터만 지원하는 간단한 검증을 수행합니다.
        데이터 타입이 "text"인 경우에만 처리 가능으로 판단합니다.
        
        Args:
            payload (Payload): 확인할 페이로드 객체
                - data_type: 데이터 타입 (문자열)
                - buffer: 실제 데이터 (바이트)
                - metadata: 메타데이터 (딕셔너리)
                - status: 처리 상태
                - processor: 처리한 프로세서 타입
        
        Returns:
            bool: 지원 여부
                - True: 텍스트 타입 데이터로 처리 가능
                - False: 지원하지 않는 데이터 타입
        
        Example:
            >>> evaluator = GenericEvaluator()
            >>> 
            >>> # 지원되는 경우
            >>> text_payload = Payload(data_type="text", buffer=b"hello", ...)
            >>> print(evaluator.is_supported(text_payload))  # True
            >>> 
            >>> # 지원되지 않는 경우
            >>> audio_payload = Payload(data_type="audio", buffer=b"...", ...)
            >>> print(evaluator.is_supported(audio_payload))  # False
        
        Notes:
            - 단순한 문자열 비교로 빠른 판단 가능
            - payload.data_type이 None이거나 빈 문자열인 경우 False 반환
            - 대소문자 구분하여 정확히 "text"와 일치해야 함
        
        Performance:
            - 시간 복잡도: O(1) - 단순 문자열 비교
            - 공간 복잡도: O(1) - 추가 메모리 사용 없음
        """
        return payload.data_type == "text"
    
    def evaluate(self, payload: Payload) -> bool:
        """
        페이로드를 평가하여 레시피 관련 여부를 판단합니다.
        
        페이로드의 바이트 데이터를 UTF-8로 디코딩하여 텍스트로 변환한 후,
        상위 클래스의 Zero-shot 분류기를 통해 레시피 관련 여부를 평가합니다.
        
        처리 흐름:
            1. 페이로드 버퍼 데이터 추출
            2. UTF-8 디코딩을 통한 텍스트 변환
            3. 상위 클래스의 _evaluate() 메소드 호출
            4. Zero-shot 분류기를 통한 레시피 관련 여부 판단
            5. 결과 반환
        
        Args:
            payload (Payload): 평가할 페이로드 객체
                - buffer (bytes): UTF-8로 인코딩된 텍스트 데이터
                - data_type: "text"여야 함
                - metadata: 추가 메타데이터 (사용되지 않음)
        
        Returns:
            bool: 레시피 관련 여부
                - True: 레시피 관련 내용으로 판단
                - False: 레시피와 관련 없는 내용으로 판단
        
        Raises:
            UnicodeDecodeError: 바이트 데이터를 UTF-8로 디코딩할 수 없을 때
                - 잘못된 인코딩 또는 손상된 데이터
            AttributeError: payload.buffer가 None이거나 바이트 타입이 아닐 때
            Exception: 상위 클래스 _evaluate() 메소드에서 발생하는 예외
                - 분류기 모델 로드 실패
                - 네트워크 연결 오류 (원격 모델 사용 시)
        
        Example:
            >>> evaluator = GenericEvaluator()
            >>> 
            >>> # 레시피 관련 텍스트
            >>> recipe_payload = Payload(
            ...     buffer="김치찌개 만드는 방법".encode('utf-8'),
            ...     data_type="text",
            ...     metadata={},
            ...     status=PayloadStatus.COMPLETED
            ... )
            >>> result = evaluator.evaluate(recipe_payload)
            >>> print(result)  # True
            >>> 
            >>> # 레시피와 무관한 텍스트
            >>> news_payload = Payload(
            ...     buffer="오늘 날씨가 좋습니다".encode('utf-8'),
            ...     data_type="text",
            ...     metadata={},
            ...     status=PayloadStatus.COMPLETED
            ... )
            >>> result = evaluator.evaluate(news_payload)
            >>> print(result)  # False
        
        Side Effects:
            - 상위 클래스의 분류기 모델 로드 (최초 호출 시)
            - 분류 결과 캐싱 (분류기 구현에 따라)
        
        Performance:
            - 시간 복잡도: O(n) (n은 텍스트 길이, 분류기 처리 시간)
            - 공간 복잡도: O(n) (텍스트 디코딩을 위한 임시 메모리)
            - 분류기 모델 크기에 따른 메모리 사용량 증가
        
        Notes:
            - 이 메소드 호출 전에 is_supported() 확인 권장
            - UTF-8 인코딩 가정하에 설계됨
            - 분류기 정확도는 사용된 모델에 의존
            - 네트워크 기반 모델 사용 시 응답 시간 고려 필요
        
        See Also:
            - EvaluatorStrategy._evaluate(): 실제 분류 수행
            - is_supported(): 페이로드 지원 여부 확인
        """
        return super()._evaluate(payload.buffer.decode("utf-8"))  # UTF-8 디코딩 후 분류기 호출
