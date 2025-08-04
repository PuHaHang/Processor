"""
오디오 변환기 모듈

이 모듈은 pydub 라이브러리를 사용하여 다양한 오디오 포맷 간의 변환을 수행하는 변환기를 제공합니다.
"""

import io
from typing import Tuple

from pydub import AudioSegment

from ...common import get_ffmpeg_extension
from ..converter_strategy import ConverterStrategy
from ...types import DataType, PayloadStatus, Payload

# 예외 핸들러 import
from ....exception import (
    ExceptionHandler,
    ValidationExceptionHandler,
    ExceptionType,
    ExceptionSeverity,
    ProcessingException,
    ValidationException
)


class AudioConverter (ConverterStrategy):
    """
    오디오 형식 변환을 수행하는 변환기
    
    pydub 라이브러리를 사용하여 webm, mp3, wav, flac 등 다양한 오디오 형식 간의
    변환을 수행합니다. FFmpeg를 백엔드로 사용합니다.
    
    Attributes:
        data_flow (Tuple[DataType, DataType]): AUDIO → AUDIO로 데이터 타입 유지
        available_input_ext (list[str]): 지원하는 입력 확장자 목록
        available_output_ext (list[str]): 지원하는 출력 확장자 목록
        default_output_ext (str): 기본 출력 확장자 ('mp3')
    """
    data_flow: Tuple[DataType, DataType] = (DataType.AUDIO, DataType.AUDIO)
    available_input_ext: list[str] = ["webm", "mp3", "m4a", "ogg", "wav", "flac"]
    available_output_ext: list[str] = ["mp3", "webm", "m4a", "ogg", "wav", "flac"]
    default_output_ext: str = "mp3"


    @ExceptionHandler(
        exception_type=ExceptionType.AUDIO_PROCESSING_ERROR,
        severity=ExceptionSeverity.MEDIUM,
        reraise=True,
        log_level="warning",
        handler_name="audio_converter_process_handler"
    )
    @ValidationExceptionHandler(reraise=True)
    def process(self, payload: Payload, opt: dict = {}) -> Payload:
        """
        오디오 데이터를 지정된 형식으로 변환합니다.
        
        Args:
            payload (Payload): 처리할 오디오 버퍼 데이터
            opt (dict, optional): 처리 옵션 ('ext' 키로 출력 형식 지정)
        
        Returns:
            Payload: 변환된 오디오 데이터가 포함된 버퍼 데이터
            
        Raises:
            ValueError: 유효하지 않은 출력 확장자인 경우
        """
        # 입력 확장자와 출력 확장자 추출
        src_ext = get_ffmpeg_extension(payload.buffer)
        dest_ext = opt.get("ext", self.default_output_ext)

        # 출력 확장자 유효성 검사
        if src_ext not in self.available_input_ext:
            raise ValidationException(
                message=f"지원되지 않는 입력 형식입니다: {src_ext}",
                field_name="src_ext",
                field_value=src_ext,
                validation_rule="supported_format"
            )
            
        if dest_ext not in self.available_output_ext:
            raise ValidationException(
                message=f"지원되지 않는 출력 형식입니다: {dest_ext}",
                field_name="dest_ext", 
                field_value=dest_ext,
                validation_rule="supported_format"
            )

        return Payload(
            buffer=self._convert_audio(payload.buffer, opt={
                "src_ext": src_ext,
                "dest_ext": dest_ext
            }),
            metadata={"ext": dest_ext},
            data_type=DataType.AUDIO,
            status=PayloadStatus.COMPLETED,
            processor=self
        )


    @ValidationExceptionHandler(reraise=False, default_return=False)
    def is_supported(self, payload: Payload) -> bool:
        """
        버퍼 데이터가 이 변환기에서 지원되는지 확인합니다.
        
        Args:
            payload (Payload): 확인할 버퍼 데이터
        
        Returns:
            bool: AUDIO 타입이고 지원하는 입력 확장자인 경우 True
        """
        try:
            return self.data_flow[0] == payload.data_type and \
                get_ffmpeg_extension(payload.buffer) in self.available_input_ext
        except Exception:
            return False


    @ExceptionHandler(
        exception_type=ExceptionType.AUDIO_PROCESSING_ERROR,
        severity=ExceptionSeverity.MEDIUM,
        reraise=True,
        log_level="error",
        handler_name="audio_conversion_handler"
    )
    @ValidationExceptionHandler(reraise=True)
    def _convert_audio(self, src_audio: bytes, opt: dict = {}) -> bytes:
        """
        오디오 바이너리 데이터를 다른 형식으로 변환합니다.
        
        Args:
            src_audio (bytes): 변환할 소스 오디오 바이너리 데이터
            opt (dict, optional): 변환 옵션 (src_ext, dest_ext 필수)
        
        Returns:
            bytes: 변환된 오디오 바이너리 데이터
            
        Raises:
            ValueError: 필수 매개변수가 누락된 경우
        """
        # 필수 매개변수 검사
        src_ext = opt.get("src_ext", "")
        dest_ext = opt.get("dest_ext", "")
        
        if src_ext not in self.available_input_ext:
            raise ValidationException(
                message=f"유효하지 않은 입력 확장자입니다: {src_ext}",
                field_name="src_ext",
                field_value=src_ext,
                validation_rule="supported_input_format"
            )
            
        if dest_ext not in self.available_output_ext:
            raise ValidationException(
                message=f"유효하지 않은 출력 확장자입니다: {dest_ext}",
                field_name="dest_ext",
                field_value=dest_ext,
                validation_rule="supported_output_format"
            )

        return self._perform_audio_conversion(src_audio, src_ext, dest_ext)

    @ExceptionHandler(
        exception_type=ExceptionType.AUDIO_PROCESSING_ERROR,
        severity=ExceptionSeverity.MEDIUM,
        reraise=True,
        log_level="error",
        handler_name="audio_conversion_core_handler"
    )
    def _perform_audio_conversion(self, src_audio: bytes, src_ext: str, dest_ext: str) -> bytes:
        """
        실제 오디오 변환을 수행하는 내부 메소드
        
        Args:
            src_audio (bytes): 변환할 소스 오디오 바이너리 데이터
            src_ext (str): 소스 확장자
            dest_ext (str): 대상 확장자
        
        Returns:
            bytes: 변환된 오디오 바이너리 데이터
        """
        # 소스 바이너리 데이터를 AudioSegment로 로드
        src_buffer = io.BytesIO(src_audio)
        src_buffer = AudioSegment.from_file(src_buffer, format=get_ffmpeg_extension(src_audio))
        
        # 변환된 데이터를 바이너리로 내보내기
        dest_buffer = io.BytesIO()
        src_buffer.export(dest_buffer, format=dest_ext)
        return dest_buffer.getvalue()
