"""
Recipe 도메인 모델 정의

이 모듈은 레시피 관련 데이터베이스 모델을 정의합니다.
SQLModel을 사용하여 타입 안전성과 데이터 검증을 제공합니다.
ERD 구조에 따라 레시피 정보를 여러 테이블로 분리하여 관리합니다.
사용자 ID는 ULID 형태로 참조됩니다.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import String, Integer, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

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
    VERY_EASY = "VERY_EASY"
    EASY = "EASY"
    NORMAL = "NORMAL"
    HARD = "HARD"
    VERY_HARD = "VERY_HARD"


class RecipeState(str, Enum):
    """레시피 정제 현황 enum"""
    PENDING = "PENDING"
    VERIFYING = "VERIFYING"
    TRANSFORMING = "TRANSFORMING"
    PROCESSING = "PROCESSING"
    EVALUATING = "EVALUATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class RecipeBase(SQLModel, table=True):
    """레시피 기본 정보 테이블"""
    __tablename__ = "recipe_bases"

    recipe_base_id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="레시피 원본 ID"
    )
    
    checksum: str = Field(
        unique=True,
        max_length=256,
        description="url sha256 해싱 값"
    )
    
    thumbnail: Optional[str] = Field(
        default=None,
        max_length=255,
        description="레시피 대표 사진 URL"
    )
    
    reference: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB),
        description="컨텐츠 소스 (platform, url, metadata)"
    )
    
    view_count: int = Field(
        default=0,
        description="레시피 조회 횟수"
    )
    
    servings: Optional[int] = Field(
        default=None,
        description="제공량"
    )
    
    difficulty: Optional[RecipeDifficulty] = Field(
        default=None,
        description="요리 난이도"
    )
    
    estimated_time: Optional[int] = Field(
        default=None,
        description="추정 요리 소요 시간(분)"
    )
    
    # 감사 필드
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="생성 시간"
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now},
        description="수정 시간"
    )
    
    # 관계 설정
    recipe_base_content: List["RecipeBaseContent"] = Relationship(
        back_populates="recipe_base",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    def __repr__(self) -> str:
        return f"<RecipeBase(recipe_base_id={self.recipe_base_id}, checksum={self.checksum})>"


class RecipeBaseContent(SQLModel, table=True):
    """레시피 컨텐츠 정보 테이블"""
    __tablename__ = "recipe_base_contents"
    
    recipe_base_content_id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="레시피 컨텐츠 ID"
    )
    
    recipe_base_id: int = Field(
        foreign_key="recipe_bases.recipe_base_id",
        description="레시피 원본 ID"
    )
    
    title: str = Field(
        max_length=30,
        description="레시피 제목"
    )
    
    author: Optional[str] = Field(
        default=None,
        max_length=24,
        description="원작자"
    )
    
    ingredients: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        sa_column=Column(JSONB),
        description="재료 리스트 [{ ingredient_id, ingredient_name, ingredient_amount, ingredient_unit }]"
    )
    
    stages: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB),
        description="요리 과정 { step, timeline, description }"
    )
    
    language: RecipeLanguage = Field(
        description="언어"
    )
    
    model_name: str = Field(
        max_length=255,
        description="정제 시 사용한 모델 버전"
    )
    
    # 감사 필드
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="생성 시간"
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now},
        description="수정 시간"
    )
    
    # 관계 설정
    recipe_base: "RecipeBase" = Relationship(back_populates="recipe_base_content")

    recipe_base_state: Optional["RecipeBaseState"] = Relationship(
        back_populates="recipe_base_content",
        sa_relationship_kwargs={"uselist": False, "cascade": "all, delete-orphan"}
    )

    recipe: List["Recipe"] = Relationship(
        back_populates="recipe_base_content",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    def __repr__(self) -> str:
        return f"<RecipeBaseContent(recipe_base_content_id={self.recipe_base_content_id}, title={self.title})>"


class RecipeBaseState(SQLModel, table=True):
    """레시피 베이스 상태 테이블"""
    __tablename__ = "recipe_base_states"
    
    recipe_base_content_id: int = Field(
        primary_key=True,
        foreign_key="recipe_base_contents.recipe_base_content_id",
        description="레시피 원본 ID"
    )
    
    state: RecipeState = Field(
        default=RecipeState.PENDING,
        description="레시피 정제 현황"
    )
    
    # 관계 설정
    recipe_base_content: "RecipeBaseContent" = Relationship(back_populates="recipe_base_state")

    def __repr__(self) -> str:
        return f"<RecipeBaseState(recipe_base_content_id={self.recipe_base_content_id}, state={self.state})>"


class Ingredient(SQLModel, table=True):
    """재료 태그 테이블 (검색용)"""
    __tablename__ = "ingredients"
    
    ingredient_id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="재료 ID"
    )
    
    ingredient: str = Field(
        max_length=32,
        description="재료명"
    )

    def __repr__(self) -> str:
        return f"<Ingredient(ingredient_id={self.ingredient_id}, ingredient={self.ingredient})>"


class Recipe(SQLModel, table=True):
    """사용자 레시피 테이블"""
    __tablename__ = "recipes"
    
    recipe_id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="레시피 ID"
    )
    
    user_id: str = Field(
        foreign_key="users.user_id",
        description="사용자 ULID"
    )
    
    recipe_base_content_id: int = Field(
        foreign_key="recipe_base_contents.recipe_base_content_id",
        description="원본 레시피 ID"
    )
    
    title: Optional[str] = Field(
        default=None,
        max_length=255,
        description="레시피 제목"
    )
    
    ingredients: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        sa_column=Column(JSONB),
        description="재료 리스트 [{ ingredient_id, ingredient_name, ingredient_amount, ingredient_unit }]"
    )
    
    stages: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB),
        description="요리 과정 { step, timeline, description }"
    )
    
    # 감사 필드
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="생성 시간"
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now},
        description="수정 시간"
    )
    
    # 관계 설정
    recipe_base_content: "RecipeBaseContent" = Relationship(back_populates="recipe")

    user: "User" = Relationship(back_populates="recipe")

    def __repr__(self) -> str:
        return f"<Recipe(recipe_id={self.recipe_id}, user_id={self.user_id}, title={self.title})>"


__all__ = [
    "RecipeBase",
    "RecipeBaseContent", 
    "RecipeBaseState",
    "Ingredient",
    "Recipe",
    "RecipeLanguage",
    "RecipeDifficulty",
    "RecipeState"
] 