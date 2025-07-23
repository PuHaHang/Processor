# """
# Recipe 도메인 Repository 테스트

# 이 모듈은 Recipe 도메인의 모든 Repository 클래스들을 테스트합니다.
# 실제 PostgreSQL 데이터베이스와 연결하여 테스트합니다.
# """

# import pytest
# import uuid
# from datetime import datetime

# from src.common.rdb.domain.recipe.models import RecipeBase, RecipeBaseContent, RecipeBaseStatus, Recipe, Ingredient, RecipeLanguage, RecipeDifficulty, RecipeState
# from src.common.rdb.domain.recipe.repository import RecipeBaseRepository, RecipeBaseContentRepository, RecipeBaseStatusRepository, RecipeRepository, IngredientRepository


# @pytest.mark.database
# @pytest.mark.repository
# class TestRecipeBaseRepository:
#     """RecipeBaseRepository 클래스의 기능을 테스트합니다."""
    
#     def test_create_recipe_base(self, session, clean_database):
#         """레시피 베이스 생성 테스트"""
#         repository = RecipeBaseRepository()
        
#         # 레시피 베이스 생성
#         recipe_base = RecipeBase(
#             chksum="test_checksum_123",
#             thumbnail="https://example.com/thumbnail.jpg",
#             referrer={"platform": "test", "url": "https://example.com/recipe"},
#             metadata={"source": "test", "author": "test_author"},
#             servings=4,
#             difficulty=RecipeDifficulty.normal,
#             estimated_time=60
#         )
        
#         created_recipe_base = repository.create(session, recipe_base)
        
#         # 결과 확인
#         assert created_recipe_base.chksum == "test_checksum_123"
#         assert created_recipe_base.thumbnail == "https://example.com/thumbnail.jpg"
#         assert created_recipe_base.referrer["platform"] == "test"
#         assert created_recipe_base.servings == 4
#         assert created_recipe_base.difficulty == RecipeDifficulty.normal
#         assert created_recipe_base.estimated_time == 60
#         assert created_recipe_base.view_count == 0
#         assert created_recipe_base.created_at is not None
#         assert created_recipe_base.updated_at is not None
    
#     def test_find_by_id(self, session, sample_recipe_base, clean_database):
#         """ID로 레시피 베이스 조회 테스트"""
#         repository = RecipeBaseRepository()
        
#         # 레시피 베이스 조회
#         found_recipe_base = repository.find_by_id(session, sample_recipe_base.recipe_base_id)
        
#         # 결과 확인
#         assert found_recipe_base is not None
#         assert found_recipe_base.recipe_base_id == sample_recipe_base.recipe_base_id
#         assert found_recipe_base.chksum == sample_recipe_base.chksum
    
#     def test_find_by_checksum(self, session, sample_recipe_base, clean_database):
#         """체크섬으로 레시피 베이스 조회 테스트"""
#         repository = RecipeBaseRepository()
        
#         # 체크섬으로 조회
#         found_recipe_base = repository.find_by_checksum(session, sample_recipe_base.chksum)
        
#         # 결과 확인
#         assert found_recipe_base is not None
#         assert found_recipe_base.chksum == sample_recipe_base.chksum
#         assert found_recipe_base.recipe_base_id == sample_recipe_base.recipe_base_id
    
#     def test_find_by_difficulty(self, session, clean_database):
#         """난이도로 레시피 베이스 조회 테스트"""
#         repository = RecipeBaseRepository()
        
#         # 여러 난이도의 레시피 베이스 생성
#         difficulties = [RecipeDifficulty.easy, RecipeDifficulty.normal, RecipeDifficulty.easy]
#         for i, difficulty in enumerate(difficulties):
#             recipe_base = RecipeBase(
#                 chksum=f"test_checksum_{i}",
#                 difficulty=difficulty
#             )
#             repository.create(session, recipe_base)
        
#         # easy 난이도로 조회
#         easy_recipes = repository.find_by_difficulty(session, RecipeDifficulty.easy)
        
#         # 결과 확인
#         assert len(easy_recipes) == 2
#         for recipe in easy_recipes:
#             assert recipe.difficulty == RecipeDifficulty.easy
    
