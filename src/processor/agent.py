"""
스트림 데이터 처리를 위한 에이전트 모듈

이 모듈은 다양한 프로세서들을 연결하여 데이터 처리 파이프라인을 구성하고 실행하는 핵심 에이전트를 제공합니다.
"""

from src.processor.classifier.url_classifier import UrlClassifier
from src.processor.converter.audio_converter import AudioConverter
from src.processor.data_structure.buffer_dto import BufferDto
from src.processor.data_structure.buffer_status import BufferStatus
from src.processor.downloader.yt_dlp_downloader import YtDlpDownloader
from src.processor.processor import Processor
from src.processor.processor_type import ProcessorType
from src.processor.transcriber.openai_transcriber import OpenAITranscriber


class Agent:
    """
    데이터 처리 파이프라인을 관리하는 에이전트 클래스
    
    다양한 프로세서들을 연결하여 URL에서 오디오를 다운로드하고, 
    형식을 변환한 후 음성 인식을 수행하는 전체 파이프라인을 관리합니다.
    
    Attributes:
        available_processors (dict[ProcessorType, Processor]): 사용 가능한 프로세서 목록
        max_retry (int): 각 프로세서의 최대 재시도 횟수
    """
    available_processors: dict[ProcessorType, Processor]
    max_retry: int = 3

    def process(self, buffer_dto: BufferDto, opt: dict = {}) -> BufferDto:
        """
        버퍼 데이터를 처리 파이프라인을 통해 처리합니다.
        
        Args:
            buffer_dto (BufferDto): 처리할 버퍼 데이터
            opt (dict, optional): 처리 옵션. 기본값은 빈 딕셔너리
        
        Returns:
            BufferDto: 처리된 버퍼 데이터
            
        Raises:
            ValueError: 프로세서가 지원되지 않거나 처리에 실패한 경우
        """
        # 파이프라인 구성
        pipeline = self._construct_pipeline(buffer_dto, opt)
        metadatas = []

        # 각 프로세서를 순차적으로 실행
        for processor in pipeline:
            if not buffer_dto:
                raise ValueError("BufferDto is None")
            # 최대 재시도 횟수만큼 시도
            for _ in range(self.max_retry):
                if processor.is_supported(buffer_dto):
                    try:
                        print(f"{processor.get_processor_type()} processing")
                        buffer_dto = processor.process(buffer_dto)
                        metadatas.append(buffer_dto.metadata)
                    except Exception as e:
                        # 마지막 시도가 아니면 재시도
                        if _ == self.max_retry - 1:
                            raise e
                        print(f"Processor {processor.get_processor_type()} failed to process {buffer_dto.get_data_type()}")
                        continue
                    break
                else:
                    raise ValueError(f"Processor {processor.get_processor_type()} is not supported for {buffer_dto.get_data_type()}")

            # 처리 상태 확인
            if buffer_dto.get_status() != BufferStatus.COMPLETED:
                raise ValueError(f"Processor {processor.get_processor_type()} failed to process {buffer_dto.get_data_type()}")
        
        print(metadatas)
        return buffer_dto

    
    def _construct_pipeline(self, buffer_dto: BufferDto, opt: dict = {}) -> list[Processor]:
        """
        처리 파이프라인을 구성합니다.
        
        현재는 하드코딩된 파이프라인을 반환하지만, 
        향후 가중치 최단 경로 탐색 알고리즘을 추가할 예정입니다.
        
        Args:
            buffer_dto (BufferDto): 처리할 버퍼 데이터
            opt (dict, optional): 파이프라인 구성 옵션
        
        Returns:
            list[Processor]: 처리 파이프라인 목록
        """
        # TODO: 가중치 최단 경로 탐색 알고리즘 추가 영역
        return [
            UrlClassifier(),       # URL 분류
            YtDlpDownloader(),     # 오디오 다운로드
            # AudioConverter(),      # 오디오 형식 변환
            OpenAITranscriber(),   # 오디오 전사
        ]
