"""
오디오 정보 추출 유틸리티 모듈

이 모듈은 FFmpeg를 사용하여 오디오 파일의 메타데이터를 추출하고
분석하는 기능을 제공합니다. 다양한 오디오 형식을 지원하며,
포맷 감지, 시간 계산, 코덱 정보 등을 추출할 수 있습니다.
"""

import tempfile
from typing import Dict, Union

import ffmpeg


# 오디오 포맷 이름을 파일 확장자로 매핑하는 딕셔너리
FORMAT_NAME_TO_EXT: Dict[str, str] = {
    "mp3": "mp3",           # MP3 오디오
    "wav": "wav",           # WAV 무압축 오디오
    "flac": "flac",         # FLAC 무손실 압축
    "ogg": "ogg",           # OGG Vorbis
    "opus": "opus",         # Opus 코덱
    "aac": "aac",           # AAC 압축
    "ipod": "m4a",          # iTunes AAC
    "mov": "mp4",           # QuickTime 컨테이너
    "mp4": "mp4",           # MP4 컨테이너
    "3gp": "3gp",           # 3GPP 모바일 포맷
    "matroska,webm": "webm", # WebM 웹 비디오
    "matroska": "mkv",      # Matroska 컨테이너
    "amr": "amr",           # AMR 음성 압축
    "wma": "wma",           # Windows Media Audio
    "aiff": "aiff",         # Apple AIFF
    "ape": "ape",           # Monkey's Audio
    "pcm_s16le": "raw",     # 16비트 PCM
    "pcm_f32le": "raw",     # 32비트 Float PCM
    "dsd": "dsf",           # DSD 고해상도 오디오
    "gsm": "gsm"            # GSM 압축
}


def get_audio_info(audio: bytes) -> dict:
    """
    오디오 바이너리 데이터에서 전체 메타데이터를 추출합니다.
    
    FFmpeg probe를 사용하여 오디오 파일의 모든 정보를 추출합니다.
    임시 파일을 생성하여 FFmpeg로 분석한 후 결과를 반환합니다.
    
    Args:
        audio (bytes): 분석할 오디오 바이너리 데이터
    
    Returns:
        dict: FFmpeg probe 결과 (format, streams 등 포함)
        
    Raises:
        ffmpeg.Error: 오디오 파일 분석 실패 시
    """
    # 임시 파일 생성하여 FFmpeg로 분석
    with tempfile.NamedTemporaryFile() as f:
        f.write(audio)
        f.flush()
        
        # FFmpeg probe로 오디오 정보 추출
        info = ffmpeg.probe(f.name)
        return info


def get_audio_duration(audio: bytes) -> float:
    """
    오디오의 재생 시간을 초 단위로 반환합니다.
    
    Args:
        audio (bytes): 분석할 오디오 바이너리 데이터
    
    Returns:
        float: 오디오 재생 시간 (초)
        
    Raises:
        KeyError: 오디오 정보에 duration 필드가 없는 경우
        ValueError: duration 값을 float으로 변환할 수 없는 경우
    """
    return float(get_audio_info(audio)["format"]["duration"])


def get_audio_format(audio: bytes) -> str:
    """
    오디오의 포맷 이름을 반환합니다.
    
    FFmpeg가 감지한 오디오 포맷 이름을 반환합니다.
    예: "mp3", "wav", "matroska,webm" 등
    
    Args:
        audio (bytes): 분석할 오디오 바이너리 데이터
    
    Returns:
        str: 오디오 포맷 이름
        
    Raises:
        KeyError: 오디오 정보에 format_name 필드가 없는 경우
    """
    return get_audio_info(audio)["format"]["format_name"]


def get_audio_extension(audio: bytes) -> str:
    """
    오디오 포맷에 해당하는 파일 확장자를 반환합니다.
    
    FFmpeg가 감지한 포맷 이름을 적절한 파일 확장자로 변환합니다.
    FORMAT_NAME_TO_EXT 매핑을 사용하여 변환됩니다.
    
    Args:
        audio (bytes): 분석할 오디오 바이너리 데이터
    
    Returns:
        str: 파일 확장자 (예: "mp3", "wav", "webm")
        
    Raises:
        KeyError: 지원되지 않는 포맷인 경우
    """
    format_name = get_audio_format(audio)
    return FORMAT_NAME_TO_EXT[format_name]


def get_audio_codec(audio: bytes) -> str:
    """
    오디오의 코덱 정보를 반환합니다.
    
    오디오 스트림에서 사용된 코덱 이름을 반환합니다.
    예: "mp3", "aac", "vorbis", "opus" 등
    
    Args:
        audio (bytes): 분석할 오디오 바이너리 데이터
    
    Returns:
        str: 오디오 코덱 이름
        
    Raises:
        KeyError: 오디오 스트림 정보가 없는 경우
        IndexError: 오디오 스트림이 없는 경우
    """
    return get_audio_info(audio)["streams"][0]["codec_name"]


def get_audio_bitrate(audio: bytes) -> int:
    """
    오디오의 비트레이트를 반환합니다.
    
    오디오 스트림의 비트레이트를 bps(bits per second) 단위로 반환합니다.
    
    Args:
        audio (bytes): 분석할 오디오 바이너리 데이터
    
    Returns:
        int: 오디오 비트레이트 (bps)
        
    Raises:
        KeyError: 비트레이트 정보가 없는 경우
        ValueError: 비트레이트 값을 int로 변환할 수 없는 경우
        IndexError: 오디오 스트림이 없는 경우
    """
    return int(get_audio_info(audio)["streams"][0]["bit_rate"])


def is_audio_format_supported(audio: bytes) -> bool:
    """
    오디오 포맷이 지원되는지 확인합니다.
    
    현재 시스템에서 지원하는 오디오 포맷인지 확인합니다.
    FORMAT_NAME_TO_EXT에 정의된 포맷만 지원됩니다.
    
    Args:
        audio (bytes): 확인할 오디오 바이너리 데이터
    
    Returns:
        bool: 지원되는 포맷이면 True, 아니면 False
    """
    try:
        format_name = get_audio_format(audio)
        return format_name in FORMAT_NAME_TO_EXT
    except Exception:
        return False


def get_audio_sample_rate(audio: bytes) -> int:
    """
    오디오의 샘플링 레이트를 반환합니다.
    
    Args:
        audio (bytes): 분석할 오디오 바이너리 데이터
    
    Returns:
        int: 샘플링 레이트 (Hz)
        
    Raises:
        KeyError: 샘플링 레이트 정보가 없는 경우
        ValueError: 샘플링 레이트 값을 int로 변환할 수 없는 경우
        IndexError: 오디오 스트림이 없는 경우
    """
    return int(get_audio_info(audio)["streams"][0]["sample_rate"])


def get_audio_channels(audio: bytes) -> int:
    """
    오디오의 채널 수를 반환합니다.
    
    Args:
        audio (bytes): 분석할 오디오 바이너리 데이터
    
    Returns:
        int: 채널 수 (1=모노, 2=스테레오)
        
    Raises:
        KeyError: 채널 정보가 없는 경우
        ValueError: 채널 수를 int로 변환할 수 없는 경우
        IndexError: 오디오 스트림이 없는 경우
    """
    return int(get_audio_info(audio)["streams"][0]["channels"])
