"""
User 수정을 위한 DTO

이 모듈은 사용자 수정 시 필요한 데이터를 전달하는 DTO를 정의합니다.
새로운 ERD 구조에 따라 사용자 정보가 여러 테이블에 분산되어 있습니다.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, field_validator
from ..models import UserProvider, UserBillingType, UserRegion, UserRole


class UpdateUserDto(BaseModel):
    """
    사용자 수정을 위한 데이터 전송 객체
    
    Attributes:
        user_uuid: 사용자 ID (필수)
        nickname: 사용자 별명
        image: 프로필 이미지 URL
        billing: 결제 플랜
        region: 사용자 지역
        role: 사용자 역할
        fcm_token: FCM 토큰
        alert_flag: 알림 플래그
    """
    user_uuid: str
    nickname: Optional[str] = None
    image: Optional[str] = None
    billing: Optional[UserBillingType] = None
    region: Optional[UserRegion] = None
    role: Optional[UserRole] = None
    fcm_token: Optional[str] = None
    alert_flag: Optional[bool] = None

    @field_validator('user_uuid')
    def validate_user_uuid(cls, v):
        """사용자 ID 검증"""
        if not v or not v.strip():
            raise ValueError("사용자 ID는 필수 항목입니다.")
        
        return v.strip()

    @field_validator('nickname')
    def validate_nickname(cls, v):
        """닉네임 검증"""
        if v is not None and (not v or not v.strip()):
            raise ValueError("닉네임이 제공된 경우 빈 문자열일 수 없습니다.")
        
        if v is not None and len(v) > 24:
            raise ValueError("닉네임은 24자를 초과할 수 없습니다.")
        
        return v.strip() if v else v

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

    def get_update_fields(self) -> Dict[str, Any]:
        """업데이트할 필드들만 반환"""
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
        if self.fcm_token is not None:
            fields['fcm_token'] = self.fcm_token
        if self.alert_flag is not None:
            fields['alert_flag'] = self.alert_flag
        return fields

    class Config:
        """Pydantic 설정"""
        use_enum_values = True
        validate_assignment = True 