"""
Recipe Base 재료 관련 DTO

이 모듈은 레시피 베이스 재료 추가 및 수정을 위한 데이터 전송 객체를 정의합니다.
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
        """레시피 베이스 ID 유효성 검사"""
        if v < 0:
            raise ValueError('레시피 베이스 ID는 0보다 커야 합니다')
        return v

    @field_validator('ingredient')
    def validate_ingredient(cls, v):
        """재료명 유효성 검사"""
        if not v or not v.strip():
            raise ValueError('재료명은 필수입니다')
        if len(v) > 32:
            raise ValueError('재료명은 32자를 초과할 수 없습니다')
        return v.strip()

    @field_validator('amount')
    def validate_amount(cls, v):
        """재료 양 유효성 검사"""
        if not v or not v.strip():
            raise ValueError('재료 양은 필수입니다')
        return v.strip()

    class Config:
        """Pydantic 설정"""
        validate_assignment = True


class UpdateRecipeBaseIngredientDto(BaseModel):
    """
    레시피 베이스 재료 수정을 위한 데이터 전송 객체
    
    Attributes:
        ingredient_id: 재료 ID
        ingredient: 재료명
        amount: 재료 양
    """
    ingredient_id: int
    ingredient: Optional[str] = None
    amount: Optional[str] = None

    @field_validator('ingredient_id')
    def validate_ingredient_id(cls, v):
        """재료 ID 유효성 검사"""
        if v < 0:
            raise ValueError('재료 ID는 0보다 커야 합니다')
        return v

    @field_validator('ingredient')
    def validate_ingredient(cls, v):
        """재료명 유효성 검사"""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('재료명이 제공된 경우 빈 문자열일 수 없습니다')
            if len(v) > 32:
                raise ValueError('재료명은 32자를 초과할 수 없습니다')
        return v

    @field_validator('amount')
    def validate_amount(cls, v):
        """재료 양 유효성 검사"""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('재료 양이 제공된 경우 빈 문자열일 수 없습니다')
        return v

    @field_validator('amount')
    def validate_at_least_one_field(cls, v, values):
        """최소 하나의 필드는 제공되어야 함"""
        if values.get('ingredient') is None and v is None:
            raise ValueError('재료명 또는 재료 양 중 최소 하나는 제공되어야 합니다')
        return v

    def get_update_fields(self) -> Dict[str, Any]:
        """업데이트할 필드들의 딕셔너리를 반환합니다."""
        fields = {}
        if self.ingredient is not None:
            fields['ingredient'] = self.ingredient
        if self.amount is not None:
            fields['amount'] = self.amount
        return fields

    class Config:
        """Pydantic 설정"""
        validate_assignment = True 