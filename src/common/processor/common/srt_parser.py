"""
SRT 자막 파일 파싱 및 처리 유틸리티 모듈

이 모듈은 SRT(SubRip Text) 형식의 자막 파일을 파싱하고 처리하는 기능을 제공합니다.
여러 개의 SRT 청크를 병합하거나, 타임스탬프를 조정하는 등의 작업을 수행할 수 있습니다.
주로 OpenAI Whisper API의 청킹 처리 결과를 병합할 때 사용됩니다.
"""

import re
from datetime import timedelta
from typing import List, Tuple


def parse_srt(srt_text: str) -> List[Tuple[int, str, str, str]]:
    """
    SRT 텍스트를 구조화된 리스트로 파싱합니다.
    
    SRT 형식의 텍스트를 파싱하여 각 자막 항목을 
    (번호, 시작시간, 종료시간, 텍스트) 튜플로 변환합니다.
    
    Args:
        srt_text (str): 파싱할 SRT 형식의 텍스트
    
    Returns:
        List[Tuple[int, str, str, str]]: 파싱된 자막 항목들의 리스트
        각 항목은 (번호, 시작시간, 종료시간, 텍스트) 형태
    
    Example:
        >>> srt_text = "1\\n00:00:01,000 --> 00:00:05,000\\n안녕하세요\\n\\n"
        >>> parse_srt(srt_text)
        [(1, '00:00:01,000', '00:00:05,000', '안녕하세요')]
    """
    # SRT 형식 정규표현식 패턴
    # 번호 + 시간 범위 + 텍스트 + 빈 줄로 구성
    pattern = re.compile(
        r'(\d+)\n'                                    # 자막 번호
        r'(\d{2}:\d{2}:\d{2},\d{3}) --> '            # 시작 시간
        r'(\d{2}:\d{2}:\d{2},\d{3})\n'               # 종료 시간
        r'(.*?)\n\n',                                 # 자막 텍스트
        re.DOTALL                                     # 여러 줄 매칭
    )
    
    # 정규표현식 매칭 결과를 튜플 리스트로 변환
    return [
        (int(num), start, end, text.strip())
        for num, start, end, text in pattern.findall(srt_text + "\n\n")
    ]


def shift_timestamp(ts: str, offset: float) -> str:
    """
    타임스탬프 문자열에 시간 오프셋을 적용합니다.
    
    SRT 형식의 타임스탬프 문자열에 초 단위의 오프셋을 더하여
    새로운 타임스탬프를 생성합니다. 청크 병합 시 사용됩니다.
    
    Args:
        ts (str): 변환할 타임스탬프 문자열 (예: "00:01:23,456")
        offset (float): 추가할 시간 오프셋 (초 단위)
    
    Returns:
        str: 오프셋이 적용된 새로운 타임스탬프 문자열
    
    Example:
        >>> shift_timestamp("00:01:23,456", 30.5)
        "00:01:53,956"
    
    Raises:
        ValueError: 타임스탬프 형식이 올바르지 않은 경우
    """
    # 타임스탬프 파싱: "HH:MM:SS,mmm" 형식
    h, m, s_ms = ts.split(':')
    s, ms = s_ms.split(',')
    
    # 현재 시간을 timedelta로 변환
    current_time = timedelta(
        hours=int(h),
        minutes=int(m),
        seconds=int(s),
        milliseconds=int(ms)
    )
    
    # 오프셋 적용
    new_time = current_time + timedelta(seconds=offset)
    
    # 새로운 타임스탬프 문자열 생성
    total_seconds = int(new_time.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    milliseconds = new_time.microseconds // 1000
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def merge_srt_chunks(srt_chunks: List[Tuple[str, float]]) -> str:
    """
    여러 개의 SRT 청크를 하나의 SRT 파일로 병합합니다.
    
    각 청크는 독립적인 SRT 텍스트와 해당 청크의 시간 오프셋을 포함합니다.
    모든 청크를 병합하여 연속된 자막 번호를 가진 하나의 SRT 파일을 생성합니다.
    
    Args:
        srt_chunks (List[Tuple[str, float]]): 병합할 SRT 청크들의 리스트
        각 항목은 (SRT 텍스트, 시간 오프셋) 형태
    
    Returns:
        str: 병합된 SRT 텍스트
    
    Example:
        >>> chunks = [
        ...     ("1\\n00:00:01,000 --> 00:00:05,000\\n첫 번째\\n\\n", 0.0),
        ...     ("1\\n00:00:01,000 --> 00:00:05,000\\n두 번째\\n\\n", 10.0)
        ... ]
        >>> merge_srt_chunks(chunks)
        "1\\n00:00:01,000 --> 00:00:05,000\\n첫 번째\\n\\n2\\n00:00:11,000 --> 00:00:15,000\\n두 번째\\n"
    """
    merged = []
    counter = 1  # 통합된 자막 번호 카운터

    # 각 청크를 순차적으로 처리
    for srt_text, offset in srt_chunks:
        # 현재 청크의 SRT 텍스트 파싱
        parsed = parse_srt(srt_text)
        
        # 파싱된 결과가 없으면 건너뛰기
        if not parsed:
            continue
            
        # 각 자막 항목에 대해 처리
        for _, start, end, text in parsed:
            # 시간 오프셋 적용
            new_start = shift_timestamp(start, offset)
            new_end = shift_timestamp(end, offset)
            
            # 새로운 자막 항목 생성
            merged.append(f"{counter}\n{new_start} --> {new_end}\n{text}\n")
            counter += 1

    # 모든 자막 항목을 하나의 문자열로 병합
    return "\n".join(merged)


def validate_srt_format(srt_text: str) -> bool:
    """
    SRT 텍스트의 형식이 올바른지 검증합니다.
    
    Args:
        srt_text (str): 검증할 SRT 텍스트
    
    Returns:
        bool: 올바른 SRT 형식이면 True, 아니면 False
    """
    try:
        parsed = parse_srt(srt_text)
        return len(parsed) > 0
    except Exception:
        return False


def get_srt_duration(srt_text: str) -> float:
    """
    SRT 텍스트의 총 재생 시간을 계산합니다.
    
    Args:
        srt_text (str): 분석할 SRT 텍스트
    
    Returns:
        float: 총 재생 시간 (초)
    
    Raises:
        ValueError: SRT 형식이 올바르지 않은 경우
    """
    parsed = parse_srt(srt_text)
    if not parsed:
        return 0.0
    
    # 마지막 자막의 종료 시간을 총 재생 시간으로 사용
    last_end_time = parsed[-1][2]  # 종료 시간
    
    # 타임스탬프를 초로 변환
    h, m, s_ms = last_end_time.split(':')
    s, ms = s_ms.split(',')
    
    total_seconds = int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0
    return total_seconds
