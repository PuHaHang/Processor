"""
SQLModel 모델 통합

이 모듈은 모든 도메인의 SQLModel 모델을 통합하여 제공합니다.
각 도메인별 모델은 해당 도메인 패키지에서 관리됩니다.
새로운 ERD 구조에 따라 모델들이 여러 테이블로 분리되어 있습니다.
"""

# 도메인별 모델 import
from ..domain.user.models import (
    User,
    UserProfile,
    UserBilling,
    UserAlert,
    UserProvider,
    UserBillingType,
    UserRegion,
    UserRole
)

from ..domain.recipe.models import (
    RecipeBase,
    RecipeBaseContent,
    RecipeBaseState,
    Ingredient,
    Recipe,
    RecipeLanguage,
    RecipeDifficulty,
    RecipeState
)

# 모든 모델을 내보내기 위한 리스트
__all__ = [
    # User 도메인
    "User",
    "UserProfile",
    "UserBilling",
    "UserAlert",
    "UserProvider",
    "UserBillingType",
    "UserRegion",
    "UserRole",
    
    # Recipe 도메인
    "RecipeBase",
    "RecipeBaseContent",
    "RecipeBaseState",
    "Ingredient",
    "Recipe",
    "RecipeLanguage",
    "RecipeDifficulty",
    "RecipeState"
] 