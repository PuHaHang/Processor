import tempfile

import ffmpeg


FORMAT_NAME_TO_EXT = {
    "mp3": "mp3",
    "wav": "wav",
    "flac": "flac",
    "ogg": "ogg",
    "opus": "opus",
    "aac": "aac",
    "ipod": "m4a",
    "mov": "mp4",
    "mp4": "mp4",
    "3gp": "3gp",
    "matroska,webm": "webm",
    "matroska": "mkv",
    "amr": "amr",
    "wma": "wma",
    "aiff": "aiff",
    "ape": "ape",
    "pcm_s16le": "raw",
    "pcm_f32le": "raw",
    "dsd": "dsf",
    "gsm": "gsm"
}


def get_audio_info(audio: bytes) -> dict:
    with tempfile.NamedTemporaryFile() as f:
        f.write(audio)
        f.flush()
        info = ffmpeg.probe(f.name)
        return info


def get_audio_duration(audio: bytes) -> float:
    return float(get_audio_info(audio)["format"]["duration"])


def get_audio_format(audio: bytes) -> str:
    return get_audio_info(audio)["format"]["format_name"]


def get_audio_extension(audio: bytes) -> str:
    return FORMAT_NAME_TO_EXT[get_audio_format(audio)]


def get_audio_codec(audio: bytes) -> str:
    return get_audio_info(audio)["streams"][0]["codec_name"]


def get_audio_bitrate(audio: bytes) -> int:
    return int(get_audio_info(audio)["streams"][0]["bit_rate"])
