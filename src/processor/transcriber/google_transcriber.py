"""
Google 음성 인식 전사기 모듈

이 모듈은 Google Speech Recognition API를 사용하여
오디오 데이터를 텍스트로 변환하는 전사기를 제공합니다.
"""

import io
from typing import Tuple

import speech_recognition as sr

from src.processor.common import audio_info
from src.processor.data_type import DataType
from src.processor.data_structure.buffer_dto import BufferDto
from src.processor.data_structure.buffer_status import BufferStatus
from src.processor.transcriber.transcriber import Transcriber


# TODO: Google Transcriber API 키 설정 필요
class GoogleTranscriber (Transcriber):
    """
    Google Speech Recognition API를 사용하는 전사기
    
    Google의 음성 인식 서비스를 통해 오디오 파일을 텍스트로 변환합니다.
    한국어 인식을 기본으로 지원합니다.
    
    Attributes:
        data_flow (Tuple[DataType, DataType]): AUDIO → TEXT로 데이터 타입 변환
        available_input_ext (list[str]): 지원하는 입력 확장자 ('wav')
        available_output_ext (list[str]): 지원하는 출력 확장자 ('txt')
        default_output_ext (str): 기본 출력 확장자 ('txt')
        recognizer (sr.Recognizer): SpeechRecognition 인식기 인스턴스
    """
    data_flow: Tuple[DataType, DataType] = (DataType.AUDIO, DataType.TEXT)
    available_input_ext: list[str] = ["wav"]
    available_output_ext: list[str] = ["txt"]
    default_output_ext: str = "txt"

    def __init__(self):
        """
        Google 전사기를 초기화합니다.
        
        SpeechRecognition 라이브러리의 인식기 인스턴스를 생성합니다.
        """
        self.recognizer = sr.Recognizer()


    def process(self, buffer_dto: BufferDto, opt: dict = {}) -> BufferDto:
        """
        오디오 데이터를 Google API로 전사하여 텍스트로 변환합니다.
        
        Args:
            buffer_dto (BufferDto): 처리할 오디오 버퍼 데이터
            opt (dict, optional): 처리 옵션
        
        Returns:
            BufferDto: 전사된 텍스트가 포함된 버퍼 데이터
            
        Raises:
            ValueError: 지원되지 않는 데이터 타입인 경우
        """
        if not self.is_supported(buffer_dto):
            raise ValueError(f"GoogleTranscriber is not supported for {buffer_dto.data_type}")

        return BufferDto(
            buffer=self._transcribe(buffer_dto.buffer).encode('utf-8'),
            metadata={"recognizer": "google"},
            data_type=DataType.TEXT,
            status=BufferStatus.COMPLETED
        )


    def is_supported(self, buffer_dto: BufferDto) -> bool:
        """
        버퍼 데이터가 이 전사기에서 지원되는지 확인합니다.
        
        Args:
            buffer_dto (BufferDto): 확인할 버퍼 데이터
        
        Returns:
            bool: AUDIO 타입이고 지원하는 확장자인 경우 True
        """
        return buffer_dto.data_type == DataType.AUDIO and \
            audio_info.get_audio_extension(buffer_dto.buffer) in self.available_input_ext


    def _transcribe(self, audio: bytes) -> str:
        """
        오디오 바이너리 데이터를 Google API로 전사합니다.
        
        Args:
            audio (bytes): 전사할 오디오 바이너리 데이터
        
        Returns:
            str: 전사된 텍스트
            
        Raises:
            Exception: Google API 호출 실패 시
        """
        # 바이너리 데이터를 오디오 파일 객체로 변환
        audio_buffer = io.BytesIO(audio)
        try:
            with sr.AudioFile(audio_buffer) as source:
                # 오디오 데이터 읽기
                audio_data = self.recognizer.record(source)
                # Google API로 한국어 인식 수행
                text = self.recognizer.recognize_google(audio_data, language='ko-KR')
                return text
        except Exception as e:
            raise e