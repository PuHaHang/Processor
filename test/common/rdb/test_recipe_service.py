# """
# Recipe 도메인 Service 테스트

# 이 모듈은 Recipe 도메인의 RecipeService와 RecipeBaseService 클래스를 테스트합니다.
# 실제 PostgreSQL 데이터베이스와 연결하여 테스트합니다.
# """

# import pytest
# import uuid
# from unittest.mock import patch

# from src.common.rdb.domain.recipe.models import RecipeBase, RecipeBaseContent, RecipeBaseState, Recipe, Ingredient, RecipeLanguage, RecipeDifficulty, RecipeState
# from src.common.rdb.domain.recipe.recipe_service import RecipeService
# from src.common.rdb.domain.recipe.recipe_base_service import RecipeBaseService
# from src.common.rdb.domain.recipe.dto import (
#     CreateRecipeDto, UpdateRecipeDto, SearchRecipesDto, CopyRecipeFromBaseDto,
#     CreateRecipeBaseDto, UpdateRecipeBaseDto, SearchRecipeBasesDto, IngredientDto
# )


# @pytest.mark.database
# @pytest.mark.service
# class TestRecipeService:
#     """RecipeService 클래스의 기능을 테스트합니다."""
    
#     def test_create_recipe(self, session, complete_user, complete_recipe_base, clean_database):
#         """레시피 생성 테스트"""
#         service = RecipeService()
        
#         # 재료 DTO 생성
#         ingredients = [
#             IngredientDto(
#                 ingredient_name="양파",
#                 ingredient_amount=2,
#                 ingredient_unit="개"
#             ),
#             IngredientDto(
#                 ingredient_name="마늘",
#                 ingredient_amount=5,
#                 ingredient_unit="쪽"
#             )
#         ]
        
#         # 레시피 생성 DTO
#         create_dto = CreateRecipeDto(
#             user_id=complete_user.user_id,
#             recipe_base_id=complete_recipe_base.recipe_base_id,
#             title="나만의 특별한 레시피",
#             ingredients=ingredients,
#             stages={"steps": ["1. 양파를 자른다", "2. 마늘을 다진다", "3. 볶는다"]}
#         )
        
#         # 레시피 생성
#         created_recipe = service.create_recipe(session, create_dto)
        
#         # 결과 확인
#         assert created_recipe.user_id == complete_user.user_id
#         assert created_recipe.recipe_base_id == complete_recipe_base.recipe_base_id
#         assert created_recipe.title == "나만의 특별한 레시피"
#         assert created_recipe.ingredients is not None
#         assert len(created_recipe.ingredients) == 2
#         assert created_recipe.stages is not None
#         assert created_recipe.created_at is not None
#         assert created_recipe.updated_at is not None
    
#     def test_create_recipe_without_user(self, session, complete_recipe_base, clean_database):
#         """존재하지 않는 사용자로 레시피 생성 테스트"""
#         service = RecipeService()
        
#         # 존재하지 않는 사용자 ID로 레시피 생성 시도
#         create_dto = CreateRecipeDto(
#             user_id=str(uuid.uuid4()),
#             recipe_base_id=complete_recipe_base.recipe_base_id,
#             title="테스트 레시피"
#         )
        
#         # 에러 발생 확인
#         with pytest.raises(ValueError, match="User not found"):
#             service.create_recipe(session, create_dto)
    
#     def test_create_recipe_without_recipe_base(self, session, complete_user, clean_database):
#         """존재하지 않는 레시피 베이스로 레시피 생성 테스트"""
#         service = RecipeService()
        
#         # 존재하지 않는 레시피 베이스 ID로 레시피 생성 시도
#         create_dto = CreateRecipeDto(
#             user_id=complete_user.user_id,
#             recipe_base_id=99999,
#             title="테스트 레시피"
#         )
        
#         # 에러 발생 확인
#         with pytest.raises(ValueError, match="Recipe base not found"):
#             service.create_recipe(session, create_dto)
    
#     def test_get_recipe_by_id(self, session, sample_recipe, clean_database):
#         """ID로 레시피 조회 테스트"""
#         service = RecipeService()
        
#         # 레시피 조회
#         found_recipe = service.get_recipe_by_id(session, sample_recipe.recipe_id)
        
#         # 결과 확인
#         assert found_recipe is not None
#         assert found_recipe.recipe_id == sample_recipe.recipe_id
#         assert found_recipe.user_id == sample_recipe.user_id
#         assert found_recipe.recipe_base_id == sample_recipe.recipe_base_id
#         assert found_recipe.title == sample_recipe.title
        
