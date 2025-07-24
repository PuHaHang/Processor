"""
RecipeBaseContent Repository

이 모듈은 RecipeBaseContent 모델의 기본 CRUD 작업을 담당하는 Repository 클래스를 제공합니다.
SQLModel을 최대한 활용하여 타입 안전성과 성능을 보장합니다.
"""

import logging
from typing import Optional, List
from datetime import datetime

from sqlmodel import Session, select, func
from sqlalchemy.exc import SQLAlchemyError

from ..models import RecipeBaseContent, RecipeLanguage


logger = logging.getLogger(__name__)


class RecipeBaseContentRepository:
    """RecipeBaseContent 모델에 대한 SQLModel 최적화 Repository 클래스"""

    def create(self, session: Session, recipe_base_content: RecipeBaseContent) -> RecipeBaseContent:
        """
        새로운 레시피 베이스 컨텐츠를 생성합니다.

        Args:
            session: SQLModel 세션
            recipe_base_content: 생성할 레시피 베이스 컨텐츠 엔티티

        Returns:
            생성된 레시피 베이스 컨텐츠 엔티티

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.add(recipe_base_content)
            session.flush()
            session.refresh(recipe_base_content)
            
            logger.debug(f"Recipe base content created: {recipe_base_content.recipe_base_content_id}")
            return recipe_base_content
            
        except SQLAlchemyError as e:
            logger.error(f"Error creating recipe base content: {e}")
            raise

    def find_by_id(self, session: Session, recipe_base_content_id: int) -> Optional[RecipeBaseContent]:
        """
        ID로 레시피 베이스 컨텐츠를 조회합니다.

        Args:
            session: SQLModel 세션
            recipe_base_content_id: 레시피 베이스 컨텐츠 ID

        Returns:
            레시피 베이스 컨텐츠 엔티티 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(RecipeBaseContent).where(RecipeBaseContent.recipe_base_content_id == recipe_base_content_id)
            result = session.exec(statement).first()
            
            if result:
                logger.debug(f"Recipe base content found: {recipe_base_content_id}")
            else:
                logger.debug(f"Recipe base content not found: {recipe_base_content_id}")
                
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding recipe base content by ID: {e}")
            raise

    def find_by_recipe_base_id(self, session: Session, recipe_base_id: int) -> List[RecipeBaseContent]:
        """
        레시피 베이스 ID로 컨텐츠들을 조회합니다.

        Args:
            session: SQLModel 세션
            recipe_base_id: 레시피 베이스 ID

        Returns:
            레시피 베이스 컨텐츠 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(RecipeBaseContent).where(RecipeBaseContent.recipe_base_id == recipe_base_id)
            result = session.exec(statement).all()
            
            logger.debug(f"Found {len(result)} recipe base contents for recipe base: {recipe_base_id}")
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding recipe base contents by recipe base ID: {e}")
            raise

    def find_by_recipe_base_and_language(self, session: Session, recipe_base_id: int, language: RecipeLanguage) -> Optional[RecipeBaseContent]:
        """
        레시피 베이스 ID와 언어로 컨텐츠를 조회합니다.

        Args:
            session: SQLModel 세션
            recipe_base_id: 레시피 베이스 ID
            language: 레시피 언어

        Returns:
            레시피 베이스 컨텐츠 엔티티 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = (
                select(RecipeBaseContent)
                .where(
                    (RecipeBaseContent.recipe_base_id == recipe_base_id) &
                    (RecipeBaseContent.language == language)
                )
            )
            result = session.exec(statement).first()
            
            if result:
                logger.debug(f"Recipe base content found for recipe base {recipe_base_id} and language {language}")
            else:
                logger.debug(f"Recipe base content not found for recipe base {recipe_base_id} and language {language}")
                
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding recipe base content by recipe base ID and language: {e}")
            raise

    def find_by_language(self, session: Session, language: RecipeLanguage, limit: int = 100, offset: int = 0) -> List[RecipeBaseContent]:
        """
        언어로 레시피 베이스 컨텐츠들을 조회합니다.

        Args:
            session: SQLModel 세션
            language: 레시피 언어
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            레시피 베이스 컨텐츠 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = (
                select(RecipeBaseContent)
                .where(RecipeBaseContent.language == language)
                .offset(offset)
                .limit(limit)
            )
            result = session.exec(statement).all()
            
            logger.debug(f"Found {len(result)} recipe base contents for language: {language}")
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding recipe base contents by language: {e}")
            raise

    def find_by_model_name(self, session: Session, model_name: str, limit: int = 100, offset: int = 0) -> List[RecipeBaseContent]:
        """
        모델명으로 레시피 베이스 컨텐츠들을 조회합니다.

        Args:
            session: SQLModel 세션
            model_name: 모델명
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            레시피 베이스 컨텐츠 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = (
                select(RecipeBaseContent)
                .where(RecipeBaseContent.model_name == model_name)
                .offset(offset)
                .limit(limit)
            )
            result = session.exec(statement).all()
            
            logger.debug(f"Found {len(result)} recipe base contents for model: {model_name}")
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding recipe base contents by model name: {e}")
            raise

    def search_by_title(self, session: Session, title_pattern: str, limit: int = 100, offset: int = 0) -> List[RecipeBaseContent]:
        """
        제목 패턴으로 레시피 베이스 컨텐츠들을 검색합니다.

        Args:
            session: SQLModel 세션
            title_pattern: 검색할 제목 패턴
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            레시피 베이스 컨텐츠 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = (
                select(RecipeBaseContent)
                .where(RecipeBaseContent.title.ilike(f"%{title_pattern}%"))
                .offset(offset)
                .limit(limit)
            )
            result = session.exec(statement).all()
            
            logger.debug(f"Found {len(result)} recipe base contents for title pattern: {title_pattern}")
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Error searching recipe base contents by title: {e}")
            raise

    def search_by_author(self, session: Session, author_pattern: str, limit: int = 100, offset: int = 0) -> List[RecipeBaseContent]:
        """
        작성자 패턴으로 레시피 베이스 컨텐츠들을 검색합니다.

        Args:
            session: SQLModel 세션
            author_pattern: 검색할 작성자 패턴
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            레시피 베이스 컨텐츠 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = (
                select(RecipeBaseContent)
                .where(RecipeBaseContent.author.ilike(f"%{author_pattern}%"))
                .offset(offset)
                .limit(limit)
            )
            result = session.exec(statement).all()
            
            logger.debug(f"Found {len(result)} recipe base contents for author pattern: {author_pattern}")
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Error searching recipe base contents by author: {e}")
            raise

    def update(self, session: Session, recipe_base_content: RecipeBaseContent) -> RecipeBaseContent:
        """
        레시피 베이스 컨텐츠를 업데이트합니다.

        Args:
            session: SQLModel 세션
            recipe_base_content: 업데이트할 레시피 베이스 컨텐츠 엔티티

        Returns:
            업데이트된 레시피 베이스 컨텐츠 엔티티

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            recipe_base_content.updated_at = datetime.now()
            session.add(recipe_base_content)
            session.flush()
            session.refresh(recipe_base_content)
            
            logger.debug(f"Recipe base content updated: {recipe_base_content.recipe_base_content_id}")
            return recipe_base_content
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating recipe base content: {e}")
            raise

    def delete(self, session: Session, recipe_base_content: RecipeBaseContent) -> bool:
        """
        레시피 베이스 컨텐츠를 삭제합니다.

        Args:
            session: SQLModel 세션
            recipe_base_content: 삭제할 레시피 베이스 컨텐츠 엔티티

        Returns:
            삭제 성공 여부

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.delete(recipe_base_content)
            session.flush()
            
            logger.debug(f"Recipe base content deleted: {recipe_base_content.recipe_base_content_id}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error deleting recipe base content: {e}")
            raise

    def find_all(self, session: Session, limit: int = 100, offset: int = 0) -> List[RecipeBaseContent]:
        """
        모든 레시피 베이스 컨텐츠를 조회합니다.

        Args:
            session: SQLModel 세션
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            레시피 베이스 컨텐츠 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(RecipeBaseContent).offset(offset).limit(limit)
            result = session.exec(statement).all()
            
            logger.debug(f"Found {len(result)} recipe base contents")
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding all recipe base contents: {e}")
            raise

    def count(self, session: Session) -> int:
        """
        전체 레시피 베이스 컨텐츠 수를 조회합니다.

        Args:
            session: SQLModel 세션

        Returns:
            전체 레시피 베이스 컨텐츠 수

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(func.count(RecipeBaseContent.recipe_base_content_id))
            count = session.exec(statement).one()
            
            logger.debug(f"Total recipe base content count: {count}")
            return count
            
        except SQLAlchemyError as e:
            logger.error(f"Error counting recipe base contents: {e}")
            raise 