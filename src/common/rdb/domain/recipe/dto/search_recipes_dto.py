"""
Recipe 도메인 검색 DTO

이 모듈은 레시피 검색과 관련된 데이터 전송 객체를 정의합니다.
사용자 ID는 ULID 형태로 전달됩니다.
"""

from typing import Optional
from pydantic import BaseModel, field_validator


class SearchRecipesDto(BaseModel):
    """
    레시피 검색을 위한 데이터 전송 객체
    
    Attributes:
        title: 제목 검색어
        user_id: 사용자 ULID
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
        """조회 제한 수 유효성 검사"""
        if v <= 0:
            raise ValueError('조회 제한 수는 0보다 커야 합니다')
        if v > 1000:
            raise ValueError('조회 제한 수는 1000을 초과할 수 없습니다')
        return v

    @field_validator('offset')
    def validate_offset(cls, v):
        """조회 시작 위치 유효성 검사"""
        if v < 0:
            raise ValueError('조회 시작 위치는 0 이상이어야 합니다')
        return v

    @field_validator('title')
    def validate_title(cls, v):
        """제목 검색어 유효성 검사"""
        if v is not None and not v.strip():
            raise ValueError('제목 검색어는 빈 문자열일 수 없습니다')
        return v

    @field_validator('user_id')
    def validate_user_id(cls, v):
        """사용자 ULID 유효성 검사"""
        if v is not None:
            if not v.strip():
                raise ValueError('User ID는 빈 문자열일 수 없습니다')
            if len(v) != 26:
                raise ValueError('User ID는 26자리 ULID 형태여야 합니다')
        return v

    @field_validator('recipe_base_id')
    def validate_recipe_base_id(cls, v):
        """레시피 베이스 ID 유효성 검사"""
        if v is not None and v <= 0:
            raise ValueError('레시피 베이스 ID는 0보다 커야 합니다')
        return v

    @field_validator('ingredient')
    def validate_ingredient(cls, v):
        """재료 검색어 유효성 검사"""
        if v is not None and not v.strip():
            raise ValueError('재료 검색어는 빈 문자열일 수 없습니다')
        return v

    class Config:
        """Pydantic 설정"""
        validate_assignment = True


class CopyRecipeFromBaseDto(BaseModel):
    """
    레시피 베이스로부터 레시피 복사를 위한 데이터 전송 객체
    
    Attributes:
        user_id: 사용자 ULID
        recipe_base_id: 레시피 베이스 ID
        title: 사용자 맞춤 레시피 제목
    """
    user_id: str
    recipe_base_content_id: int
    title: Optional[str] = None

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
        """레시피 베이스 컨텐츠 ID 유효성 검사"""
        if v <= 0:
            raise ValueError('레시피 베이스 컨텐츠 ID는 0보다 커야 합니다')
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

    class Config:
        """Pydantic 설정"""
        validate_assignment = True 