"""
Recipe Repository

이 모듈은 Recipe 모델의 기본 CRUD 작업을 담당하는 Repository 클래스를 제공합니다.
"""

from typing import Optional, List
from datetime import datetime

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, func

from ..models import Recipe
from ....common.dependency_injection import inject_session, transactional

import logging

logger = logging.getLogger(__name__)


class RecipeRepository:
    """Recipe 모델 기본 CRUD 작업을 담당하는 Repository"""

    @transactional
    def create(self, session: Session, recipe: Recipe) -> Recipe:
        """
        새로운 레시피를 생성합니다.

        Args:
            session: 데이터베이스 세션
            recipe: 생성할 레시피 엔티티

        Returns:
            생성된 레시피 엔티티

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.add(recipe)
            session.flush()
            
            logger.debug(f"Recipe created: {recipe.recipe_id}")
            return recipe
            
        except SQLAlchemyError as e:
            logger.error(f"Error creating recipe: {e}")
            raise

    @inject_session
    def find_by_id(self, session: Session, recipe_id: int) -> Optional[Recipe]:
        """
        ID로 레시피를 조회합니다.

        Args:
            session: 데이터베이스 세션
            recipe_id: 레시피 ID

        Returns:
            레시피 엔티티 또는 None

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
            logger.error(f"Error finding recipe by ID: {e}")
            raise

    @inject_session
    def find_by_user_id(self, session: Session, user_id: str, limit: int = 100, offset: int = 0) -> List[Recipe]:
        """
        사용자 ID로 레시피들을 조회합니다.

        Args:
            session: 데이터베이스 세션
            user_id: 사용자 ID
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            레시피 엔티티 리스트

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
            logger.error(f"Error finding recipes by user ID: {e}")
            raise

    @inject_session
    def find_by_recipe_base_id(self, session: Session, recipe_base_id: int, limit: int = 100, offset: int = 0) -> List[Recipe]:
        """
        레시피 베이스 ID로 레시피들을 조회합니다.

        Args:
            session: 데이터베이스 세션
            recipe_base_id: 레시피 베이스 ID
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            레시피 엔티티 리스트

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
            logger.error(f"Error finding recipes by recipe base ID: {e}")
            raise

    @inject_session
    def search_by_title(self, session: Session, title_pattern: str, limit: int = 100, offset: int = 0) -> List[Recipe]:
        """
        제목 패턴으로 레시피들을 검색합니다.

        Args:
            session: 데이터베이스 세션
            title_pattern: 검색할 제목 패턴
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            레시피 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            recipes = session.query(Recipe).options(
                joinedload(Recipe.user),
                joinedload(Recipe.recipe_base)
            ).filter(
                Recipe.title.ilike(f"%{title_pattern}%")
            ).offset(offset).limit(limit).all()
            
            logger.debug(f"Found {len(recipes)} recipes for title pattern: {title_pattern}")
            return recipes
            
        except SQLAlchemyError as e:
            logger.error(f"Error searching recipes by title: {e}")
            raise

    @inject_session
    def find_recent(self, session: Session, limit: int = 100, offset: int = 0) -> List[Recipe]:
        """
        최근 생성된 레시피들을 조회합니다.

        Args:
            session: 데이터베이스 세션
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            레시피 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            recipes = session.query(Recipe).options(
                joinedload(Recipe.user),
                joinedload(Recipe.recipe_base)
            ).order_by(
                Recipe.created_at.desc()
            ).offset(offset).limit(limit).all()
            
            logger.debug(f"Found {len(recipes)} recent recipes")
            return recipes
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding recent recipes: {e}")
            raise

    @transactional
    def update(self, session: Session, recipe: Recipe) -> Recipe:
        """
        레시피를 업데이트합니다.

        Args:
            session: 데이터베이스 세션
            recipe: 업데이트할 레시피 엔티티

        Returns:
            업데이트된 레시피 엔티티

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            recipe.updated_at = datetime.utcnow()
            session.merge(recipe)
            session.flush()
            
            logger.debug(f"Recipe updated: {recipe.recipe_id}")
            return recipe
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating recipe: {e}")
            raise

    @transactional
    def delete(self, session: Session, recipe: Recipe) -> bool:
        """
        레시피를 삭제합니다.

        Args:
            session: 데이터베이스 세션
            recipe: 삭제할 레시피 엔티티

        Returns:
            삭제 성공 여부

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.delete(recipe)
            session.flush()
            
            logger.debug(f"Recipe deleted: {recipe.recipe_id}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error deleting recipe: {e}")
            raise

    @inject_session
    def find_all(self, session: Session, limit: int = 100, offset: int = 0) -> List[Recipe]:
        """
        모든 레시피를 조회합니다.

        Args:
            session: 데이터베이스 세션
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            레시피 엔티티 리스트

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
            logger.error(f"Error finding all recipes: {e}")
            raise

    @inject_session
    def count(self, session: Session) -> int:
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
            logger.error(f"Error counting recipes: {e}")
            raise

    @inject_session
    def count_by_user_id(self, session: Session, user_id: str) -> int:
        """
        사용자별 레시피 수를 조회합니다.

        Args:
            session: 데이터베이스 세션
            user_id: 사용자 ID

        Returns:
            사용자별 레시피 수

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            count = session.query(func.count(Recipe.recipe_id)).filter(
                Recipe.user_id == user_id
            ).scalar()
            
            logger.debug(f"Recipe count for user {user_id}: {count}")
            return count
            
        except SQLAlchemyError as e:
            logger.error(f"Error counting recipes by user ID: {e}")
            raise

    @inject_session
    def count_by_recipe_base_id(self, session: Session, recipe_base_id: int) -> int:
        """
        레시피 베이스별 레시피 수를 조회합니다.

        Args:
            session: 데이터베이스 세션
            recipe_base_id: 레시피 베이스 ID

        Returns:
            레시피 베이스별 레시피 수

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            count = session.query(func.count(Recipe.recipe_id)).filter(
                Recipe.recipe_base_id == recipe_base_id
            ).scalar()
            
            logger.debug(f"Recipe count for recipe base {recipe_base_id}: {count}")
            return count
            
        except SQLAlchemyError as e:
            logger.error(f"Error counting recipes by recipe base ID: {e}")
            raise 