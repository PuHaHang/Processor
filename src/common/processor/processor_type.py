"""
프로세서 타입 정의 모듈

이 모듈은 시스템에서 사용되는 다양한 프로세서들의 타입을 정의합니다.
"""

from enum import Enum

# TODO: add more processor types

class ProcessorType(Enum):
    """
    프로세서 타입을 정의하는 열거형
    
    시스템에서 사용되는 모든 프로세서의 타입을 정의합니다.
    각 프로세서는 특정 데이터 변환 작업을 담당합니다.
    """
    DOWNLOADER = 0   # 다운로더 (URL → 미디어 파일)
    CONVERTER = 1    # 변환기 (미디어 형식 변환)
    TRANSCRIBER = 2  # 전사기 (오디오 → 텍스트)
    TRANSLATOR = 3   # 번역기 (텍스트 언어 변환)
    SUMMARIZER = 4   # 요약기 (텍스트 요약)
    MONITOR = 5      # 모니터 (시스템 상태 감시)
    NOTIFIER = 6     # 알림기 (알림 전송)
    CLASSIFIER = 7   # 분류기 (데이터 분류)
    REFINER = 8      # 정제기 (데이터 정제)