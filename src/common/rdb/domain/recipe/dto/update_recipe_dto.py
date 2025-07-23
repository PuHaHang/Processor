"""
Recipe 수정을 위한 DTO

이 모듈은 레시피 수정 시 필요한 데이터를 전달하는 DTO를 정의합니다.
새로운 ERD 구조에 따라 레시피 정보가 여러 테이블로 분산되어 있습니다.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, field_validator


class UpdateRecipeDto(BaseModel):
    """
    레시피 수정을 위한 데이터 전송 객체
    
    Attributes:
        recipe_uuid: 레시피 ID (필수)
        title: 레시피 제목
        stages: 요리 과정
    """
    recipe_uuid: int
    title: Optional[str] = None
    stages: Optional[Dict[str, Any]] = None

    @field_validator('recipe_uuid')
    def validate_recipe_uuid(cls, v):
        """레시피 ID 검증"""
        if v <= 0:
            raise ValueError("레시피 ID는 1 이상이어야 합니다.")
        
        return v

    @field_validator('title')
    def validate_title(cls, v):
        """제목 검증"""
        if v is not None and not v.strip():
            raise ValueError("제목이 제공된 경우 빈 문자열일 수 없습니다.")
        
        if v is not None and len(v) > 255:
            raise ValueError("제목은 255자를 초과할 수 없습니다.")
        
        return v.strip() if v else v

    def get_update_fields(self) -> Dict[str, Any]:
        """업데이트할 필드들만 반환"""
        fields = {}
        if self.title is not None:
            fields['title'] = self.title
        if self.stages is not None:
            fields['stages'] = self.stages
        return fields

    class Config:
        """Pydantic 설정"""
        validate_assignment = True 