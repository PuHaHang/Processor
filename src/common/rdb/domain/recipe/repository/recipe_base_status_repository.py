"""
RecipeBaseState Repository

이 모듈은 RecipeBaseState 모델의 기본 CRUD 작업을 담당하는 Repository 클래스를 제공합니다.
"""

from typing import Optional, List

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, func

from ..models import RecipeBaseState, RecipeState
from ....common.dependency_injection import inject_session, transactional

import logging

logger = logging.getLogger(__name__)


class RecipeBaseStateRepository:
    """RecipeBaseState 모델 기본 CRUD 작업을 담당하는 Repository"""

    @transactional
    def create(self, session: Session, recipe_base_status: RecipeBaseState) -> RecipeBaseState:
        """
        새로운 레시피 베이스 상태를 생성합니다.

        Args:
            session: 데이터베이스 세션
            recipe_base_status: 생성할 레시피 베이스 상태 엔티티

        Returns:
            생성된 레시피 베이스 상태 엔티티

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.add(recipe_base_status)
            session.flush()
            
            logger.debug(f"Recipe base status created: {recipe_base_status.recipe_base_id}")
            return recipe_base_status
            
        except SQLAlchemyError as e:
            logger.error(f"Error creating recipe base status: {e}")
            raise

    @inject_session
    def find_by_recipe_base_id(self, session: Session, recipe_base_id: int) -> Optional[RecipeBaseState]:
        """
        레시피 베이스 ID로 상태를 조회합니다.

        Args:
            session: 데이터베이스 세션
            recipe_base_id: 레시피 베이스 ID

        Returns:
            레시피 베이스 상태 엔티티 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            status = session.query(RecipeBaseState).options(
                joinedload(RecipeBaseState.recipe_base)
            ).filter(RecipeBaseState.recipe_base_id == recipe_base_id).first()
            
            if status:
                logger.debug(f"Recipe base status found: {recipe_base_id}")
            else:
                logger.debug(f"Recipe base status not found: {recipe_base_id}")
                
            return status
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding recipe base status by recipe base ID: {e}")
            raise

    @inject_session
    def find_by_state(self, session: Session, state: RecipeState, limit: int = 100, offset: int = 0) -> List[RecipeBaseState]:
        """
        상태로 레시피 베이스 상태들을 조회합니다.

        Args:
            session: 데이터베이스 세션
            state: 레시피 상태
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            레시피 베이스 상태 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statuses = session.query(RecipeBaseState).options(
                joinedload(RecipeBaseState.recipe_base)
            ).filter(
                RecipeBaseState.state == state
            ).offset(offset).limit(limit).all()
            
            logger.debug(f"Found {len(statuses)} recipe base statuses for state: {state}")
            return statuses
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding recipe base statuses by state: {e}")
            raise

    @transactional
    def update(self, session: Session, recipe_base_status: RecipeBaseState) -> RecipeBaseState:
        """
        레시피 베이스 상태를 업데이트합니다.

        Args:
            session: 데이터베이스 세션
            recipe_base_status: 업데이트할 레시피 베이스 상태 엔티티

        Returns:
            업데이트된 레시피 베이스 상태 엔티티

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.merge(recipe_base_status)
            session.flush()
            
            logger.debug(f"Recipe base status updated: {recipe_base_status.recipe_base_id}")
            return recipe_base_status
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating recipe base status: {e}")
            raise

    @transactional
    def delete(self, session: Session, recipe_base_status: RecipeBaseState) -> bool:
        """
        레시피 베이스 상태를 삭제합니다.

        Args:
            session: 데이터베이스 세션
            recipe_base_status: 삭제할 레시피 베이스 상태 엔티티

        Returns:
            삭제 성공 여부

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.delete(recipe_base_status)
            session.flush()
            
            logger.debug(f"Recipe base status deleted: {recipe_base_status.recipe_base_id}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error deleting recipe base status: {e}")
            raise

    @inject_session
    def find_all(self, session: Session, limit: int = 100, offset: int = 0) -> List[RecipeBaseState]:
        """
        모든 레시피 베이스 상태를 조회합니다.

        Args:
            session: 데이터베이스 세션
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            레시피 베이스 상태 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statuses = session.query(RecipeBaseState).options(
                joinedload(RecipeBaseState.recipe_base)
            ).offset(offset).limit(limit).all()
            
            logger.debug(f"Found {len(statuses)} recipe base statuses")
            return statuses
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding all recipe base statuses: {e}")
            raise

    @inject_session
    def count(self, session: Session) -> int:
        """
        전체 레시피 베이스 상태 수를 조회합니다.

        Args:
            session: 데이터베이스 세션

        Returns:
            전체 레시피 베이스 상태 수

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            count = session.query(func.count(RecipeBaseState.recipe_base_id)).scalar()
            
            logger.debug(f"Total recipe base status count: {count}")
            return count
            
        except SQLAlchemyError as e:
            logger.error(f"Error counting recipe base statuses: {e}")
            raise

    @inject_session
    def count_by_state(self, session: Session, state: RecipeState) -> int:
        """
        특정 상태의 레시피 베이스 상태 수를 조회합니다.

        Args:
            session: 데이터베이스 세션
            state: 레시피 상태

        Returns:
            특정 상태의 레시피 베이스 상태 수

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            count = session.query(func.count(RecipeBaseState.recipe_base_id)).filter(
                RecipeBaseState.state == state
            ).scalar()
            
            logger.debug(f"Recipe base status count for state {state}: {count}")
            return count
            
        except SQLAlchemyError as e:
            logger.error(f"Error counting recipe base statuses by state: {e}")
            raise

    @inject_session
    def exists_by_recipe_base_id(self, session: Session, recipe_base_id: int) -> bool:
        """
        레시피 베이스 ID로 상태 존재 여부를 확인합니다.

        Args:
            session: 데이터베이스 세션
            recipe_base_id: 레시피 베이스 ID

        Returns:
            존재 여부

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            exists = session.query(RecipeBaseState).filter(
                RecipeBaseState.recipe_base_id == recipe_base_id
            ).first() is not None
            
            logger.debug(f"Recipe base status exists for recipe base {recipe_base_id}: {exists}")
            return exists
            
        except SQLAlchemyError as e:
            logger.error(f"Error checking recipe base status existence: {e}")
            raise 