#         # 관련 정보 로드 확인
#         assert found_recipe.user is not None
#         assert found_recipe.recipe_base is not None
    
#     def test_get_recipe_by_id_not_found(self, session, clean_database):
#         """존재하지 않는 ID로 레시피 조회 테스트"""
#         service = RecipeService()
        
#         # 존재하지 않는 레시피 조회
#         found_recipe = service.get_recipe_by_id(session, 99999)
        
#         # 결과 확인
#         assert found_recipe is None
    
#     def test_get_recipes_by_user(self, session, complete_user, complete_recipe_base, clean_database):
#         """사용자별 레시피 조회 테스트"""
#         service = RecipeService()
        
#         # 여러 레시피 생성
#         for i in range(3):
#             create_dto = CreateRecipeDto(
#                 user_id=complete_user.user_id,
#                 recipe_base_id=complete_recipe_base.recipe_base_id,
#                 title=f"레시피 {i}"
#             )
#             service.create_recipe(session, create_dto)
        
#         # 사용자별 레시피 조회
#         user_recipes = service.get_recipes_by_user(session, complete_user.user_id)
        
#         # 결과 확인
#         assert len(user_recipes) == 3
#         for recipe in user_recipes:
#             assert recipe.user_id == complete_user.user_id
#             assert recipe.user is not None
#             assert recipe.recipe_base is not None
    
#     def test_get_recipes_by_base(self, session, complete_user, complete_recipe_base, clean_database):
#         """레시피 베이스별 레시피 조회 테스트"""
#         service = RecipeService()
        
#         # 여러 레시피 생성
#         for i in range(2):
#             create_dto = CreateRecipeDto(
#                 user_id=complete_user.user_id,
#                 recipe_base_id=complete_recipe_base.recipe_base_id,
#                 title=f"레시피 {i}"
#             )
#             service.create_recipe(session, create_dto)
        
#         # 레시피 베이스별 레시피 조회
#         base_recipes = service.get_recipes_by_base(session, complete_recipe_base.recipe_base_id)
        
#         # 결과 확인
#         assert len(base_recipes) == 2
#         for recipe in base_recipes:
#             assert recipe.recipe_base_id == complete_recipe_base.recipe_base_id
#             assert recipe.user is not None
#             assert recipe.recipe_base is not None
    
#     def test_delete_recipe(self, session, sample_recipe, clean_database):
#         """레시피 삭제 테스트"""
#         service = RecipeService()
        
#         # 레시피 삭제
#         result = service.delete_recipe(session, sample_recipe.recipe_id)
        
#         # 결과 확인
#         assert result is True
        
#         # 삭제 확인
#         found_recipe = service.get_recipe_by_id(session, sample_recipe.recipe_id)
#         assert found_recipe is None
    
#     def test_delete_recipe_not_found(self, session, clean_database):
#         """존재하지 않는 레시피 삭제 테스트"""
#         service = RecipeService()
        
#         # 존재하지 않는 레시피 삭제
#         result = service.delete_recipe(session, 99999)
        
#         # 결과 확인
#         assert result is False
    
#     def test_update_recipe(self, session, sample_recipe, clean_database):
#         """레시피 수정 테스트"""
#         service = RecipeService()
        
#         # 레시피 수정 DTO
#         update_dto = UpdateRecipeDto(
#             recipe_uuid=sample_recipe.recipe_id,
#             title="수정된 레시피 제목",
#             stages={"steps": ["1. 수정된 단계 1", "2. 수정된 단계 2"]}
#         )
        
#         # 레시피 수정
#         updated_recipe = service.update_recipe(session, update_dto)
        
#         # 결과 확인
#         assert updated_recipe is not None
#         assert updated_recipe.recipe_id == sample_recipe.recipe_id
#         assert updated_recipe.title == "수정된 레시피 제목"
#         assert updated_recipe.stages["steps"] == ["1. 수정된 단계 1", "2. 수정된 단계 2"]
#         assert updated_recipe.updated_at is not None
    
#     def test_update_recipe_not_found(self, session, clean_database):
#         """존재하지 않는 레시피 수정 테스트"""
#         service = RecipeService()
        
#         # 존재하지 않는 레시피 수정
#         update_dto = UpdateRecipeDto(
#             recipe_uuid=99999,
#             title="수정된 레시피 제목"
#         )
        
