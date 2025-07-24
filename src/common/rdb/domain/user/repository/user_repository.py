"""
User Repository

이 모듈은 User 모델에 대한 데이터 접근 계층을 제공합니다.
SQLModel을 최대한 활용하여 타입 안전성과 성능을 보장합니다.
"""

import logging
from typing import Optional, List

from sqlmodel import Session, select, func
from sqlalchemy.exc import SQLAlchemyError

from ..models import User, UserRole, UserProvider

logger = logging.getLogger(__name__)


class UserRepository:
    """User 모델에 대한 SQLModel 최적화 Repository 클래스"""

    def create(self, session: Session, user: User) -> User:
        """
        새로운 사용자를 생성합니다.

        Args:
            session: SQLModel 세션
            user: 생성할 사용자 객체

        Returns:
            생성된 사용자 객체

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.add(user)
            session.flush()
            session.refresh(user)
            logger.debug(f"User created: {user.user_id}")
            return user
        except SQLAlchemyError as e:
            logger.error(f"Error creating user: {e}")
            raise

    def find_by_id(self, session: Session, user_id: str) -> Optional[User]:
        """
        ID로 사용자를 조회합니다.

        Args:
            session: SQLModel 세션
            user_id: 사용자 ID

        Returns:
            사용자 객체 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(User).where(User.user_id == user_id)
            result = session.exec(statement).first()
            
            if result:
                logger.debug(f"User found: {user_id}")
            else:
                logger.debug(f"User not found: {user_id}")
                
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error finding user by ID: {e}")
            raise

    def find_by_openid(self, session: Session, openid: str) -> Optional[User]:
        """
        OAuth OpenID로 사용자를 조회합니다.

        Args:
            session: SQLModel 세션
            openid: OAuth OpenID

        Returns:
            사용자 객체 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(User).where(User.openid == openid)
            result = session.exec(statement).first()
            
            if result:
                logger.debug(f"User found by openid: {openid}")
            else:
                logger.debug(f"User not found by openid: {openid}")
                
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error finding user by openid: {e}")
            raise

    def find_by_provider(self, session: Session, provider: UserProvider, limit: int = 100, offset: int = 0) -> List[User]:
        """
        인증 제공자별로 사용자를 조회합니다.

        Args:
            session: SQLModel 세션
            provider: 인증 제공자
            limit: 조회할 최대 개수
            offset: 건너뛸 개수

        Returns:
            사용자 객체 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = (
                select(User)
                .where(User.provider == provider)
                .limit(limit)
                .offset(offset)
                .order_by(User.created_at.desc())
            )
            result = session.exec(statement).all()
            
            logger.debug(f"Found {len(result)} users for provider: {provider}")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error finding users by provider: {e}")
            raise

    def find_by_role(self, session: Session, role: UserRole, limit: int = 100, offset: int = 0) -> List[User]:
        """
        역할별로 사용자를 조회합니다.

        Args:
            session: SQLModel 세션
            role: 사용자 역할
            limit: 조회할 최대 개수
            offset: 건너뛸 개수

        Returns:
            사용자 객체 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = (
                select(User)
                .where(User.role == role)
                .limit(limit)
                .offset(offset)
                .order_by(User.created_at.desc())
            )
            result = session.exec(statement).all()
            
            logger.debug(f"Found {len(result)} users for role: {role}")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error finding users by role: {e}")
            raise

    def update(self, session: Session, user: User) -> User:
        """
        사용자 정보를 업데이트합니다.

        Args:
            session: SQLModel 세션
            user: 업데이트할 사용자 객체

        Returns:
            업데이트된 사용자 객체

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.add(user)
            session.flush()
            session.refresh(user)
            logger.debug(f"User updated: {user.user_id}")
            return user
        except SQLAlchemyError as e:
            logger.error(f"Error updating user: {e}")
            raise

    def delete(self, session: Session, user: User) -> bool:
        """
        사용자를 삭제합니다.

        Args:
            session: SQLModel 세션
            user: 삭제할 사용자 객체

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

    def find_all(self, session: Session, limit: int = 100, offset: int = 0) -> List[User]:
        """
        모든 사용자를 조회합니다.

        Args:
            session: SQLModel 세션
            limit: 조회할 최대 개수
            offset: 건너뛸 개수

        Returns:
            사용자 객체 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = (
                select(User)
                .limit(limit)
                .offset(offset)
                .order_by(User.created_at.desc())
            )
            result = session.exec(statement).all()
            
            logger.debug(f"Found {len(result)} users")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error finding all users: {e}")
            raise

    def count(self, session: Session) -> int:
        """
        전체 사용자 수를 조회합니다.

        Args:
            session: SQLModel 세션

        Returns:
            사용자 수

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(func.count(User.user_id))
            result = session.exec(statement).one()
            
            logger.debug(f"Total user count: {result}")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error counting users: {e}")
            raise

    def count_by_provider(self, session: Session, provider: UserProvider) -> int:
        """
        인증 제공자별 사용자 수를 조회합니다.

        Args:
            session: SQLModel 세션
            provider: 인증 제공자

        Returns:
            사용자 수

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(func.count(User.user_id)).where(User.provider == provider)
            result = session.exec(statement).one()
            
            logger.debug(f"User count for provider {provider}: {result}")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error counting users by provider: {e}")
            raise

    def count_by_role(self, session: Session, role: UserRole) -> int:
        """
        역할별 사용자 수를 조회합니다.

        Args:
            session: SQLModel 세션
            role: 사용자 역할

        Returns:
            사용자 수

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(func.count(User.user_id)).where(User.role == role)
            result = session.exec(statement).one()
            
            logger.debug(f"User count for role {role}: {result}")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error counting users by role: {e}")
            raise

    def exists_by_id(self, session: Session, user_id: str) -> bool:
        """
        ID로 사용자 존재 여부를 확인합니다.

        Args:
            session: SQLModel 세션
            user_id: 사용자 ID

        Returns:
            존재 여부

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(func.count(User.user_id)).where(User.user_id == user_id)
            result = session.exec(statement).one()
            
            exists = result > 0
            logger.debug(f"User exists by ID {user_id}: {exists}")
            return exists
        except SQLAlchemyError as e:
            logger.error(f"Error checking user existence by ID: {e}")
            raise

    def exists_by_openid(self, session: Session, openid: str) -> bool:
        """
        OpenID로 사용자 존재 여부를 확인합니다.

        Args:
            session: SQLModel 세션
            openid: OAuth OpenID

        Returns:
            존재 여부

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(func.count(User.user_id)).where(User.openid == openid)
            result = session.exec(statement).one()
            
            exists = result > 0
            logger.debug(f"User exists by openid {openid}: {exists}")
            return exists
        except SQLAlchemyError as e:
            logger.error(f"Error checking user existence by openid: {e}")
            raise

    def find_recent(self, session: Session, limit: int = 100) -> List[User]:
        """
        최근 생성된 사용자를 조회합니다.

        Args:
            session: SQLModel 세션
            limit: 조회할 최대 개수

        Returns:
            사용자 객체 리스트 (최신순)

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = (
                select(User)
                .order_by(User.created_at.desc())
                .limit(limit)
            )
            result = session.exec(statement).all()
            
            logger.debug(f"Found {len(result)} recent users")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error finding recent users: {e}")
            raise 