"""
RDB 테스트 설정

이 모듈은 RDB 관련 테스트를 위한 공통 설정을 제공합니다.
테스트용 데이터베이스 연결 및 fixture를 설정합니다.
"""

import pytest
import os
import tempfile
import time
from typing import Generator
from sqlmodel import Session, select, text
from ulid import ULID

from src.common.rdb.common.database import DatabaseManager
from src.common.rdb.domain.user.models import User, UserProfile, UserBilling, UserAlert
from src.common.rdb.domain.recipe.models import RecipeBase, RecipeBaseContent, RecipeBaseState, RecipeLanguage, RecipeState, Ingredient, Recipe, RecipeDifficulty


@pytest.fixture(scope="session")
def test_database_url():
    """테스트용 데이터베이스 URL을 생성합니다."""
    # PostgreSQL 환경 변수 확인
    postgres_host = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port = os.getenv("POSTGRES_PORT", "5432")
    postgres_db = os.getenv("POSTGRES_DB", "puhahang_test")
    # postgres_db = "test"
    postgres_user = os.getenv("POSTGRES_USER", "postgres")
    postgres_pw = os.getenv("POSTGRES_PW", "postgres")
    
    # PostgreSQL 환경 변수가 설정되어 있으면 PostgreSQL 사용
    if all([postgres_host, postgres_port, postgres_db, postgres_user]):
        return f"postgresql+psycopg2://{postgres_user}:{postgres_pw}@{postgres_host}:{postgres_port}/{postgres_db}"

@pytest.fixture(scope="session")
def create_test_database(test_database_url):
    """테스트용 데이터베이스를 생성합니다."""
    # 테스트용 DatabaseManager 인스턴스 생성
    db_manager = DatabaseManager()
    db_manager.initialize(test_database_url)
    
    # PostgreSQL인지 SQLite인지 확인
    is_postgresql = "postgresql" in test_database_url
    
    if is_postgresql:
        # PostgreSQL: 모든 테이블 생성 (JSONB 지원)
        from sqlmodel import SQLModel
        SQLModel.metadata.create_all(bind=db_manager.engine)
    else:
        # SQLite: JSONB 필드가 있는 테이블은 제외하고 테이블 생성
        from sqlmodel import SQLModel
        from src.common.rdb.domain.user.models import User, UserProfile, UserBilling, UserAlert
        from src.common.rdb.domain.recipe.models import Ingredient
        
        # JSONB 필드가 없는 테이블만 생성
        SQLModel.metadata.create_all(
            bind=db_manager.engine,
            tables=[
                User.__table__,
                UserProfile.__table__,
                UserBilling.__table__,
                UserAlert.__table__,
                Ingredient.__table__
            ]
        )
    
    yield db_manager
    
    # 테스트 완료 후 정리
    db_manager.close()
    
    # SQLite 임시 파일 삭제
    if hasattr(pytest, 'test_db_path') and os.path.exists(pytest.test_db_path):
        os.unlink(pytest.test_db_path)


@pytest.fixture(scope="session")
def db_manager(test_database_url, create_test_database):
    """테스트용 DatabaseManager 인스턴스를 반환합니다."""
    return create_test_database


@pytest.fixture
def session(db_manager) -> Generator[Session, None, None]:
    """테스트용 데이터베이스 세션을 제공합니다."""
    with db_manager.session_scope() as session:
        yield session


