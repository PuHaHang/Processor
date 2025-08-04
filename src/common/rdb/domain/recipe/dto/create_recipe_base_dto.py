"""
RecipeBase 생성을 위한 DTO

이 모듈은 레시피 베이스 생성 시 필요한 데이터를 전달하는 DTO를 정의합니다.
새로운 ERD 구조에 따라 레시피 정보가 여러 테이블로 분산되어 있습니다.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, field_validator
from ..models import RecipeLanguage, RecipeDifficulty


class CreateRecipeBaseDto(BaseModel):
    """
    레시피 베이스 생성을 위한 데이터 전송 객체
    
    Attributes:
        thumbnail: 썸네일 이미지 URL
        reference: 참조 정보 (platform, url)
        servings: 인분 수
        difficulty: 요리 난이도
        estimated_time: 추정 요리 소요 시간(분)
        title: 레시피 제목
        author: 레시피 작성자
        ingredients: 재료 리스트
        stages: 요리 과정
        language: 레시피 언어 (기본값: ko)
        model_name: 정제 시 사용한 모델 버전
    """
    # RecipeBase 필드들
    thumbnail: Optional[str] = None
    reference: Optional[Dict[str, Any]] = None
    servings: Optional[int] = None
    difficulty: Optional[RecipeDifficulty] = None
    estimated_time: Optional[int] = None
    
    # RecipeBaseContent 필드들
    title: Optional[str] = None
    author: Optional[str] = None
    ingredients: Optional[List[Dict[str, Any]]] = None
    stages: Optional[Dict[str, Any]] = None
    language: RecipeLanguage = RecipeLanguage.ko
    model_name: str = "default"

    @field_validator('title')
    def validate_title(cls, v):
        """레시피 제목 검증"""
        if v is not None and not v.strip():
            raise ValueError("레시피 제목이 제공된 경우 빈 문자열일 수 없습니다.")
        
        if v is not None and len(v) > 30:
            raise ValueError("레시피 제목은 30자를 초과할 수 없습니다.")
        
        return v.strip() if v else v

    @field_validator('author')
    def validate_author(cls, v):
        """작성자 검증"""
        if v is not None and len(v) > 24:
            raise ValueError("작성자는 24자를 초과할 수 없습니다.")
        
        return v

    @field_validator('servings')
    def validate_servings(cls, v):
        """인분 수 검증"""
        if v is not None and v <= 0:
            raise ValueError("인분 수는 1 이상이어야 합니다.")
        
        if v is not None and v > 100:
            raise ValueError("인분 수는 100 이하여야 합니다.")
        
        return v

    @field_validator('estimated_time')
    def validate_estimated_time(cls, v):
        """추정 요리 시간 검증"""
        if v is not None and v <= 0:
            raise ValueError("추정 요리 시간은 1분 이상이어야 합니다.")
        
        if v is not None and v > 1440:  # 24시간
            raise ValueError("추정 요리 시간은 1440분(24시간) 이하여야 합니다.")
        
        return v

    @field_validator('thumbnail')
    def validate_thumbnail(cls, v):
        """썸네일 URL 검증"""
        if v is not None and len(v) > 255:
            raise ValueError("썸네일 URL은 255자를 초과할 수 없습니다.")
        
        return v

    @field_validator('model_name')
    def validate_model_name(cls, v):
        """모델명 검증"""
        if not v or not v.strip():
            raise ValueError("모델명은 필수 항목입니다.")
        
        if len(v) > 255:
            raise ValueError("모델명은 255자를 초과할 수 없습니다.")
        
        return v.strip()

    @field_validator('ingredients')
    def validate_ingredients(cls, v):
        """재료 리스트 검증"""
        if v is not None:
            if not isinstance(v, list):
                raise ValueError("재료는 리스트 형태여야 합니다.")
            
            for ingredient in v:
                if not isinstance(ingredient, dict):
                    raise ValueError("재료는 딕셔너리 형태여야 합니다.")
                
                required_fields = ['ingredient_name', 'ingredient_amount']
                for field in required_fields:
                    if field not in ingredient:
                        raise ValueError(f"재료는 '{field}' 필드를 포함해야 합니다.")
                    if not ingredient[field]:
                        raise ValueError(f"재료의 '{field}' 필드는 비어있을 수 없습니다.")
        
        return v

    @field_validator('reference')
    def validate_reference(cls, v):
        """참조 정보 검증"""
        if v is not None:
            if not isinstance(v, dict):
                raise ValueError("참조 정보는 딕셔너리 형태여야 합니다.")
            
            if 'platform' not in v and 'url' not in v:
                raise ValueError("참조 정보는 'platform' 또는 'url' 필드를 포함해야 합니다.")
        
        return v

    class Config:
        """Pydantic 설정"""
        use_enum_values = True
        validate_assignment = True 