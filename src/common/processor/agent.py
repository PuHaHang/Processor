"""
스트림 데이터 처리를 위한 에이전트 모듈

이 모듈은 다양한 프로세서들을 연결하여 데이터 처리 파이프라인을 구성하고 실행하는 핵심 에이전트를 제공합니다.
URL에서 오디오를 다운로드하고, 필요시 형식을 변환한 후, STT를 통해 텍스트로 변환하는 전체 워크플로우를 관리합니다.
"""

import logfire
from src.common.processor.evaluator.strategies.yt_dlp_evaluator import YtDlpEvaluator
from src.common.rdb.common.database import DatabaseManager
from src.common.rdb.domain.recipe.models import RecipeState
from src.common.rdb.domain.recipe.recipe_base_service import RecipeBaseService
from .evaluator import Evaluator
from .converter import Converter
from .types import DataType, Payload, PayloadStatus
from .downloader import Downloader
from .formatter import Formatter
from .processor import Processor
from .processor_type import ProcessorType
from .transcriber import Transcriber
from .refiner import Refiner

# 예외 핸들러 import
from ..exception import (
    ExceptionHandler,
    RetryOnException,
    ValidationExceptionHandler,
    ExceptionType,
    ExceptionSeverity,
    ProcessingException,
    ValidationException
)


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

    db_manager = DatabaseManager()
    db_manager.initialize()

    recipe_base_service = RecipeBaseService()

    @ExceptionHandler(
        exception_type=ExceptionType.PIPELINE_ERROR,
        severity=ExceptionSeverity.HIGH,
        reraise=True,
        log_level="error",
        handler_name="agent_pipeline_handler"
    )
    @ValidationExceptionHandler(
        reraise=True,
        collect_errors=True
    )
    def process(self, payload: Payload, recipe_base_content_id: int, language: str) -> Payload:
        """
        버퍼 데이터를 처리 파이프라인을 통해 처리합니다.
        
        구성된 파이프라인의 각 프로세서를 순차적으로 실행하여
        데이터를 변환합니다. 각 단계에서 오류가 발생하면 
        재시도를 수행하고, 최종 실패 시 예외를 발생시킵니다.
        
        Args:
            payload (Payload): 처리할 버퍼 데이터 (초기에는 URL 텍스트)
            opt (dict, optional): 처리 옵션. 기본값은 빈 딕셔너리
        
        Returns:
            BufferDto: 처리된 버퍼 데이터 (최종적으로는 전사된 텍스트)
            
        Raises:
            ValueError: 프로세서가 지원되지 않거나 처리에 실패한 경우
        
        Example:
            >>> agent = Agent()
            >>> url_dto = Payload(
            ...     buffer="https://youtube.com/watch?v=...".encode(),
            ...     data_type=DataType.TEXT,
            ...     status=BufferStatus.INIT,
            ... )
            >>> result = agent.process(url_dto)
        """
        # 입력 유효성 검증
        if not payload:
            raise ValidationException(
                message="페이로드가 None입니다",
                field_name="payload",
                validation_rule="required"
            )
            
        if not payload.buffer:
            raise ValidationException(
                message="버퍼 데이터가 비어있습니다",
                field_name="buffer",
                validation_rule="not_empty"
            )
        
        # 파이프라인 구성
        pipeline = self._construct_pipeline(payload)
        metadatas = []  # 각 단계의 메타데이터 수집

        evaluator = Evaluator()
        logfire.info('Agent 처리 시작 {recipe_base_content_id}, data_type: {data_type}', recipe_base_content_id=recipe_base_content_id, data_type=payload.data_type.name)
        # 각 프로세서를 순차적으로 실행
        for processor in pipeline:
            # 버퍼 데이터 유효성 검사
            if not payload:
                raise ProcessingException(
                    message="파이프라인 중간에 페이로드가 None이 되었습니다",
                    processor_name=processor.get_processor_type().name
                )
            
            # 최대 재시도 횟수만큼 시도
            for retry_count in range(self.max_retry):
                # 현재 프로세서가 버퍼 데이터를 지원하는지 확인
                if processor.is_supported(payload):
                    # 프로세서 실행을 내부 메소드로 분리
                    with self.db_manager.session_scope() as session:
                        if any(downloader in processor.__class__.__bases__ for downloader in [Formatter, Downloader, YtDlpEvaluator]):
                            self.recipe_base_service.update_recipe_base_state(session, recipe_base_content_id, RecipeState.VERIFYING)
                        elif any(p in processor.__class__.__bases__ for p in [Evaluator]):
                            self.recipe_base_service.update_recipe_base_state(session, recipe_base_content_id, RecipeState.EVALUATING)
                        else:
                            self.recipe_base_service.update_recipe_base_state(session, recipe_base_content_id, RecipeState.TRANSFORMING)

                    success, result_payload = self._execute_processor_with_retry(processor, payload, evaluator, retry_count)

                    if success:
                        payload = result_payload
                        # 처리 결과의 메타데이터 저장
                        metadatas.append(payload.metadata)
                        logfire.debug('프로세서 처리 성공 {processor_type}', processor_type=processor.get_processor_type().name)
                        # 성공 시 재시도 루프 탈출
                        break
                    elif retry_count == self.max_retry - 1:
                        # 최종 실패 시 예외 발생
                        with self.db_manager.session_scope() as session:
                            self.recipe_base_service.update_recipe_base_state(session, recipe_base_content_id, RecipeState.FAILED)
                        raise ProcessingException(
                            message=f"프로세서 {processor.get_processor_type().name} 최종 실패",
                            processor_name=processor.get_processor_type().name
                        )
                    else:
                        # 재시도 로그
                        logfire.warn('프로세서 처리 실패, 재시도 중 {processor_type}, retry_count: {retry_count}', processor_type=processor.get_processor_type().name, retry_count=retry_count)
                        continue
                else:
                    # 프로세서가 현재 데이터 타입을 지원하지 않는 경우
                    with self.db_manager.session_scope() as session:
                        self.recipe_base_service.update_recipe_base_state(session, recipe_base_content_id, RecipeState.FAILED)
                    raise ValidationException(
                        message=f"프로세서 {processor.get_processor_type().name}가 {payload.data_type.name} 타입을 지원하지 않습니다",
                        field_name="data_type",
                        field_value=payload.data_type.name,
                        validation_rule="processor_compatibility"
                    )

            # 처리 상태 검증
            if payload.status != PayloadStatus.COMPLETED:
                raise ProcessingException(
                    message=f"프로세서 {processor.get_processor_type().name}가 데이터 처리를 완료하지 못했습니다",
                    processor_name=processor.get_processor_type().name
                )
            
            with self.db_manager.session_scope() as session:
                if any(downloader in processor.__class__.__bases__ for downloader in [Formatter, Downloader, YtDlpEvaluator]):
                    self.recipe_base_service.update_recipe_base_state(session, recipe_base_content_id, RecipeState.VERIFIED)
                elif any(p in processor.__class__.__bases__ for p in [Evaluator]):
                    pass
                else:
                    self.recipe_base_service.update_recipe_base_state(session, recipe_base_content_id, RecipeState.TRANSFORMED)
        
        # 전체 파이프라인의 메타데이터 출력 (디버깅용)
        # print("Pipeline metadata:", metadatas)

        payload.metadata = {}
        for md in metadatas:
            for key, value in md.items():
                payload.metadata[key] = value

        logfire.info('Agent 처리 완료 {recipe_base_content_id}', recipe_base_content_id=recipe_base_content_id)
        return payload

    @ExceptionHandler(
        exception_type=ExceptionType.PROCESSING_ERROR,
        severity=ExceptionSeverity.MEDIUM,
        reraise=False,
        default_return=(False, None),
        log_level="warning",
        handler_name="processor_execution_handler"
    )
    def _execute_processor_with_retry(self, processor: Processor, payload: Payload, evaluator: Evaluator, retry_count: int) -> tuple[bool, Payload]:
        """
        프로세서를 실행하고 평가를 수행하는 내부 메소드
        
        Args:
            processor (Processor): 실행할 프로세서
            payload (Payload): 처리할 페이로드
            evaluator (Evaluator): 평가기
            retry_count (int): 현재 재시도 횟수
            
        Returns:
            tuple[bool, Payload]: (성공 여부, 처리된 페이로드 또는 None)
        """
        # 프로세서 실행 로그
        logfire.debug('프로세서 실행 시작 {processor_type}', processor_type=processor.get_processor_type().name)
        
        # 실제 프로세서 실행
        processed_payload = processor.process(payload)
        
        if not evaluator.evaluate(processed_payload):
            raise ProcessingException(
                message="프로세서 출력이 유효하지 않습니다",
                processor_name=processor.get_processor_type().name
            )
        
        return True, processed_payload
        
    
    @ExceptionHandler(
        exception_type=ExceptionType.PIPELINE_ERROR,
        severity=ExceptionSeverity.MEDIUM,
        reraise=True,
        log_level="info",
        handler_name="pipeline_construction_handler"
    )
    def _construct_pipeline(self, payload: Payload, opt: dict = {}) -> list[Processor]:
        """
        처리 파이프라인을 구성합니다.
        
        현재는 하드코딩된 파이프라인을 반환하지만, 
        향후 가중치 최단 경로 탐색 알고리즘을 추가할 예정입니다.
        이를 통해 입력 데이터 타입과 원하는 출력 타입에 따라
        최적의 프로세서 경로를 자동으로 선택할 수 있게 됩니다.
        
        Args:
            payload (Payload): 처리할 버퍼 데이터 (파이프라인 결정에 사용)
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
        
        if payload.data_type == DataType.URL:
            return [
                Downloader(),     # 오디오 다운로드
                # Converter(),    # 오디오 형식 변환 (현재 비활성화)
                # Transcriber(),   # 오디오 → 텍스트 전사
                Refiner(),       # 텍스트 → 정제
            ]
        elif payload.data_type == DataType.TEXT:
            return [
                Refiner(),       # 텍스트 → 정제
            ]

    def get_available_processors(self) -> dict[ProcessorType, Processor]:
        """
        현재 사용 가능한 프로세서 목록을 반환합니다.
        
        Returns:
            dict[ProcessorType, Processor]: 프로세서 타입별 인스턴스 딕셔너리
        """
        return self.available_processors if hasattr(self, 'available_processors') else {}


    @ValidationExceptionHandler(reraise=True)
    def set_max_retry(self, retry_count: int) -> None:
        """
        최대 재시도 횟수를 설정합니다.
        
        Args:
            retry_count (int): 설정할 최대 재시도 횟수 (1 이상)
            
        Raises:
            ValueError: retry_count가 1보다 작은 경우
        """
        if retry_count < 1:
            raise ValidationException(
                message="재시도 횟수는 1 이상이어야 합니다",
                field_name="retry_count",
                field_value=retry_count,
                validation_rule="min_value"
            )
        self.max_retry = retry_count


    @ValidationExceptionHandler(reraise=True)
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
            raise ValidationException(
                message="파이프라인이 비어있습니다",
                field_name="pipeline",
                validation_rule="not_empty"
            )
            
        # 연속된 프로세서 간의 데이터 플로우 호환성 검사
        for i in range(len(pipeline) - 1):
            current_output = pipeline[i].get_data_flow()[1]   # 현재 프로세서의 출력 타입
            next_input = pipeline[i + 1].get_data_flow()[0]   # 다음 프로세서의 입력 타입
            
            if current_output != next_input:
                print(f"Pipeline validation failed: {pipeline[i].get_processor_type()} output ({current_output}) "
                      f"incompatible with {pipeline[i + 1].get_processor_type()} input ({next_input})")
                return False
                
        return True
