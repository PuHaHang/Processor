"""
동적 의존성 주입 시스템

이 모듈은 데코레이터를 통해 데이터베이스 세션과 서비스 의존성을
자동으로 주입하는 시스템을 제공합니다.
"""

import functools
import inspect
import logging
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union, get_type_hints, cast
from contextlib import contextmanager

from sqlalchemy.orm import Session

from .database import get_database_manager, DatabaseManager

logger = logging.getLogger(__name__)

# 타입 변수 정의
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])


class DependencyContainer:
    """의존성 컨테이너 클래스"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[[], Any]] = {}
        self._singletons: Dict[str, Any] = {}
        
    def register_service(self, service_type: Type[T], instance: T) -> None:
        """서비스 인스턴스를 등록합니다."""
        service_name = service_type.__name__
        self._services[service_name] = instance
        logger.debug(f"Registered service: {service_name}")
        
    def register_factory(self, service_type: Type[T], factory: Callable[[], T]) -> None:
        """서비스 팩토리를 등록합니다."""
        service_name = service_type.__name__
        self._factories[service_name] = factory
        logger.debug(f"Registered factory: {service_name}")
        
    def register_singleton(self, service_type: Type[T], factory: Callable[[], T]) -> None:
        """싱글톤 서비스를 등록합니다."""
        service_name = service_type.__name__
        self._factories[service_name] = factory
        logger.debug(f"Registered singleton: {service_name}")
        
    def get_service(self, service_type: Type[T]) -> T:
        """서비스를 가져옵니다."""
        service_name = service_type.__name__
        
        # 싱글톤 확인
        if service_name in self._singletons:
            return self._singletons[service_name]
            
        # 등록된 서비스 확인
        if service_name in self._services:
            return self._services[service_name]
            
        # 팩토리 확인
        if service_name in self._factories:
            instance = self._factories[service_name]()
            # 싱글톤으로 등록된 경우 캐시
            if service_name in self._factories:
                self._singletons[service_name] = instance
            return instance
            
        raise ValueError(f"Service {service_name} not found")
        
    def clear(self) -> None:
        """모든 의존성을 제거합니다."""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()


# 글로벌 의존성 컨테이너
container = DependencyContainer()


def get_container() -> DependencyContainer:
    """의존성 컨테이너를 반환합니다."""
    return container


class DatabaseSession:
    """데이터베이스 세션을 나타내는 마커 클래스"""
    pass


def inject_session(func: F) -> F:
    """
    데이터베이스 세션을 함수에 주입하는 데코레이터
    
    Usage:
        @inject_session
        def my_function(session: Session):
            # 세션을 사용한 데이터베이스 작업
            pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 함수 시그니처 분석
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)
        
        # 세션 파라미터 찾기
        session_param = None
        for param_name, param in sig.parameters.items():
            if param_name == 'session' or type_hints.get(param_name) == Session:
                session_param = param_name
                break
                
        if session_param is None:
            # 세션이 필요하지 않은 함수인 경우 그대로 실행
            return func(*args, **kwargs)
            
        # 이미 세션이 전달된 경우 그대로 사용
        if session_param in kwargs:
            return func(*args, **kwargs)
            
        # 세션 생성 및 주입
        db_manager = get_database_manager()
        with db_manager.session_scope() as session:
            kwargs[session_param] = session
            return func(*args, **kwargs)
            
    return wrapper  # type: ignore


