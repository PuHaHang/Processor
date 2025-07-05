"""
스트림 데이터 처리를 위한 에이전트 모듈

이 모듈은 다양한 프로세서들을 연결하여 데이터 처리 파이프라인을 구성하고 실행하는 핵심 에이전트를 제공합니다.
URL에서 오디오를 다운로드하고, 필요시 형식을 변환한 후, STT를 통해 텍스트로 변환하는 전체 워크플로우를 관리합니다.
"""

from src.common.processor.data_structure.buffer_dto import BufferDto
from src.common.processor.data_structure.buffer_status import BufferStatus
from src.common.processor.downloader.yt_dlp_downloader import YtDlpDownloader
from src.common.processor.processor import Processor
from src.common.processor.processor_type import ProcessorType
from src.common.processor.transcriber.openai_transcriber import OpenAITranscriber


class Agent:
    """
    데이터 처리 파이프라인을 관리하는 에이전트 클래스
    
    다양한 프로세서들을 연결하여 URL에서 오디오를 다운로드하고, 
    형식을 변환한 후 음성 인식을 수행하는 전체 파이프라인을 관리합니다.
    강건한 오류 처리와 재시도 메커니즘을 제공합니다.
    
    처리 흐름:
    1. URL 분류 (YouTube, Twitter 등 플랫폼 식별)
    2. 오디오 다운로드 (yt-dlp 사용)
    3. [선택적] 오디오 형식 변환
    4. STT 전사 (OpenAI Whisper 또는 Google)
    
    Attributes:
        available_processors (dict[ProcessorType, Processor]): 사용 가능한 프로세서 목록
        max_retry (int): 각 프로세서의 최대 재시도 횟수 (기본 3회)
    """
    # 사용 가능한 프로세서들을 타입별로 관리
    available_processors: dict[ProcessorType, Processor]
    
    # 프로세서 처리 실패 시 최대 재시도 횟수
    max_retry: int = 3

    def process(self, buffer_dto: BufferDto, opt: dict = {}) -> BufferDto:
        """
        버퍼 데이터를 처리 파이프라인을 통해 처리합니다.
        
        구성된 파이프라인의 각 프로세서를 순차적으로 실행하여
        데이터를 변환합니다. 각 단계에서 오류가 발생하면 
        재시도를 수행하고, 최종 실패 시 예외를 발생시킵니다.
        
        Args:
            buffer_dto (BufferDto): 처리할 버퍼 데이터 (초기에는 URL 텍스트)
            opt (dict, optional): 처리 옵션. 기본값은 빈 딕셔너리
        
        Returns:
            BufferDto: 처리된 버퍼 데이터 (최종적으로는 전사된 텍스트)
            
        Raises:
            ValueError: 프로세서가 지원되지 않거나 처리에 실패한 경우
        
        Example:
            >>> agent = Agent()
            >>> url_dto = BufferDto(
            ...     buffer="https://youtube.com/watch?v=...".encode(),
            ...     data_type=DataType.TEXT,
            ...     status=BufferStatus.INIT
            ... )
            >>> result = agent.process(url_dto)
            >>> print(result.get_buffer_string())  # 전사된 텍스트 출력
        """
        # 파이프라인 구성
        pipeline = self._construct_pipeline(buffer_dto, opt)
        metadatas = []  # 각 단계의 메타데이터 수집

        # 각 프로세서를 순차적으로 실행
        for processor in pipeline:
            # 버퍼 데이터 유효성 검사
            if not buffer_dto:
                raise ValueError("BufferDto is None")
                
            # 최대 재시도 횟수만큼 시도
            for retry_count in range(self.max_retry):
                # 현재 프로세서가 버퍼 데이터를 지원하는지 확인
                if processor.is_supported(buffer_dto):
                    try:
                        # 프로세서 실행 로그
                        print(f"{processor.get_processor_type()} processing")
                        
                        # 실제 프로세서 실행
                        buffer_dto = processor.process(buffer_dto)
                        
                        # 처리 결과의 메타데이터 저장
                        metadatas.append(buffer_dto.metadata)
                        
                        # 성공 시 재시도 루프 탈출
                        break
                        
                    except Exception as e:
                        # 마지막 시도가 아니면 재시도
                        if retry_count == self.max_retry - 1:
                            # 최종 실패 시 예외 재발생
                            raise e
                        
                        # 재시도 로그
                        print(f"Processor {processor.get_processor_type()} failed to process {buffer_dto.get_data_type()}")
                        continue
                else:
                    # 프로세서가 현재 데이터 타입을 지원하지 않는 경우
                    raise ValueError(f"Processor {processor.get_processor_type()} is not supported for {buffer_dto.get_data_type()}")

            # 처리 상태 검증
            if buffer_dto.get_status() != BufferStatus.COMPLETED:
                raise ValueError(f"Processor {processor.get_processor_type()} failed to process {buffer_dto.get_data_type()}")
        
        # 전체 파이프라인의 메타데이터 출력 (디버깅용)
        print("Pipeline metadata:", metadatas)
        return buffer_dto

    
    def _construct_pipeline(self, buffer_dto: BufferDto, opt: dict = {}) -> list[Processor]:
        """
        처리 파이프라인을 구성합니다.
        
        현재는 하드코딩된 파이프라인을 반환하지만, 
        향후 가중치 최단 경로 탐색 알고리즘을 추가할 예정입니다.
        이를 통해 입력 데이터 타입과 원하는 출력 타입에 따라
        최적의 프로세서 경로를 자동으로 선택할 수 있게 됩니다.
        
        Args:
            buffer_dto (BufferDto): 처리할 버퍼 데이터 (파이프라인 결정에 사용)
            opt (dict, optional): 파이프라인 구성 옵션
                - 'target_format': 원하는 최종 출력 형식
                - 'quality': 처리 품질 설정 ('fast', 'balanced', 'high')
                - 'language': 전사 언어 설정
        
        Returns:
            list[Processor]: 처리 파이프라인 목록 (실행 순서대로)
        
        Note:
            현재 구현된 파이프라인:
            1. UrlClassifier: URL에서 플랫폼과 비디오 ID 추출
            2. YtDlpDownloader: YouTube 등에서 오디오 다운로드
            3. OpenAITranscriber: Whisper API를 통한 STT 변환
            
            AudioConverter는 현재 비활성화됨 (WebM → 직접 전사)
        """
        # TODO: 가중치 최단 경로 탐색 알고리즘 추가 영역
        # 향후 개선사항:
        # - 입력/출력 데이터 타입 기반 경로 탐색
        # - 프로세서별 품질/속도 가중치 적용
        # - 사용자 선호도 반영 (속도 vs 품질)
        # - 동적 프로세서 선택 (API 가용성, 비용 등)
        
        return [
            YtDlpDownloader(),     # 오디오 다운로드
            # AudioConverter(),    # 오디오 형식 변환 (현재 비활성화)
            OpenAITranscriber(),   # 오디오 → 텍스트 전사
        ]


    def get_available_processors(self) -> dict[ProcessorType, Processor]:
        """
        현재 사용 가능한 프로세서 목록을 반환합니다.
        
        Returns:
            dict[ProcessorType, Processor]: 프로세서 타입별 인스턴스 딕셔너리
        """
        return self.available_processors if hasattr(self, 'available_processors') else {}


    def set_max_retry(self, retry_count: int) -> None:
        """
        최대 재시도 횟수를 설정합니다.
        
        Args:
            retry_count (int): 설정할 최대 재시도 횟수 (1 이상)
            
        Raises:
            ValueError: retry_count가 1보다 작은 경우
        """
        if retry_count < 1:
            raise ValueError("Retry count must be at least 1")
        self.max_retry = retry_count


    def validate_pipeline(self, pipeline: list[Processor]) -> bool:
        """
        파이프라인의 연결 유효성을 검증합니다.
        
        각 프로세서의 출력이 다음 프로세서의 입력과 호환되는지 확인합니다.
        
        Args:
            pipeline (list[Processor]): 검증할 파이프라인
            
        Returns:
            bool: 파이프라인이 유효하면 True, 아니면 False
        """
        if not pipeline:
            return False
            
        # 연속된 프로세서 간의 데이터 플로우 호환성 검사
        for i in range(len(pipeline) - 1):
            current_output = pipeline[i].get_data_flow()[1]   # 현재 프로세서의 출력 타입
            next_input = pipeline[i + 1].get_data_flow()[0]   # 다음 프로세서의 입력 타입
            
            if current_output != next_input:
                print(f"Pipeline validation failed: {pipeline[i].get_processor_type()} output ({current_output}) "
                      f"incompatible with {pipeline[i + 1].get_processor_type()} input ({next_input})")
                return False
                
        return True
