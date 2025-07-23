"""
Recipe 검색을 위한 DTO

이 모듈은 레시피 검색 시 필요한 데이터를 전달하는 DTO를 정의합니다.
새로운 ERD 구조에 따라 레시피 정보가 여러 테이블로 분산되어 있습니다.
"""

from typing import Optional
from pydantic import BaseModel, field_validator


class SearchRecipesDto(BaseModel):
    """
    레시피 검색을 위한 데이터 전송 객체
    
    Attributes:
        title: 제목 검색어
        user_id: 사용자 ID
        recipe_base_id: 레시피 베이스 ID
        ingredient: 재료 검색어
        limit: 조회 제한 수 (기본값: 100)
        offset: 조회 시작 위치 (기본값: 0)
    """
    title: Optional[str] = None
    user_id: Optional[str] = None
    recipe_base_id: Optional[int] = None
    ingredient: Optional[str] = None
    limit: int = 100
    offset: int = 0

    @field_validator('limit')
    def validate_limit(cls, v):
        """조회 제한 수 검증"""
        if v <= 0:
            raise ValueError("조회 제한 수는 1 이상이어야 합니다.")
        
        if v > 1000:
            raise ValueError("조회 제한 수는 1000을 초과할 수 없습니다.")
        
        return v

    @field_validator('offset')
    def validate_offset(cls, v):
        """조회 시작 위치 검증"""
        if v < 0:
            raise ValueError("조회 시작 위치는 0 이상이어야 합니다.")
        
        return v

    @field_validator('title')
    def validate_title(cls, v):
        """제목 검증"""
        if v is not None and not v.strip():
            raise ValueError("제목 검색어가 제공된 경우 빈 문자열일 수 없습니다.")
        
        return v.strip() if v else v

    @field_validator('user_id')
    def validate_user_id(cls, v):
        """사용자 ID 검증"""
        if v is not None and not v.strip():
            raise ValueError("사용자 ID가 제공된 경우 빈 문자열일 수 없습니다.")
        
        return v.strip() if v else v

    @field_validator('recipe_base_id')
    def validate_recipe_base_id(cls, v):
        """레시피 베이스 ID 검증"""
        if v is not None and v <= 0:
            raise ValueError("레시피 베이스 ID는 1 이상이어야 합니다.")
        
        return v

    @field_validator('ingredient')
    def validate_ingredient(cls, v):
        """재료 검색어 검증"""
        if v is not None and not v.strip():
            raise ValueError("재료 검색어가 제공된 경우 빈 문자열일 수 없습니다.")
        
        return v.strip() if v else v

    class Config:
        """Pydantic 설정"""
        validate_assignment = True


class CopyRecipeFromBaseDto(BaseModel):
    """
    레시피 베이스로부터 레시피 복사를 위한 데이터 전송 객체
    
    Attributes:
        user_id: 사용자 ID
        recipe_base_id: 레시피 베이스 ID
        title: 사용자 맞춤 레시피 제목
    """
    user_id: str
    recipe_base_id: int
    title: Optional[str] = None

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

    class Config:
        """Pydantic 설정"""
        validate_assignment = True 