"""
OpenAI Whisper 전사기 모듈

이 모듈은 OpenAI Whisper API를 사용하여
오디오 데이터를 텍스트로 변환하는 전사기를 제공합니다.
대용량 오디오 파일을 청킹하여 처리하고, SRT 형식의 자막을 생성합니다.
"""

from collections.abc import Generator
import io
from typing import Tuple

from openai import OpenAI

from src.common.processor.common import audio_info, srt_parser
from src.common.processor.data_structure.buffer_status import BufferStatus
from src.common.processor.data_type import DataType
from src.common.processor.data_structure.buffer_dto import BufferDto
from src.common.processor.transcriber.transcriber import Transcriber


class OpenAITranscriber(Transcriber):
    """
    OpenAI Whisper API를 사용하는 전사기
    
    OpenAI의 Whisper 모델을 통해 오디오 파일을 텍스트로 변환합니다.
    다양한 언어를 지원하며 높은 정확도를 제공합니다.
    대용량 오디오 파일은 청킹하여 처리하고, SRT 형식으로 출력합니다.
    
    Attributes:
        data_flow (Tuple[DataType, DataType]): AUDIO → TEXT로 데이터 타입 변환
        available_input_ext (list[str]): 지원하는 입력 확장자 목록
        available_output_ext (list[str]): 지원하는 출력 확장자 목록
        default_output_ext (str): 기본 출력 확장자 ('txt')
        max_bytes_per_chunk (int): 청크당 최대 바이트 수 (OpenAI API 제한)
    """
    
    # 데이터 플로우 정의: 오디오 → 텍스트
    data_flow: Tuple[DataType, DataType] = (DataType.AUDIO, DataType.TEXT)
    
    # 지원하는 오디오 형식들 (OpenAI Whisper API 지원 형식)
    available_input_ext: list[str] = ["flac", "m4a", "mp3", "mp4", "mpeg", "mpga", "oga", "ogg", "wav", "webm"]
    available_output_ext: list[str] = ["txt"]
    default_output_ext: str = "txt"

    # OpenAI API 업로드 제한 (약 25MB)
    max_bytes_per_chunk: int = 26267012

    def __init__(self):
        """
        OpenAI Transcriber를 초기화합니다.
        
        OpenAI API 키는 환경변수나 설정에서 자동으로 로드됩니다.
        """
        pass

    def process(self, buffer_dto: BufferDto, opt: dict = {}) -> BufferDto:
        """
        오디오 데이터를 OpenAI Whisper API로 전사하여 텍스트로 변환합니다.
        
        대용량 오디오 파일은 청킹하여 처리하고, SRT 형식의 자막으로 출력합니다.
        
        Args:
            buffer_dto (BufferDto): 처리할 오디오 버퍼 데이터
            opt (dict, optional): 처리 옵션. 기본값은 빈 딕셔너리
        
        Returns:
            BufferDto: 전사된 텍스트(SRT 형식)가 포함된 버퍼 데이터
            
        Raises:
            ValueError: 지원되지 않는 오디오 형식인 경우
        """
        # 지원되는 오디오 형식인지 확인
        if not self.is_supported(buffer_dto):
            raise ValueError(f"Audio is not supported. Supported formats: {self.available_input_ext}")

        # 오디오 전사 수행 및 결과 반환
        return BufferDto(
            buffer=self._transcribe_by_stream(buffer_dto.buffer).encode('utf-8'),
            metadata={
                "model": "whisper-1",
                "language": "ko",
                "response_format": "srt",
            },
            data_type=self.data_flow[1],
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
        return self.data_flow[0] == buffer_dto.data_type and \
            audio_info.get_audio_extension(buffer_dto.buffer) in self.available_input_ext


    def _transcribe_by_stream(self, audio: bytes) -> str:
        """
        OpenAI Whisper API를 사용하여 오디오를 텍스트로 변환합니다.
        
        대용량 오디오 파일은 청킹하여 처리하고, 각 청크의 결과를 병합합니다.
        
        사용 가능한 모델:
        - whisper-1: OpenAI의 기본 Whisper 모델 (가장 정확함, 처리 시간이 오래 걸림)
        - gpt-4o: GPT-4o 모델의 음성 인식 기능 (빠른 처리, 실시간에 적합)
        - gpt-4o-mini: GPT-4o-mini 모델의 음성 인식 기능 (가장 빠름, 정확도는 상대적으로 낮음)
        
        Args:
            audio (bytes): 전사할 오디오 바이너리 데이터
        
        Returns:
            str: 전사된 텍스트 (SRT 형식)
            
        Raises:
            Exception: OpenAI API 호출 실패 시
        """
        try:
            # OpenAI 클라이언트 초기화
            client = OpenAI()
            
            # 오디오 데이터를 청크로 분할
            chunks = self._create_audio_stream(audio)
            transcripts = []

            # 각 청크에 대해 Whisper API 호출
            idx = 0
            while True:
                chunk, time_offset = next(chunks)
                if chunk is None:
                    break
                
                try:
                    # Whisper API 호출
                    response = client.audio.transcriptions.create(
                        model="whisper-1",  # 사용 가능한 모델: "whisper-1", "gpt-4o", "gpt-4o-mini"
                        file=chunk,
                        response_format="srt",  # text, srt, verbose_json, json, vtt
                    )
                    
                    # 결과와 시간 오프셋 저장
                    transcripts.append((idx, response, time_offset))
                except Exception as e:
                    # 개별 청크 처리 실패 시 예외 발생
                    raise e
                idx += 1
            
            # 모든 청크의 SRT 결과를 병합
            return srt_parser.merge_srt_chunks(
                [
                    (transcript[1], transcript[2])
                    for transcript in sorted(transcripts, key=lambda x: x[0])
                ]
            )
        except Exception as e:
            # API 호출 실패 시 예외 발생
            raise e
            raise Exception(f"OpenAI Whisper transcription failed: {str(e)}")