#         # 레시피 수정
#         updated_recipe = service.update_recipe(session, update_dto)
        
#         # 결과 확인
#         assert updated_recipe is None
    
#     def test_copy_recipe_from_base(self, session, complete_user, complete_recipe_base, clean_database):
#         """레시피 베이스로부터 레시피 복사 테스트"""
#         service = RecipeService()
        
#         # 레시피 복사 DTO
#         copy_dto = CopyRecipeFromBaseDto(
#             user_id=complete_user.user_id,
#             recipe_base_id=complete_recipe_base.recipe_base_id,
#             title="복사된 레시피"
#         )
        
#         # 레시피 복사
#         copied_recipe = service.copy_recipe_from_base(session, copy_dto)
        
#         # 결과 확인
#         assert copied_recipe.user_id == complete_user.user_id
#         assert copied_recipe.recipe_base_id == complete_recipe_base.recipe_base_id
#         assert copied_recipe.title == "복사된 레시피"
#         assert copied_recipe.created_at is not None
#         assert copied_recipe.updated_at is not None
    
#     def test_copy_recipe_from_base_not_found(self, session, complete_user, clean_database):
#         """존재하지 않는 레시피 베이스로부터 레시피 복사 테스트"""
#         service = RecipeService()
        
#         # 존재하지 않는 레시피 베이스로부터 복사 시도
#         copy_dto = CopyRecipeFromBaseDto(
#             user_id=complete_user.user_id,
#             recipe_base_id=99999,
#             title="복사된 레시피"
#         )
        
#         # 에러 발생 확인
#         with pytest.raises(ValueError, match="Recipe base not found"):
#             service.copy_recipe_from_base(session, copy_dto)
    
#     def test_search_recipes(self, session, complete_user, complete_recipe_base, clean_database):
#         """레시피 검색 테스트"""
#         service = RecipeService()
        
#         # 여러 레시피 생성
#         recipe_titles = ["김치찌개", "된장찌개", "김치볶음밥"]
#         for title in recipe_titles:
#             create_dto = CreateRecipeDto(
#                 user_id=complete_user.user_id,
#                 recipe_base_id=complete_recipe_base.recipe_base_id,
#                 title=title
#             )
#             service.create_recipe(session, create_dto)
        
#         # 제목으로 검색
#         search_dto = SearchRecipesDto(
#             title="김치",
#             limit=10,
#             offset=0
#         )
#         search_results = service.search_recipes(session, search_dto)
        
#         # 결과 확인
#         assert len(search_results) == 2
#         for recipe in search_results:
#             assert "김치" in recipe.title
#             assert recipe.user is not None
#             assert recipe.recipe_base is not None
        
#         # 사용자로 검색
#         user_search_dto = SearchRecipesDto(
#             user_id=complete_user.user_id,
#             limit=10,
#             offset=0
#         )
#         user_results = service.search_recipes(session, user_search_dto)
        
#         # 결과 확인
#         assert len(user_results) == 3
#         for recipe in user_results:
#             assert recipe.user_id == complete_user.user_id
    
#     def test_get_recipe_statistics(self, session, complete_user, complete_recipe_base, clean_database):
#         """레시피 통계 조회 테스트"""
#         service = RecipeService()
        
#         # 여러 레시피 생성
#         for i in range(5):
#             create_dto = CreateRecipeDto(
#                 user_id=complete_user.user_id,
#                 recipe_base_id=complete_recipe_base.recipe_base_id,
#                 title=f"레시피 {i}"
#             )
#             service.create_recipe(session, create_dto)
        
#         # 통계 조회
#         statistics = service.get_recipe_statistics(session)
        
#         # 결과 확인
#         assert statistics['total_recipes'] == 5
#         assert len(statistics['top_users']) >= 1
#         assert len(statistics['top_recipe_bases']) >= 1
#         assert len(statistics['daily_creation']) >= 1
        
#         # 사용자별 통계 확인
#         user_stats = statistics['top_users'][0]
#         assert user_stats['user_id'] == complete_user.user_id
#         assert user_stats['recipe_count'] == 5
        
#         # 레시피 베이스별 통계 확인
#         base_stats = statistics['top_recipe_bases'][0]
#         assert base_stats['recipe_base_id'] == complete_recipe_base.recipe_base_id
#         assert base_stats['usage_count'] == 5


# @pytest.mark.database
# @pytest.mark.service
# class TestRecipeBaseService:
#     """RecipeBaseService 클래스의 기능을 테스트합니다."""
    
