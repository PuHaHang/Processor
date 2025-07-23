"""
RDB Common 모듈

이 패키지는 데이터베이스 관련 공통 기능을 제공합니다.
새로운 ERD 구조에 따라 모델들이 여러 테이블로 분산되어 있습니다.
"""

from .database import (
    Base,
    DatabaseManager,
    db_manager,
    get_database_manager,
    get_session,
    initialize_database
)

from .dependency_injection import (
    DependencyContainer,
    container,
    get_container,
    inject_session,
    inject_dependencies,
    inject_db_service,
    transactional,
    dependency_scope,
    setup_default_dependencies
)

from .models import (
    # User 도메인 모델
    User,
    UserProfile,
    UserBilling,
    UserAlert,
    
    # User 도메인 enum
    UserProvider,
    UserBillingType,
    UserRegion,
    UserRole,
    
    # Recipe 도메인 모델
    RecipeBase,
    RecipeBaseContent,
    RecipeBaseStatus,
    Ingredient,
    Recipe,
    
    # Recipe 도메인 enum
    RecipeLanguage,
    RecipeDifficulty,
    RecipeState
)

__all__ = [
    # Database
    "Base",
    "DatabaseManager",
    "db_manager",
    "get_database_manager",
    "get_session",
    "initialize_database",
    
    # Dependency Injection
    "DependencyContainer",
    "container",
    "get_container",
    "inject_session",
    "inject_dependencies",
    "inject_db_service",
    "transactional",
    "dependency_scope",
    "setup_default_dependencies",
    
    # User 도메인 모델
    "User",
    "UserProfile",
    "UserBilling",
    "UserAlert",
    
    # User 도메인 enum
    "UserProvider",
    "UserBillingType",
    "UserRegion",
    "UserRole",
    
    # Recipe 도메인 모델
    "RecipeBase",
    "RecipeBaseContent",
    "RecipeBaseStatus",
    "Ingredient",
    "Recipe",
    
    # Recipe 도메인 enum
    "RecipeLanguage",
    "RecipeDifficulty",
    "RecipeState"
] 