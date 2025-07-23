"""
도메인 패키지

이 패키지는 모든 도메인 관련 모델, 서비스, DTO를 포함합니다.
새로운 ERD 구조에 따라 모델들이 여러 테이블로 분산되어 있습니다.
"""

from .user import (
    User, UserProfile, UserBilling, UserAlert, UserRole, UserProvider, UserRegion, UserBillingType,
    UserService,
    CreateUserDto, UpdateUserDto, SearchUsersDto, GetUsersByBillingDto,
    UserRepository, UserProfileRepository, UserBillingRepository, UserAlertRepository
)
from .recipe import (
    RecipeBase, RecipeBaseContent, RecipeBaseState, Ingredient, Recipe,
    RecipeLanguage, RecipeDifficulty, RecipeState,
    RecipeService, RecipeBaseService,
    CreateRecipeDto, IngredientDto, UpdateRecipeDto, SearchRecipesDto, CopyRecipeFromBaseDto,
    AddIngredientToRecipeDto, UpdateRecipeIngredientDto,
    CreateRecipeBaseDto, UpdateRecipeBaseDto, SearchRecipeBasesDto,
    AddIngredientToRecipeBaseDto, UpdateRecipeBaseIngredientDto,
    RecipeBaseRepository, RecipeBaseContentRepository, RecipeBaseStateRepository,
    RecipeRepository, IngredientRepository
)

__all__ = [
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