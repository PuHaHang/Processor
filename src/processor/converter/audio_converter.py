"""
오디오 변환기 모듈

이 모듈은 pydub 라이브러리를 사용하여 다양한 오디오 포맷 간의 변환을 수행하는 변환기를 제공합니다.
"""

import io
from typing import Tuple

from pydub import AudioSegment

from src.processor.converter.converter import Converter
from src.processor.data_structure.buffer_dto import BufferDto
from src.processor.data_structure.buffer_status import BufferStatus
from src.processor.data_type import DataType


class AudioConverter (Converter):
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

    def process(self, buffer_dto: BufferDto, opt: dict = {}) -> BufferDto:
        """
        오디오 데이터를 지정된 형식으로 변환합니다.
        
        Args:
            buffer_dto (BufferDto): 처리할 오디오 버퍼 데이터
            opt (dict, optional): 처리 옵션 ('ext' 키로 출력 형식 지정)
        
        Returns:
            BufferDto: 변환된 오디오 데이터가 포함된 버퍼 데이터
            
        Raises:
            ValueError: 유효하지 않은 출력 확장자인 경우
        """
        # 입력 확장자와 출력 확장자 추출
        src_ext = self._extract_audio_extension(buffer_dto.metadata)
        dest_ext = opt.get("ext", "")

        # 출력 확장자 유효성 검사
        if dest_ext not in self.available_output_ext:
            raise ValueError(f"Invalid output extension: {dest_ext}")

        return BufferDto(
            buffer=self._convert_audio(buffer_dto.buffer, opt={
                "src_ext": src_ext,
                "dest_ext": dest_ext
            }),
            metadata={"ext": dest_ext},
            data_type=DataType.AUDIO,
            status=BufferStatus.COMPLETED
        )


    def is_supported(self, buffer_dto: BufferDto) -> bool:
        """
        버퍼 데이터가 이 변환기에서 지원되는지 확인합니다.
        
        Args:
            buffer_dto (BufferDto): 확인할 버퍼 데이터
        
        Returns:
            bool: AUDIO 타입이고 지원하는 입력 확장자인 경우 True
        """
        return self.data_flow[0] == buffer_dto.data_type and \
            buffer_dto.metadata.get("ext", "") in self.available_input_ext


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
        if not (src_ext := opt.get("src_ext", "")) or \
            not (dest_ext := opt.get("dest_ext", "")):
            raise ValueError("src_ext and dest_ext are required")

        # 소스 바이너리 데이터를 AudioSegment로 로드
        src_buffer = io.BytesIO(src_audio)

        src_buffer = AudioSegment.from_file(src_buffer, format=src_ext)
        
        # 변환된 데이터를 바이너리로 내보내기
        dest_buffer = io.BytesIO()
        src_buffer.export(dest_buffer, format=dest_ext)
        return dest_buffer.getvalue()


    def _extract_audio_extension(self, metadata: dict) -> str:
        """
        메타데이터에서 오디오 확장자를 추출합니다.
        
        Args:
            metadata (dict): 메타데이터 딕셔너리
        
        Returns:
            str: 추출된 확장자 문자열, 없으면 빈 문자열
        """
        return metadata.get("ext", "")