#     def test_find_by_servings(self, session, clean_database):
#         """인분 수로 레시피 베이스 조회 테스트"""
#         repository = RecipeBaseRepository()
        
#         # 여러 인분 수의 레시피 베이스 생성
#         servings_list = [2, 4, 2, 6]
#         for i, servings in enumerate(servings_list):
#             recipe_base = RecipeBase(
#                 chksum=f"test_checksum_{i}",
#                 servings=servings
#             )
#             repository.create(session, recipe_base)
        
#         # 2인분으로 조회
#         two_serving_recipes = repository.find_by_servings(session, 2)
        
#         # 결과 확인
#         assert len(two_serving_recipes) == 2
#         for recipe in two_serving_recipes:
#             assert recipe.servings == 2
    
#     def test_find_popular(self, session, clean_database):
#         """인기 레시피 베이스 조회 테스트"""
#         repository = RecipeBaseRepository()
        
#         # 여러 조회수의 레시피 베이스 생성
#         view_counts = [100, 50, 200, 75]
#         created_recipes = []
#         for i, view_count in enumerate(view_counts):
#             recipe_base = RecipeBase(
#                 chksum=f"test_checksum_{i}",
#                 view_count=view_count
#             )
#             created_recipes.append(repository.create(session, recipe_base))
        
#         # 인기 레시피 조회
#         popular_recipes = repository.find_popular(session, limit=3)
        
#         # 결과 확인 (조회수 내림차순)
#         assert len(popular_recipes) == 3
#         assert popular_recipes[0].view_count == 200
#         assert popular_recipes[1].view_count == 100
#         assert popular_recipes[2].view_count == 75
    
#     def test_update_recipe_base(self, session, sample_recipe_base, clean_database):
#         """레시피 베이스 업데이트 테스트"""
#         repository = RecipeBaseRepository()
        
#         # 레시피 베이스 정보 변경
#         sample_recipe_base.thumbnail = "https://example.com/updated_thumbnail.jpg"
#         sample_recipe_base.servings = 6
#         sample_recipe_base.difficulty = RecipeDifficulty.hard
        
#         # 업데이트 실행
#         updated_recipe_base = repository.update(session, sample_recipe_base)
        
#         # 결과 확인
#         assert updated_recipe_base.thumbnail == "https://example.com/updated_thumbnail.jpg"
#         assert updated_recipe_base.servings == 6
#         assert updated_recipe_base.difficulty == RecipeDifficulty.hard
#         assert updated_recipe_base.updated_at is not None
    
#     def test_delete_recipe_base(self, session, sample_recipe_base, clean_database):
#         """레시피 베이스 삭제 테스트"""
#         repository = RecipeBaseRepository()
        
#         # 레시피 베이스 삭제
#         result = repository.delete(session, sample_recipe_base)
        
#         # 결과 확인
#         assert result is True
        
#         # 삭제 확인
#         found_recipe_base = repository.find_by_id(session, sample_recipe_base.recipe_base_id)
#         assert found_recipe_base is None
    
#     def test_increment_view_count(self, session, sample_recipe_base, clean_database):
#         """조회수 증가 테스트"""
#         repository = RecipeBaseRepository()
        
#         # 초기 조회수 확인
#         initial_view_count = sample_recipe_base.view_count
        
#         # 조회수 증가
#         updated_recipe_base = repository.increment_view_count(session, sample_recipe_base)
        
#         # 결과 확인
#         assert updated_recipe_base.view_count == initial_view_count + 1
    
#     def test_exists_by_checksum(self, session, sample_recipe_base, clean_database):
#         """체크섬으로 레시피 베이스 존재 여부 확인 테스트"""
#         repository = RecipeBaseRepository()
        
#         # 존재하는 체크섬 확인
#         exists = repository.exists_by_checksum(session, sample_recipe_base.chksum)
#         assert exists is True
        
#         # 존재하지 않는 체크섬 확인
#         exists = repository.exists_by_checksum(session, "nonexistent_checksum")
#         assert exists is False


# @pytest.mark.database
# @pytest.mark.repository
# class TestRecipeBaseContentRepository:
#     """RecipeBaseContentRepository 클래스의 기능을 테스트합니다."""
    
