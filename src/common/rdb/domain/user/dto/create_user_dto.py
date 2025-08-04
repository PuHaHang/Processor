"""
User 생성을 위한 DTO

이 모듈은 사용자 생성 시 필요한 데이터를 전달하는 DTO를 정의합니다.
새로운 ERD 구조에 따라 사용자 정보가 여러 테이블에 분산되어 있습니다.
"""

from typing import Optional
from pydantic import BaseModel, field_validator
from ..models import UserProvider, UserBillingType, UserRegion, UserRole


class CreateUserDto(BaseModel):
    """
    사용자 생성을 위한 데이터 전송 객체
    
    Attributes:
        nickname: 사용자 별명 (GUEST는 자동 생성)
        role: 사용자 역할 (기본값: USER)
        provider: 인증 제공자 (기본값: GUEST)
        openid: OAuth2.0 식별자
        image: 프로필 이미지 URL
        billing: 결제 플랜 (기본값: FREE)
        region: 사용자 지역 (기본값: KR)
        fcm_token: FCM 토큰
        is_alerted: 알림 플래그 (기본값: False)
    """
    nickname: str
    role: UserRole = UserRole.USER
    provider: UserProvider = UserProvider.GUEST
    openid: Optional[str] = None
    image: Optional[str] = None
    billing: UserBillingType = UserBillingType.FREE
    region: UserRegion = UserRegion.KR
    fcm_token: Optional[str] = None
    is_alerted: bool = False

    @field_validator('nickname')
    def validate_nickname(cls, v):
        """닉네임 검증"""
        if not v or not v.strip():
            raise ValueError("닉네임은 필수 항목입니다.")
        
        if len(v) > 24:
            raise ValueError("닉네임은 24자를 초과할 수 없습니다.")
        
        return v.strip()

    @field_validator('openid')
    def validate_openid(cls, v, info):
        """OpenID 검증"""
        provider = info.data.get('provider')
        if provider != UserProvider.GUEST and not v:
            raise ValueError("GUEST가 아닌 제공자는 OpenID가 필요합니다.")
        
        return v

    @field_validator('image')
    def validate_image(cls, v):
        """이미지 URL 검증"""
        if v is not None and len(v) > 255:
            raise ValueError("이미지 URL은 255자를 초과할 수 없습니다.")
        
        return v

    @field_validator('fcm_token')
    def validate_fcm_token(cls, v):
        """FCM 토큰 검증"""
        if v is not None and len(v) > 255:
            raise ValueError("FCM 토큰은 255자를 초과할 수 없습니다.")
        
        return v

    class Config:
        """Pydantic 설정"""
        use_enum_values = True
        validate_assignment = True 