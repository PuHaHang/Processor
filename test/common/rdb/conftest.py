# """
# pytest 테스트 설정 파일

# 이 파일은 pytest 테스트 실행 시 사용되는 설정과 픽스처를 정의합니다.
# 실제 PostgreSQL 데이터베이스와 연결하여 테스트를 수행합니다.
# """

# import os
# import pytest
# import uuid
# from typing import Generator

# from sqlalchemy import create_engine, text
# from sqlalchemy.orm import Session

# from src.common.rdb.common.database import DatabaseManager, Base
# from src.common.rdb.domain.user.models import User, UserProfile, UserBilling, UserAlert, UserRole, UserProvider, UserRegion, UserBillingType
# from src.common.rdb.domain.recipe.models import RecipeBase, RecipeBaseContent, RecipeBaseState, Recipe, Ingredient, RecipeLanguage, RecipeDifficulty, RecipeState


# @pytest.fixture(scope="session")
# def test_database_url():
#     """테스트 데이터베이스 URL을 반환합니다."""
#     host = os.getenv("POSTGRES_HOST", "localhost")
#     port = os.getenv("POSTGRES_PORT", "5432")
#     # database = os.getenv("POSTGRES_DB", "puhahang_test")
#     database = "puhahang_test"
#     username = os.getenv("POSTGRES_USER", "postgres")
#     password = os.getenv("POSTGRES_PW", "")
#     print("host", host)
#     print("port", port)
#     print("database", database)
#     print("username", username)
#     print("password", password)
#     return f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"


# @pytest.fixture(scope="session")
# def create_test_database(test_database_url):
#     """테스트 데이터베이스를 생성합니다."""
#     # 기본 데이터베이스에 연결하여 테스트 DB 생성
#     base_url = test_database_url.rsplit('/', 1)[0] + '/postgres'
#     engine = create_engine(base_url)
    
#     # 테스트 데이터베이스 이름 추출
#     test_db_name = test_database_url.split('/')[-1]
    
#     with engine.connect() as connection:
#         # 자동 커밋 모드로 설정
#         connection.execute(text("COMMIT"))
        
#         # 기존 테스트 데이터베이스 삭제 (있는 경우)
#         try:
#             connection.execute(text(f"DROP DATABASE IF EXISTS {test_db_name}"))
#         except Exception:
#             pass
        
#         # 새 테스트 데이터베이스 생성
#         connection.execute(text(f"CREATE DATABASE {test_db_name}"))
    
#     engine.dispose()
    
#     yield test_db_name
    
#     # 테스트 완료 후 데이터베이스 정리
#     engine = create_engine(base_url)
#     with engine.connect() as connection:
#         connection.execute(text("COMMIT"))
#         try:
#             connection.execute(text(f"DROP DATABASE IF EXISTS {test_db_name}"))
#         except Exception:
#             pass
#     engine.dispose()


# @pytest.fixture(scope="session")
# def db_manager(test_database_url, create_test_database):
#     """테스트용 데이터베이스 매니저를 생성합니다."""
#     manager = DatabaseManager()
#     manager.initialize(
#         database_url=test_database_url,
#         echo=False,  # 테스트 시 SQL 로그 출력 안함
#         pool_size=5,
#         max_overflow=10,
#         pool_timeout=30,
#         pool_recycle=3600
#     )
    
#     # 테이블 생성
#     manager.create_tables()
    
#     yield manager
    
#     # 테스트 완료 후 연결 정리
#     manager.close()


# @pytest.fixture
# def session(db_manager) -> Generator[Session, None, None]:
#     """각 테스트에 대해 새로운 데이터베이스 세션을 제공합니다."""
#     session = db_manager.get_session()
    
#     try:
#         yield session
#     finally:
#         session.rollback()
#         session.close()


# @pytest.fixture
# def clean_database(session):
#     """각 테스트 후 데이터베이스를 정리합니다."""
#     yield
    
#     # 테스트 후 모든 테이블 데이터 삭제 (외래키 제약 조건 순서 고려)
#     session.execute(text("DELETE FROM recipes"))
#     session.execute(text("DELETE FROM ingredients"))
#     session.execute(text("DELETE FROM recipe_bases_content"))
#     session.execute(text("DELETE FROM recipe_bases_status"))
#     session.execute(text("DELETE FROM recipe_bases"))
#     session.execute(text("DELETE FROM users_alert"))
#     session.execute(text("DELETE FROM users_billing"))
#     session.execute(text("DELETE FROM users_profile"))
#     session.execute(text("DELETE FROM users"))
    
#     session.commit()


# @pytest.fixture
# def sample_user(session) -> User:
#     """테스트용 샘플 사용자를 생성합니다."""
#     user_id = str(uuid.uuid4())
#     user = User(
#         user_id=user_id,
#         role=UserRole.USER,
#         provider=UserProvider.GUEST,
#         openid=None
#     )
#     session.add(user)
#     session.flush()
#     return user


