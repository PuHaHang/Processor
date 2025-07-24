"""
User 검색을 위한 DTO

이 모듈은 사용자 검색 시 필요한 데이터를 전달하는 DTO를 정의합니다.
새로운 ERD 구조에 따라 사용자 정보가 여러 테이블에 분산되어 있습니다.
"""

from typing import Optional
from pydantic import BaseModel, field_validator
from ..models import UserProvider, UserBillingType, UserRegion, UserRole


class SearchUsersDto(BaseModel):
    """
    사용자 검색을 위한 데이터 전송 객체
    
    Attributes:
        nickname: 닉네임 검색어
        provider: 인증 제공자
        billing: 결제 플랜
        region: 사용자 지역
        role: 사용자 역할
        limit: 조회 제한 수 (기본값: 100)
        offset: 조회 시작 위치 (기본값: 0)
    """
    nickname: Optional[str] = None
    provider: Optional[UserProvider] = None
    billing: Optional[UserBillingType] = None
    region: Optional[UserRegion] = None
    role: Optional[UserRole] = None
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

    @field_validator('nickname')
    def validate_nickname(cls, v):
        """닉네임 검색어 검증"""
        if v is not None and not v.strip():
            raise ValueError("닉네임 검색어가 제공된 경우 빈 문자열일 수 없습니다.")
        
        return v.strip() if v else v

    class Config:
        """Pydantic 설정"""
        use_enum_values = True
        validate_assignment = True


class GetUsersByBillingDto(BaseModel):
    """
    결제 플랜별 사용자 조회를 위한 데이터 전송 객체
    
    Attributes:
        billing: 결제 플랜
        limit: 조회 제한 수 (기본값: 100)
        offset: 조회 시작 위치 (기본값: 0)
    """
    billing: UserBillingType
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

    class Config:
        """Pydantic 설정"""
        use_enum_values = True
        validate_assignment = True 