#     def test_create_recipe_base_content(self, session, sample_recipe_base, clean_database):
#         """레시피 베이스 컨텐츠 생성 테스트"""
#         repository = RecipeBaseContentRepository()
        
#         # 레시피 베이스 컨텐츠 생성
#         content = RecipeBaseContent(
#             recipe_base_id=sample_recipe_base.recipe_base_id,
#             title="테스트 레시피 제목",
#             author="테스트 작성자",
#             ingredients=[
#                 {"ingredient_name": "양파", "ingredient_amount": "1개", "ingredient_unit": "개"},
#                 {"ingredient_name": "마늘", "ingredient_amount": "3쪽", "ingredient_unit": "쪽"}
#             ],
#             stages={"steps": ["1. 양파를 자른다", "2. 마늘을 다진다", "3. 볶는다"]},
#             language=RecipeLanguage.ko,
#             model_name="test_model_v1"
#         )
        
#         created_content = repository.create(session, content)
        
#         # 결과 확인
#         assert created_content.recipe_base_id == sample_recipe_base.recipe_base_id
#         assert created_content.title == "테스트 레시피 제목"
#         assert created_content.author == "테스트 작성자"
#         assert len(created_content.ingredients) == 2
#         assert created_content.ingredients[0]["ingredient_name"] == "양파"
#         assert created_content.language == RecipeLanguage.ko
#         assert created_content.model_name == "test_model_v1"
#         assert created_content.created_at is not None
#         assert created_content.updated_at is not None
    
#     def test_find_by_recipe_base_id(self, session, sample_recipe_base_content, clean_database):
#         """레시피 베이스 ID로 컨텐츠 조회 테스트"""
#         repository = RecipeBaseContentRepository()
        
#         # 레시피 베이스 ID로 조회
#         contents = repository.find_by_recipe_base_id(session, sample_recipe_base_content.recipe_base_id)
        
#         # 결과 확인
#         assert len(contents) == 1
#         assert contents[0].recipe_base_id == sample_recipe_base_content.recipe_base_id
#         assert contents[0].title == sample_recipe_base_content.title
    
#     def test_find_by_recipe_base_and_language(self, session, sample_recipe_base_content, clean_database):
#         """레시피 베이스 ID와 언어로 컨텐츠 조회 테스트"""
#         repository = RecipeBaseContentRepository()
        
#         # 레시피 베이스 ID와 언어로 조회
#         content = repository.find_by_recipe_base_and_language(
#             session, 
#             sample_recipe_base_content.recipe_base_id, 
#             sample_recipe_base_content.language
#         )
        
#         # 결과 확인
#         assert content is not None
#         assert content.recipe_base_id == sample_recipe_base_content.recipe_base_id
#         assert content.language == sample_recipe_base_content.language
    
#     def test_find_by_language(self, session, sample_recipe_base, clean_database):
#         """언어로 컨텐츠 조회 테스트"""
#         repository = RecipeBaseContentRepository()
        
#         # 여러 언어의 컨텐츠 생성
#         languages = [RecipeLanguage.ko, RecipeLanguage.en, RecipeLanguage.ko]
#         for i, language in enumerate(languages):
#             content = RecipeBaseContent(
#                 recipe_base_id=sample_recipe_base.recipe_base_id,
#                 title=f"Test Recipe {i}",
#                 language=language,
#                 model_name="test_model"
#             )
#             repository.create(session, content)
        
#         # 한국어 컨텐츠 조회
#         ko_contents = repository.find_by_language(session, RecipeLanguage.ko)
        
#         # 결과 확인
#         assert len(ko_contents) == 2
#         for content in ko_contents:
#             assert content.language == RecipeLanguage.ko
    
#     def test_find_by_model_name(self, session, sample_recipe_base, clean_database):
#         """모델명으로 컨텐츠 조회 테스트"""
#         repository = RecipeBaseContentRepository()
        
