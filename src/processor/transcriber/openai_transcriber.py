"""
OpenAI Whisper 전사기 모듈

이 모듈은 OpenAI Whisper API를 사용하여
오디오 데이터를 텍스트로 변환하는 전사기를 제공합니다.

Note: 현재 구현되지 않은 상태입니다.
"""

import io
from typing import Tuple

from openai import OpenAI
from pydub import AudioSegment

from src.processor.common import audio_info, srt_parser
from src.processor.data_structure.buffer_status import BufferStatus
from src.processor.data_type import DataType
from src.processor.data_structure.buffer_dto import BufferDto
from src.processor.transcriber.transcriber import Transcriber


class OpenAITranscriber(Transcriber):
    """
    OpenAI Whisper API를 사용하는 전사기
    
    OpenAI의 Whisper 모델을 통해 오디오 파일을 텍스트로 변환합니다.
    다양한 언어를 지원하며 높은 정확도를 제공합니다.
    """
    data_flow: Tuple[DataType, DataType] = (DataType.AUDIO, DataType.TEXT)
    available_input_ext: list[str] = ["flac", "m4a", "mp3", "mp4", "mpeg", "mpga", "oga", "ogg", "wav", "webm"]
    available_output_ext: list[str] = ["txt"]
    default_output_ext: str = "txt"

    max_bytes_per_chunk: int = 26267012

    def __init__(self):
        pass

    def process(self, buffer_dto: BufferDto, opt: dict = {}) -> BufferDto:
        if not self.is_supported(buffer_dto):
            raise ValueError(f"Audio is not supported. Supported formats: {self.available_input_ext}")

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
        return self.data_flow[0] == buffer_dto.data_type and \
            audio_info.get_audio_extension(buffer_dto.buffer) in self.available_input_ext


    def _transcribe_by_stream(self, audio: bytes) -> str:
        """
        OpenAI Whisper API를 사용하여 오디오를 텍스트로 변환합니다.
        
        사용 가능한 모델:
        - whisper-1: OpenAI의 기본 Whisper 모델 (가장 정확함, 처리 시간이 오래 걸림)
        - gpt-4o: GPT-4o 모델의 음성 인식 기능 (빠른 처리, 실시간에 적합)
        - gpt-4o-mini: GPT-4o-mini 모델의 음성 인식 기능 (가장 빠름, 정확도는 상대적으로 낮음)
        
        Args:
            audio (bytes): 전사할 오디오 바이너리 데이터
        
        Returns:
            str: 전사된 텍스트
            
        Raises:
            Exception: OpenAI API 호출 실패 시
        """
        try:
            # OpenAI 클라이언트 초기화
            client = OpenAI()
            
            # 오디오 데이터를 스트림으로 변환
            chunks = self._create_audio_stream(audio)
            transcripts = []

            # Whisper API 호출 (스트림 형태로 처리)x
            for idx, (chunk, time_offset) in enumerate(chunks):
                try:
                    response = client.audio.transcriptions.create(
                        model="whisper-1",  # 사용 가능한 모델: "whisper-1", "gpt-4o", "gpt-4o-mini"
                        file=chunk,
                        response_format="srt",  # text, srt, verbose_json, json, vtt
                    )
                    transcripts.append((idx, response, time_offset))
                except Exception as e:
                    raise e
            
            return srt_parser.merge_srt_chunks(
                [
                    (transcript[1], transcript[2])
                    for transcript in sorted(transcripts, key=lambda x: x[0])
                ]
            )
        except Exception as e:
            raise e
            raise Exception(f"OpenAI Whisper transcription failed: {str(e)}")


    def _create_audio_stream(self, audio: bytes) -> list[tuple[io.BytesIO, float]]:
        ext = audio_info.get_audio_extension(audio)
        audio_segment = AudioSegment.from_file(io.BytesIO(audio), format=ext)
        chunks = []
        time_offset = 0.0
        for i in range(0, len(audio_segment), self.max_bytes_per_chunk):
            chunk = audio_segment[i:i + self.max_bytes_per_chunk]

            buffer = io.BytesIO()
            chunk.export(buffer, format=ext)
            buffer.seek(0)
            buffer.name = f"chunk_{i}.{ext}"
            chunks.append((buffer, time_offset))

            time_offset += audio_info.get_audio_duration(buffer.getvalue())
            print(time_offset)
        return chunks
    