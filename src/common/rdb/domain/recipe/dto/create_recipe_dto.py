"""
Recipe 생성을 위한 DTO

이 모듈은 레시피 생성 시 필요한 데이터를 전달하는 DTO를 정의합니다.
새로운 ERD 구조에 따라 레시피 정보가 여러 테이블로 분산되어 있습니다.
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
        """재료명 검증"""
        if not v or not v.strip():
            raise ValueError("재료명은 필수 항목입니다.")
        
        return v.strip()

    @field_validator('ingredient_amount')
    def validate_amount(cls, v):
        """재료 양 검증"""
        if not v or not v.strip():
            raise ValueError("재료 양은 필수 항목입니다.")
        
        return v.strip()

    class Config:
        """Pydantic 설정"""
        validate_assignment = True


class CreateRecipeDto(BaseModel):
    """
    레시피 생성을 위한 데이터 전송 객체
    
    Attributes:
        user_id: 사용자 ID
        recipe_base_id: 레시피 베이스 ID
        title: 사용자 맞춤 레시피 제목
        stages: 요리 과정
        ingredients: 재료 리스트
    """
    user_id: str
    recipe_base_id: int
    title: Optional[str] = None
    stages: Optional[Dict[str, Any]] = None
    ingredients: Optional[List[IngredientDto]] = None

    @field_validator('user_id')
    def validate_user_id(cls, v):
        """사용자 ID 검증"""
        if not v or not v.strip():
            raise ValueError("사용자 ID는 필수 항목입니다.")
        
        return v.strip()

    @field_validator('recipe_base_id')
    def validate_recipe_base_id(cls, v):
        """레시피 베이스 ID 검증"""
        if v <= 0:
            raise ValueError("레시피 베이스 ID는 1 이상이어야 합니다.")
        
        return v

    @field_validator('title')
    def validate_title(cls, v):
        """제목 검증"""
        if v is not None and not v.strip():
            raise ValueError("제목이 제공된 경우 빈 문자열일 수 없습니다.")
        
        if v is not None and len(v) > 255:
            raise ValueError("제목은 255자를 초과할 수 없습니다.")
        
        return v.strip() if v else v

    def get_ingredients_dict(self) -> Optional[List[Dict[str, Any]]]:
        """재료를 딕셔너리 형태로 반환"""
        if self.ingredients is None:
            return None
        
        return [
            {
                'ingredient_name': ing.ingredient_name,
                'ingredient_amount': ing.ingredient_amount,
                'ingredient_unit': ing.ingredient_unit
            }
            for ing in self.ingredients
        ]

    class Config:
        """Pydantic 설정"""
        validate_assignment = True 