#         # 여러 모델명의 컨텐츠 생성
#         model_names = ["model_v1", "model_v2", "model_v1"]
#         for i, model_name in enumerate(model_names):
#             content = RecipeBaseContent(
#                 recipe_base_id=sample_recipe_base.recipe_base_id,
#                 title=f"Test Recipe {i}",
#                 language=RecipeLanguage.ko,
#                 model_name=model_name
#             )
#             repository.create(session, content)
        
#         # model_v1으로 조회
#         v1_contents = repository.find_by_model_name(session, "model_v1")
        
#         # 결과 확인
#         assert len(v1_contents) == 2
#         for content in v1_contents:
#             assert content.model_name == "model_v1"
    
#     def test_search_by_title(self, session, sample_recipe_base, clean_database):
#         """제목으로 컨텐츠 검색 테스트"""
#         repository = RecipeBaseContentRepository()
        
#         # 여러 제목의 컨텐츠 생성
#         titles = ["김치찌개", "된장찌개", "김치볶음밥", "볶음밥"]
#         for i, title in enumerate(titles):
#             content = RecipeBaseContent(
#                 recipe_base_id=sample_recipe_base.recipe_base_id,
#                 title=title,
#                 language=RecipeLanguage.ko,
#                 model_name="test_model"
#             )
#             repository.create(session, content)
        
#         # "김치"로 검색
#         kimchi_contents = repository.search_by_title(session, "김치")
        
#         # 결과 확인
#         assert len(kimchi_contents) == 2
#         for content in kimchi_contents:
#             assert "김치" in content.title
    
#     def test_search_by_author(self, session, sample_recipe_base, clean_database):
#         """작성자로 컨텐츠 검색 테스트"""
#         repository = RecipeBaseContentRepository()
        
#         # 여러 작성자의 컨텐츠 생성
#         authors = ["김요리사", "이요리사", "김셰프", "박요리사"]
#         for i, author in enumerate(authors):
#             content = RecipeBaseContent(
#                 recipe_base_id=sample_recipe_base.recipe_base_id,
#                 title=f"Test Recipe {i}",
#                 author=author,
#                 language=RecipeLanguage.ko,
#                 model_name="test_model"
#             )
#             repository.create(session, content)
        
#         # "김"으로 검색
#         kim_contents = repository.search_by_author(session, "김")
        
#         # 결과 확인
#         assert len(kim_contents) == 2
#         for content in kim_contents:
#             assert "김" in content.author
    
#     def test_update_content(self, session, sample_recipe_base_content, clean_database):
#         """컨텐츠 업데이트 테스트"""
#         repository = RecipeBaseContentRepository()
        
#         # 컨텐츠 정보 변경
#         sample_recipe_base_content.title = "수정된 레시피 제목"
#         sample_recipe_base_content.author = "수정된 작성자"
#         sample_recipe_base_content.ingredients = [
#             {"ingredient_name": "새로운 재료", "ingredient_amount": "1개", "ingredient_unit": "개"}
#         ]
        
#         # 업데이트 실행
#         updated_content = repository.update(session, sample_recipe_base_content)
        
#         # 결과 확인
#         assert updated_content.title == "수정된 레시피 제목"
#         assert updated_content.author == "수정된 작성자"
#         assert len(updated_content.ingredients) == 1
#         assert updated_content.ingredients[0]["ingredient_name"] == "새로운 재료"
#         assert updated_content.updated_at is not None
    
#     def test_delete_content(self, session, sample_recipe_base_content, clean_database):
#         """컨텐츠 삭제 테스트"""
#         repository = RecipeBaseContentRepository()
        
#         # 컨텐츠 삭제
#         result = repository.delete(session, sample_recipe_base_content)
        
#         # 결과 확인
#         assert result is True
        
#         # 삭제 확인
#         found_content = repository.find_by_id(session, sample_recipe_base_content.recipe_base_content_id)
#         assert found_content is None


# @pytest.mark.database
# @pytest.mark.repository
# class TestRecipeBaseStatusRepository:
#     """RecipeBaseStatusRepository 클래스의 기능을 테스트합니다."""
    
#     def test_create_recipe_base_status(self, session, sample_recipe_base, clean_database):
#         """레시피 베이스 상태 생성 테스트"""
#         repository = RecipeBaseStatusRepository()
        
