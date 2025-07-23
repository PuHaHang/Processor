"""
Ingredient Repository

이 모듈은 Ingredient 모델의 기본 CRUD 작업을 담당하는 Repository 클래스를 제공합니다.
"""

from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, func

from ..models import Ingredient
from ....common.dependency_injection import inject_session, transactional

import logging

logger = logging.getLogger(__name__)


class IngredientRepository:
    """Ingredient 모델 기본 CRUD 작업을 담당하는 Repository"""

    @transactional
    def create(self, session: Session, ingredient: Ingredient) -> Ingredient:
        """
        새로운 재료를 생성합니다.

        Args:
            session: 데이터베이스 세션
            ingredient: 생성할 재료 엔티티

        Returns:
            생성된 재료 엔티티

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.add(ingredient)
            session.flush()
            
            logger.debug(f"Ingredient created: {ingredient.id}")
            return ingredient
            
        except SQLAlchemyError as e:
            logger.error(f"Error creating ingredient: {e}")
            raise

    @inject_session
    def find_by_id(self, session: Session, ingredient_id: int) -> Optional[Ingredient]:
        """
        ID로 재료를 조회합니다.

        Args:
            session: 데이터베이스 세션
            ingredient_id: 재료 ID

        Returns:
            재료 엔티티 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            ingredient = session.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
            
            if ingredient:
                logger.debug(f"Ingredient found: {ingredient_id}")
            else:
                logger.debug(f"Ingredient not found: {ingredient_id}")
                
            return ingredient
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding ingredient by ID: {e}")
            raise

    @inject_session
    def find_by_name(self, session: Session, ingredient_name: str) -> Optional[Ingredient]:
        """
        재료명으로 재료를 조회합니다.

        Args:
            session: 데이터베이스 세션
            ingredient_name: 재료명

        Returns:
            재료 엔티티 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            ingredient = session.query(Ingredient).filter(Ingredient.ingredient == ingredient_name).first()
            
            if ingredient:
                logger.debug(f"Ingredient found by name: {ingredient_name}")
            else:
                logger.debug(f"Ingredient not found by name: {ingredient_name}")
                
            return ingredient
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding ingredient by name: {e}")
            raise

    @inject_session
    def search_by_name(self, session: Session, name_pattern: str, limit: int = 100, offset: int = 0) -> List[Ingredient]:
        """
        재료명 패턴으로 재료들을 검색합니다.

        Args:
            session: 데이터베이스 세션
            name_pattern: 검색할 재료명 패턴
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            재료 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            ingredients = session.query(Ingredient).filter(
                Ingredient.ingredient.ilike(f"%{name_pattern}%")
            ).offset(offset).limit(limit).all()
            
            logger.debug(f"Found {len(ingredients)} ingredients for name pattern: {name_pattern}")
            return ingredients
            
        except SQLAlchemyError as e:
            logger.error(f"Error searching ingredients by name: {e}")
            raise

    @transactional
    def update(self, session: Session, ingredient: Ingredient) -> Ingredient:
        """
        재료를 업데이트합니다.

        Args:
            session: 데이터베이스 세션
            ingredient: 업데이트할 재료 엔티티

        Returns:
            업데이트된 재료 엔티티

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.merge(ingredient)
            session.flush()
            
            logger.debug(f"Ingredient updated: {ingredient.id}")
            return ingredient
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating ingredient: {e}")
            raise

    @transactional
    def delete(self, session: Session, ingredient: Ingredient) -> bool:
        """
        재료를 삭제합니다.

        Args:
            session: 데이터베이스 세션
            ingredient: 삭제할 재료 엔티티

        Returns:
            삭제 성공 여부

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.delete(ingredient)
            session.flush()
            
            logger.debug(f"Ingredient deleted: {ingredient.id}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error deleting ingredient: {e}")
            raise

    @inject_session
    def find_all(self, session: Session, limit: int = 100, offset: int = 0) -> List[Ingredient]:
        """
        모든 재료를 조회합니다.

        Args:
            session: 데이터베이스 세션
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            재료 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            ingredients = session.query(Ingredient).offset(offset).limit(limit).all()
            
            logger.debug(f"Found {len(ingredients)} ingredients")
            return ingredients
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding all ingredients: {e}")
            raise

    @inject_session
    def count(self, session: Session) -> int:
        """
        전체 재료 수를 조회합니다.

        Args:
            session: 데이터베이스 세션

        Returns:
            전체 재료 수

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            count = session.query(func.count(Ingredient.id)).scalar()
            
            logger.debug(f"Total ingredient count: {count}")
            return count
            
        except SQLAlchemyError as e:
            logger.error(f"Error counting ingredients: {e}")
            raise

    @inject_session
    def exists_by_name(self, session: Session, ingredient_name: str) -> bool:
        """
        재료명으로 존재 여부를 확인합니다.

        Args:
            session: 데이터베이스 세션
            ingredient_name: 재료명

        Returns:
            존재 여부

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            exists = session.query(Ingredient).filter(Ingredient.ingredient == ingredient_name).first() is not None
            
            logger.debug(f"Ingredient exists by name: {ingredient_name} -> {exists}")
            return exists
            
        except SQLAlchemyError as e:
            logger.error(f"Error checking ingredient existence by name: {e}")
            raise

    @transactional
    def create_or_get(self, session: Session, ingredient_name: str) -> Ingredient:
        """
        재료가 없으면 생성하고, 있으면 기존 재료를 반환합니다.

        Args:
            session: 데이터베이스 세션
            ingredient_name: 재료명

        Returns:
            재료 엔티티

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            # 기존 재료 조회
            existing_ingredient = session.query(Ingredient).filter(
                Ingredient.ingredient == ingredient_name
            ).first()
            
            if existing_ingredient:
                logger.debug(f"Ingredient found: {ingredient_name}")
                return existing_ingredient
            
            # 새로운 재료 생성
            new_ingredient = Ingredient(ingredient=ingredient_name)
            session.add(new_ingredient)
            session.flush()
            
            logger.debug(f"New ingredient created: {ingredient_name}")
            return new_ingredient
            
        except SQLAlchemyError as e:
            logger.error(f"Error creating or getting ingredient: {e}")
            raise

    @transactional
    def bulk_create_or_get(self, session: Session, ingredient_names: List[str]) -> List[Ingredient]:
        """
        여러 재료를 한번에 생성하거나 조회합니다.

        Args:
            session: 데이터베이스 세션
            ingredient_names: 재료명 리스트

        Returns:
            재료 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            # 기존 재료들 조회
            existing_ingredients = session.query(Ingredient).filter(
                Ingredient.ingredient.in_(ingredient_names)
            ).all()
            
            existing_names = {ingredient.ingredient for ingredient in existing_ingredients}
            
            # 새로운 재료들 생성
            new_ingredients = []
            for name in ingredient_names:
                if name not in existing_names:
                    new_ingredient = Ingredient(ingredient=name)
                    session.add(new_ingredient)
                    new_ingredients.append(new_ingredient)
            
            if new_ingredients:
                session.flush()
                logger.debug(f"Created {len(new_ingredients)} new ingredients")
            
            # 모든 재료 반환
            all_ingredients = existing_ingredients + new_ingredients
            logger.debug(f"Total ingredients returned: {len(all_ingredients)}")
            return all_ingredients
            
        except SQLAlchemyError as e:
            logger.error(f"Error bulk creating or getting ingredients: {e}")
            raise 