"""
User 도메인 수정 DTO

이 모듈은 사용자 정보 수정을 위한 데이터 전송 객체를 정의합니다.
ULID 형태의 사용자 식별자를 사용합니다.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, field_validator

from ..models import UserRole, UserBillingType, UserRegion, UserProvider


class UpdateUserDto(BaseModel):
    """
    사용자 수정을 위한 데이터 전송 객체
    
    Attributes:
        user_id: 사용자 ULID (필수)
        nickname: 사용자 별명
        image: 프로필 이미지 URL
        billing: 결제 플랜
        region: 사용자 지역
        role: 사용자 역할
        provider: 인증 제공자
        openid: OAuth2.0 식별자
        fcm_token: FCM 토큰
        is_alerted: 알림 플래그
    """
    user_id: str
    nickname: Optional[str] = None
    image: Optional[str] = None
    billing: Optional[UserBillingType] = None
    region: Optional[UserRegion] = None
    role: Optional[UserRole] = None
    provider: Optional[UserProvider] = None
    openid: Optional[str] = None
    fcm_token: Optional[str] = None
    is_alerted: Optional[bool] = None

    @field_validator('user_id')
    def validate_user_id(cls, v):
        """사용자 ULID 유효성 검사"""
        if not v or not v.strip():
            raise ValueError('User ID는 필수입니다')
        if len(v) != 26:
            raise ValueError('User ID는 26자리 ULID 형태여야 합니다')
        return v.strip()

    @field_validator('nickname')
    def validate_nickname(cls, v):
        """닉네임 유효성 검사"""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('닉네임은 빈 문자열일 수 없습니다')
            if len(v) > 24:
                raise ValueError('닉네임은 24자를 초과할 수 없습니다')
        return v

    @field_validator('image')
    def validate_image(cls, v):
        """이미지 URL 유효성 검사"""
        if v is not None and not v.strip():
            raise ValueError('이미지 URL은 빈 문자열일 수 없습니다')
        return v

    @field_validator('fcm_token')
    def validate_fcm_token(cls, v):
        """FCM 토큰 유효성 검사"""
        if v is not None and not v.strip():
            raise ValueError('FCM 토큰은 빈 문자열일 수 없습니다')
        return v

    def get_update_fields(self) -> Dict[str, Any]:
        """업데이트할 필드들의 딕셔너리를 반환합니다."""
        fields = {}
        
        if self.nickname is not None:
            fields['nickname'] = self.nickname
        if self.image is not None:
            fields['image'] = self.image
        if self.billing is not None:
            fields['billing'] = self.billing
        if self.region is not None:
            fields['region'] = self.region
        if self.role is not None:
            fields['role'] = self.role
        if self.provider is not None:
            fields['provider'] = self.provider
        if self.openid is not None:
            fields['openid'] = self.openid
        if self.fcm_token is not None:
            fields['fcm_token'] = self.fcm_token
        if self.is_alerted is not None:
            fields['is_alerted'] = self.is_alerted
            
        return fields

    class Config:
        """Pydantic 설정"""
        use_enum_values = True
        validate_assignment = True 