#         # 레시피 베이스 상태 생성
#         status = RecipeBaseStatus(
#             recipe_base_id=sample_recipe_base.recipe_base_id,
#             state=RecipeState.PROCESSING
#         )
        
#         created_status = repository.create(session, status)
        
#         # 결과 확인
#         assert created_status.recipe_base_id == sample_recipe_base.recipe_base_id
#         assert created_status.state == RecipeState.PROCESSING
    
#     def test_find_by_recipe_base_id(self, session, sample_recipe_base_status, clean_database):
#         """레시피 베이스 ID로 상태 조회 테스트"""
#         repository = RecipeBaseStatusRepository()
        
#         # 레시피 베이스 ID로 조회
#         found_status = repository.find_by_recipe_base_id(session, sample_recipe_base_status.recipe_base_id)
        
#         # 결과 확인
#         assert found_status is not None
#         assert found_status.recipe_base_id == sample_recipe_base_status.recipe_base_id
#         assert found_status.state == sample_recipe_base_status.state
    
#     def test_find_by_state(self, session, sample_recipe_base, clean_database):
#         """상태로 레시피 베이스 상태 조회 테스트"""
#         repository = RecipeBaseStatusRepository()
        
#         # 여러 상태의 레시피 베이스 상태 생성
#         states = [RecipeState.PENDING, RecipeState.COMPLETED, RecipeState.PENDING]
#         recipe_bases = []
#         for i, state in enumerate(states):
#             recipe_base = RecipeBase(chksum=f"test_checksum_{i}")
#             session.add(recipe_base)
#             session.flush()
#             recipe_bases.append(recipe_base)
            
#             status = RecipeBaseStatus(
#                 recipe_base_id=recipe_base.recipe_base_id,
#                 state=state
#             )
#             repository.create(session, status)
        
#         # PENDING 상태로 조회
#         pending_statuses = repository.find_by_state(session, RecipeState.PENDING)
        
#         # 결과 확인
#         assert len(pending_statuses) == 2
#         for status in pending_statuses:
#             assert status.state == RecipeState.PENDING
    
#     def test_update_status(self, session, sample_recipe_base_status, clean_database):
#         """상태 업데이트 테스트"""
#         repository = RecipeBaseStatusRepository()
        
#         # 상태 변경
#         sample_recipe_base_status.state = RecipeState.FAILED
        
#         # 업데이트 실행
#         updated_status = repository.update(session, sample_recipe_base_status)
        
#         # 결과 확인
#         assert updated_status.state == RecipeState.FAILED
    
#     def test_delete_status(self, session, sample_recipe_base_status, clean_database):
#         """상태 삭제 테스트"""
#         repository = RecipeBaseStatusRepository()
        
#         # 상태 삭제
#         result = repository.delete(session, sample_recipe_base_status)
        
#         # 결과 확인
#         assert result is True
        
#         # 삭제 확인
#         found_status = repository.find_by_recipe_base_id(session, sample_recipe_base_status.recipe_base_id)
#         assert found_status is None
    
#     def test_count_by_state(self, session, sample_recipe_base, clean_database):
#         """상태별 레시피 베이스 상태 수 조회 테스트"""
#         repository = RecipeBaseStatusRepository()
        
#         # 여러 상태의 레시피 베이스 상태 생성
#         states = [RecipeState.PENDING, RecipeState.COMPLETED, RecipeState.PENDING, RecipeState.FAILED]
#         for i, state in enumerate(states):
#             recipe_base = RecipeBase(chksum=f"test_checksum_{i}")
#             session.add(recipe_base)
#             session.flush()
            
#             status = RecipeBaseStatus(
#                 recipe_base_id=recipe_base.recipe_base_id,
#                 state=state
#             )
#             repository.create(session, status)
        
#         # PENDING 상태 수 조회
#         pending_count = repository.count_by_state(session, RecipeState.PENDING)
        
#         # 결과 확인
#         assert pending_count == 2
    
#     def test_exists_by_recipe_base_id(self, session, sample_recipe_base_status, clean_database):
#         """레시피 베이스 ID로 상태 존재 여부 확인 테스트"""
#         repository = RecipeBaseStatusRepository()
        
