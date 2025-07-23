"""
RecipeBase 재료 관련 DTO

이 모듈은 레시피 베이스 재료 관련 데이터를 전달하는 DTO를 정의합니다.
새로운 ERD 구조에서는 재료가 JSONB로 저장되므로 이 DTO들은 호환성을 위해 유지됩니다.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, field_validator


class AddIngredientToRecipeBaseDto(BaseModel):
    """
    레시피 베이스에 재료 추가를 위한 데이터 전송 객체
    
    Attributes:
        recipe_base_id: 레시피 베이스 ID
        ingredient: 재료명
        amount: 재료 양
    """
    recipe_base_id: int
    ingredient: str
    amount: str

    @field_validator('recipe_base_id')
    def validate_recipe_base_id(cls, v):
        """레시피 베이스 ID 검증"""
        if v <= 0:
            raise ValueError("레시피 베이스 ID는 1 이상이어야 합니다.")
        
        return v

    @field_validator('ingredient')
    def validate_ingredient(cls, v):
        """재료명 검증"""
        if not v or not v.strip():
            raise ValueError("재료명은 필수 항목입니다.")
        
        if len(v) > 100:
            raise ValueError("재료명은 100자를 초과할 수 없습니다.")
        
        return v.strip()

    @field_validator('amount')
    def validate_amount(cls, v):
        """재료 양 검증"""
        if not v or not v.strip():
            raise ValueError("재료 양은 필수 항목입니다.")
        
        if len(v) > 50:
            raise ValueError("재료 양은 50자를 초과할 수 없습니다.")
        
        return v.strip()

    class Config:
        """Pydantic 설정"""
        validate_assignment = True


class UpdateRecipeBaseIngredientDto(BaseModel):
    """
    레시피 베이스 재료 수정을 위한 데이터 전송 객체
    
    Attributes:
        ingredient_uuid: 재료 ID
        ingredient: 재료명
        amount: 재료 양
    """
    ingredient_uuid: int
    ingredient: Optional[str] = None
    amount: Optional[str] = None

    @field_validator('ingredient_uuid')
    def validate_ingredient_uuid(cls, v):
        """재료 ID 검증"""
        if v <= 0:
            raise ValueError("재료 ID는 1 이상이어야 합니다.")
        
        return v

    @field_validator('ingredient')
    def validate_ingredient(cls, v):
        """재료명 검증"""
        if v is not None and not v.strip():
            raise ValueError("재료명이 제공된 경우 빈 문자열일 수 없습니다.")
        
        if v is not None and len(v) > 100:
            raise ValueError("재료명은 100자를 초과할 수 없습니다.")
        
        return v.strip() if v else v

    @field_validator('amount')
    def validate_amount(cls, v):
        """재료 양 검증"""
        if v is not None and not v.strip():
            raise ValueError("재료 양이 제공된 경우 빈 문자열일 수 없습니다.")
        
        if v is not None and len(v) > 50:
            raise ValueError("재료 양은 50자를 초과할 수 없습니다.")
        
        return v.strip() if v else v

    @field_validator('amount')
    def validate_at_least_one_field(cls, v, values):
        """적어도 하나의 필드는 제공되어야 함을 검증"""
        ingredient = values.get('ingredient')
        if ingredient is None and v is None:
            raise ValueError("재료명 또는 재료 양 중 하나 이상은 제공되어야 합니다.")
        
        return v

    def get_update_fields(self) -> Dict[str, Any]:
        """업데이트할 필드들만 반환"""
        fields = {}
        if self.ingredient is not None:
            fields['ingredient'] = self.ingredient
        if self.amount is not None:
            fields['amount'] = self.amount
        return fields

    class Config:
        """Pydantic 설정"""
        validate_assignment = True 