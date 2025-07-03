import re
from datetime import timedelta


def parse_srt(srt_text: str):
    """SRT 텍스트를 리스트로 파싱 ([(start, end, text), ...])"""
    pattern = re.compile(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)\n\n', re.DOTALL)
    return [
        (int(num), start, end, text.strip())
        for num, start, end, text in pattern.findall(srt_text + "\n\n")
    ]


def shift_timestamp(ts: str, offset: float) -> str:
    """타임스탬프 문자열에 시간 offset(초) 추가"""
    h, m, s_ms = ts.split(':')
    s, ms = s_ms.split(',')
    total = timedelta(
        hours=int(h), minutes=int(m), seconds=int(s), milliseconds=int(ms)
    ) + timedelta(seconds=offset)

    return f"{total.seconds//3600:02}:{(total.seconds//60)%60:02}:{total.seconds%60:02},{total.microseconds//1000:03}"


def merge_srt_chunks(srt_chunks: list[tuple[str, float]]) -> str:
    """
    srt_chunks: List of tuples -> (srt_text, chunk_offset_seconds)
    각 청크의 자막은 string, 시작 시간 offset은 float(초 단위)
    """
    merged = []
    counter = 1

    for srt_text, offset in srt_chunks:
        parsed = parse_srt(srt_text)
        if not parsed:  # 파싱된 결과가 없으면 건너뛰기
            continue
            
        for _, start, end, text in parsed:
            new_start = shift_timestamp(start, offset)
            new_end = shift_timestamp(end, offset)
            merged.append(f"{counter}\n{new_start} --> {new_end}\n{text}\n")
            counter += 1

    return "\n".join(merged)