#         # 존재하는 레시피 베이스 ID 확인
#         exists = repository.exists_by_recipe_base_id(session, sample_recipe_base_status.recipe_base_id)
#         assert exists is True
        
#         # 존재하지 않는 레시피 베이스 ID 확인
#         exists = repository.exists_by_recipe_base_id(session, 99999)
#         assert exists is False


# @pytest.mark.database
# @pytest.mark.repository
# class TestRecipeRepository:
#     """RecipeRepository 클래스의 기능을 테스트합니다."""
    
#     def test_create_recipe(self, session, complete_user, complete_recipe_base, clean_database):
#         """레시피 생성 테스트"""
#         repository = RecipeRepository()
        
#         # 레시피 생성
#         recipe = Recipe(
#             user_id=complete_user.user_id,
#             recipe_base_id=complete_recipe_base.recipe_base_id,
#             title="나만의 레시피",
#             ingredients=[
#                 {"ingredient_name": "양파", "ingredient_amount": "2개", "ingredient_unit": "개"},
#                 {"ingredient_name": "마늘", "ingredient_amount": "5쪽", "ingredient_unit": "쪽"}
#             ],
#             stages={"steps": ["1. 양파를 많이 자른다", "2. 마늘을 많이 다진다", "3. 볶는다"]}
#         )
        
#         created_recipe = repository.create(session, recipe)
        
#         # 결과 확인
#         assert created_recipe.user_id == complete_user.user_id
#         assert created_recipe.recipe_base_id == complete_recipe_base.recipe_base_id
#         assert created_recipe.title == "나만의 레시피"
#         assert len(created_recipe.ingredients) == 2
#         assert created_recipe.ingredients[0]["ingredient_name"] == "양파"
#         assert created_recipe.created_at is not None
#         assert created_recipe.updated_at is not None
    
#     def test_find_by_user_id(self, session, sample_recipe, clean_database):
#         """사용자 ID로 레시피 조회 테스트"""
#         repository = RecipeRepository()
        
#         # 사용자 ID로 조회
#         user_recipes = repository.find_by_user_id(session, sample_recipe.user_id)
        
#         # 결과 확인
#         assert len(user_recipes) == 1
#         assert user_recipes[0].user_id == sample_recipe.user_id
#         assert user_recipes[0].title == sample_recipe.title
    
#     def test_find_by_recipe_base_id(self, session, sample_recipe, clean_database):
#         """레시피 베이스 ID로 레시피 조회 테스트"""
#         repository = RecipeRepository()
        
#         # 레시피 베이스 ID로 조회
#         base_recipes = repository.find_by_recipe_base_id(session, sample_recipe.recipe_base_id)
        
#         # 결과 확인
#         assert len(base_recipes) == 1
#         assert base_recipes[0].recipe_base_id == sample_recipe.recipe_base_id
#         assert base_recipes[0].title == sample_recipe.title
    
#     def test_search_by_title(self, session, complete_user, complete_recipe_base, clean_database):
#         """제목으로 레시피 검색 테스트"""
#         repository = RecipeRepository()
        
#         # 여러 제목의 레시피 생성
#         titles = ["김치찌개 레시피", "된장찌개 레시피", "김치볶음밥", "볶음밥"]
#         for title in titles:
#             recipe = Recipe(
#                 user_id=complete_user.user_id,
#                 recipe_base_id=complete_recipe_base.recipe_base_id,
#                 title=title
#             )
#             repository.create(session, recipe)
        
#         # "김치"로 검색
#         kimchi_recipes = repository.search_by_title(session, "김치")
        
#         # 결과 확인
#         assert len(kimchi_recipes) == 2
#         for recipe in kimchi_recipes:
#             assert "김치" in recipe.title
    
#     def test_find_recent(self, session, complete_user, complete_recipe_base, clean_database):
#         """최근 레시피 조회 테스트"""
#         repository = RecipeRepository()
        
#         # 여러 레시피 생성
#         import time
#         for i in range(3):
#             recipe = Recipe(
#                 user_id=complete_user.user_id,
#                 recipe_base_id=complete_recipe_base.recipe_base_id,
#                 title=f"레시피 {i}"
#             )
#             repository.create(session, recipe)
#             time.sleep(0.01)  # 시간 차이를 위한 짧은 대기
        
