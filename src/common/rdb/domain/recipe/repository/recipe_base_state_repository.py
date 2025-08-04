"""
RecipeBaseState Repository

이 모듈은 RecipeBaseState 모델의 기본 CRUD 작업을 담당하는 Repository 클래스를 제공합니다.
SQLModel을 최대한 활용하여 타입 안전성과 성능을 보장합니다.
"""

import logging
from typing import Optional, List

from sqlmodel import Session, select, func
from sqlalchemy.exc import SQLAlchemyError

from ..models import RecipeBaseState, RecipeState


logger = logging.getLogger(__name__)


class RecipeBaseStateRepository:
    """RecipeBaseState 모델에 대한 SQLModel 최적화 Repository 클래스"""

    def create(self, session: Session, recipe_base_state: RecipeBaseState) -> RecipeBaseState:
        """
        새로운 레시피 베이스 상태를 생성합니다.

        Args:
            session: SQLModel 세션
            recipe_base_status: 생성할 레시피 베이스 상태 엔티티

        Returns:
            생성된 레시피 베이스 상태 엔티티

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.add(recipe_base_state)
            session.flush()
            session.refresh(recipe_base_state)
            
            logger.debug(f"Recipe base state created: {recipe_base_state.recipe_base_content_id}")
            return recipe_base_state
            
        except SQLAlchemyError as e:
            logger.error(f"Error creating recipe base state: {e}")
            raise

    def find_by_recipe_base_content_id(self, session: Session, recipe_base_content_id: int) -> Optional[RecipeBaseState]:
        """
        레시피 베이스 ID로 상태를 조회합니다.

        Args:
            session: SQLModel 세션
            recipe_base_id: 레시피 베이스 ID

        Returns:
            레시피 베이스 상태 엔티티 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(RecipeBaseState).where(RecipeBaseState.recipe_base_content_id == recipe_base_content_id)
            result = session.exec(statement).first()
            
            if result:
                logger.debug(f"Recipe base state found: {recipe_base_content_id}")
            else:
                logger.debug(f"Recipe base state not found: {recipe_base_content_id}")
                
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding recipe base state by recipe base content ID: {e}")
            raise

    def find_by_state(self, session: Session, state: RecipeState, limit: int = 100, offset: int = 0) -> List[RecipeBaseState]:
        """
        상태로 레시피 베이스 상태들을 조회합니다.

        Args:
            session: SQLModel 세션
            state: 레시피 상태
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            레시피 베이스 상태 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = (
                select(RecipeBaseState)
                .where(RecipeBaseState.state == state)
                .offset(offset)
                .limit(limit)
            )
            result = session.exec(statement).all()
            
            logger.debug(f"Found {len(result)} recipe base states for state: {state}")
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding recipe base states by state: {e}")
            raise

    def update(self, session: Session, recipe_base_state: RecipeBaseState) -> RecipeBaseState:
        """
        레시피 베이스 상태를 업데이트합니다.

        Args:
            session: SQLModel 세션
            recipe_base_status: 업데이트할 레시피 베이스 상태 엔티티

        Returns:
            업데이트된 레시피 베이스 상태 엔티티

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.add(recipe_base_state)
            session.flush()
            session.refresh(recipe_base_state)
            
            logger.debug(f"Recipe base state updated: {recipe_base_state.recipe_base_content_id}")
            return recipe_base_state
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating recipe base state: {e}")
            raise

    def delete(self, session: Session, recipe_base_state: RecipeBaseState) -> bool:
        """
        레시피 베이스 상태를 삭제합니다.

        Args:
            session: SQLModel 세션
            recipe_base_status: 삭제할 레시피 베이스 상태 엔티티

        Returns:
            삭제 성공 여부

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.delete(recipe_base_state)
            session.flush()
            
            logger.debug(f"Recipe base state deleted: {recipe_base_state.recipe_base_content_id}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error deleting recipe base state: {e}")
            raise

    def find_all(self, session: Session, limit: int = 100, offset: int = 0) -> List[RecipeBaseState]:
        """
        모든 레시피 베이스 상태를 조회합니다.

        Args:
            session: SQLModel 세션
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            레시피 베이스 상태 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(RecipeBaseState).offset(offset).limit(limit)
            result = session.exec(statement).all()
            
            logger.debug(f"Found {len(result)} recipe base states")
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding all recipe base states: {e}")
            raise

    def count(self, session: Session) -> int:
        """
        전체 레시피 베이스 상태 수를 조회합니다.

        Args:
            session: SQLModel 세션

        Returns:
            전체 레시피 베이스 상태 수

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(func.count(RecipeBaseState.recipe_base_content_id))
            count = session.exec(statement).one()
            
            logger.debug(f"Total recipe base state count: {count}")
            return count
            
        except SQLAlchemyError as e:
            logger.error(f"Error counting recipe base states: {e}")
            raise

    def count_by_state(self, session: Session, state: RecipeState) -> int:
        """
        특정 상태의 레시피 베이스 상태 수를 조회합니다.

        Args:
            session: SQLModel 세션
            state: 레시피 상태

        Returns:
            특정 상태의 레시피 베이스 상태 수

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(func.count(RecipeBaseState.recipe_base_content_id)).where(RecipeBaseState.state == state)
            count = session.exec(statement).one()
            
            logger.debug(f"Recipe base state count for state {state}: {count}")
            return count
            
        except SQLAlchemyError as e:
            logger.error(f"Error counting recipe base states by state: {e}")
            raise

    def exists_by_recipe_base_content_id(self, session: Session, recipe_base_content_id: int) -> bool:
        """
        레시피 베이스 ID로 상태 존재 여부를 확인합니다.

        Args:
            session: SQLModel 세션
            recipe_base_content_id: 레시피 베이스 컨텐츠 ID

        Returns:
            존재 여부

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(RecipeBaseState.recipe_base_content_id).where(RecipeBaseState.recipe_base_content_id == recipe_base_content_id)
            result = session.exec(statement).first()
            exists = result is not None
            
            logger.debug(f"Recipe base state exists for recipe base content {recipe_base_content_id}: {exists}")
            return exists
            
        except SQLAlchemyError as e:
            logger.error(f"Error checking recipe base state existence: {e}")
            raise 