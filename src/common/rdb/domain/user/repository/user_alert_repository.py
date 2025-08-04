"""
User Alert Repository

이 모듈은 UserAlert 모델에 대한 데이터 접근 계층을 제공합니다.
SQLModel을 최대한 활용하여 타입 안전성과 성능을 보장합니다.
"""

import logging
from typing import Optional, List

from sqlmodel import Session, select, func
from sqlalchemy.exc import SQLAlchemyError

from ..models import UserAlert

logger = logging.getLogger(__name__)


class UserAlertRepository:
    """UserAlert 모델에 대한 SQLModel 최적화 Repository 클래스"""

    def create(self, session: Session, alert: UserAlert) -> UserAlert:
        """
        새로운 사용자 알림 정보를 생성합니다.

        Args:
            session: SQLModel 세션
            alert: 생성할 알림 정보 객체

        Returns:
            생성된 알림 정보 객체

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.add(alert)
            session.flush()
            session.refresh(alert)
            logger.debug(f"UserAlert created for user: {alert.user_id}")
            return alert
        except SQLAlchemyError as e:
            logger.error(f"Error creating user alert: {e}")
            raise

    def find_by_user_ids(self, session: Session, user_ids: List[str]) -> List[UserAlert]:
        """
        사용자 ID로 알림 정보를 조회합니다.

        Args:
            session: SQLModel 세션
            user_id: 사용자 ID

        Returns:
            알림 정보 객체 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(UserAlert).where(UserAlert.user_id.in_(user_ids))
            result = session.exec(statement).all()
            
            if result:
                logger.debug(f"UserAlert found for users: {user_ids}")
            else:
                logger.debug(f"UserAlert not found for users: {user_ids}")
                
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error finding user alert by user IDs: {e}")
            raise

    def find_by_fcm_token(self, session: Session, fcm_token: str) -> Optional[UserAlert]:
        """
        FCM 토큰으로 알림 정보를 조회합니다.

        Args:
            session: SQLModel 세션
            fcm_token: FCM 토큰

        Returns:
            알림 정보 객체 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(UserAlert).where(UserAlert.fcm_token == fcm_token)
            result = session.exec(statement).first()
            
            if result:
                logger.debug(f"UserAlert found by FCM token: {fcm_token}")
            else:
                logger.debug(f"UserAlert not found by FCM token: {fcm_token}")
                
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error finding user alert by FCM token: {e}")
            raise

    def find_by_alert_enabled(self, session: Session, alert_enabled: bool, limit: int = 100, offset: int = 0) -> List[UserAlert]:
        """
        알림 활성화 상태별로 사용자를 조회합니다.

        Args:
            session: SQLModel 세션
            alert_enabled: 알림 활성화 여부
            limit: 조회할 최대 개수
            offset: 건너뛸 개수

        Returns:
            알림 정보 객체 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = (
                select(UserAlert)
                .where(UserAlert.is_alerted == alert_enabled)
                .limit(limit)
                .offset(offset)
                .order_by(UserAlert.created_at.desc())
            )
            result = session.exec(statement).all()
            
            logger.debug(f"Found {len(result)} users with alert enabled: {alert_enabled}")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error finding user alerts by alert enabled: {e}")
            raise

    def find_active_alerts_with_tokens(self, session: Session, limit: int = 100, offset: int = 0) -> List[UserAlert]:
        """
        FCM 토큰이 있는 활성 알림을 조회합니다.

        Args:
            session: SQLModel 세션
            limit: 조회할 최대 개수
            offset: 건너뛸 개수

        Returns:
            알림 정보 객체 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = (
                select(UserAlert)
                .where(UserAlert.is_alerted == True)
                .where(UserAlert.fcm_token.is_not(None))
                .limit(limit)
                .offset(offset)
                .order_by(UserAlert.created_at.desc())
            )
            result = session.exec(statement).all()
            
            logger.debug(f"Found {len(result)} active alerts with FCM tokens")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error finding active alerts with tokens: {e}")
            raise

    def update(self, session: Session, alert: UserAlert) -> UserAlert:
        """
        알림 정보를 업데이트합니다.

        Args:
            session: SQLModel 세션
            alert: 업데이트할 알림 정보 객체

        Returns:
            업데이트된 알림 정보 객체

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.add(alert)
            session.flush()
            session.refresh(alert)
            logger.debug(f"UserAlert updated for user: {alert.user_id}")
            return alert
        except SQLAlchemyError as e:
            logger.error(f"Error updating user alert: {e}")
            raise

    def delete(self, session: Session, alert: UserAlert) -> bool:
        """
        알림 정보를 삭제합니다.

        Args:
            session: SQLModel 세션
            alert: 삭제할 알림 정보 객체

        Returns:
            삭제 성공 여부

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.delete(alert)
            session.flush()
            logger.debug(f"UserAlert deleted for user: {alert.user_id}")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error deleting user alert: {e}")
            raise

    def find_all(self, session: Session, limit: int = 100, offset: int = 0) -> List[UserAlert]:
        """
        모든 알림 정보를 조회합니다.

        Args:
            session: SQLModel 세션
            limit: 조회할 최대 개수
            offset: 건너뛸 개수

        Returns:
            알림 정보 객체 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = (
                select(UserAlert)
                .limit(limit)
                .offset(offset)
                .order_by(UserAlert.created_at.desc())
            )
            result = session.exec(statement).all()
            
            logger.debug(f"Found {len(result)} user alerts")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error finding all user alerts: {e}")
            raise

    def count(self, session: Session) -> int:
        """
        전체 알림 정보 수를 조회합니다.

        Args:
            session: SQLModel 세션

        Returns:
            알림 정보 수

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(func.count(UserAlert.user_id))
            result = session.exec(statement).one()
            
            logger.debug(f"Total user alert count: {result}")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error counting user alerts: {e}")
            raise

    def count_by_alert_enabled(self, session: Session, is_alerted: bool) -> int:
        """
        알림 활성화 상태별 사용자 수를 조회합니다.

        Args:
            session: SQLModel 세션
            is_alerted: 알림 활성화 여부

        Returns:
            사용자 수

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = select(func.count(UserAlert.user_id)).where(UserAlert.is_alerted == is_alerted)
            result = session.exec(statement).one()
            
            logger.debug(f"User count with alert enabled {is_alerted}: {result}")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error counting users by alert enabled: {e}")
            raise

    def count_active_with_tokens(self, session: Session) -> int:
        """
        FCM 토큰이 있는 활성 알림 수를 조회합니다.

        Args:
            session: SQLModel 세션

        Returns:
            활성 알림 수

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            statement = (
                select(func.count(UserAlert.user_id))
                .where(UserAlert.is_alerted == True)
                .where(UserAlert.fcm_token.is_not(None))
            )
            result = session.exec(statement).one()
            
            logger.debug(f"Active alerts with FCM tokens count: {result}")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error counting active alerts with tokens: {e}")
            raise 