"""
RecipeBase 도메인 서비스

이 모듈은 레시피 베이스 관련 CRUD 작업을 처리하는 서비스를 제공합니다.
새로운 ERD 구조에 따라 레시피 정보가 여러 테이블로 분산되어 있어
트랜잭션 처리가 중요합니다.
"""

import hashlib
from typing import Optional, List, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, func

from .models import (
    RecipeBase, RecipeBaseContent, RecipeBaseStatus, Ingredient,
    RecipeLanguage, RecipeDifficulty, RecipeState
)
from .dto import (
    CreateRecipeBaseDto, UpdateRecipeBaseDto, SearchRecipeBasesDto,
    AddIngredientToRecipeBaseDto, UpdateRecipeBaseIngredientDto
)
from .repository import (
    RecipeBaseRepository, RecipeBaseContentRepository, RecipeBaseStatusRepository,
    IngredientRepository
)
from ...common.dependency_injection import inject_session, transactional

import logging

logger = logging.getLogger(__name__)


class RecipeBaseService:
    """레시피 베이스 관련 비즈니스 로직을 처리하는 서비스"""

    def __init__(self):
        self.recipe_base_repository = RecipeBaseRepository()
        self.recipe_base_content_repository = RecipeBaseContentRepository()
        self.recipe_base_status_repository = RecipeBaseStatusRepository()
        self.ingredient_repository = IngredientRepository()

    @transactional
    def create_recipe_base(self, session: Session, dto: CreateRecipeBaseDto) -> RecipeBase:
        """
        새로운 레시피 베이스를 생성합니다.
        여러 테이블에 분산된 정보를 트랜잭션 내에서 생성합니다.

        Args:
            session: 데이터베이스 세션
            dto: 레시피 베이스 생성 데이터 전송 객체

        Returns:
            생성된 레시피 베이스 객체

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            # URL 해시 생성
            url = dto.referrer.get('url', '') if dto.referrer else ''
            chksum = self._generate_checksum(url)
            
            # 기본 레시피 베이스 생성
            recipe_base = RecipeBase(
                chksum=chksum,
                thumbnail=dto.thumbnail,
                referrer=dto.referrer,
                metadata=dto.metadata,
                servings=dto.servings,
                difficulty=dto.difficulty,
                estimated_time=dto.estimated_time
            )
            
            # Repository를 통해 레시피 베이스 생성
            recipe_base = self.recipe_base_repository.create(session, recipe_base)
            
            # 레시피 베이스 컨텐츠 생성
            if dto.title or dto.author or dto.ingredients or dto.stages:
                content = RecipeBaseContent(
                    recipe_base_id=recipe_base.recipe_base_id,
                    title=dto.title,
                    author=dto.author,
                    ingredients=dto.ingredients,  # 이미 리스트 형태
                    stages=dto.stages,
                    language=dto.language,
                    model_name=dto.model_name
                )
                self.recipe_base_content_repository.create(session, content)
                
                # 재료 태그 생성 (검색용)
                if dto.ingredients and isinstance(dto.ingredients, list):
                    self._create_ingredient_tags(
                        session,
                        [ingredient['ingredient_name'] for ingredient in dto.ingredients]
                    )
            
            # 레시피 베이스 상태 생성
            status = RecipeBaseStatus(
                recipe_base_id=recipe_base.recipe_base_id,
                state=RecipeState.PENDING
            )
            self.recipe_base_status_repository.create(session, status)
            
            logger.info(f"Recipe base created: {recipe_base.recipe_base_id}")
            return recipe_base
            
        except SQLAlchemyError as e:
            logger.error(f"Error creating recipe base: {e}")
            raise

    def _create_ingredient_tags(self, session: Session, ingredients: List[str]) -> None:
        """
        재료 태그를 생성합니다 (검색용).
        
        Args:
            session: 데이터베이스 세션
            ingredients: 재료 리스트
        """
        try:
            # Repository를 통해 재료 태그 생성
            self.ingredient_repository.bulk_create_or_get(session, ingredients)
            logger.debug(f"Created {len(ingredients)} ingredient tags")
            
        except SQLAlchemyError as e:
            logger.error(f"Error creating ingredient tags: {e}")
            raise

    @inject_session
    def get_recipe_base_by_id(self, session: Session, recipe_base_id: int) -> Optional[RecipeBase]:
        """
        ID로 레시피 베이스를 조회합니다.
        관련된 모든 정보를 함께 로드합니다.

        Args:
            session: 데이터베이스 세션
            recipe_base_id: 레시피 베이스 ID

        Returns:
            레시피 베이스 객체 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            recipe_base = self.recipe_base_repository.find_by_id(session, recipe_base_id)
            
            if recipe_base:
                logger.debug(f"Recipe base found: {recipe_base_id}")
            else:
                logger.debug(f"Recipe base not found: {recipe_base_id}")
                
            return recipe_base
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting recipe base by ID: {e}")
            raise

    @inject_session
    def get_recipe_base_by_checksum(self, session: Session, chksum: str) -> Optional[RecipeBase]:
        """
        체크섬으로 레시피 베이스를 조회합니다.

        Args:
            session: 데이터베이스 세션
            chksum: URL 해시값

        Returns:
            레시피 베이스 객체 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            recipe_base = self.recipe_base_repository.find_by_checksum(session, chksum)
            
            if recipe_base:
                logger.debug(f"Recipe base found by checksum: {chksum}")
            else:
                logger.debug(f"Recipe base not found by checksum: {chksum}")
                
            return recipe_base
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting recipe base by checksum: {e}")
            raise

    @inject_session
    def get_recipe_bases_by_difficulty(self, session: Session, difficulty: RecipeDifficulty, limit: int = 100, offset: int = 0) -> List[RecipeBase]:
        """
        난이도별 레시피 베이스들을 조회합니다.

        Args:
            session: 데이터베이스 세션
            difficulty: 레시피 난이도
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            레시피 베이스 객체 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            recipe_bases = self.recipe_base_repository.find_by_difficulty(session, difficulty, limit, offset)
            
            logger.debug(f"Found {len(recipe_bases)} recipe bases for difficulty: {difficulty}")
            return recipe_bases
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting recipe bases by difficulty: {e}")
            raise

    @inject_session
    def get_popular_recipe_bases(self, session: Session, limit: int = 100, offset: int = 0) -> List[RecipeBase]:
        """
        인기 레시피 베이스들을 조회합니다.

        Args:
            session: 데이터베이스 세션
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            레시피 베이스 객체 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            recipe_bases = self.recipe_base_repository.find_popular(session, limit, offset)
            
            logger.debug(f"Found {len(recipe_bases)} popular recipe bases")
            return recipe_bases
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting popular recipe bases: {e}")
            raise

    @transactional
    def delete_recipe_base(self, session: Session, recipe_base_id: int) -> bool:
        """
        레시피 베이스를 삭제합니다.
        CASCADE 설정으로 관련 정보들도 함께 삭제됩니다.

        Args:
            session: 데이터베이스 세션
            recipe_base_id: 레시피 베이스 ID

        Returns:
            삭제 성공 여부

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            recipe_base = self.recipe_base_repository.find_by_id(session, recipe_base_id)
            
            if not recipe_base:
                logger.warning(f"Recipe base not found for deletion: {recipe_base_id}")
                return False
            
            result = self.recipe_base_repository.delete(session, recipe_base)
            
            logger.info(f"Recipe base deleted: {recipe_base_id}")
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Error deleting recipe base: {e}")
            raise

    @transactional
    def update_recipe_base(self, session: Session, dto: UpdateRecipeBaseDto) -> Optional[RecipeBase]:
        """
        레시피 베이스 정보를 수정합니다.
        여러 테이블에 분산된 정보를 업데이트합니다.

        Args:
            session: 데이터베이스 세션
            dto: 레시피 베이스 수정 데이터 전송 객체

        Returns:
            수정된 레시피 베이스 객체 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            recipe_base = session.query(RecipeBase).options(
                joinedload(RecipeBase.contents),
                joinedload(RecipeBase.status)
            ).filter(RecipeBase.recipe_base_id == dto.recipe_base_id).first()
            
            if not recipe_base:
                logger.warning(f"Recipe base not found for update: {dto.recipe_base_id}")
                return None
            
            update_fields = dto.get_update_fields()
            updated_sections = []
            
            # 기본 정보 업데이트
            base_fields = ['thumbnail', 'referrer', 'metadata', 'servings', 'difficulty', 'estimated_time']
            if any(field in update_fields for field in base_fields):
                for field in base_fields:
                    if field in update_fields:
                        setattr(recipe_base, field, update_fields[field])
                
                recipe_base.updated_at = datetime.utcnow()
                updated_sections.append('base')
            
            # 컨텐츠 정보 업데이트
            content_fields = ['title', 'author', 'ingredients', 'stages', 'language', 'model_name']
            if any(field in update_fields for field in content_fields):
                # 컨텐츠가 없으면 생성
                if not recipe_base.contents:
                    content = RecipeBaseContent(
                        recipe_base_id=recipe_base.recipe_base_id,
                        title=update_fields.get('title', ''),
                        language=update_fields.get('language', RecipeLanguage.ko),
                        model_name=update_fields.get('model_name', 'default')
                    )
                    session.add(content)
                    recipe_base.contents = [content]
                
                # 첫 번째 컨텐츠 업데이트
                content = recipe_base.contents[0]
                for field in content_fields:
                    if field in update_fields:
                        setattr(content, field, update_fields[field])
                
                content.updated_at = datetime.utcnow()
                updated_sections.append('content')
                
                # 재료가 업데이트된 경우 태그 재생성
                if 'ingredients' in update_fields and update_fields['ingredients']:
                    self._create_ingredient_tags(
                        session,
                        update_fields['ingredients']
                    )
            
            if updated_sections:
                session.flush()
                logger.info(f"Recipe base updated: {dto.recipe_base_id}, sections: {updated_sections}")
            else:
                logger.debug(f"No valid fields to update for recipe base: {dto.recipe_base_id}")
            
            return recipe_base
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating recipe base: {e}")
            raise

    @transactional
    def increment_view_count(self, session: Session, recipe_base_id: int) -> Optional[RecipeBase]:
        """
        레시피 베이스의 조회수를 증가시킵니다.

        Args:
            session: 데이터베이스 세션
            recipe_base_id: 레시피 베이스 ID

        Returns:
            수정된 레시피 베이스 객체 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            recipe_base = self.recipe_base_repository.find_by_id(session, recipe_base_id)
            
            if not recipe_base:
                logger.warning(f"Recipe base not found for view count increment: {recipe_base_id}")
                return None
            
            recipe_base = self.recipe_base_repository.increment_view_count(session, recipe_base)
            
            logger.debug(f"Recipe base view count incremented: {recipe_base_id}")
            return recipe_base
            
        except SQLAlchemyError as e:
            logger.error(f"Error incrementing recipe base view count: {e}")
            raise

    @inject_session
    def get_all_recipe_bases(self, session: Session, limit: int = 100, offset: int = 0) -> List[RecipeBase]:
        """
        모든 레시피 베이스를 조회합니다.

        Args:
            session: 데이터베이스 세션
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            레시피 베이스 객체 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            recipe_bases = self.recipe_base_repository.find_all(session, limit, offset)
            
            logger.debug(f"Found {len(recipe_bases)} recipe bases")
            return recipe_bases
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting all recipe bases: {e}")
            raise

    @inject_session
    def get_recipe_base_count(self, session: Session) -> int:
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
            count = self.recipe_base_repository.count(session)
            
            logger.debug(f"Total recipe base count: {count}")
            return count
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting recipe base count: {e}")
            raise

    @inject_session
    def get_recipe_base_statistics(self, session: Session) -> Dict[str, Any]:
        """
        레시피 베이스 통계 정보를 조회합니다.

        Args:
            session: 데이터베이스 세션

        Returns:
            레시피 베이스 통계 정보

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            # 총 레시피 베이스 수
            total_bases = session.query(func.count(RecipeBase.recipe_base_id)).scalar()
            
            # 난이도별 통계
            difficulty_stats = session.query(
                RecipeBase.difficulty,
                func.count(RecipeBase.recipe_base_id).label('count')
            ).group_by(RecipeBase.difficulty).all()
            
            # 언어별 통계
            language_stats = session.query(
                RecipeBaseContent.language,
                func.count(RecipeBaseContent.recipe_base_content_id).label('count')
            ).group_by(RecipeBaseContent.language).all()
            
            # 상태별 통계
            status_stats = session.query(
                RecipeBaseStatus.state,
                func.count(RecipeBaseStatus.recipe_base_id).label('count')
            ).group_by(RecipeBaseStatus.state).all()
            
            # 조회수 통계
            view_stats = session.query(
                func.avg(RecipeBase.view_count).label('avg_views'),
                func.max(RecipeBase.view_count).label('max_views'),
                func.min(RecipeBase.view_count).label('min_views')
            ).first()
            
            statistics = {
                'total_recipe_bases': total_bases,
                'by_difficulty': {stat.difficulty: stat.count for stat in difficulty_stats if stat.difficulty},
                'by_language': {stat.language: stat.count for stat in language_stats},
                'by_status': {stat.state: stat.count for stat in status_stats},
                'view_statistics': {
                    'average_views': float(view_stats.avg_views) if view_stats and view_stats.avg_views else 0,
                    'max_views': view_stats.max_views if view_stats else 0,
                    'min_views': view_stats.min_views if view_stats else 0
                }
            }
            
            logger.debug(f"Recipe base statistics calculated: {statistics}")
            return statistics
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting recipe base statistics: {e}")
            raise

    @inject_session
    def search_recipe_bases(self, session: Session, dto: SearchRecipeBasesDto) -> List[RecipeBase]:
        """
        다양한 조건으로 레시피 베이스를 검색합니다.

        Args:
            session: 데이터베이스 세션
            dto: 레시피 베이스 검색 데이터 전송 객체

        Returns:
            검색된 레시피 베이스 객체 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            query = session.query(RecipeBase).options(
                joinedload(RecipeBase.contents),
                joinedload(RecipeBase.status)
            )
            
            # 기본 정보 필터
            if dto.difficulty:
                query = query.filter(RecipeBase.difficulty == dto.difficulty)
            if dto.servings:
                query = query.filter(RecipeBase.servings == dto.servings)
            
            # 컨텐츠 정보 필터
            if dto.title or dto.author or dto.language:
                query = query.join(RecipeBaseContent)
                if dto.title:
                    query = query.filter(RecipeBaseContent.title.ilike(f"%{dto.title}%"))
                if dto.author:
                    query = query.filter(RecipeBaseContent.author.ilike(f"%{dto.author}%"))
                if dto.language:
                    query = query.filter(RecipeBaseContent.language == dto.language)
            
            # 재료 검색 (태그 테이블 사용)
            if dto.ingredient:
                # TODO: 재료 검색 로직 추가
                # full text search 사용
                pass
            
            recipe_bases = query.offset(dto.offset).limit(dto.limit).all()
            
            logger.debug(f"Found {len(recipe_bases)} recipe bases with search criteria")
            return recipe_bases
            
        except SQLAlchemyError as e:
            logger.error(f"Error searching recipe bases: {e}")
            raise

    @transactional
    def update_recipe_base_status(self, session: Session, recipe_base_id: int, state: RecipeState) -> Optional[RecipeBaseStatus]:
        """
        레시피 베이스의 상태를 업데이트합니다.

        Args:
            session: 데이터베이스 세션
            recipe_base_id: 레시피 베이스 ID
            state: 새로운 상태

        Returns:
            업데이트된 상태 객체 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            status = self.recipe_base_status_repository.find_by_recipe_base_id(session, recipe_base_id)
            
            if not status:
                # 상태가 없으면 새로 생성
                status = RecipeBaseStatus(
                    recipe_base_id=recipe_base_id,
                    state=state
                )
                status = self.recipe_base_status_repository.create(session, status)
            else:
                status.state = state
                status = self.recipe_base_status_repository.update(session, status)
            
            logger.info(f"Recipe base status updated: {recipe_base_id}, state: {state}")
            return status
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating recipe base status: {e}")
            raise

    def _generate_checksum(self, url: str) -> str:
        """URL의 SHA256 해시를 생성합니다."""
        return hashlib.sha256(url.encode('utf-8')).hexdigest() 