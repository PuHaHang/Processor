"""
전사기 기본 클래스 모듈

이 모듈은 오디오를 텍스트로 변환하는 모든 전사기가 상속받는 추상 기본 클래스를 정의합니다.
"""

from abc import ABC
from collections.abc import Generator
import io

from ..common import get_audio_extension, get_audio_duration
from ..processor import Processor
from ..processor_type import ProcessorType

class TranscriberStrategy (Processor, ABC):
    """
    오디오 전사를 수행하는 프로세서의 기본 추상 클래스
    
    오디오 데이터를 텍스트로 변환하는 음성 인식 프로세서들이
    상속받는 기본 클래스입니다.
    
    Attributes:
        processor_type (ProcessorType): 전사기 타입으로 고정
    """
    processor_type: ProcessorType = ProcessorType.TRANSCRIBER
    max_bytes_per_chunk: int = 0


    def _create_audio_stream(self, audio: bytes) -> Generator[tuple[io.BytesIO|None, float], None, None]:
        """
        오디오 데이터를 청크로 분할하여 스트림 목록을 생성합니다.
        
        OpenAI API의 파일 크기 제한을 고려하여 오디오를 적절한 크기로 분할합니다.
        각 청크는 시간 오프셋과 함께 반환되어 나중에 SRT 병합 시 사용됩니다.
        
        Args:
            audio (bytes): 분할할 오디오 바이너리 데이터
        
        Returns:
            list[tuple[io.BytesIO, float]]: 청크 리스트 (버퍼, 시간_오프셋)
        """
        max_bytes_per_chunk = self.max_bytes_per_chunk if self.max_bytes_per_chunk > 0 else 1024 ** 4
        # 오디오 포맷 감지
        ext = get_audio_extension(audio)
        
        # 최대 청크 크기에 따라 오디오 분할
        time_offset = 0.0
        audio_stream = io.BytesIO(audio)
        while audio_stream.tell() < len(audio):
            # 청크 추출
            chunk_data = audio_stream.read(max_bytes_per_chunk)

            # 청크를 바이너리 버퍼로 변환
            buffer = io.BytesIO(chunk_data)
            buffer.seek(0)
            buffer.name = f"chunk_{audio_stream.tell()}.{ext}"

            # 청크와 시간 오프셋 저장
            yield buffer, time_offset

            # 다음 청크의 시간 오프셋 계산
            time_offset += get_audio_duration(buffer.getvalue())
            print(f"Chunk {audio_stream.tell()//max_bytes_per_chunk + 1} created, time offset: {time_offset:.2f}s")

        yield None, time_offset
    