def inject_dependencies(*dependency_types: Type[Any]) -> Callable[[F], F]:
    """
    의존성을 함수에 주입하는 데코레이터
    
    Usage:
        @inject_dependencies(UserService, RecipeService)
        def my_function(user_service: UserService, recipe_service: RecipeService):
            # 서비스들을 사용한 비즈니스 로직
            pass
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 함수 시그니처 분석
            sig = inspect.signature(func)
            type_hints = get_type_hints(func)
            
            # 의존성 주입
            for param_name, param in sig.parameters.items():
                param_type = type_hints.get(param_name)
                
                # 이미 값이 전달된 경우 스킵
                if param_name in kwargs:
                    continue
                    
                # 지정된 의존성 타입 중 하나인 경우 주입
                if param_type in dependency_types:
                    try:
                        kwargs[param_name] = container.get_service(param_type)
                    except ValueError:
                        logger.warning(f"Dependency {param_type.__name__} not found")
                        
            return func(*args, **kwargs)
            
        return wrapper  # type: ignore
    return decorator


def inject_db_service(func: F) -> F:
    """
    데이터베이스 세션과 서비스를 자동으로 주입하는 데코레이터
    
    Usage:
        @inject_db_service
        def my_function(session: Session, user_service: UserService):
            # 세션과 서비스가 자동으로 주입됨
            pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 함수 시그니처 분석
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)
        
        # 세션 주입
        session_param = None
        for param_name, param in sig.parameters.items():
            if param_name == 'session' or type_hints.get(param_name) == Session:
                session_param = param_name
                break
                
        # 의존성 주입
        injected_dependencies = []
        for param_name, param in sig.parameters.items():
            param_type = type_hints.get(param_name)
            
            # 이미 값이 전달된 경우 스킵
            if param_name in kwargs:
                continue
                
            # 세션이 아니고 등록된 서비스인 경우 주입
            if param_type and param_type != Session and param_name != session_param:
                try:
                    kwargs[param_name] = container.get_service(param_type)
                    injected_dependencies.append(param_type.__name__)
                except ValueError:
                    # 등록되지 않은 의존성은 무시
                    pass
                    
        logger.debug(f"Injected dependencies: {injected_dependencies}")
        
        # 세션이 필요한 경우 세션 스코프 내에서 실행
        if session_param and session_param not in kwargs:
            db_manager = get_database_manager()
            with db_manager.session_scope() as session:
                kwargs[session_param] = session
                return func(*args, **kwargs)
        else:
            return func(*args, **kwargs)
            
    return wrapper  # type: ignore


def transactional(func: F) -> F:
    """
    트랜잭션 범위를 관리하는 데코레이터
    
    Usage:
        @transactional
        def my_function(session: Session):
            # 트랜잭션 내에서 실행됨
            # 예외 발생 시 자동으로 롤백
            pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 함수 시그니처 분석
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)
        
        # 세션 파라미터 찾기
        session_param = None
        for param_name, param in sig.parameters.items():
            if param_name == 'session' or type_hints.get(param_name) == Session:
                session_param = param_name
                break
                
        if session_param is None:
            # 세션이 필요하지 않은 함수인 경우 그대로 실행
            return func(*args, **kwargs)
            
        # 이미 세션이 전달된 경우 그대로 사용 (중첩 트랜잭션 방지)
        if session_param in kwargs:
            return func(*args, **kwargs)
            
        # 트랜잭션 스코프 내에서 실행
        db_manager = get_database_manager()
        with db_manager.session_scope() as session:
            kwargs[session_param] = session
            return func(*args, **kwargs)
            
    return wrapper  # type: ignore


@contextmanager
def dependency_scope(**dependencies):
    """
    임시 의존성 스코프를 생성하는 컨텍스트 매니저
    
    Usage:
        with dependency_scope(user_service=user_service_instance):
            # 이 스코프 내에서만 의존성이 유효
            my_function()
    """
    original_services = container._services.copy()
    
    try:
        # 임시 의존성 등록
        for name, service in dependencies.items():
            container._services[name] = service
        yield
    finally:
        # 원래 상태로 복원
        container._services = original_services


def setup_default_dependencies():
    """기본 의존성들을 설정합니다."""
    # 데이터베이스 매니저 등록
    container.register_service(DatabaseManager, get_database_manager())
    
    logger.info("Default dependencies registered")


# 모듈 로드 시 기본 의존성 설정
setup_default_dependencies() 