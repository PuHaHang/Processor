"""
Recipe 도메인 생성 DTO

이 모듈은 레시피 생성과 관련된 데이터 전송 객체를 정의합니다.
사용자 ID는 ULID 형태로 전달됩니다.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, field_validator


class IngredientDto(BaseModel):
    """
    재료 정보를 위한 데이터 전송 객체
    
    Attributes:
        ingredient: 재료명
        amount: 재료 양
    """
    ingredient_name: str
    ingredient_amount: Optional[int] = None
    ingredient_unit: Optional[str] = None

    @field_validator('ingredient_name')
    def validate_ingredient(cls, v):
        """재료명 유효성 검사"""
        if not v or not v.strip():
            raise ValueError('재료명은 필수입니다')
        return v.strip()

    @field_validator('ingredient_amount')
    def validate_amount(cls, v):
        """재료 양 유효성 검사"""
        if v is not None and v <= 0:
            raise ValueError('재료 양은 0보다 커야 합니다')
        return v

    class Config:
        """Pydantic 설정"""
        validate_assignment = True


class CreateRecipeDto(BaseModel):
    """
    레시피 생성을 위한 데이터 전송 객체
    
    Attributes:
        user_id: 사용자 ULID
        recipe_base_id: 레시피 베이스 ID
        title: 사용자 맞춤 레시피 제목
        stages: 요리 과정
        ingredients: 재료 리스트
    """
    user_id: str
    recipe_base_content_id: int
    title: Optional[str] = None
    stages: Optional[Dict[str, Any]] = None
    ingredients: Optional[List[IngredientDto]] = None

    @field_validator('user_id')
    def validate_user_id(cls, v):
        """사용자 ULID 유효성 검사"""
        if not v or not v.strip():
            raise ValueError('User ID는 필수입니다')
        if len(v) != 26:
            raise ValueError('User ID는 26자리 ULID 형태여야 합니다')
        return v.strip()

    @field_validator('recipe_base_content_id')
    def validate_recipe_base_content_id(cls, v):
        """레시피 베이스 ID 유효성 검사"""
        if v <= 0:
            raise ValueError('레시피 베이스 ID는 0보다 커야 합니다')
        return v

    @field_validator('title')
    def validate_title(cls, v):
        """제목 유효성 검사"""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('제목이 제공된 경우 빈 문자열일 수 없습니다')
            if len(v) > 255:
                raise ValueError('제목은 255자를 초과할 수 없습니다')
        return v

    def get_ingredients_dict(self) -> Optional[List[Dict[str, Any]]]:
        """재료 리스트를 딕셔너리 형태로 변환합니다."""
        if not self.ingredients:
            return None
        
        return [
            {
                'ingredient_name': ingredient.ingredient_name,
                'ingredient_amount': ingredient.ingredient_amount,
                'ingredient_unit': ingredient.ingredient_unit
            }
            for ingredient in self.ingredients
        ]

    class Config:
        """Pydantic 설정"""
        validate_assignment = True 