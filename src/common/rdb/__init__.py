"""
RDB 패키지

이 패키지는 관계형 데이터베이스 관련 모든 기능을 제공합니다.
- 데이터베이스 연결 및 세션 관리
- 의존성 주입 시스템
- 도메인별 모델, 서비스, DTO
새로운 ERD 구조에 따라 모델들이 여러 테이블로 분산되어 있습니다.
"""

from .common.database import DatabaseManager, db_manager
from .common.dependency_injection import DependencyContainer, inject_session, inject_db_service, transactional

from .domain import (
    # User 도메인 모델
    User, UserProfile, UserBilling, UserAlert,
    
    # User 도메인 enum
    UserRole, UserProvider, UserRegion, UserBillingType,
    
    # User 도메인 서비스
    UserService,
    
    # User 도메인 DTO
    CreateUserDto, UpdateUserDto, SearchUsersDto, GetUsersByBillingDto,
    
    # User 도메인 Repository
    UserRepository, UserProfileRepository, UserBillingRepository, UserAlertRepository,
    
    # Recipe 도메인 모델
    RecipeBase, RecipeBaseContent, RecipeBaseState, Ingredient, Recipe,
    
    # Recipe 도메인 enum
    RecipeLanguage, RecipeDifficulty, RecipeState,
    
    # Recipe 도메인 서비스
    RecipeService, RecipeBaseService,
    
    # Recipe 도메인 DTO
    CreateRecipeDto, IngredientDto, UpdateRecipeDto, SearchRecipesDto, CopyRecipeFromBaseDto,
    AddIngredientToRecipeDto, UpdateRecipeIngredientDto,
    CreateRecipeBaseDto, UpdateRecipeBaseDto, SearchRecipeBasesDto,
    AddIngredientToRecipeBaseDto, UpdateRecipeBaseIngredientDto,
    
    # Recipe 도메인 Repository
    RecipeBaseRepository, RecipeBaseContentRepository, RecipeBaseStateRepository,
    RecipeRepository, IngredientRepository
)

__all__ = [
    # Database
    'DatabaseManager',
    'db_manager',
    'DependencyContainer',
    'inject_session',
    'inject_db_service',
    'transactional',
    
    # User 도메인 모델
    'User', 'UserProfile', 'UserBilling', 'UserAlert',
    
    # User 도메인 enum
    'UserRole', 'UserProvider', 'UserRegion', 'UserBillingType',
    
    # User 도메인 서비스
    'UserService',
    
    # User 도메인 DTO
    'CreateUserDto', 'UpdateUserDto', 'SearchUsersDto', 'GetUsersByBillingDto',
    
    # User 도메인 Repository
    'UserRepository', 'UserProfileRepository', 'UserBillingRepository', 'UserAlertRepository',
    
    # Recipe 도메인 모델
    'RecipeBase', 'RecipeBaseContent', 'RecipeBaseState', 'Ingredient', 'Recipe',
    
    # Recipe 도메인 enum
    'RecipeLanguage', 'RecipeDifficulty', 'RecipeState',
    
    # Recipe 도메인 서비스
    'RecipeService', 'RecipeBaseService',
    
    # Recipe 도메인 DTO
    'CreateRecipeDto', 'IngredientDto', 'UpdateRecipeDto', 'SearchRecipesDto', 'CopyRecipeFromBaseDto',
    'AddIngredientToRecipeDto', 'UpdateRecipeIngredientDto',
    'CreateRecipeBaseDto', 'UpdateRecipeBaseDto', 'SearchRecipeBasesDto',
    'AddIngredientToRecipeBaseDto', 'UpdateRecipeBaseIngredientDto',
    
    # Recipe 도메인 Repository
    'RecipeBaseRepository', 'RecipeBaseContentRepository', 'RecipeBaseStateRepository',
    'RecipeRepository', 'IngredientRepository'
] 