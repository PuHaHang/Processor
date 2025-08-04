"""
Recipe 도메인 수정 DTO

이 모듈은 레시피 수정을 위한 데이터 전송 객체를 정의합니다.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, field_validator


class UpdateRecipeDto(BaseModel):
    """
    레시피 수정을 위한 데이터 전송 객체
    
    Attributes:
        recipe_id: 레시피 ID (필수)
        title: 레시피 제목
        stages: 요리 과정
    """
    recipe_id: int
    title: Optional[str] = None
    stages: Optional[Dict[str, Any]] = None

    @field_validator('recipe_id')
    def validate_recipe_id(cls, v):
        """레시피 ID 유효성 검사"""
        if v < 0:
            raise ValueError('레시피 ID는 0보다 커야 합니다')
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

    def get_update_fields(self) -> Dict[str, Any]:
        """업데이트할 필드들의 딕셔너리를 반환합니다."""
        fields = {}
        if self.title is not None:
            fields['title'] = self.title
        if self.stages is not None:
            fields['stages'] = self.stages
        return fields

    class Config:
        """Pydantic 설정"""
        validate_assignment = True 