@pytest.fixture
def clean_database(session):
    """테스트 전후로 데이터베이스를 정리합니다."""
    # PostgreSQL인지 SQLite인지 확인
    is_postgresql = "postgresql" in str(session.bind.url)
    
    if is_postgresql:
        # PostgreSQL: 모든 테이블 정리
        # 테스트 전에 기존 데이터 확인 (트랜잭션 시작)
        session.exec(select(Recipe)).all()
        session.exec(select(RecipeBaseState)).all()
        session.exec(select(RecipeBaseContent)).all()
        session.exec(select(RecipeBase)).all()
        session.exec(select(Ingredient)).all()
        session.exec(select(UserAlert)).all()
        session.exec(select(UserBilling)).all()
        session.exec(select(UserProfile)).all()
        session.exec(select(User)).all()
        
        yield
        
        # 테스트 후 정리 (역순으로 삭제하여 외래키 제약조건 준수)
        from sqlmodel import delete
        try:
            session.exec(delete(Recipe))
            session.exec(delete(RecipeBaseState))
            session.exec(delete(RecipeBaseContent))
            session.exec(delete(RecipeBase))
            session.exec(delete(Ingredient))
            session.exec(delete(UserAlert))
            session.exec(delete(UserBilling))
            session.exec(delete(UserProfile))
            session.exec(delete(User))
            session.exec(text("DROP TABLE IF EXISTS test_table"))
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"데이터베이스 정리 중 오류 발생: {e}")
    else:
        # SQLite: JSONB 필드가 있는 테이블 제외
        session.exec(select(Ingredient)).all()
        session.exec(select(UserAlert)).all()
        session.exec(select(UserBilling)).all()
        session.exec(select(UserProfile)).all()
        session.exec(select(User)).all()
        
        yield
        
        # 테스트 후 정리 (JSONB 필드가 있는 테이블 제외)
        from sqlmodel import delete
        try:
            session.exec(delete(Ingredient))
            session.exec(delete(UserAlert))
            session.exec(delete(UserBilling))
            session.exec(delete(UserProfile))
            session.exec(delete(User))
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"데이터베이스 정리 중 오류 발생: {e}")


