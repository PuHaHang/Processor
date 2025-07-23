"""
UserBilling Repository

이 모듈은 UserBilling 모델의 기본 CRUD 작업을 담당하는 Repository 클래스를 제공합니다.
"""

from typing import Optional, List
from datetime import datetime

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, func

from ..models import UserBilling, UserBillingType
from ....common.dependency_injection import inject_session, transactional

import logging

logger = logging.getLogger(__name__)


class UserBillingRepository:
    """UserBilling 모델 기본 CRUD 작업을 담당하는 Repository"""

    @transactional
    def create(self, session: Session, user_billing: UserBilling) -> UserBilling:
        """
        새로운 사용자 결제 정보를 생성합니다.

        Args:
            session: 데이터베이스 세션
            user_billing: 생성할 사용자 결제 정보 엔티티

        Returns:
            생성된 사용자 결제 정보 엔티티

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.add(user_billing)
            session.flush()
            
            logger.debug(f"User billing created: {user_billing.user_id}")
            return user_billing
            
        except SQLAlchemyError as e:
            logger.error(f"Error creating user billing: {e}")
            raise

    @inject_session
    def find_by_user_id(self, session: Session, user_id: str) -> Optional[UserBilling]:
        """
        사용자 ID로 결제 정보를 조회합니다.

        Args:
            session: 데이터베이스 세션
            user_id: 사용자 ID

        Returns:
            사용자 결제 정보 엔티티 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            billing = session.query(UserBilling).options(
                joinedload(UserBilling.user)
            ).filter(UserBilling.user_id == user_id).first()
            
            if billing:
                logger.debug(f"User billing found: {user_id}")
            else:
                logger.debug(f"User billing not found: {user_id}")
                
            return billing
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding user billing by user ID: {e}")
            raise

    @inject_session
    def find_by_billing_type(self, session: Session, billing_type: UserBillingType, limit: int = 100, offset: int = 0) -> List[UserBilling]:
        """
        결제 플랜으로 결제 정보들을 조회합니다.

        Args:
            session: 데이터베이스 세션
            billing_type: 결제 플랜
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            사용자 결제 정보 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            billings = session.query(UserBilling).options(
                joinedload(UserBilling.user)
            ).filter(
                UserBilling.billing == billing_type
            ).offset(offset).limit(limit).all()
            
            logger.debug(f"Found {len(billings)} user billings for billing type: {billing_type}")
            return billings
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding user billings by billing type: {e}")
            raise

    @transactional
    def update(self, session: Session, user_billing: UserBilling) -> UserBilling:
        """
        사용자 결제 정보를 업데이트합니다.

        Args:
            session: 데이터베이스 세션
            user_billing: 업데이트할 사용자 결제 정보 엔티티

        Returns:
            업데이트된 사용자 결제 정보 엔티티

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            user_billing.updated_at = datetime.utcnow()
            session.merge(user_billing)
            session.flush()
            
            logger.debug(f"User billing updated: {user_billing.user_id}")
            return user_billing
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating user billing: {e}")
            raise

    @transactional
    def delete(self, session: Session, user_billing: UserBilling) -> bool:
        """
        사용자 결제 정보를 삭제합니다.

        Args:
            session: 데이터베이스 세션
            user_billing: 삭제할 사용자 결제 정보 엔티티

        Returns:
            삭제 성공 여부

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.delete(user_billing)
            session.flush()
            
            logger.debug(f"User billing deleted: {user_billing.user_id}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error deleting user billing: {e}")
            raise

    @inject_session
    def find_all(self, session: Session, limit: int = 100, offset: int = 0) -> List[UserBilling]:
        """
        모든 사용자 결제 정보를 조회합니다.

        Args:
            session: 데이터베이스 세션
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            사용자 결제 정보 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            billings = session.query(UserBilling).options(
                joinedload(UserBilling.user)
            ).offset(offset).limit(limit).all()
            
            logger.debug(f"Found {len(billings)} user billings")
            return billings
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding all user billings: {e}")
            raise

    @inject_session
    def count(self, session: Session) -> int:
        """
        전체 사용자 결제 정보 수를 조회합니다.

        Args:
            session: 데이터베이스 세션

        Returns:
            전체 사용자 결제 정보 수

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            count = session.query(func.count(UserBilling.user_id)).scalar()
            
            logger.debug(f"Total user billing count: {count}")
            return count
            
        except SQLAlchemyError as e:
            logger.error(f"Error counting user billings: {e}")
            raise

    @inject_session
    def count_by_billing_type(self, session: Session, billing_type: UserBillingType) -> int:
        """
        특정 결제 플랜의 사용자 수를 조회합니다.

        Args:
            session: 데이터베이스 세션
            billing_type: 결제 플랜

        Returns:
            특정 결제 플랜의 사용자 수

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            count = session.query(func.count(UserBilling.user_id)).filter(
                UserBilling.billing == billing_type
            ).scalar()
            
            logger.debug(f"User billing count for type {billing_type}: {count}")
            return count
            
        except SQLAlchemyError as e:
            logger.error(f"Error counting user billings by type: {e}")
            raise 