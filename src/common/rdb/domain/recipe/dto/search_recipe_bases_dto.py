"""
RecipeBase 검색을 위한 DTO

이 모듈은 레시피 베이스 검색 시 필요한 데이터를 전달하는 DTO를 정의합니다.
새로운 ERD 구조에 따라 레시피 정보가 여러 테이블로 분산되어 있습니다.
"""

from typing import Optional
from pydantic import BaseModel, field_validator
from ..models import RecipeLanguage, RecipeDifficulty


class SearchRecipeBasesDto(BaseModel):
    """
    레시피 베이스 검색을 위한 데이터 전송 객체
    
    Attributes:
        title: 제목 검색어
        author: 작성자 검색어
        language: 레시피 언어
        difficulty: 요리 난이도
        servings: 인분 수
        ingredient: 재료 검색어
        limit: 조회 제한 수 (기본값: 100)
        offset: 조회 시작 위치 (기본값: 0)
    """
    title: Optional[str] = None
    author: Optional[str] = None
    language: Optional[RecipeLanguage] = None
    difficulty: Optional[RecipeDifficulty] = None
    servings: Optional[int] = None
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
        """제목 검색어 검증"""
        if v is not None and not v.strip():
            raise ValueError("제목 검색어가 제공된 경우 빈 문자열일 수 없습니다.")
        
        return v.strip() if v else v

    @field_validator('author')
    def validate_author(cls, v):
        """작성자 검색어 검증"""
        if v is not None and not v.strip():
            raise ValueError("작성자 검색어가 제공된 경우 빈 문자열일 수 없습니다.")
        
        return v.strip() if v else v

    @field_validator('ingredient')
    def validate_ingredient(cls, v):
        """재료 검색어 검증"""
        if v is not None and not v.strip():
            raise ValueError("재료 검색어가 제공된 경우 빈 문자열일 수 없습니다.")
        
        return v.strip() if v else v

    @field_validator('servings')
    def validate_servings(cls, v):
        """인분 수 검증"""
        if v is not None and v <= 0:
            raise ValueError("인분 수는 1 이상이어야 합니다.")
        
        if v is not None and v > 100:
            raise ValueError("인분 수는 100 이하여야 합니다.")
        
        return v

    class Config:
        """Pydantic 설정"""
        use_enum_values = True
        validate_assignment = True 