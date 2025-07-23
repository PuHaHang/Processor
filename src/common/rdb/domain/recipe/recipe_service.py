"""
Recipe 도메인 서비스

이 모듈은 레시피 관련 CRUD 작업을 처리하는 서비스를 제공합니다.
새로운 ERD 구조에 따라 레시피 정보가 여러 테이블로 분산되어 있어
트랜잭션 처리가 중요합니다.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, func

from .models import Recipe, RecipeBase, Ingredient
from ..user.models import User
from .dto import (
    CreateRecipeDto, UpdateRecipeDto, SearchRecipesDto, CopyRecipeFromBaseDto,
)
from ...common.dependency_injection import inject_session, transactional

import logging

logger = logging.getLogger(__name__)


class RecipeService:
    """레시피 관련 비즈니스 로직을 처리하는 서비스"""

    @transactional
    def create_recipe(self, session: Session, dto: CreateRecipeDto) -> Recipe:
        """
        새로운 레시피를 생성합니다.

        Args:
            session: 데이터베이스 세션
            dto: 레시피 생성 데이터 전송 객체

        Returns:
            생성된 레시피 객체

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            # 사용자와 레시피 베이스 존재 확인
            user = session.query(User).filter(User.user_id == dto.user_id).first()
            if not user:
                raise ValueError(f"User not found: {dto.user_id}")
            
            recipe_base = session.query(RecipeBase).filter(
                RecipeBase.recipe_base_id == dto.recipe_base_id
            ).first()
            if not recipe_base:
                raise ValueError(f"Recipe base not found: {dto.recipe_base_id}")
            
            # 재료 리스트 처리
            ingredients_list = None
            if dto.ingredients:
                ingredients_list = [ingredient.ingredient_name for ingredient in dto.ingredients]
            
            recipe = Recipe(
                user_id=dto.user_id,
                recipe_base_id=dto.recipe_base_id,
                title=dto.title,
                ingredients=ingredients_list,
                stages=dto.stages
            )
            
            session.add(recipe)
            session.flush()  # ID 생성을 위해 flush
            
            # 재료 태그 생성 (검색용)
            if ingredients_list:
                self._create_ingredient_tags(
                    session,
                    ingredients_list
                )
            
            logger.info(f"Recipe created: {recipe.recipe_id}")
            return recipe
            
        except SQLAlchemyError as e:
            logger.error(f"Error creating recipe: {e}")
            raise

    def _create_ingredient_tags(self, session: Session, ingredients: List[str]) -> None:
        """
        재료 태그를 생성합니다 (검색용).
        
        Args:
            session: 데이터베이스 세션
            ingredients: 재료 리스트
        """
        try:        
            # 새 태그 생성
            for ingredient_data in ingredients:
                if isinstance(ingredient_data, str):
                    ingredient_tag = Ingredient(
                        ingredient=ingredient_data
                    )
                    session.add(ingredient_tag)
            
            session.flush()
            logger.debug(f"Created {len(ingredients)} ingredient tags")
            
        except SQLAlchemyError as e:
            logger.error(f"Error creating ingredient tags: {e}")
            raise

    @inject_session
    def get_recipe_by_id(self, session: Session, recipe_id: int) -> Optional[Recipe]:
        """
        ID로 레시피를 조회합니다.

        Args:
            session: 데이터베이스 세션
            recipe_id: 레시피 ID

        Returns:
            레시피 객체 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            recipe = session.query(Recipe).options(
                joinedload(Recipe.user),
                joinedload(Recipe.recipe_base)
            ).filter(Recipe.recipe_id == recipe_id).first()
            
            if recipe:
                logger.debug(f"Recipe found: {recipe_id}")
            else:
                logger.debug(f"Recipe not found: {recipe_id}")
                
            return recipe
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting recipe by ID: {e}")
            raise

    @inject_session
    def get_recipes_by_user(self, session: Session, user_id: str, limit: int = 100, offset: int = 0) -> List[Recipe]:
        """
        사용자의 레시피들을 조회합니다.

        Args:
            session: 데이터베이스 세션
            user_id: 사용자 ID
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            레시피 객체 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            recipes = session.query(Recipe).options(
                joinedload(Recipe.user),
                joinedload(Recipe.recipe_base)
            ).filter(
                Recipe.user_id == user_id
            ).offset(offset).limit(limit).all()
            
            logger.debug(f"Found {len(recipes)} recipes for user: {user_id}")
            return recipes
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting recipes by user: {e}")
            raise

    @inject_session
    def get_recipes_by_base(self, session: Session, recipe_base_id: int, limit: int = 100, offset: int = 0) -> List[Recipe]:
        """
        레시피 베이스의 레시피들을 조회합니다.

        Args:
            session: 데이터베이스 세션
            recipe_base_id: 레시피 베이스 ID
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            레시피 객체 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            recipes = session.query(Recipe).options(
                joinedload(Recipe.user),
                joinedload(Recipe.recipe_base)
            ).filter(
                Recipe.recipe_base_id == recipe_base_id
            ).offset(offset).limit(limit).all()
            
            logger.debug(f"Found {len(recipes)} recipes for recipe base: {recipe_base_id}")
            return recipes
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting recipes by base: {e}")
            raise

    @transactional
    def delete_recipe(self, session: Session, recipe_id: int) -> bool:
        """
        레시피를 삭제합니다.

        Args:
            session: 데이터베이스 세션
            recipe_id: 레시피 ID

        Returns:
            삭제 성공 여부

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            recipe = session.query(Recipe).filter(Recipe.recipe_id == recipe_id).first()
            if not recipe:
                logger.warning(f"Recipe not found for deletion: {recipe_id}")
                return False
            
            session.delete(recipe)
            session.flush()
            
            logger.info(f"Recipe deleted: {recipe_id}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error deleting recipe: {e}")
            raise

    @transactional
    def update_recipe(self, session: Session, dto: UpdateRecipeDto) -> Optional[Recipe]:
        """
        레시피 정보를 수정합니다.

        Args:
            session: 데이터베이스 세션
            dto: 레시피 수정 데이터 전송 객체

        Returns:
            수정된 레시피 객체 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            recipe = session.query(Recipe).filter(Recipe.recipe_id == dto.recipe_uuid).first()
            if not recipe:
                logger.warning(f"Recipe not found for update: {dto.recipe_uuid}")
                return None
            
            # 업데이트할 필드들 가져오기
            update_fields = dto.get_update_fields()
            
            if update_fields:
                for field, value in update_fields.items():
                    setattr(recipe, field, value)
                
                recipe.updated_at = datetime.now()
                
                # 재료가 업데이트된 경우 태그 재생성
                if 'ingredients' in update_fields and update_fields['ingredients']:
                    self._create_ingredient_tags(
                        session,
                        [ingredient['ingredient_name'] for ingredient in update_fields['ingredients']]
                    )
                
                session.flush()
                
                logger.info(f"Recipe updated: {dto.recipe_uuid}, fields: {list(update_fields.keys())}")
            else:
                logger.debug(f"No valid fields to update for recipe: {dto.recipe_uuid}")
            
            return recipe
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating recipe: {e}")
            raise

    @inject_session
    def get_all_recipes(self, session: Session, limit: int = 100, offset: int = 0) -> List[Recipe]:
        """
        모든 레시피를 조회합니다.

        Args:
            session: 데이터베이스 세션
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            레시피 객체 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            recipes = session.query(Recipe).options(
                joinedload(Recipe.user),
                joinedload(Recipe.recipe_base)
            ).offset(offset).limit(limit).all()
            
            logger.debug(f"Found {len(recipes)} recipes")
            return recipes
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting all recipes: {e}")
            raise

    @inject_session
    def get_recipe_count(self, session: Session) -> int:
        """
        전체 레시피 수를 조회합니다.

        Args:
            session: 데이터베이스 세션

        Returns:
            전체 레시피 수

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            count = session.query(func.count(Recipe.recipe_id)).scalar()
            
            logger.debug(f"Total recipe count: {count}")
            return count
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting recipe count: {e}")
            raise

    @transactional
    def copy_recipe_from_base(self, session: Session, dto: CopyRecipeFromBaseDto) -> Recipe:
        """
        레시피 베이스로부터 레시피를 복사합니다.

        Args:
            session: 데이터베이스 세션
            dto: 레시피 복사 데이터 전송 객체

        Returns:
            생성된 레시피 객체

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            # 레시피 베이스 조회
            recipe_base = session.query(RecipeBase).options(
                joinedload(RecipeBase.contents)
            ).filter(RecipeBase.recipe_base_id == dto.recipe_base_id).first()
            
            if not recipe_base:
                raise ValueError(f"Recipe base not found: {dto.recipe_base_id}")
            
            # 첫 번째 컨텐츠 사용 (기본 언어)
            base_content = recipe_base.contents[0] if recipe_base.contents else None
            
            # 레시피 생성
            recipe = Recipe(
                user_id=dto.user_id,
                recipe_base_id=dto.recipe_base_id,
                title=dto.title or (base_content.title if base_content else None),
                ingredients=base_content.ingredients if base_content else None,
                stages=base_content.stages if base_content else None
            )
            
            session.add(recipe)
            session.flush()
            
            # 재료 태그 복사
            if base_content and base_content.ingredients:
                self._create_ingredient_tags(
                    session,
                    [ingredient['ingredient_name'] for ingredient in base_content.ingredients]
                )
            
            logger.info(f"Recipe copied from base: {recipe.recipe_id}")
            return recipe
            
        except SQLAlchemyError as e:
            logger.error(f"Error copying recipe from base: {e}")
            raise

    @inject_session
    def search_recipes(self, session: Session, dto: SearchRecipesDto) -> List[Recipe]:
        """
        다양한 조건으로 레시피를 검색합니다.

        Args:
            session: 데이터베이스 세션
            dto: 레시피 검색 데이터 전송 객체

        Returns:
            검색된 레시피 객체 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            query = session.query(Recipe).options(
                joinedload(Recipe.user),
                joinedload(Recipe.recipe_base)
            )
            
            # 필터 조건 추가
            if dto.title:
                query = query.filter(Recipe.title.ilike(f"%{dto.title}%"))
            if dto.user_id:
                query = query.filter(Recipe.user_id == dto.user_id)
            if dto.recipe_base_id:
                query = query.filter(Recipe.recipe_base_id == dto.recipe_base_id)
            
            # 재료 검색 (태그 테이블 사용)
            if dto.ingredient:
                # TODO: 재료 검색 로직 추가
                # full text search 사용
                pass
            
            recipes = query.offset(dto.offset).limit(dto.limit).all()
            
            logger.debug(f"Found {len(recipes)} recipes with search criteria")
            return recipes
            
        except SQLAlchemyError as e:
            logger.error(f"Error searching recipes: {e}")
            raise

    @inject_session
    def get_recipe_statistics(self, session: Session) -> Dict[str, Any]:
        """
        레시피 통계 정보를 조회합니다.

        Args:
            session: 데이터베이스 세션

        Returns:
            레시피 통계 정보

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            # 총 레시피 수
            total_recipes = session.query(func.count(Recipe.recipe_id)).scalar()
            
            # 사용자별 레시피 수 상위 10
            user_stats = session.query(
                Recipe.user_id,
                func.count(Recipe.recipe_id).label('count')
            ).group_by(Recipe.user_id).order_by(
                func.count(Recipe.recipe_id).desc()
            ).limit(10).all()
            
            # 레시피 베이스별 활용도 상위 10
            base_stats = session.query(
                Recipe.recipe_base_id,
                func.count(Recipe.recipe_id).label('count')
            ).group_by(Recipe.recipe_base_id).order_by(
                func.count(Recipe.recipe_id).desc()
            ).limit(10).all()
            
            # 일별 레시피 생성 통계 (최근 30일)
            daily_stats = session.query(
                func.date(Recipe.created_at).label('date'),
                func.count(Recipe.recipe_id).label('count')
            ).group_by(func.date(Recipe.created_at)).order_by(
                func.date(Recipe.created_at).desc()
            ).limit(30).all()
            
            statistics = {
                'total_recipes': total_recipes,
                'top_users': [
                    {'user_id': stat.user_id, 'recipe_count': stat.count}
                    for stat in user_stats
                ],
                'top_recipe_bases': [
                    {'recipe_base_id': stat.recipe_base_id, 'usage_count': stat.count}
                    for stat in base_stats
                ],
                'daily_creation': [
                    {'date': str(stat.date), 'count': stat.count}
                    for stat in daily_stats
                ]
            }
            
            logger.debug(f"Recipe statistics calculated: {statistics}")
            return statistics
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting recipe statistics: {e}")
            raise 