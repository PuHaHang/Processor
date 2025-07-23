"""
Recipe 도메인 패키지

이 패키지는 레시피 도메인 관련 모델, 서비스, DTO를 포함합니다.
새로운 ERD 구조에 따라 레시피 정보가 여러 테이블로 분산되어 있습니다.
"""

from .models import (
    RecipeBase, RecipeBaseContent, RecipeBaseStatus, Ingredient, Recipe,
    RecipeLanguage, RecipeDifficulty, RecipeState
)
from .recipe_service import RecipeService
from .recipe_base_service import RecipeBaseService
from .dto import (
    # Recipe 관련 DTO
    CreateRecipeDto,
    IngredientDto,
    UpdateRecipeDto,
    SearchRecipesDto,
    CopyRecipeFromBaseDto,
    AddIngredientToRecipeDto,
    UpdateRecipeIngredientDto,
    
    # RecipeBase 관련 DTO
    CreateRecipeBaseDto,
    UpdateRecipeBaseDto,
    SearchRecipeBasesDto,
    AddIngredientToRecipeBaseDto,
    UpdateRecipeBaseIngredientDto
)
from .repository import (
    RecipeBaseRepository, RecipeBaseContentRepository, RecipeBaseStatusRepository,
    RecipeRepository, IngredientRepository
)

__all__ = [
    # Models
    'RecipeBase',
    'RecipeBaseContent',
    'RecipeBaseStatus',
    'Ingredient',
    'Recipe',
    
    # Enums
    'RecipeLanguage',
    'RecipeDifficulty',
    'RecipeState',
    
    # Services
    'RecipeService',
    'RecipeBaseService',
    
    # Recipe DTOs
    'CreateRecipeDto',
    'IngredientDto',
    'UpdateRecipeDto',
    'SearchRecipesDto',
    'CopyRecipeFromBaseDto',
    'AddIngredientToRecipeDto',
    'UpdateRecipeIngredientDto',
    
    # RecipeBase DTOs
    'CreateRecipeBaseDto',
    'UpdateRecipeBaseDto',
    'SearchRecipeBasesDto',
    'AddIngredientToRecipeBaseDto',
    'UpdateRecipeBaseIngredientDto',
    
    # Repositories
    'RecipeBaseRepository',
    'RecipeBaseContentRepository',
    'RecipeBaseStatusRepository',
    'RecipeRepository',
    'IngredientRepository'
] 