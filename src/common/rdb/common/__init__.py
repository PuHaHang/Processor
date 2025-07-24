"""
RDB Common 모듈

이 패키지는 데이터베이스 관련 공통 기능을 제공합니다.
SQLModel을 사용하여 타입 안전성과 데이터 검증을 제공합니다.
새로운 ERD 구조에 따라 모델들이 여러 테이블로 분산되어 있습니다.
"""

from .database import DatabaseManager


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
    RecipeBaseState,
    Ingredient,
    Recipe,
    
    # Recipe 도메인 enum
    RecipeLanguage,
    RecipeDifficulty,
    RecipeState
)

__all__ = [
    # Database
    "DatabaseManager",
    
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
    "RecipeState",
    "Ingredient",
    "Recipe",
    
    # Recipe 도메인 enum
    "RecipeLanguage",
    "RecipeDifficulty",
    "RecipeState"
] 