

from ..types import Payload

from .evaluator_strategy import EvaluatorStrategy
from .strategies import InitEvaluator, YtDlpEvaluator


class Evaluator:
    # 사용 가능한 평가 전략들을 리스트로 관리
    # 현재는 YouTube 다운로더 전용 평가기만 등록됨
    strategies: list[EvaluatorStrategy] = [
        InitEvaluator(),
        YtDlpEvaluator(),
    ]

    strategy_map: dict[type, list[EvaluatorStrategy]] = {}

    def __init__(self):
        # 동적으로 전략 매핑 테이블 생성 | 순환 참조 방지
        for strategy in self.strategies:
            for processor in strategy.get_available_processors():
                if processor not in self.strategy_map:
                    self.strategy_map[processor] = []
                self.strategy_map[processor].append(strategy)

    def evaluate(self, payload: Payload) -> bool:
        # 페이로드에 적합한 평가 전략을 찾음
        strategy = self._get_context(payload)
        
        # 적합한 전략이 없으면 기본적으로 True 반환 (통과)
        if not strategy:
            return True
        
        # 찾은 전략으로 실제 평가 수행
        return strategy.evaluate(payload)
    
    def _get_context(self, payload: Payload) -> EvaluatorStrategy|None:
        processor = payload.get_processor()
        if processor is None:
            return None
        
        # 등록된 모든 전략을 순회하면서
        for strategy in self.strategy_map[processor]:
            # 현재 페이로드를 지원하는 전략이 있는지 확인
            if strategy.is_supported(payload):
                return strategy
        
        # 지원하는 전략이 없으면 None 반환
        return None