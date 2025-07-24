"""
User Billing Repository

이 모듈은 UserBilling 모델에 대한 데이터 접근 계층을 제공합니다.
SQLModel을 최대한 활용하여 타입 안전성과 성능을 보장합니다.
"""

import logging
from typing import Optional, List

from sqlmodel import Session, select, func
from sqlalchemy.exc import SQLAlchemyError

from ..models import UserBilling, UserBillingType

logger = logging.getLogger(__name__)


class UserBillingRepository:
    """UserBilling 모델에 대한 SQLModel 최적화 Repository 클래스"""

    def create(self, session: Session, billing: UserBilling) -> UserBilling:
        """
        새로운 사용자 결제 정보를 생성합니다.

        Args:
            session: SQLModel 세션
            billing: 생성할 결제 정보 객체

        Returns:
            생성된 결제 정보 객체

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.add(billing)
            session.flush()
            session.refresh(billing)
            logger.debug(f"UserBilling created for user: {billing.user_id}")
            return billing
        except SQLAlchemyError as e:
            logger.error(f"Error creating user billing: {e}")
            raise

    def find_by_user_id(self, session: Session, user_id: str) -> Optional[UserBilling]:
        """
        사용자 ID로 결제 정보를 조회합니다.

        Args:
            session: SQLModel 세션
            user_id: 사용자 ID

        Returns:
            결제 정보 객체 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(UserBilling).where(UserBilling.user_id == user_id)
            result = session.exec(statement).first()
            
            if result:
                logger.debug(f"UserBilling found for user: {user_id}")
            else:
                logger.debug(f"UserBilling not found for user: {user_id}")
                
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error finding user billing by user ID: {e}")
            raise

    def find_by_billing_type(self, session: Session, billing_type: UserBillingType, limit: int = 100, offset: int = 0) -> List[UserBilling]:
        """
        결제 플랜별로 사용자를 조회합니다.

        Args:
            session: SQLModel 세션
            billing_type: 결제 플랜 타입
            limit: 조회할 최대 개수
            offset: 건너뛸 개수

        Returns:
            결제 정보 객체 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = (
                select(UserBilling)
                .where(UserBilling.billing == billing_type)
                .limit(limit)
                .offset(offset)
                .order_by(UserBilling.created_at.desc())
            )
            result = session.exec(statement).all()
            
            logger.debug(f"Found {len(result)} users for billing type: {billing_type}")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error finding user billings by billing type: {e}")
            raise

    def update(self, session: Session, billing: UserBilling) -> UserBilling:
        """
        결제 정보를 업데이트합니다.

        Args:
            session: SQLModel 세션
            billing: 업데이트할 결제 정보 객체

        Returns:
            업데이트된 결제 정보 객체

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.add(billing)
            session.flush()
            session.refresh(billing)
            logger.debug(f"UserBilling updated for user: {billing.user_id}")
            return billing
        except SQLAlchemyError as e:
            logger.error(f"Error updating user billing: {e}")
            raise

    def delete(self, session: Session, billing: UserBilling) -> bool:
        """
        결제 정보를 삭제합니다.

        Args:
            session: SQLModel 세션
            billing: 삭제할 결제 정보 객체

        Returns:
            삭제 성공 여부

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.delete(billing)
            session.flush()
            logger.debug(f"UserBilling deleted for user: {billing.user_id}")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error deleting user billing: {e}")
            raise

    def find_all(self, session: Session, limit: int = 100, offset: int = 0) -> List[UserBilling]:
        """
        모든 결제 정보를 조회합니다.

        Args:
            session: SQLModel 세션
            limit: 조회할 최대 개수
            offset: 건너뛸 개수

        Returns:
            결제 정보 객체 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = (
                select(UserBilling)
                .limit(limit)
                .offset(offset)
                .order_by(UserBilling.created_at.desc())
            )
            result = session.exec(statement).all()
            
            logger.debug(f"Found {len(result)} user billings")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error finding all user billings: {e}")
            raise

    def count(self, session: Session) -> int:
        """
        전체 결제 정보 수를 조회합니다.

        Args:
            session: SQLModel 세션

        Returns:
            결제 정보 수

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(func.count(UserBilling.user_id))
            result = session.exec(statement).one()
            
            logger.debug(f"Total user billing count: {result}")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error counting user billings: {e}")
            raise

    def count_by_billing_type(self, session: Session, billing_type: UserBillingType) -> int:
        """
        결제 플랜별 사용자 수를 조회합니다.

        Args:
            session: SQLModel 세션
            billing_type: 결제 플랜 타입

        Returns:
            사용자 수

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(func.count(UserBilling.user_id)).where(UserBilling.billing == billing_type)
            result = session.exec(statement).one()
            
            logger.debug(f"User count for billing type {billing_type}: {result}")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error counting users by billing type: {e}")
            raise 