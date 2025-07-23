"""
UserProfile Repository

이 모듈은 UserProfile 모델의 기본 CRUD 작업을 담당하는 Repository 클래스를 제공합니다.
"""

from typing import Optional, List
from datetime import datetime

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, func

from ..models import UserProfile, UserRegion
from ....common.dependency_injection import inject_session, transactional

import logging

logger = logging.getLogger(__name__)


class UserProfileRepository:
    """UserProfile 모델 기본 CRUD 작업을 담당하는 Repository"""

    @transactional
    def create(self, session: Session, user_profile: UserProfile) -> UserProfile:
        """
        새로운 사용자 프로필을 생성합니다.

        Args:
            session: 데이터베이스 세션
            user_profile: 생성할 사용자 프로필 엔티티

        Returns:
            생성된 사용자 프로필 엔티티

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.add(user_profile)
            session.flush()
            
            logger.debug(f"User profile created: {user_profile.user_id}")
            return user_profile
            
        except SQLAlchemyError as e:
            logger.error(f"Error creating user profile: {e}")
            raise

    @inject_session
    def find_by_user_id(self, session: Session, user_id: str) -> Optional[UserProfile]:
        """
        사용자 ID로 프로필을 조회합니다.

        Args:
            session: 데이터베이스 세션
            user_id: 사용자 ID

        Returns:
            사용자 프로필 엔티티 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            profile = session.query(UserProfile).options(
                joinedload(UserProfile.user)
            ).filter(UserProfile.user_id == user_id).first()
            
            if profile:
                logger.debug(f"User profile found: {user_id}")
            else:
                logger.debug(f"User profile not found: {user_id}")
                
            return profile
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding user profile by user ID: {e}")
            raise

    @inject_session
    def find_by_nickname(self, session: Session, nickname: str) -> Optional[UserProfile]:
        """
        닉네임으로 프로필을 조회합니다.

        Args:
            session: 데이터베이스 세션
            nickname: 사용자 닉네임

        Returns:
            사용자 프로필 엔티티 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            profile = session.query(UserProfile).options(
                joinedload(UserProfile.user)
            ).filter(UserProfile.nickname == nickname).first()
            
            if profile:
                logger.debug(f"User profile found by nickname: {nickname}")
            else:
                logger.debug(f"User profile not found by nickname: {nickname}")
                
            return profile
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding user profile by nickname: {e}")
            raise

    @inject_session
    def find_by_region(self, session: Session, region: UserRegion, limit: int = 100, offset: int = 0) -> List[UserProfile]:
        """
        지역으로 프로필들을 조회합니다.

        Args:
            session: 데이터베이스 세션
            region: 사용자 지역
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            사용자 프로필 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            profiles = session.query(UserProfile).options(
                joinedload(UserProfile.user)
            ).filter(
                UserProfile.region == region
            ).offset(offset).limit(limit).all()
            
            logger.debug(f"Found {len(profiles)} user profiles for region: {region}")
            return profiles
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding user profiles by region: {e}")
            raise

    @inject_session
    def search_by_nickname(self, session: Session, nickname_pattern: str, limit: int = 100, offset: int = 0) -> List[UserProfile]:
        """
        닉네임 패턴으로 프로필들을 검색합니다.

        Args:
            session: 데이터베이스 세션
            nickname_pattern: 검색할 닉네임 패턴
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            사용자 프로필 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            profiles = session.query(UserProfile).options(
                joinedload(UserProfile.user)
            ).filter(
                UserProfile.nickname.ilike(f"%{nickname_pattern}%")
            ).offset(offset).limit(limit).all()
            
            logger.debug(f"Found {len(profiles)} user profiles for nickname pattern: {nickname_pattern}")
            return profiles
            
        except SQLAlchemyError as e:
            logger.error(f"Error searching user profiles by nickname: {e}")
            raise

    @transactional
    def update(self, session: Session, user_profile: UserProfile) -> UserProfile:
        """
        사용자 프로필을 업데이트합니다.

        Args:
            session: 데이터베이스 세션
            user_profile: 업데이트할 사용자 프로필 엔티티

        Returns:
            업데이트된 사용자 프로필 엔티티

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            user_profile.updated_at = datetime.utcnow()
            session.merge(user_profile)
            session.flush()
            
            logger.debug(f"User profile updated: {user_profile.user_id}")
            return user_profile
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating user profile: {e}")
            raise

    @transactional
    def delete(self, session: Session, user_profile: UserProfile) -> bool:
        """
        사용자 프로필을 삭제합니다.

        Args:
            session: 데이터베이스 세션
            user_profile: 삭제할 사용자 프로필 엔티티

        Returns:
            삭제 성공 여부

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.delete(user_profile)
            session.flush()
            
            logger.debug(f"User profile deleted: {user_profile.user_id}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error deleting user profile: {e}")
            raise

    @inject_session
    def find_all(self, session: Session, limit: int = 100, offset: int = 0) -> List[UserProfile]:
        """
        모든 사용자 프로필을 조회합니다.

        Args:
            session: 데이터베이스 세션
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            사용자 프로필 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            profiles = session.query(UserProfile).options(
                joinedload(UserProfile.user)
            ).offset(offset).limit(limit).all()
            
            logger.debug(f"Found {len(profiles)} user profiles")
            return profiles
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding all user profiles: {e}")
            raise

    @inject_session
    def count(self, session: Session) -> int:
        """
        전체 사용자 프로필 수를 조회합니다.

        Args:
            session: 데이터베이스 세션

        Returns:
            전체 사용자 프로필 수

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            count = session.query(func.count(UserProfile.user_id)).scalar()
            
            logger.debug(f"Total user profile count: {count}")
            return count
            
        except SQLAlchemyError as e:
            logger.error(f"Error counting user profiles: {e}")
            raise

    @inject_session
    def exists_by_nickname(self, session: Session, nickname: str) -> bool:
        """
        닉네임으로 존재 여부를 확인합니다.

        Args:
            session: 데이터베이스 세션
            nickname: 사용자 닉네임

        Returns:
            존재 여부

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            exists = session.query(UserProfile).filter(UserProfile.nickname == nickname).first() is not None
            
            logger.debug(f"User profile exists by nickname: {nickname} -> {exists}")
            return exists
            
        except SQLAlchemyError as e:
            logger.error(f"Error checking user profile existence by nickname: {e}")
            raise 