# @pytest.fixture
# def sample_user_profile(session, sample_user) -> UserProfile:
#     """테스트용 샘플 사용자 프로필을 생성합니다."""
#     profile = UserProfile(
#         user_id=sample_user.user_id,
#         nickname="test_user",
#         image="https://example.com/image.jpg",
#         region=UserRegion.KR
#     )
#     session.add(profile)
#     session.flush()
#     return profile


# @pytest.fixture
# def sample_user_billing(session, sample_user) -> UserBilling:
#     """테스트용 샘플 사용자 결제 정보를 생성합니다."""
#     billing = UserBilling(
#         user_id=sample_user.user_id,
#         billing=UserBillingType.FREE
#     )
#     session.add(billing)
#     session.flush()
#     return billing


# @pytest.fixture
# def sample_user_alert(session, sample_user) -> UserAlert:
#     """테스트용 샘플 사용자 알림 정보를 생성합니다."""
#     alert = UserAlert(
#         user_id=sample_user.user_id,
#         fcm_token="test_fcm_token",
#         alert_flag=True
#     )
#     session.add(alert)
#     session.flush()
#     return alert


# @pytest.fixture
# def complete_user(session, sample_user, sample_user_profile, sample_user_billing, sample_user_alert) -> User:
#     """완전한 사용자 정보를 가진 테스트용 사용자를 생성합니다."""
#     session.commit()
#     return sample_user


# @pytest.fixture
# def sample_recipe_base(session) -> RecipeBase:
#     """테스트용 샘플 레시피 베이스를 생성합니다."""
#     recipe_base = RecipeBase(
#         chksum="test_checksum_12345",
#         thumbnail="https://example.com/thumbnail.jpg",
#         referrer={"platform": "test", "url": "https://example.com/recipe"},
#         metadata={"source": "test"},
#         servings=4,
#         difficulty=RecipeDifficulty.normal,
#         estimated_time=60
#     )
#     session.add(recipe_base)
#     session.flush()
#     return recipe_base


# @pytest.fixture
# def sample_recipe_base_content(session, sample_recipe_base) -> RecipeBaseContent:
#     """테스트용 샘플 레시피 베이스 컨텐츠를 생성합니다."""
#     content = RecipeBaseContent(
#         recipe_base_id=sample_recipe_base.recipe_base_id,
#         title="테스트 레시피",
#         author="테스트 요리사",
#         ingredients=[
#             {"ingredient_name": "양파", "ingredient_amount": "1개", "ingredient_unit": "개"},
#             {"ingredient_name": "당근", "ingredient_amount": "2개", "ingredient_unit": "개"}
#         ],
#         stages={"steps": ["1. 양파를 자른다", "2. 당근을 자른다"]},
#         language=RecipeLanguage.ko,
#         model_name="test_model_v1"
#     )
#     session.add(content)
#     session.flush()
#     return content


# @pytest.fixture
# def sample_recipe_base_status(session, sample_recipe_base) -> RecipeBaseState:
#     """테스트용 샘플 레시피 베이스 상태를 생성합니다."""
#     status = RecipeBaseState(
#         recipe_base_id=sample_recipe_base.recipe_base_id,
#         state=RecipeState.COMPLETED
#     )
#     session.add(status)
#     session.flush()
#     return status


# @pytest.fixture
# def complete_recipe_base(session, sample_recipe_base, sample_recipe_base_content, sample_recipe_base_status) -> RecipeBase:
#     """완전한 레시피 베이스 정보를 가진 테스트용 레시피 베이스를 생성합니다."""
#     session.commit()
#     return sample_recipe_base


# @pytest.fixture
# def sample_recipe(session, complete_user, complete_recipe_base) -> Recipe:
#     """테스트용 샘플 레시피를 생성합니다."""
#     recipe = Recipe(
#         user_id=complete_user.user_id,
#         recipe_base_id=complete_recipe_base.recipe_base_id,
#         title="내 맞춤 레시피",
#         ingredients=[
#             {"ingredient_name": "양파", "ingredient_amount": "2개", "ingredient_unit": "개"},
#             {"ingredient_name": "당근", "ingredient_amount": "1개", "ingredient_unit": "개"}
#         ],
#         stages={"steps": ["1. 양파를 많이 자른다", "2. 당근을 조금 자른다"]}
#     )
#     session.add(recipe)
#     session.flush()
#     return recipe


# @pytest.fixture
# def sample_ingredient(session) -> Ingredient:
#     """테스트용 샘플 재료를 생성합니다."""
#     ingredient = Ingredient(
#         ingredient="테스트 재료"
#     )
#     session.add(ingredient)
#     session.flush()
#     return ingredient


# # 테스트 마커 정의
# def pytest_configure(config):
#     """pytest 설정을 구성합니다."""
#     config.addinivalue_line(
#         "markers", "slow: 느린 테스트 표시"
#     )
#     config.addinivalue_line(
#         "markers", "integration: 통합 테스트 표시"
#     )
#     config.addinivalue_line(
#         "markers", "database: 데이터베이스 테스트 표시"
#     ) 