"""
User Repository

이 모듈은 User 모델의 기본 CRUD 작업을 담당하는 Repository 클래스를 제공합니다.
Repository 패턴을 통해 데이터 접근 로직을 분리하고 서비스 계층에서 조합하여 사용합니다.
"""

from typing import Optional, List
from datetime import datetime

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, func

from ..models import User, UserRole, UserProvider
from ....common.dependency_injection import inject_session, transactional

import logging

logger = logging.getLogger(__name__)


class UserRepository:
    """User 모델 기본 CRUD 작업을 담당하는 Repository"""

    @transactional
    def create(self, session: Session, user: User) -> User:
        """
        새로운 사용자를 생성합니다.

        Args:
            session: 데이터베이스 세션
            user: 생성할 사용자 엔티티

        Returns:
            생성된 사용자 엔티티

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.add(user)
            session.flush()
            
            logger.debug(f"User created: {user.user_id}")
            return user
            
        except SQLAlchemyError as e:
            logger.error(f"Error creating user: {e}")
            raise

    @inject_session
    def find_by_id(self, session: Session, user_id: str) -> Optional[User]:
        """
        ID로 사용자를 조회합니다.

        Args:
            session: 데이터베이스 세션
            user_id: 사용자 ID

        Returns:
            사용자 엔티티 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            user = session.query(User).options(
                joinedload(User.profile),
                joinedload(User.billing),
                joinedload(User.alert)
            ).filter(User.user_id == user_id).first()
            
            if user:
                logger.debug(f"User found: {user_id}")
            else:
                logger.debug(f"User not found: {user_id}")
                
            return user
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding user by ID: {e}")
            raise

    @inject_session
    def find_by_openid(self, session: Session, openid: str) -> Optional[User]:
        """
        OpenID로 사용자를 조회합니다.

        Args:
            session: 데이터베이스 세션
            openid: OAuth2.0 식별자

        Returns:
            사용자 엔티티 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            user = session.query(User).options(
                joinedload(User.profile),
                joinedload(User.billing),
                joinedload(User.alert)
            ).filter(User.openid == openid).first()
            
            if user:
                logger.debug(f"User found by OpenID: {openid}")
            else:
                logger.debug(f"User not found by OpenID: {openid}")
                
            return user
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding user by OpenID: {e}")
            raise

    @inject_session
    def find_by_provider(self, session: Session, provider: UserProvider, limit: int = 100, offset: int = 0) -> List[User]:
        """
        제공자로 사용자들을 조회합니다.

        Args:
            session: 데이터베이스 세션
            provider: 인증 제공자
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            사용자 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            users = session.query(User).options(
                joinedload(User.profile),
                joinedload(User.billing),
                joinedload(User.alert)
            ).filter(
                User.provider == provider
            ).offset(offset).limit(limit).all()
            
            logger.debug(f"Found {len(users)} users for provider: {provider}")
            return users
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding users by provider: {e}")
            raise

    @inject_session
    def find_by_role(self, session: Session, role: UserRole, limit: int = 100, offset: int = 0) -> List[User]:
        """
        역할로 사용자들을 조회합니다.

        Args:
            session: 데이터베이스 세션
            role: 사용자 역할
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            사용자 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            users = session.query(User).options(
                joinedload(User.profile),
                joinedload(User.billing),
                joinedload(User.alert)
            ).filter(
                User.role == role
            ).offset(offset).limit(limit).all()
            
            logger.debug(f"Found {len(users)} users for role: {role}")
            return users
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding users by role: {e}")
            raise

    @transactional
    def update(self, session: Session, user: User) -> User:
        """
        사용자 정보를 업데이트합니다.

        Args:
            session: 데이터베이스 세션
            user: 업데이트할 사용자 엔티티

        Returns:
            업데이트된 사용자 엔티티

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.merge(user)
            session.flush()
            
            logger.debug(f"User updated: {user.user_id}")
            return user
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating user: {e}")
            raise

    @transactional
    def delete(self, session: Session, user: User) -> bool:
        """
        사용자를 삭제합니다.

        Args:
            session: 데이터베이스 세션
            user: 삭제할 사용자 엔티티

        Returns:
            삭제 성공 여부

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.delete(user)
            session.flush()
            
            logger.debug(f"User deleted: {user.user_id}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error deleting user: {e}")
            raise

    @inject_session
    def find_all(self, session: Session, limit: int = 100, offset: int = 0) -> List[User]:
        """
        모든 사용자를 조회합니다.

        Args:
            session: 데이터베이스 세션
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            사용자 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            users = session.query(User).options(
                joinedload(User.profile),
                joinedload(User.billing),
                joinedload(User.alert)
            ).offset(offset).limit(limit).all()
            
            logger.debug(f"Found {len(users)} users")
            return users
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding all users: {e}")
            raise

    @inject_session
    def count(self, session: Session) -> int:
        """
        전체 사용자 수를 조회합니다.

        Args:
            session: 데이터베이스 세션

        Returns:
            전체 사용자 수

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            count = session.query(func.count(User.user_id)).scalar()
            
            logger.debug(f"Total user count: {count}")
            return count
            
        except SQLAlchemyError as e:
            logger.error(f"Error counting users: {e}")
            raise

    @inject_session
    def exists_by_id(self, session: Session, user_id: str) -> bool:
        """
        사용자 ID로 존재 여부를 확인합니다.

        Args:
            session: 데이터베이스 세션
            user_id: 사용자 ID

        Returns:
            존재 여부

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            exists = session.query(User).filter(User.user_id == user_id).first() is not None
            
            logger.debug(f"User exists: {user_id} -> {exists}")
            return exists
            
        except SQLAlchemyError as e:
            logger.error(f"Error checking user existence: {e}")
            raise

    @inject_session
    def exists_by_openid(self, session: Session, openid: str) -> bool:
        """
        OpenID로 존재 여부를 확인합니다.

        Args:
            session: 데이터베이스 세션
            openid: OAuth2.0 식별자

        Returns:
            존재 여부

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            exists = session.query(User).filter(User.openid == openid).first() is not None
            
            logger.debug(f"User exists by OpenID: {openid} -> {exists}")
            return exists
            
        except SQLAlchemyError as e:
            logger.error(f"Error checking user existence by OpenID: {e}")
            raise 