#     def test_create_recipe_base(self, session, clean_database):
#         """레시피 베이스 생성 테스트"""
#         service = RecipeBaseService()
        
#         # 레시피 베이스 생성 DTO
#         create_dto = CreateRecipeBaseDto(
#             thumbnail="https://example.com/thumbnail.jpg",
#             referrer={"platform": "test", "url": "https://example.com/recipe"},
#             metadata={"source": "test", "author": "test_chef"},
#             servings=4,
#             difficulty=RecipeDifficulty.normal,
#             estimated_time=60,
#             title="테스트 레시피 베이스",
#             author="테스트 요리사",
#             ingredients=[
#                 {"ingredient_name": "양파", "ingredient_amount": "1개", "ingredient_unit": "개"},
#                 {"ingredient_name": "마늘", "ingredient_amount": "3쪽", "ingredient_unit": "쪽"}
#             ],
#             stages={"steps": ["1. 양파를 자른다", "2. 마늘을 다진다", "3. 볶는다"]},
#             language=RecipeLanguage.ko,
#             model_name="test_model_v1"
#         )
        
#         # 레시피 베이스 생성
#         created_recipe_base = service.create_recipe_base(session, create_dto)
        
#         # 결과 확인
#         assert created_recipe_base.thumbnail == "https://example.com/thumbnail.jpg"
#         assert created_recipe_base.referrer["platform"] == "test"
#         assert created_recipe_base.servings == 4
#         assert created_recipe_base.difficulty == RecipeDifficulty.normal
#         assert created_recipe_base.estimated_time == 60
#         assert created_recipe_base.view_count == 0
#         assert created_recipe_base.chksum is not None
#         assert created_recipe_base.created_at is not None
#         assert created_recipe_base.updated_at is not None
        
#         # 관련 정보 생성 확인
#         assert len(created_recipe_base.contents) == 1
#         assert created_recipe_base.contents[0].title == "테스트 레시피 베이스"
#         assert created_recipe_base.contents[0].author == "테스트 요리사"
#         assert len(created_recipe_base.contents[0].ingredients) == 2
        
#         assert created_recipe_base.status is not None
#         assert created_recipe_base.status.state == RecipeState.PENDING
    
#     def test_get_recipe_base_by_id(self, session, complete_recipe_base, clean_database):
#         """ID로 레시피 베이스 조회 테스트"""
#         service = RecipeBaseService()
        
#         # 레시피 베이스 조회
#         found_recipe_base = service.get_recipe_base_by_id(session, complete_recipe_base.recipe_base_id)
        
#         # 결과 확인
#         assert found_recipe_base is not None
#         assert found_recipe_base.recipe_base_id == complete_recipe_base.recipe_base_id
#         assert found_recipe_base.chksum == complete_recipe_base.chksum
        
#         # 관련 정보 로드 확인
#         assert found_recipe_base.contents is not None
#         assert found_recipe_base.status is not None
    
#     def test_get_recipe_base_by_checksum(self, session, complete_recipe_base, clean_database):
#         """체크섬으로 레시피 베이스 조회 테스트"""
#         service = RecipeBaseService()
        
#         # 체크섬으로 조회
#         found_recipe_base = service.get_recipe_base_by_checksum(session, complete_recipe_base.chksum)
        
#         # 결과 확인
#         assert found_recipe_base is not None
#         assert found_recipe_base.chksum == complete_recipe_base.chksum
#         assert found_recipe_base.recipe_base_id == complete_recipe_base.recipe_base_id
    
#     def test_get_recipe_bases_by_difficulty(self, session, clean_database):
#         """난이도별 레시피 베이스 조회 테스트"""
#         service = RecipeBaseService()
        
#         # 여러 난이도의 레시피 베이스 생성
#         difficulties = [RecipeDifficulty.easy, RecipeDifficulty.normal, RecipeDifficulty.easy]
#         for i, difficulty in enumerate(difficulties):
#             create_dto = CreateRecipeBaseDto(
#                 title=f"레시피 {i}",
#                 difficulty=difficulty,
#                 language=RecipeLanguage.ko,
#                 model_name="test_model"
#             )
#             service.create_recipe_base(session, create_dto)
        
#         # easy 난이도로 조회
#         easy_recipes = service.get_recipe_bases_by_difficulty(session, RecipeDifficulty.easy)
        
#         # 결과 확인
#         assert len(easy_recipes) == 2
#         for recipe in easy_recipes:
#             assert recipe.difficulty == RecipeDifficulty.easy
    
