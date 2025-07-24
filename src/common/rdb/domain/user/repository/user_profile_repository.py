"""
User Profile Repository

이 모듈은 UserProfile 모델에 대한 데이터 접근 계층을 제공합니다.
SQLModel을 최대한 활용하여 타입 안전성과 성능을 보장합니다.
"""

import logging
from typing import Optional, List

from sqlmodel import Session, select, func
from sqlalchemy.exc import SQLAlchemyError

from ..models import UserProfile, UserRegion

logger = logging.getLogger(__name__)


class UserProfileRepository:
    """UserProfile 모델에 대한 SQLModel 최적화 Repository 클래스"""

    def create(self, session: Session, profile: UserProfile) -> UserProfile:
        """
        새로운 사용자 프로필을 생성합니다.

        Args:
            session: SQLModel 세션
            profile: 생성할 프로필 객체

        Returns:
            생성된 프로필 객체

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.add(profile)
            session.flush()
            session.refresh(profile)
            logger.debug(f"UserProfile created for user: {profile.user_id}")
            return profile
        except SQLAlchemyError as e:
            logger.error(f"Error creating user profile: {e}")
            raise

    def find_by_user_id(self, session: Session, user_id: str) -> Optional[UserProfile]:
        """
        사용자 ID로 프로필을 조회합니다.

        Args:
            session: SQLModel 세션
            user_id: 사용자 ID

        Returns:
            프로필 객체 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(UserProfile).where(UserProfile.user_id == user_id)
            result = session.exec(statement).first()
            
            if result:
                logger.debug(f"UserProfile found for user: {user_id}")
            else:
                logger.debug(f"UserProfile not found for user: {user_id}")
                
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error finding user profile by user ID: {e}")
            raise

    def find_by_nickname(self, session: Session, nickname: str) -> Optional[UserProfile]:
        """
        닉네임으로 프로필을 조회합니다.

        Args:
            session: SQLModel 세션
            nickname: 닉네임

        Returns:
            프로필 객체 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(UserProfile).where(UserProfile.nickname == nickname)
            result = session.exec(statement).first()
            
            if result:
                logger.debug(f"UserProfile found by nickname: {nickname}")
            else:
                logger.debug(f"UserProfile not found by nickname: {nickname}")
                
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error finding user profile by nickname: {e}")
            raise

    def find_by_region(self, session: Session, region: UserRegion, limit: int = 100, offset: int = 0) -> List[UserProfile]:
        """
        지역별로 프로필을 조회합니다.

        Args:
            session: SQLModel 세션
            region: 사용자 지역
            limit: 조회할 최대 개수
            offset: 건너뛸 개수

        Returns:
            프로필 객체 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = (
                select(UserProfile)
                .where(UserProfile.region == region)
                .limit(limit)
                .offset(offset)
                .order_by(UserProfile.created_at.desc())
            )
            result = session.exec(statement).all()
            
            logger.debug(f"Found {len(result)} profiles for region: {region}")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error finding user profiles by region: {e}")
            raise

    def search_by_nickname(self, session: Session, nickname_pattern: str, limit: int = 100, offset: int = 0) -> List[UserProfile]:
        """
        닉네임 패턴으로 프로필을 검색합니다.

        Args:
            session: SQLModel 세션
            nickname_pattern: 닉네임 검색 패턴
            limit: 조회할 최대 개수
            offset: 건너뛸 개수

        Returns:
            프로필 객체 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = (
                select(UserProfile)
                .where(UserProfile.nickname.ilike(f"%{nickname_pattern}%"))
                .limit(limit)
                .offset(offset)
                .order_by(UserProfile.created_at.desc())
            )
            result = session.exec(statement).all()
            
            logger.debug(f"Found {len(result)} profiles matching pattern: {nickname_pattern}")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error searching user profiles by nickname: {e}")
            raise

    def update(self, session: Session, profile: UserProfile) -> UserProfile:
        """
        프로필 정보를 업데이트합니다.

        Args:
            session: SQLModel 세션
            profile: 업데이트할 프로필 객체

        Returns:
            업데이트된 프로필 객체

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.add(profile)
            session.flush()
            session.refresh(profile)
            logger.debug(f"UserProfile updated for user: {profile.user_id}")
            return profile
        except SQLAlchemyError as e:
            logger.error(f"Error updating user profile: {e}")
            raise

    def delete(self, session: Session, profile: UserProfile) -> bool:
        """
        프로필을 삭제합니다.

        Args:
            session: SQLModel 세션
            profile: 삭제할 프로필 객체

        Returns:
            삭제 성공 여부

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.delete(profile)
            session.flush()
            logger.debug(f"UserProfile deleted for user: {profile.user_id}")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error deleting user profile: {e}")
            raise

    def find_all(self, session: Session, limit: int = 100, offset: int = 0) -> List[UserProfile]:
        """
        모든 프로필을 조회합니다.

        Args:
            session: SQLModel 세션
            limit: 조회할 최대 개수
            offset: 건너뛸 개수

        Returns:
            프로필 객체 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = (
                select(UserProfile)
                .limit(limit)
                .offset(offset)
                .order_by(UserProfile.created_at.desc())
            )
            result = session.exec(statement).all()
            
            logger.debug(f"Found {len(result)} user profiles")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error finding all user profiles: {e}")
            raise

    def count(self, session: Session) -> int:
        """
        전체 프로필 수를 조회합니다.

        Args:
            session: SQLModel 세션

        Returns:
            프로필 수

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(func.count(UserProfile.user_id))
            result = session.exec(statement).one()
            
            logger.debug(f"Total user profile count: {result}")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error counting user profiles: {e}")
            raise

    def exists_by_nickname(self, session: Session, nickname: str) -> bool:
        """
        닉네임으로 프로필 존재 여부를 확인합니다.

        Args:
            session: SQLModel 세션
            nickname: 닉네임

        Returns:
            존재 여부

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(func.count(UserProfile.user_id)).where(UserProfile.nickname == nickname)
            result = session.exec(statement).one()
            
            exists = result > 0
            logger.debug(f"UserProfile exists by nickname {nickname}: {exists}")
            return exists
        except SQLAlchemyError as e:
            logger.error(f"Error checking user profile existence by nickname: {e}")
            raise 