"""
RecipeBase Repository

이 모듈은 RecipeBase 모델의 기본 CRUD 작업을 담당하는 Repository 클래스를 제공합니다.
"""

from typing import Optional, List
from datetime import datetime

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, func

from ..models import RecipeBase, RecipeDifficulty
from ....common.dependency_injection import inject_session, transactional

import logging

logger = logging.getLogger(__name__)


class RecipeBaseRepository:
    """RecipeBase 모델 기본 CRUD 작업을 담당하는 Repository"""

    @transactional
    def create(self, session: Session, recipe_base: RecipeBase) -> RecipeBase:
        """
        새로운 레시피 베이스를 생성합니다.

        Args:
            session: 데이터베이스 세션
            recipe_base: 생성할 레시피 베이스 엔티티

        Returns:
            생성된 레시피 베이스 엔티티

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.add(recipe_base)
            session.flush()
            
            logger.debug(f"Recipe base created: {recipe_base.recipe_base_id}")
            return recipe_base
            
        except SQLAlchemyError as e:
            logger.error(f"Error creating recipe base: {e}")
            raise

    @inject_session
    def find_by_id(self, session: Session, recipe_base_id: int) -> Optional[RecipeBase]:
        """
        ID로 레시피 베이스를 조회합니다.

        Args:
            session: 데이터베이스 세션
            recipe_base_id: 레시피 베이스 ID

        Returns:
            레시피 베이스 엔티티 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            recipe_base = session.query(RecipeBase).options(
                joinedload(RecipeBase.contents),
                joinedload(RecipeBase.status)
            ).filter(RecipeBase.recipe_base_id == recipe_base_id).first()
            
            if recipe_base:
                logger.debug(f"Recipe base found: {recipe_base_id}")
            else:
                logger.debug(f"Recipe base not found: {recipe_base_id}")
                
            return recipe_base
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding recipe base by ID: {e}")
            raise

    @inject_session
    def find_by_checksum(self, session: Session, chksum: str) -> Optional[RecipeBase]:
        """
        체크섬으로 레시피 베이스를 조회합니다.

        Args:
            session: 데이터베이스 세션
            chksum: URL 해시값

        Returns:
            레시피 베이스 엔티티 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            recipe_base = session.query(RecipeBase).options(
                joinedload(RecipeBase.contents),
                joinedload(RecipeBase.status)
            ).filter(RecipeBase.chksum == chksum).first()
            
            if recipe_base:
                logger.debug(f"Recipe base found by checksum: {chksum}")
            else:
                logger.debug(f"Recipe base not found by checksum: {chksum}")
                
            return recipe_base
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding recipe base by checksum: {e}")
            raise

    @inject_session
    def find_by_difficulty(self, session: Session, difficulty: RecipeDifficulty, limit: int = 100, offset: int = 0) -> List[RecipeBase]:
        """
        난이도로 레시피 베이스들을 조회합니다.

        Args:
            session: 데이터베이스 세션
            difficulty: 레시피 난이도
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            레시피 베이스 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            recipe_bases = session.query(RecipeBase).options(
                joinedload(RecipeBase.contents),
                joinedload(RecipeBase.status)
            ).filter(
                RecipeBase.difficulty == difficulty
            ).offset(offset).limit(limit).all()
            
            logger.debug(f"Found {len(recipe_bases)} recipe bases for difficulty: {difficulty}")
            return recipe_bases
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding recipe bases by difficulty: {e}")
            raise

    @inject_session
    def find_by_servings(self, session: Session, servings: int, limit: int = 100, offset: int = 0) -> List[RecipeBase]:
        """
        인분 수로 레시피 베이스들을 조회합니다.

        Args:
            session: 데이터베이스 세션
            servings: 인분 수
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            레시피 베이스 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            recipe_bases = session.query(RecipeBase).options(
                joinedload(RecipeBase.contents),
                joinedload(RecipeBase.status)
            ).filter(
                RecipeBase.servings == servings
            ).offset(offset).limit(limit).all()
            
            logger.debug(f"Found {len(recipe_bases)} recipe bases for servings: {servings}")
            return recipe_bases
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding recipe bases by servings: {e}")
            raise

    @inject_session
    def find_popular(self, session: Session, limit: int = 100, offset: int = 0) -> List[RecipeBase]:
        """
        인기 레시피 베이스들을 조회합니다.

        Args:
            session: 데이터베이스 세션
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            레시피 베이스 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            recipe_bases = session.query(RecipeBase).options(
                joinedload(RecipeBase.contents),
                joinedload(RecipeBase.status)
            ).order_by(
                RecipeBase.view_count.desc()
            ).offset(offset).limit(limit).all()
            
            logger.debug(f"Found {len(recipe_bases)} popular recipe bases")
            return recipe_bases
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding popular recipe bases: {e}")
            raise

    @transactional
    def update(self, session: Session, recipe_base: RecipeBase) -> RecipeBase:
        """
        레시피 베이스를 업데이트합니다.

        Args:
            session: 데이터베이스 세션
            recipe_base: 업데이트할 레시피 베이스 엔티티

        Returns:
            업데이트된 레시피 베이스 엔티티

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            recipe_base.updated_at = datetime.utcnow()
            session.merge(recipe_base)
            session.flush()
            
            logger.debug(f"Recipe base updated: {recipe_base.recipe_base_id}")
            return recipe_base
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating recipe base: {e}")
            raise

    @transactional
    def delete(self, session: Session, recipe_base: RecipeBase) -> bool:
        """
        레시피 베이스를 삭제합니다.

        Args:
            session: 데이터베이스 세션
            recipe_base: 삭제할 레시피 베이스 엔티티

        Returns:
            삭제 성공 여부

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.delete(recipe_base)
            session.flush()
            
            logger.debug(f"Recipe base deleted: {recipe_base.recipe_base_id}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error deleting recipe base: {e}")
            raise

    @transactional
    def increment_view_count(self, session: Session, recipe_base: RecipeBase) -> RecipeBase:
        """
        레시피 베이스의 조회수를 증가시킵니다.

        Args:
            session: 데이터베이스 세션
            recipe_base: 조회수를 증가시킬 레시피 베이스 엔티티

        Returns:
            업데이트된 레시피 베이스 엔티티

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            recipe_base.view_count += 1
            recipe_base.updated_at = datetime.utcnow()
            session.merge(recipe_base)
            session.flush()
            
            logger.debug(f"Recipe base view count incremented: {recipe_base.recipe_base_id}")
            return recipe_base
            
        except SQLAlchemyError as e:
            logger.error(f"Error incrementing recipe base view count: {e}")
            raise

    @inject_session
    def find_all(self, session: Session, limit: int = 100, offset: int = 0) -> List[RecipeBase]:
        """
        모든 레시피 베이스를 조회합니다.

        Args:
            session: 데이터베이스 세션
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            레시피 베이스 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            recipe_bases = session.query(RecipeBase).options(
                joinedload(RecipeBase.contents),
                joinedload(RecipeBase.status)
            ).offset(offset).limit(limit).all()
            
            logger.debug(f"Found {len(recipe_bases)} recipe bases")
            return recipe_bases
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding all recipe bases: {e}")
            raise

    @inject_session
    def count(self, session: Session) -> int:
        """
        전체 레시피 베이스 수를 조회합니다.

        Args:
            session: 데이터베이스 세션

        Returns:
            전체 레시피 베이스 수

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            count = session.query(func.count(RecipeBase.recipe_base_id)).scalar()
            
            logger.debug(f"Total recipe base count: {count}")
            return count
            
        except SQLAlchemyError as e:
            logger.error(f"Error counting recipe bases: {e}")
            raise

    @inject_session
    def exists_by_checksum(self, session: Session, chksum: str) -> bool:
        """
        체크섬으로 존재 여부를 확인합니다.

        Args:
            session: 데이터베이스 세션
            chksum: URL 해시값

        Returns:
            존재 여부

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            exists = session.query(RecipeBase).filter(RecipeBase.chksum == chksum).first() is not None
            
            logger.debug(f"Recipe base exists by checksum: {chksum} -> {exists}")
            return exists
            
        except SQLAlchemyError as e:
            logger.error(f"Error checking recipe base existence by checksum: {e}")
            raise 