#     def test_get_popular_recipe_bases(self, session, clean_database):
#         """인기 레시피 베이스 조회 테스트"""
#         service = RecipeBaseService()
        
#         # 여러 레시피 베이스 생성
#         for i in range(3):
#             create_dto = CreateRecipeBaseDto(
#                 title=f"레시피 {i}",
#                 language=RecipeLanguage.ko,
#                 model_name="test_model"
#             )
#             created_recipe_base = service.create_recipe_base(session, create_dto)
            
#             # 조회수 증가
#             for _ in range(i + 1):
#                 service.increment_view_count(session, created_recipe_base.recipe_base_id)
        
#         # 인기 레시피 조회
#         popular_recipes = service.get_popular_recipe_bases(session)
        
#         # 결과 확인
#         assert len(popular_recipes) == 3
#         # 조회수 내림차순으로 정렬되어야 함
#         assert popular_recipes[0].view_count >= popular_recipes[1].view_count
#         assert popular_recipes[1].view_count >= popular_recipes[2].view_count
    
#     def test_delete_recipe_base(self, session, complete_recipe_base, clean_database):
#         """레시피 베이스 삭제 테스트"""
#         service = RecipeBaseService()
        
#         # 레시피 베이스 삭제
#         result = service.delete_recipe_base(session, complete_recipe_base.recipe_base_id)
        
#         # 결과 확인
#         assert result is True
        
#         # 삭제 확인
#         found_recipe_base = service.get_recipe_base_by_id(session, complete_recipe_base.recipe_base_id)
#         assert found_recipe_base is None
    
#     def test_delete_recipe_base_not_found(self, session, clean_database):
#         """존재하지 않는 레시피 베이스 삭제 테스트"""
#         service = RecipeBaseService()
        
#         # 존재하지 않는 레시피 베이스 삭제
#         result = service.delete_recipe_base(session, 99999)
        
#         # 결과 확인
#         assert result is False
    
#     def test_update_recipe_base(self, session, complete_recipe_base, clean_database):
#         """레시피 베이스 수정 테스트"""
#         service = RecipeBaseService()
        
#         # 레시피 베이스 수정 DTO
#         update_dto = UpdateRecipeBaseDto(
#             recipe_base_id=complete_recipe_base.recipe_base_id,
#             thumbnail="https://example.com/updated_thumbnail.jpg",
#             servings=6,
#             difficulty=RecipeDifficulty.hard,
#             title="수정된 레시피 제목",
#             author="수정된 요리사"
#         )
        
#         # 레시피 베이스 수정
#         updated_recipe_base = service.update_recipe_base(session, update_dto)
        
#         # 결과 확인
#         assert updated_recipe_base is not None
#         assert updated_recipe_base.recipe_base_id == complete_recipe_base.recipe_base_id
#         assert updated_recipe_base.thumbnail == "https://example.com/updated_thumbnail.jpg"
#         assert updated_recipe_base.servings == 6
#         assert updated_recipe_base.difficulty == RecipeDifficulty.hard
#         assert updated_recipe_base.updated_at is not None
        
#         # 컨텐츠 수정 확인
#         assert updated_recipe_base.contents[0].title == "수정된 레시피 제목"
#         assert updated_recipe_base.contents[0].author == "수정된 요리사"
    
#     def test_update_recipe_base_not_found(self, session, clean_database):
#         """존재하지 않는 레시피 베이스 수정 테스트"""
#         service = RecipeBaseService()
        
#         # 존재하지 않는 레시피 베이스 수정
#         update_dto = UpdateRecipeBaseDto(
#             recipe_base_id=99999,
#             title="수정된 레시피 제목"
#         )
        
#         # 레시피 베이스 수정
#         updated_recipe_base = service.update_recipe_base(session, update_dto)
        
#         # 결과 확인
#         assert updated_recipe_base is None
    
#     def test_increment_view_count(self, session, complete_recipe_base, clean_database):
#         """조회수 증가 테스트"""
#         service = RecipeBaseService()
        
#         # 초기 조회수 확인
#         initial_view_count = complete_recipe_base.view_count
        
#         # 조회수 증가
#         updated_recipe_base = service.increment_view_count(session, complete_recipe_base.recipe_base_id)
        
#         # 결과 확인
#         assert updated_recipe_base is not None
#         assert updated_recipe_base.view_count == initial_view_count + 1
    
#     def test_increment_view_count_not_found(self, session, clean_database):
#         """존재하지 않는 레시피 베이스 조회수 증가 테스트"""
#         service = RecipeBaseService()
        
