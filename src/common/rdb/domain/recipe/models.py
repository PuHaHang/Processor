"""
Recipe 도메인 모델 정의

이 모듈은 레시피 관련 데이터베이스 모델을 정의합니다.
ERD 구조에 따라 레시피 정보를 여러 테이블로 분리하여 관리합니다.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from enum import Enum

from sqlalchemy import String, Integer, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from ...common.database import Base

# Forward reference를 위한 TYPE_CHECKING
if TYPE_CHECKING:
    from ..user.models import User


class RecipeLanguage(str, Enum):
    """레시피 언어 enum"""
    ko = "ko"
    en = "en"
    ja = "ja"
    zh = "zh"


class RecipeDifficulty(str, Enum):
    """레시피 난이도 enum"""
    very_easy = "very_easy"
    easy = "easy"
    normal = "normal"
    hard = "hard"
    very_hard = "very_hard"


class RecipeState(str, Enum):
    """레시피 정제 현황 enum"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class RecipeBase(Base):
    """레시피 기본 정보 테이블"""
    __tablename__ = "recipe_bases"

    recipe_base_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="레시피 원본 ID"
    )
    
    chksum: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        unique=True,
        comment="url sha256 해싱 값"
    )
    
    thumbnail: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="레시피 대표 사진 URL"
    )
    
    referrer: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="컨텐츠 소스 (platform, url)"
    )
    
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="컨텐츠 메타데이터"
    )
    
    view_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="레시피 조회 횟수"
    )
    
    servings: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="제공량"
    )
    
    difficulty: Mapped[Optional[RecipeDifficulty]] = mapped_column(
        String(20),
        nullable=True,
        comment="요리 난이도"
    )
    
    estimated_time: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="추정 요리 소요 시간(분)"
    )
    
    # 감사 필드
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="생성 시간"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="수정 시간"
    )
    
    # 관계 설정
    contents: Mapped[List["RecipeBaseContent"]] = relationship(
        "RecipeBaseContent",
        back_populates="recipe_base",
        cascade="all, delete-orphan"
    )
    
    status: Mapped[Optional["RecipeBaseStatus"]] = relationship(
        "RecipeBaseStatus",
        back_populates="recipe_base",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    recipes: Mapped[List["Recipe"]] = relationship(
        "Recipe",
        back_populates="recipe_base",
        cascade="all, delete-orphan"
    )
    
    # 인덱스 설정
    __table_args__ = (
        Index('idx_recipe_bases_chksum', 'chksum'),
        Index('idx_recipe_bases_difficulty', 'difficulty'),
        Index('idx_recipe_bases_view_count', 'view_count'),
    )

    def __repr__(self) -> str:
        return f"<RecipeBase(recipe_base_id={self.recipe_base_id}, chksum={self.chksum})>"


class RecipeBaseContent(Base):
    """레시피 컨텐츠 정보 테이블"""
    __tablename__ = "recipe_bases_content"
    
    recipe_base_content_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="레시피 컨텐츠 ID"
    )
    
    recipe_base_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("recipe_bases.recipe_base_id", ondelete="CASCADE"),
        nullable=False,
        comment="레시피 원본 ID"
    )
    
    title: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="레시피 제목"
    )
    
    author: Mapped[Optional[str]] = mapped_column(
        String(24),
        nullable=True,
        comment="원작자"
    )
    
    ingredients: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="재료 리스트 [{ ingredient_id, ingredient_name, ingredient_amount, ingredient_unit }]"
    )
    
    stages: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="요리 과정 { step, timeline, description }"
    )
    
    language: Mapped[RecipeLanguage] = mapped_column(
        String(5),
        nullable=False,
        comment="언어"
    )
    
    model_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="정제 시 사용한 모델 버전"
    )
    
    # 감사 필드
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="생성 시간"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="수정 시간"
    )
    
    # 관계 설정
    recipe_base: Mapped["RecipeBase"] = relationship(
        "RecipeBase",
        back_populates="contents"
    )
    
    # 유니크 제약 조건
    __table_args__ = (
        UniqueConstraint('language', 'model_name', name='uq_recipe_bases_content_language_model'),
        Index('idx_recipe_bases_content_recipe_base_id', 'recipe_base_id'),
        Index('idx_recipe_bases_content_language', 'language'),
        Index('idx_recipe_bases_content_model_name', 'model_name'),
    )

    def __repr__(self) -> str:
        return f"<RecipeBaseContent(recipe_base_content_id={self.recipe_base_content_id}, title={self.title})>"


class RecipeBaseStatus(Base):
    """레시피 베이스 상태 테이블"""
    __tablename__ = "recipe_bases_status"
    
    recipe_base_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("recipe_bases.recipe_base_id", ondelete="CASCADE"),
        primary_key=True,
        comment="레시피 원본 ID"
    )
    
    state: Mapped[RecipeState] = mapped_column(
        String(20),
        nullable=False,
        default=RecipeState.PENDING,
        comment="레시피 정제 현황"
    )
    
    # 관계 설정
    recipe_base: Mapped["RecipeBase"] = relationship(
        "RecipeBase",
        back_populates="status"
    )

    def __repr__(self) -> str:
        return f"<RecipeBaseStatus(recipe_base_id={self.recipe_base_id}, state={self.state})>"


class Ingredient(Base):
    """재료 태그 테이블 (검색용)"""
    __tablename__ = "ingredients"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="재료 ID"
    )
    
    ingredient: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="재료명"
    )
    
    # 인덱스 설정
    __table_args__ = (
        Index('idx_ingredients_ingredient', 'ingredient'),
    )

    def __repr__(self) -> str:
        return f"<Ingredient(id={self.id}, ingredient={self.ingredient})>"


class Recipe(Base):
    """사용자 레시피 테이블"""
    __tablename__ = "recipes"
    
    recipe_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="레시피 ID"
    )
    
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="사용자 ID"
    )
    
    recipe_base_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("recipe_bases.recipe_base_id", ondelete="CASCADE"),
        nullable=False,
        comment="원본 레시피 ID"
    )
    
    title: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="레시피 제목"
    )
    
    ingredients: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="재료 리스트 [{ ingredient_id, ingredient_name, ingredient_amount, ingredient_unit }]"
    )
    
    stages: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="요리 과정 { step, timeline, description }"
    )
    
    # 감사 필드
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="생성 시간"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="수정 시간"
    )
    
    # 관계 설정
    user: Mapped["User"] = relationship(
        "User",
        back_populates="recipes"
    )
    
    recipe_base: Mapped["RecipeBase"] = relationship(
        "RecipeBase",
        back_populates="recipes"
    )
    
    # 인덱스 설정
    __table_args__ = (
        Index('idx_recipes_user_id', 'user_id'),
        Index('idx_recipes_recipe_base_id', 'recipe_base_id'),
        Index('idx_recipes_created_at', 'created_at'),
    )

    def __repr__(self) -> str:
        return f"<Recipe(recipe_id={self.recipe_id}, user_id={self.user_id}, title={self.title})>"


__all__ = [
    "RecipeBase",
    "RecipeBaseContent", 
    "RecipeBaseStatus",
    "Ingredient",
    "Recipe",
    "RecipeLanguage",
    "RecipeDifficulty",
    "RecipeState"
] 