#         # 최근 레시피 조회
#         recent_recipes = repository.find_recent(session, limit=2)
        
#         # 결과 확인
#         assert len(recent_recipes) == 2
#         # 최근 순서로 정렬되어야 함
#         assert recent_recipes[0].title == "레시피 2"
#         assert recent_recipes[1].title == "레시피 1"
    
#     def test_update_recipe(self, session, sample_recipe, clean_database):
#         """레시피 업데이트 테스트"""
#         repository = RecipeRepository()
        
#         # 레시피 정보 변경
#         sample_recipe.title = "수정된 레시피 제목"
#         sample_recipe.ingredients = [
#             {"ingredient_name": "새로운 재료", "ingredient_amount": "1개", "ingredient_unit": "개"}
#         ]
        
#         # 업데이트 실행
#         updated_recipe = repository.update(session, sample_recipe)
        
#         # 결과 확인
#         assert updated_recipe.title == "수정된 레시피 제목"
#         assert len(updated_recipe.ingredients) == 1
#         assert updated_recipe.ingredients[0]["ingredient_name"] == "새로운 재료"
#         assert updated_recipe.updated_at is not None
    
#     def test_delete_recipe(self, session, sample_recipe, clean_database):
#         """레시피 삭제 테스트"""
#         repository = RecipeRepository()
        
#         # 레시피 삭제
#         result = repository.delete(session, sample_recipe)
        
#         # 결과 확인
#         assert result is True
        
#         # 삭제 확인
#         found_recipe = repository.find_by_id(session, sample_recipe.recipe_id)
#         assert found_recipe is None
    
#     def test_count_by_user_id(self, session, complete_user, complete_recipe_base, clean_database):
#         """사용자별 레시피 수 조회 테스트"""
#         repository = RecipeRepository()
        
#         # 여러 레시피 생성
#         for i in range(3):
#             recipe = Recipe(
#                 user_id=complete_user.user_id,
#                 recipe_base_id=complete_recipe_base.recipe_base_id,
#                 title=f"레시피 {i}"
#             )
#             repository.create(session, recipe)
        
#         # 사용자별 레시피 수 조회
#         user_recipe_count = repository.count_by_user_id(session, complete_user.user_id)
        
#         # 결과 확인
#         assert user_recipe_count == 3
    
#     def test_count_by_recipe_base_id(self, session, complete_user, complete_recipe_base, clean_database):
#         """레시피 베이스별 레시피 수 조회 테스트"""
#         repository = RecipeRepository()
        
#         # 여러 레시피 생성
#         for i in range(2):
#             recipe = Recipe(
#                 user_id=complete_user.user_id,
#                 recipe_base_id=complete_recipe_base.recipe_base_id,
#                 title=f"레시피 {i}"
#             )
#             repository.create(session, recipe)
        
#         # 레시피 베이스별 레시피 수 조회
#         base_recipe_count = repository.count_by_recipe_base_id(session, complete_recipe_base.recipe_base_id)
        
#         # 결과 확인
#         assert base_recipe_count == 2


# @pytest.mark.database
# @pytest.mark.repository
# class TestIngredientRepository:
#     """IngredientRepository 클래스의 기능을 테스트합니다."""
    
#     def test_create_ingredient(self, session, clean_database):
#         """재료 생성 테스트"""
#         repository = IngredientRepository()
        
#         # 재료 생성
#         ingredient = Ingredient(
#             ingredient="테스트 재료"
#         )
        
#         created_ingredient = repository.create(session, ingredient)
        
#         # 결과 확인
#         assert created_ingredient.ingredient == "테스트 재료"
#         assert created_ingredient.id is not None
    
#     def test_find_by_name(self, session, sample_ingredient, clean_database):
#         """재료명으로 재료 조회 테스트"""
#         repository = IngredientRepository()
        
#         # 재료명으로 조회
#         found_ingredient = repository.find_by_name(session, sample_ingredient.ingredient)
        
#         # 결과 확인
#         assert found_ingredient is not None
#         assert found_ingredient.ingredient == sample_ingredient.ingredient
#         assert found_ingredient.id == sample_ingredient.id
    
