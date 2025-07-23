"""
User 도메인 모델 정의

이 모듈은 사용자 관련 데이터베이스 모델을 정의합니다.
ERD 구조에 따라 사용자 정보를 여러 테이블로 분리하여 관리합니다.
"""

import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from enum import Enum

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from ...common.database import Base

# Forward reference를 위한 TYPE_CHECKING
if TYPE_CHECKING:
    from ..recipe.models import Recipe


class UserRole(str, Enum):
    """사용자 역할 enum"""
    USER = "USER"
    ADMIN = "ADMIN"


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


class User(Base):
    """사용자 기본 정보 테이블"""
    __tablename__ = "users"
    
    # 복합 기본키: 생성 시간 + UUID
    _time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        primary_key=True,
        default=func.now(),
        comment="생성 시간, Index 재정렬에 의한 삽입 오버헤드를 줄이기 위함"
    )
    
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="사용자 UUID"
    )
    
    role: Mapped[UserRole] = mapped_column(
        String(20),
        nullable=False,
        default=UserRole.USER,
        comment="유저 역할군"
    )
    
    provider: Mapped[UserProvider] = mapped_column(
        String(20),
        nullable=False,
        default=UserProvider.GUEST,
        comment="로그인 방식"
    )
    
    openid: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="OAuth2.0 대비 식별자"
    )
    
    # 관계 설정
    profile: Mapped[Optional["UserProfile"]] = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    billing: Mapped[Optional["UserBilling"]] = relationship(
        "UserBilling", 
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    alert: Mapped[Optional["UserAlert"]] = relationship(
        "UserAlert",
        back_populates="user", 
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    recipes: Mapped[List["Recipe"]] = relationship(
        "Recipe",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # 인덱스 설정
    __table_args__ = (
        Index('idx_users_id', '_time', 'user_id'),
        Index('idx_users_openid', 'openid'),
        Index('idx_users_provider', 'provider'),
    )

    def __repr__(self) -> str:
        return f"<User(user_id={self.user_id}, role={self.role})>"


class UserProfile(Base):
    """사용자 프로필 정보 테이블"""
    __tablename__ = "users_profile"
    
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True,
        comment="사용자 UUID"
    )
    
    nickname: Mapped[str] = mapped_column(
        String(24),
        nullable=False,
        comment="사용자 별명 | guest는 guest_랜덤숫자 / login 시 별명 설정"
    )
    
    image: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="프로필 사진 URL"
    )
    
    region: Mapped[UserRegion] = mapped_column(
        String(5),
        nullable=False,
        default=UserRegion.KR,
        comment="사용자 지역"
    )
    
    # 감사 필드
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="계정 생성 시간"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="계정 수정 시간"
    )
    
    # 관계 설정
    user: Mapped["User"] = relationship(
        "User",
        back_populates="profile"
    )

    def __repr__(self) -> str:
        return f"<UserProfile(user_id={self.user_id}, nickname={self.nickname})>"


class UserBilling(Base):
    """사용자 결제 정보 테이블"""
    __tablename__ = "users_billing"
    
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True,
        comment="사용자 UUID"
    )
    
    billing: Mapped[UserBillingType] = mapped_column(
        String(20),
        nullable=False,
        default=UserBillingType.FREE,
        comment="요금제"
    )
    
    # 감사 필드
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="계정 생성 시간"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="계정 수정 시간"
    )
    
    # 관계 설정
    user: Mapped["User"] = relationship(
        "User",
        back_populates="billing"
    )

    def __repr__(self) -> str:
        return f"<UserBilling(user_id={self.user_id}, billing={self.billing})>"


class UserAlert(Base):
    """사용자 알림 정보 테이블"""
    __tablename__ = "users_alert"
    
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True,
        comment="사용자 UUID"
    )
    
    fcm_token: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="FCM 디바이스 토큰 | 유저가 알림 권한을 허용해야 획득 가능"
    )
    
    alert_flag: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="푸시 알림 T/F | 유저가 알림 설정하면 True, 해제하면 False"
    )
    
    # 감사 필드
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="계정 생성 시간"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="계정 수정 시간"
    )
    
    # 관계 설정
    user: Mapped["User"] = relationship(
        "User",
        back_populates="alert"
    )

    def __repr__(self) -> str:
        return f"<UserAlert(user_id={self.user_id}, alert_flag={self.alert_flag})>"


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