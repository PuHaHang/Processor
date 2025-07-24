"""
Ingredient Repository

이 모듈은 Ingredient 모델의 기본 CRUD 작업을 담당하는 Repository 클래스를 제공합니다.
SQLModel을 최대한 활용하여 타입 안전성과 성능을 보장합니다.
"""

import logging
from typing import Optional, List

from sqlmodel import Session, select, func
from sqlalchemy.exc import SQLAlchemyError

from ..models import Ingredient


logger = logging.getLogger(__name__)


class IngredientRepository:
    """Ingredient 모델에 대한 SQLModel 최적화 Repository 클래스"""

    def create(self, session: Session, ingredient: Ingredient) -> Ingredient:
        """
        새로운 재료를 생성합니다.

        Args:
            session: SQLModel 세션
            ingredient: 생성할 재료 엔티티

        Returns:
            생성된 재료 엔티티

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.add(ingredient)
            session.flush()
            session.refresh(ingredient)
            
            logger.debug(f"Ingredient created: {ingredient.ingredient_id}")
            return ingredient
            
        except SQLAlchemyError as e:
            logger.error(f"Error creating ingredient: {e}")
            raise

    def find_by_id(self, session: Session, ingredient_id: int) -> Optional[Ingredient]:
        """
        ID로 재료를 조회합니다.

        Args:
            session: SQLModel 세션
            ingredient_id: 재료 ID

        Returns:
            재료 엔티티 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(Ingredient).where(Ingredient.ingredient_id == ingredient_id)
            result = session.exec(statement).first()
            
            if result:
                logger.debug(f"Ingredient found: {ingredient_id}")
            else:
                logger.debug(f"Ingredient not found: {ingredient_id}")
                
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding ingredient by ID: {e}")
            raise

    def find_by_name(self, session: Session, ingredient_name: str) -> Optional[Ingredient]:
        """
        이름으로 재료를 조회합니다.

        Args:
            session: SQLModel 세션
            ingredient_name: 재료명

        Returns:
            재료 엔티티 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(Ingredient).where(Ingredient.ingredient == ingredient_name)
            result = session.exec(statement).first()
            
            if result:
                logger.debug(f"Ingredient found by name: {ingredient_name}")
            else:
                logger.debug(f"Ingredient not found by name: {ingredient_name}")
                
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding ingredient by name: {e}")
            raise

    def search_by_name(self, session: Session, name_pattern: str, limit: int = 100, offset: int = 0) -> List[Ingredient]:
        """
        이름 패턴으로 재료들을 검색합니다.

        Args:
            session: SQLModel 세션
            name_pattern: 검색할 이름 패턴
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            재료 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = (
                select(Ingredient)
                .where(Ingredient.ingredient.ilike(f"%{name_pattern}%"))
                .offset(offset)
                .limit(limit)
            )
            result = session.exec(statement).all()
            
            logger.debug(f"Found {len(result)} ingredients for name pattern: {name_pattern}")
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Error searching ingredients by name: {e}")
            raise

    def update(self, session: Session, ingredient: Ingredient) -> Ingredient:
        """
        재료를 업데이트합니다.

        Args:
            session: SQLModel 세션
            ingredient: 업데이트할 재료 엔티티

        Returns:
            업데이트된 재료 엔티티

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.add(ingredient)
            session.flush()
            session.refresh(ingredient)
            
            logger.debug(f"Ingredient updated: {ingredient.ingredient_id}")
            return ingredient
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating ingredient: {e}")
            raise

    def delete(self, session: Session, ingredient: Ingredient) -> bool:
        """
        재료를 삭제합니다.

        Args:
            session: SQLModel 세션
            ingredient: 삭제할 재료 엔티티

        Returns:
            삭제 성공 여부

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.delete(ingredient)
            session.flush()
            
            logger.debug(f"Ingredient deleted: {ingredient.ingredient_id}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error deleting ingredient: {e}")
            raise

    def find_all(self, session: Session, limit: int = 100, offset: int = 0) -> List[Ingredient]:
        """
        모든 재료를 조회합니다.

        Args:
            session: SQLModel 세션
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            재료 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(Ingredient).offset(offset).limit(limit)
            result = session.exec(statement).all()
            
            logger.debug(f"Found {len(result)} ingredients")
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding all ingredients: {e}")
            raise

    def count(self, session: Session) -> int:
        """
        전체 재료 수를 조회합니다.

        Args:
            session: SQLModel 세션

        Returns:
            전체 재료 수

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(func.count(Ingredient.ingredient_id))
            count = session.exec(statement).one()
            
            logger.debug(f"Total ingredient count: {count}")
            return count
            
        except SQLAlchemyError as e:
            logger.error(f"Error counting ingredients: {e}")
            raise

    def exists_by_name(self, session: Session, ingredient_name: str) -> bool:
        """
        이름으로 존재 여부를 확인합니다.

        Args:
            session: SQLModel 세션
            ingredient_name: 재료명

        Returns:
            존재 여부

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(Ingredient.ingredient_id).where(Ingredient.ingredient == ingredient_name)
            result = session.exec(statement).first()
            exists = result is not None
            
            logger.debug(f"Ingredient exists by name {ingredient_name}: {exists}")
            return exists
            
        except SQLAlchemyError as e:
            logger.error(f"Error checking ingredient existence by name: {e}")
            raise

    def create_or_get(self, session: Session, ingredient_name: str) -> Ingredient:
        """
        재료가 없으면 생성하고, 있으면 기존 재료를 반환합니다.

        Args:
            session: SQLModel 세션
            ingredient_name: 재료명

        Returns:
            재료 엔티티

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            # 기존 재료 조회
            statement = select(Ingredient).where(Ingredient.ingredient == ingredient_name)
            existing_ingredient = session.exec(statement).first()
            
            if existing_ingredient:
                logger.debug(f"Ingredient found: {ingredient_name}")
                return existing_ingredient
            
            # 새로운 재료 생성
            new_ingredient = Ingredient(ingredient=ingredient_name)
            session.add(new_ingredient)
            session.flush()
            session.refresh(new_ingredient)
            
            logger.debug(f"New ingredient created: {ingredient_name}")
            return new_ingredient
            
        except SQLAlchemyError as e:
            logger.error(f"Error creating or getting ingredient: {e}")
            raise

    def bulk_create_or_get(self, session: Session, ingredient_names: List[str]) -> List[Ingredient]:
        """
        여러 재료를 일괄 생성하거나 기존 재료를 반환합니다.

        Args:
            session: SQLModel 세션
            ingredient_names: 재료명 리스트

        Returns:
            재료 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            ingredients = []
            for ingredient_name in ingredient_names:
                ingredient = self.create_or_get(session, ingredient_name)
                ingredients.append(ingredient)
            
            logger.debug(f"Bulk created or got {len(ingredients)} ingredients")
            return ingredients
            
        except SQLAlchemyError as e:
            logger.error(f"Error bulk creating or getting ingredients: {e}")
            raise 