#     def test_search_by_name(self, session, clean_database):
#         """재료명 패턴으로 재료 검색 테스트"""
#         repository = IngredientRepository()
        
#         # 여러 재료 생성
#         ingredients = ["양파", "양배추", "대파", "파슬리"]
#         for ingredient_name in ingredients:
#             ingredient = Ingredient(ingredient=ingredient_name)
#             repository.create(session, ingredient)
        
#         # "파"로 검색
#         pa_ingredients = repository.search_by_name(session, "파")
        
#         # 결과 확인
#         assert len(pa_ingredients) == 3
#         for ingredient in pa_ingredients:
#             assert "파" in ingredient.ingredient
    
#     def test_update_ingredient(self, session, sample_ingredient, clean_database):
#         """재료 업데이트 테스트"""
#         repository = IngredientRepository()
        
#         # 재료 정보 변경
#         sample_ingredient.ingredient = "수정된 재료"
        
#         # 업데이트 실행
#         updated_ingredient = repository.update(session, sample_ingredient)
        
#         # 결과 확인
#         assert updated_ingredient.ingredient == "수정된 재료"
    
#     def test_delete_ingredient(self, session, sample_ingredient, clean_database):
#         """재료 삭제 테스트"""
#         repository = IngredientRepository()
        
#         # 재료 삭제
#         result = repository.delete(session, sample_ingredient)
        
#         # 결과 확인
#         assert result is True
        
#         # 삭제 확인
#         found_ingredient = repository.find_by_id(session, sample_ingredient.id)
#         assert found_ingredient is None
    
#     def test_exists_by_name(self, session, sample_ingredient, clean_database):
#         """재료명으로 재료 존재 여부 확인 테스트"""
#         repository = IngredientRepository()
        
#         # 존재하는 재료명 확인
#         exists = repository.exists_by_name(session, sample_ingredient.ingredient)
#         assert exists is True
        
#         # 존재하지 않는 재료명 확인
#         exists = repository.exists_by_name(session, "존재하지 않는 재료")
#         assert exists is False
    
#     def test_create_or_get(self, session, clean_database):
#         """재료 생성 또는 조회 테스트"""
#         repository = IngredientRepository()
        
#         # 새로운 재료 생성
#         ingredient1 = repository.create_or_get(session, "새로운 재료")
        
#         # 결과 확인
#         assert ingredient1.ingredient == "새로운 재료"
#         assert ingredient1.id is not None
        
#         # 기존 재료 조회
#         ingredient2 = repository.create_or_get(session, "새로운 재료")
        
#         # 결과 확인 (같은 재료여야 함)
#         assert ingredient2.id == ingredient1.id
#         assert ingredient2.ingredient == ingredient1.ingredient
    
#     def test_bulk_create_or_get(self, session, clean_database):
#         """여러 재료 일괄 생성 또는 조회 테스트"""
#         repository = IngredientRepository()
        
#         # 기존 재료 생성
#         existing_ingredient = Ingredient(ingredient="기존 재료")
#         repository.create(session, existing_ingredient)
        
#         # 여러 재료 일괄 생성 또는 조회
#         ingredient_names = ["기존 재료", "새로운 재료1", "새로운 재료2"]
#         ingredients = repository.bulk_create_or_get(session, ingredient_names)
        
#         # 결과 확인
#         assert len(ingredients) == 3
#         ingredient_dict = {ing.ingredient: ing for ing in ingredients}
        
#         # 기존 재료는 기존 ID 유지
#         assert ingredient_dict["기존 재료"].id == existing_ingredient.id
        
#         # 새로운 재료들은 새로운 ID
#         assert ingredient_dict["새로운 재료1"].id != existing_ingredient.id
#         assert ingredient_dict["새로운 재료2"].id != existing_ingredient.id
        
#         # 모든 재료명이 정확히 설정되었는지 확인
#         assert ingredient_dict["기존 재료"].ingredient == "기존 재료"
#         assert ingredient_dict["새로운 재료1"].ingredient == "새로운 재료1"
#         assert ingredient_dict["새로운 재료2"].ingredient == "새로운 재료2" 