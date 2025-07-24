"""
User 도메인 모델 정의

이 모듈은 사용자 관련 데이터베이스 모델을 정의합니다.
SQLModel을 사용하여 타입 안전성과 데이터 검증을 제공합니다.
ERD 구조에 따라 사용자 정보를 여러 테이블로 분리하여 관리합니다.
ULID를 사용하여 시간순 정렬 가능한 고유 식별자를 제공합니다.
"""

from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.sql import func
from ulid import ULID

# Forward reference를 위한 TYPE_CHECKING
if TYPE_CHECKING:
    from ..recipe.models import Recipe


class UserRole(str, Enum):
    """사용자 역할 enum"""
    ADMIN = "ADMIN"
    USER = "USER"
    GUEST = "GUEST"


class UserProvider(str, Enum):
    """사용자 인증 제공자 enum"""
    GUEST = "GUEST"
    GOOGLE = "GOOGLE"
    KAKAO = "KAKAO"
    APPLE = "APPLE"


class UserRegion(str, Enum):
    """사용자 지역 enum"""
    KR = "KR"
    US = "US"
    JP = "JP"
    CN = "CN"
    CA = "CA"


class UserBillingType(str, Enum):
    """사용자 결제 플랜 enum"""
    FREE = "FREE"
    PLUS = "PLUS"
    PRO = "PRO"


class User(SQLModel, table=True):
    """사용자 기본 정보 테이블"""
    __tablename__ = "users"

    user_id: str = Field(
        default_factory=lambda: str(ULID()),
        sa_column=Column(String(26), primary_key=True),
        description="사용자 ULID"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=True)),
        description="생성 시간"
    )

    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now},
        description="수정 시간"
    )
    
    role: UserRole = Field(
        default=UserRole.USER,
        description="유저 역할군"
    )
    
    provider: UserProvider = Field(
        default=UserProvider.GUEST,
        description="로그인 방식"
    )
    
    openid: Optional[str] = Field(
        default=None,
        max_length=255,
        description="OAuth2.0 대비 식별자"
    )

    # 관계 설정
    profile: Optional["UserProfile"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"uselist": False, "cascade": "all, delete-orphan"}
    )
    
    billing: Optional["UserBilling"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"uselist": False, "cascade": "all, delete-orphan"}
    )
    
    alert: Optional["UserAlert"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"uselist": False, "cascade": "all, delete-orphan"}
    )

    recipe: List["Recipe"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    def __repr__(self) -> str:
        return f"<User(user_id={self.user_id}, role={self.role})>"


class UserProfile(SQLModel, table=True):
    """사용자 프로필 정보 테이블"""
    __tablename__ = "users_profile"

    user_id: str = Field(
        primary_key=True,
        foreign_key="users.user_id",
        description="사용자 ULID"
    )
    
    nickname: str = Field(
        max_length=24,
        description="사용자 별명 | guest는 guest_랜덤숫자 / login 시 별명 설정"
    )
    
    image: Optional[str] = Field(
        default=None,
        max_length=255,
        description="프로필 사진 URL"
    )
    
    region: UserRegion = Field(
        default=UserRegion.KR,
        description="사용자 지역"
    )
    
    # 감사 필드
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="계정 생성 시간"
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now},
        description="계정 수정 시간"
    )

    # 관계 설정
    user: "User" = Relationship(back_populates="profile")

    def __repr__(self) -> str:
        return f"<UserProfile(user_id={self.user_id}, nickname={self.nickname})>"


class UserBilling(SQLModel, table=True):
    """사용자 결제 정보 테이블"""
    __tablename__ = "users_billing"

    user_id: str = Field(
        primary_key=True,
        foreign_key="users.user_id",
        description="사용자 ULID"
    )
    
    billing: UserBillingType = Field(
        default=UserBillingType.FREE,
        description="요금제"
    )
    
    # 감사 필드
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="계정 생성 시간"
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now},
        description="계정 수정 시간"
    )

    # 관계 설정
    user: "User" = Relationship(back_populates="billing")

    def __repr__(self) -> str:
        return f"<UserBilling(user_id={self.user_id}, billing={self.billing})>"


class UserAlert(SQLModel, table=True):
    """사용자 알림 정보 테이블"""
    __tablename__ = "users_alert"

    user_id: str = Field(
        primary_key=True,
        foreign_key="users.user_id",
        description="사용자 ULID"
    )
    
    fcm_token: Optional[str] = Field(
        default=None,
        max_length=255,
        description="FCM 디바이스 토큰 | 유저가 알림 권한을 허용해야 획득 가능"
    )
    
    is_alerted: bool = Field(
        default=False,
        description="푸시 알림 T/F | 유저가 알림 설정하면 True, 해제하면 False"
    )
    
    # 감사 필드
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="계정 생성 시간"
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now},
        description="계정 수정 시간"
    )

    # 관계 설정
    user: "User" = Relationship(back_populates="alert")

    def __repr__(self) -> str:
        return f"<UserAlert(user_id={self.user_id}, is_alerted={self.is_alerted})>"


__all__ = [
    "User",
    "UserProfile",
    "UserBilling",
    "UserAlert",
    "UserRole",
    "UserProvider",
    "UserRegion",
    "UserBillingType"
] 