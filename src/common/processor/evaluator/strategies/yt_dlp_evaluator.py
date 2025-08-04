
from ...formatter.strategies.youtube_formatter import YoutubeFormatter
from ...formatter.formatter_strategy import FormatterStrategy
from ...types import Payload
from ...downloader.strategies.yt_dlp_downloader import YtDlpDownloader

# 부모 평가 전략 클래스 import
from ..evaluator_strategy import EvaluatorStrategy

class YtDlpEvaluator (EvaluatorStrategy):
    # 이 평가기가 지원하는 프로세서 - YtDlpDownloader만 지원
    available_processors: list[type] = [YtDlpDownloader]
    
    # 사용 가능한 포맷터들 - 현재는 YouTube 포맷터만 지원
    formatters: list[FormatterStrategy] = [
        YoutubeFormatter(),
    ]

    # 평가에 사용할 메타데이터 키들 - 제목과 설명을 기준으로 판단
    target_keys: list[str] = [
        'title',
        "description",
    ]

    def is_supported(self, payload: Payload) -> bool:
        # 페이로드가 YtDlpDownloader로 처리된 경우에만 지원
        print(f"payload.get_processor(): {payload.get_processor()}")
        print(f"type(payload.get_processor()): {type(payload.get_processor())}")
        print(f"self.available_processors: {self.available_processors}")
        print(f"type(payload.get_processor()) in self.available_processors: {type(payload.get_processor()) in self.available_processors}")
        return type(payload.get_processor()) in self.available_processors

    def evaluate(self, payload: Payload) -> bool:
        # 페이로드에 메타데이터가 있는지 확인
        if payload.get_metadata():
            target = {}
            
            # 평가 대상 키들(title, description)만 추출
            for key in self.target_keys:
                if key in payload.get_metadata():
                    target[key] = payload.get_metadata()[key]
            
            # 추출한 메타데이터를 부모 클래스의 분류기로 평가
            return super()._evaluate(target)
        
        # 메타데이터가 없으면 평가 실패
        return False