#         # 존재하지 않는 레시피 베이스 조회수 증가
#         updated_recipe_base = service.increment_view_count(session, 99999)
        
#         # 결과 확인
#         assert updated_recipe_base is None
    
#     def test_get_recipe_base_statistics(self, session, clean_database):
#         """레시피 베이스 통계 조회 테스트"""
#         service = RecipeBaseService()
        
#         # 다양한 레시피 베이스 생성
#         test_cases = [
#             (RecipeDifficulty.easy, RecipeLanguage.ko, RecipeState.COMPLETED),
#             (RecipeDifficulty.normal, RecipeLanguage.en, RecipeState.PENDING),
#             (RecipeDifficulty.easy, RecipeLanguage.ko, RecipeState.COMPLETED),
#         ]
        
#         for difficulty, language, state in test_cases:
#             create_dto = CreateRecipeBaseDto(
#                 title="테스트 레시피",
#                 difficulty=difficulty,
#                 language=language,
#                 model_name="test_model"
#             )
#             created_recipe_base = service.create_recipe_base(session, create_dto)
            
#             # 상태 업데이트
#             service.update_recipe_base_status(session, created_recipe_base.recipe_base_id, state)
        
#         # 통계 조회
#         statistics = service.get_recipe_base_statistics(session)
        
#         # 결과 확인
#         assert statistics['total_recipe_bases'] == 3
#         assert statistics['by_difficulty'][RecipeDifficulty.easy] == 2
#         assert statistics['by_difficulty'][RecipeDifficulty.normal] == 1
#         assert statistics['by_language'][RecipeLanguage.ko] == 2
#         assert statistics['by_language'][RecipeLanguage.en] == 1
#         assert statistics['by_status'][RecipeState.COMPLETED] == 2
#         assert statistics['by_status'][RecipeState.PENDING] == 1
#         assert 'view_statistics' in statistics
    
#     def test_update_recipe_base_status(self, session, complete_recipe_base, clean_database):
#         """레시피 베이스 상태 업데이트 테스트"""
#         service = RecipeBaseService()
        
#         # 상태 업데이트
#         updated_status = service.update_recipe_base_status(
#             session, 
#             complete_recipe_base.recipe_base_id, 
#             RecipeState.COMPLETED
#         )
        
#         # 결과 확인
#         assert updated_status is not None
#         assert updated_status.recipe_base_id == complete_recipe_base.recipe_base_id
#         assert updated_status.state == RecipeState.COMPLETED
    
#     def test_update_recipe_base_status_new(self, session, clean_database):
#         """새로운 레시피 베이스 상태 생성 테스트"""
#         service = RecipeBaseService()
        
#         # 레시피 베이스 생성 (상태 없이)
#         create_dto = CreateRecipeBaseDto(
#             title="테스트 레시피",
#             language=RecipeLanguage.ko,
#             model_name="test_model"
#         )
#         created_recipe_base = service.create_recipe_base(session, create_dto)
        
#         # 기존 상태 삭제
#         if created_recipe_base.status:
#             session.delete(created_recipe_base.status)
#             session.commit()
        
#         # 새로운 상태 생성
#         new_status = service.update_recipe_base_status(
#             session, 
#             created_recipe_base.recipe_base_id, 
#             RecipeState.PROCESSING
#         )
        
#         # 결과 확인
#         assert new_status is not None
#         assert new_status.recipe_base_id == created_recipe_base.recipe_base_id
#         assert new_status.state == RecipeState.PROCESSING
    
#     @pytest.mark.slow
#     def test_create_recipe_base_performance(self, session, clean_database):
#         """레시피 베이스 생성 성능 테스트"""
#         service = RecipeBaseService()
#         import time
        
#         # 여러 레시피 베이스 생성 시간 측정
#         start_time = time.time()
        
#         for i in range(5):
#             create_dto = CreateRecipeBaseDto(
#                 title=f"성능 테스트 레시피 {i}",
#                 language=RecipeLanguage.ko,
#                 model_name="test_model"
#             )
#             service.create_recipe_base(session, create_dto)
        
#         end_time = time.time()
#         execution_time = end_time - start_time
        
#         # 5개 레시피 베이스 생성이 3초 이내에 완료되어야 함
#         assert execution_time < 3.0
        
#         # 생성된 레시피 베이스 수 확인
#         count = service.get_recipe_base_count(session)
#         assert count == 5 