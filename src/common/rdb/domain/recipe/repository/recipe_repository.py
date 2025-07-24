"""
Recipe Repository

이 모듈은 Recipe 모델의 기본 CRUD 작업을 담당하는 Repository 클래스를 제공합니다.
SQLModel을 최대한 활용하여 타입 안전성과 성능을 보장합니다.
"""

import logging
from typing import Optional, List
from datetime import datetime

from sqlmodel import Session, select, func
from sqlalchemy.exc import SQLAlchemyError

from ..models import Recipe, RecipeBaseContent


logger = logging.getLogger(__name__)


class RecipeRepository:
    """Recipe 모델에 대한 SQLModel 최적화 Repository 클래스"""

    def create(self, session: Session, recipe: Recipe) -> Recipe:
        """
        새로운 레시피를 생성합니다.

        Args:
            session: SQLModel 세션
            recipe: 생성할 레시피 엔티티

        Returns:
            생성된 레시피 엔티티

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.add(recipe)
            session.flush()
            session.refresh(recipe)
            
            logger.debug(f"Recipe created: {recipe.recipe_id}")
            return recipe
            
        except SQLAlchemyError as e:
            logger.error(f"Error creating recipe: {e}")
            raise

    def find_by_id(self, session: Session, recipe_id: int) -> Optional[Recipe]:
        """
        ID로 레시피를 조회합니다.

        Args:
            session: SQLModel 세션
            recipe_id: 레시피 ID

        Returns:
            레시피 엔티티 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(Recipe).where(Recipe.recipe_id == recipe_id)
            result = session.exec(statement).first()
            
            if result:
                logger.debug(f"Recipe found: {recipe_id}")
            else:
                logger.debug(f"Recipe not found: {recipe_id}")
                
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding recipe by ID: {e}")
            raise

    def find_by_user_id(self, session: Session, user_id: str, limit: int = 100, offset: int = 0) -> List[Recipe]:
        """
        사용자 ID로 레시피들을 조회합니다.

        Args:
            session: SQLModel 세션
            user_id: 사용자 ID
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            레시피 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = (
                select(Recipe)
                .where(Recipe.user_id == user_id)
                .offset(offset)
                .limit(limit)
            )
            result = session.exec(statement).all()
            
            logger.debug(f"Found {len(result)} recipes for user: {user_id}")
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding recipes by user ID: {e}")
            raise

    def find_by_recipe_base_id(self, session: Session, recipe_base_id: int, limit: int = 100, offset: int = 0) -> List[Recipe]:
        """
        레시피 베이스 ID로 레시피들을 조회합니다.

        Args:
            session: SQLModel 세션
            recipe_base_id: 레시피 베이스 ID
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            레시피 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            recipe_base_content_ids = session.exec(
                select(RecipeBaseContent.recipe_base_content_id)
                .where(RecipeBaseContent.recipe_base_id == recipe_base_id)
            ).all()

            statement = (
                select(Recipe)
                .where(Recipe.recipe_base_content_id.in_(recipe_base_content_ids))
                .offset(offset)
                .limit(limit)
            )
            result = session.exec(statement).all()
            
            logger.debug(f"Found {len(result)} recipes for recipe base: {recipe_base_id}")
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding recipes by recipe base ID: {e}")
            raise

    def search_by_title(self, session: Session, title_pattern: str, limit: int = 100, offset: int = 0) -> List[Recipe]:
        """
        제목 패턴으로 레시피들을 검색합니다.

        Args:
            session: SQLModel 세션
            title_pattern: 검색할 제목 패턴
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            레시피 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = (
                select(Recipe)
                .where(Recipe.title.ilike(f"%{title_pattern}%"))
                .offset(offset)
                .limit(limit)
            )
            result = session.exec(statement).all()
            
            logger.debug(f"Found {len(result)} recipes for title pattern: {title_pattern}")
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Error searching recipes by title: {e}")
            raise

    def find_recent(self, session: Session, limit: int = 100, offset: int = 0) -> List[Recipe]:
        """
        최근 생성된 레시피들을 조회합니다.

        Args:
            session: SQLModel 세션
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            레시피 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = (
                select(Recipe)
                .order_by(Recipe.created_at.desc())
                .offset(offset)
                .limit(limit)
            )
            result = session.exec(statement).all()
            
            logger.debug(f"Found {len(result)} recent recipes")
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding recent recipes: {e}")
            raise

    def update(self, session: Session, recipe: Recipe) -> Recipe:
        """
        레시피를 업데이트합니다.

        Args:
            session: SQLModel 세션
            recipe: 업데이트할 레시피 엔티티

        Returns:
            업데이트된 레시피 엔티티

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            recipe.updated_at = datetime.now()
            session.add(recipe)
            session.flush()
            session.refresh(recipe)
            
            logger.debug(f"Recipe updated: {recipe.recipe_id}")
            return recipe
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating recipe: {e}")
            raise

    def delete(self, session: Session, recipe: Recipe) -> bool:
        """
        레시피를 삭제합니다.

        Args:
            session: SQLModel 세션
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

    def find_all(self, session: Session, limit: int = 100, offset: int = 0) -> List[Recipe]:
        """
        모든 레시피를 조회합니다.

        Args:
            session: SQLModel 세션
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            레시피 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(Recipe).offset(offset).limit(limit)
            result = session.exec(statement).all()
            
            logger.debug(f"Found {len(result)} recipes")
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding all recipes: {e}")
            raise

    def count(self, session: Session) -> int:
        """
        전체 레시피 수를 조회합니다.

        Args:
            session: SQLModel 세션

        Returns:
            전체 레시피 수

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(func.count(Recipe.recipe_id))
            count = session.exec(statement).one()
            
            logger.debug(f"Total recipe count: {count}")
            return count
            
        except SQLAlchemyError as e:
            logger.error(f"Error counting recipes: {e}")
            raise

    def count_by_user_id(self, session: Session, user_id: str) -> int:
        """
        사용자별 레시피 수를 조회합니다.

        Args:
            session: SQLModel 세션
            user_id: 사용자 ID

        Returns:
            사용자별 레시피 수

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(func.count(Recipe.recipe_id)).where(Recipe.user_id == user_id)
            count = session.exec(statement).one()
            
            logger.debug(f"Recipe count for user {user_id}: {count}")
            return count
            
        except SQLAlchemyError as e:
            logger.error(f"Error counting recipes by user ID: {e}")
            raise

    def count_by_recipe_base_id(self, session: Session, recipe_base_id: int) -> int:
        """
        레시피 베이스별 레시피 수를 조회합니다.

        Args:
            session: SQLModel 세션
            recipe_base_id: 레시피 베이스 ID

        Returns:
            레시피 베이스별 레시피 수

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            recipe_base_content_ids = session.exec(
                select(RecipeBaseContent.recipe_base_content_id)
                .where(RecipeBaseContent.recipe_base_id == recipe_base_id)
            ).all()

            statement = select(func.count(Recipe.recipe_id)).where(Recipe.recipe_base_content_id.in_(recipe_base_content_ids))
            count = session.exec(statement).one()
            
            logger.debug(f"Recipe count for recipe base {recipe_base_id}: {count}")
            return count
            
        except SQLAlchemyError as e:
            logger.error(f"Error counting recipes by recipe base ID: {e}")
            raise

    def exists_by_id(self, session: Session, recipe_id: int) -> bool:
        """
        레시피 ID 존재 여부를 확인합니다.

        Args:
            session: SQLModel 세션
            recipe_id: 레시피 ID

        Returns:
            존재 여부

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(Recipe.recipe_id).where(Recipe.recipe_id == recipe_id)
            result = session.exec(statement).first()
            exists = result is not None
            
            logger.debug(f"Recipe exists by ID {recipe_id}: {exists}")
            return exists
            
        except SQLAlchemyError as e:
            logger.error(f"Error checking recipe existence by ID: {e}")
            raise 