@pytest.fixture
def sample_user(session) -> User:
    """샘플 사용자를 생성합니다."""
    user = User(
        role="USER",
        provider="GUEST"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def sample_user_profile(session, sample_user) -> UserProfile:
    """샘플 사용자 프로필을 생성합니다."""
    profile = UserProfile(
        user_id=sample_user.user_id,
        nickname=f"test_user_{str(ULID())[-8:]}",
        region="KR"
    )
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


@pytest.fixture
def sample_user_billing(session, sample_user) -> UserBilling:
    """샘플 사용자 결제 정보를 생성합니다."""
    billing = UserBilling(
        user_id=sample_user.user_id,
        billing="FREE"
    )
    session.add(billing)
    session.commit()
    session.refresh(billing)
    return billing


@pytest.fixture
def sample_user_alert(session, sample_user) -> UserAlert:
    """샘플 사용자 알림 정보를 생성합니다."""
    alert = UserAlert(
        user_id=sample_user.user_id,
        fcm_token="test_fcm_token",
        is_alerted=False
    )
    session.add(alert)
    session.commit()
    session.refresh(alert)
    return alert


@pytest.fixture
def complete_user(session, sample_user, sample_user_profile, sample_user_billing, sample_user_alert) -> User:
    """완전한 사용자 정보를 가진 사용자를 반환합니다."""
    return sample_user


@pytest.fixture
def sample_ingredient(session) -> Ingredient:
    """샘플 재료를 생성합니다."""
    ingredient = Ingredient(
        ingredient="Test Ingredient"
    )
    session.add(ingredient)
    session.commit()
    session.refresh(ingredient)
    return ingredient


# PostgreSQL 환경에서만 사용할 수 있는 fixture들
@pytest.fixture
def sample_recipe_base(session) -> RecipeBase:
    """샘플 레시피 베이스를 생성합니다. (PostgreSQL 환경에서만 사용 가능)"""
    # PostgreSQL 환경인지 확인
    is_postgresql = "postgresql" in str(session.bind.url)
    if not is_postgresql:
        pytest.skip("PostgreSQL 환경에서만 사용 가능한 fixture입니다.")
    
    recipe_base = RecipeBase(
        checksum=f"test_checksum_{int(time.time() * 1000)}",
        thumbnail="https://example.com/thumbnail.jpg",
        reference={
            "platform": "test", 
            "url": "https://example.com/recipe", 
            "metadata": {"source": "test", "author": "test_author"}
        },
        servings=4,
        difficulty=RecipeDifficulty.NORMAL,
        estimated_time=60
    )
    session.add(recipe_base)
    session.commit()
    session.refresh(recipe_base)
    return recipe_base


@pytest.fixture
def sample_recipe_base_state(session, sample_recipe_base_content) -> RecipeBaseState:
    """샘플 레시피 베이스 상태를 생성합니다. (PostgreSQL 환경에서만 사용 가능)"""
    state = RecipeBaseState(
        recipe_base_content_id=sample_recipe_base_content.recipe_base_content_id,
        state=RecipeState.PENDING
    )
    session.add(state)
    session.commit()
    session.refresh(state)
    return state

@pytest.fixture
def sample_recipe_base_content(session, sample_recipe_base) -> RecipeBaseContent:
    """샘플 레시피 베이스 컨텐츠를 생성합니다. (PostgreSQL 환경에서만 사용 가능)"""
    # PostgreSQL 환경인지 확인
    is_postgresql = "postgresql" in str(session.bind.url)
    if not is_postgresql:
        pytest.skip("PostgreSQL 환경에서만 사용 가능한 fixture입니다.")
    
    content = RecipeBaseContent(
        recipe_base_id=sample_recipe_base.recipe_base_id,
        title="테스트 레시피 제목",
        author="테스트 작성자",
        ingredients=[
            {"ingredient_name": "양파", "ingredient_amount": "1개", "ingredient_unit": "개"},
            {"ingredient_name": "마늘", "ingredient_amount": "3쪽", "ingredient_unit": "쪽"}
        ],
        stages={"steps": ["1. 양파를 자른다", "2. 마늘을 다진다", "3. 볶는다"]},
        language="ko",
        model_name="test_model_v1"
    )
    session.add(content)
    session.commit()
    session.refresh(content)
    return content


@pytest.fixture
def sample_recipe_base_state(session, sample_recipe_base_content) -> RecipeBaseState:
    """샘플 레시피 베이스 상태를 생성합니다. (PostgreSQL 환경에서만 사용 가능)"""
    state = RecipeBaseState(
        recipe_base_content_id=sample_recipe_base_content.recipe_base_content_id,
        state=RecipeState.PENDING
    )
    session.add(state)
    session.commit()
    session.refresh(state)
    return state

@pytest.fixture
def complete_recipe_base(session, sample_recipe_base) -> RecipeBase:
    """완전한 레시피 베이스 정보를 가진 레시피 베이스를 반환합니다. (PostgreSQL 환경에서만 사용 가능)"""
    return sample_recipe_base

@pytest.fixture
def complete_recipe_base_content(session, sample_recipe_base_content) -> RecipeBaseContent:
    """완전한 레시피 베이스 정보를 가진 레시피 베이스를 반환합니다. (PostgreSQL 환경에서만 사용 가능)"""
    return sample_recipe_base_content

@pytest.fixture
def complete_recipe_base_state(session, sample_recipe_base_state) -> RecipeBaseState:
    """완전한 레시피 베이스 상태 정보를 가진 레시피 베이스 상태를 반환합니다. (PostgreSQL 환경에서만 사용 가능)"""
    return sample_recipe_base_state


@pytest.fixture
def sample_recipe(session, complete_user, complete_recipe_base_content) -> Recipe:
    """샘플 레시피를 생성합니다. (PostgreSQL 환경에서만 사용 가능)"""
    # PostgreSQL 환경인지 확인
    is_postgresql = "postgresql" in str(session.bind.url)
    if not is_postgresql:
        pytest.skip("PostgreSQL 환경에서만 사용 가능한 fixture입니다.")
    
    recipe = Recipe(
        user_id=complete_user.user_id,
        recipe_base_content_id=complete_recipe_base_content.recipe_base_content_id,
        title="테스트 레시피",
        ingredients=[
            {"ingredient_name": "양파", "ingredient_amount": "2개", "ingredient_unit": "개"},
            {"ingredient_name": "마늘", "ingredient_amount": "5쪽", "ingredient_unit": "쪽"}
        ],
        stages={"steps": ["1. 양파를 자른다", "2. 마늘을 다진다", "3. 볶는다"]}
    )
    session.add(recipe)
    session.commit()
    session.refresh(recipe)
    return recipe


def pytest_configure(config):
    """pytest 설정을 구성합니다."""
    config.addinivalue_line("markers", "database: mark test as database test")
    config.addinivalue_line("markers", "repository: mark test as repository test")
    config.addinivalue_line("markers", "service: mark test as service test")
    config.addinivalue_line("markers", "slow: mark test as slow test") 