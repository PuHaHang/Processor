"""
UserAlert Repository

이 모듈은 UserAlert 모델의 기본 CRUD 작업을 담당하는 Repository 클래스를 제공합니다.
"""

from typing import Optional, List
from datetime import datetime

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, func

from ..models import UserAlert
from ....common.dependency_injection import inject_session, transactional

import logging

logger = logging.getLogger(__name__)


class UserAlertRepository:
    """UserAlert 모델 기본 CRUD 작업을 담당하는 Repository"""

    @transactional
    def create(self, session: Session, user_alert: UserAlert) -> UserAlert:
        """
        새로운 사용자 알림 정보를 생성합니다.

        Args:
            session: 데이터베이스 세션
            user_alert: 생성할 사용자 알림 정보 엔티티

        Returns:
            생성된 사용자 알림 정보 엔티티

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.add(user_alert)
            session.flush()
            
            logger.debug(f"User alert created: {user_alert.user_id}")
            return user_alert
            
        except SQLAlchemyError as e:
            logger.error(f"Error creating user alert: {e}")
            raise

    @inject_session
    def find_by_user_id(self, session: Session, user_id: str) -> Optional[UserAlert]:
        """
        사용자 ID로 알림 정보를 조회합니다.

        Args:
            session: 데이터베이스 세션
            user_id: 사용자 ID

        Returns:
            사용자 알림 정보 엔티티 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            alert = session.query(UserAlert).options(
                joinedload(UserAlert.user)
            ).filter(UserAlert.user_id == user_id).first()
            
            if alert:
                logger.debug(f"User alert found: {user_id}")
            else:
                logger.debug(f"User alert not found: {user_id}")
                
            return alert
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding user alert by user ID: {e}")
            raise

    @inject_session
    def find_by_fcm_token(self, session: Session, fcm_token: str) -> Optional[UserAlert]:
        """
        FCM 토큰으로 알림 정보를 조회합니다.

        Args:
            session: 데이터베이스 세션
            fcm_token: FCM 토큰

        Returns:
            사용자 알림 정보 엔티티 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            alert = session.query(UserAlert).options(
                joinedload(UserAlert.user)
            ).filter(UserAlert.fcm_token == fcm_token).first()
            
            if alert:
                logger.debug(f"User alert found by FCM token: {fcm_token}")
            else:
                logger.debug(f"User alert not found by FCM token: {fcm_token}")
                
            return alert
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding user alert by FCM token: {e}")
            raise

    @inject_session
    def find_by_alert_enabled(self, session: Session, alert_enabled: bool = True, limit: int = 100, offset: int = 0) -> List[UserAlert]:
        """
        알림 활성화 여부로 알림 정보들을 조회합니다.

        Args:
            session: 데이터베이스 세션
            alert_enabled: 알림 활성화 여부
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            사용자 알림 정보 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            alerts = session.query(UserAlert).options(
                joinedload(UserAlert.user)
            ).filter(
                UserAlert.alert_flag == alert_enabled
            ).offset(offset).limit(limit).all()
            
            logger.debug(f"Found {len(alerts)} user alerts with alert_flag: {alert_enabled}")
            return alerts
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding user alerts by alert flag: {e}")
            raise

    @inject_session
    def find_active_alerts_with_tokens(self, session: Session, limit: int = 100, offset: int = 0) -> List[UserAlert]:
        """
        활성화된 알림 정보들 중 FCM 토큰이 있는 것들을 조회합니다.

        Args:
            session: 데이터베이스 세션
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            사용자 알림 정보 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            alerts = session.query(UserAlert).options(
                joinedload(UserAlert.user)
            ).filter(
                and_(
                    UserAlert.alert_flag == True,
                    UserAlert.fcm_token != None
                )
            ).offset(offset).limit(limit).all()
            
            logger.debug(f"Found {len(alerts)} active user alerts with FCM tokens")
            return alerts
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding active user alerts with tokens: {e}")
            raise

    @transactional
    def update(self, session: Session, user_alert: UserAlert) -> UserAlert:
        """
        사용자 알림 정보를 업데이트합니다.

        Args:
            session: 데이터베이스 세션
            user_alert: 업데이트할 사용자 알림 정보 엔티티

        Returns:
            업데이트된 사용자 알림 정보 엔티티

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            user_alert.updated_at = datetime.utcnow()
            session.merge(user_alert)
            session.flush()
            
            logger.debug(f"User alert updated: {user_alert.user_id}")
            return user_alert
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating user alert: {e}")
            raise

    @transactional
    def delete(self, session: Session, user_alert: UserAlert) -> bool:
        """
        사용자 알림 정보를 삭제합니다.

        Args:
            session: 데이터베이스 세션
            user_alert: 삭제할 사용자 알림 정보 엔티티

        Returns:
            삭제 성공 여부

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            session.delete(user_alert)
            session.flush()
            
            logger.debug(f"User alert deleted: {user_alert.user_id}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error deleting user alert: {e}")
            raise

    @inject_session
    def find_all(self, session: Session, limit: int = 100, offset: int = 0) -> List[UserAlert]:
        """
        모든 사용자 알림 정보를 조회합니다.

        Args:
            session: 데이터베이스 세션
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            사용자 알림 정보 엔티티 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            alerts = session.query(UserAlert).options(
                joinedload(UserAlert.user)
            ).offset(offset).limit(limit).all()
            
            logger.debug(f"Found {len(alerts)} user alerts")
            return alerts
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding all user alerts: {e}")
            raise

    @inject_session
    def count(self, session: Session) -> int:
        """
        전체 사용자 알림 정보 수를 조회합니다.

        Args:
            session: 데이터베이스 세션

        Returns:
            전체 사용자 알림 정보 수

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            count = session.query(func.count(UserAlert.user_id)).scalar()
            
            logger.debug(f"Total user alert count: {count}")
            return count
            
        except SQLAlchemyError as e:
            logger.error(f"Error counting user alerts: {e}")
            raise

    @inject_session
    def count_by_alert_enabled(self, session: Session, alert_enabled: bool = True) -> int:
        """
        알림 활성화 여부별 사용자 수를 조회합니다.

        Args:
            session: 데이터베이스 세션
            alert_enabled: 알림 활성화 여부

        Returns:
            알림 활성화 여부별 사용자 수

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            count = session.query(func.count(UserAlert.user_id)).filter(
                UserAlert.alert_flag == alert_enabled
            ).scalar()
            
            logger.debug(f"User alert count for enabled {alert_enabled}: {count}")
            return count
            
        except SQLAlchemyError as e:
            logger.error(f"Error counting user alerts by alert flag: {e}")
            raise

    @inject_session
    def count_active_with_tokens(self, session: Session) -> int:
        """
        활성화된 알림 정보 중 FCM 토큰이 있는 사용자 수를 조회합니다.

        Args:
            session: 데이터베이스 세션

        Returns:
            활성화된 알림 정보 중 FCM 토큰이 있는 사용자 수

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            count = session.query(func.count(UserAlert.user_id)).filter(
                and_(
                    UserAlert.alert_flag == True,
                    UserAlert.fcm_token != None
                )
            ).scalar()
            
            logger.debug(f"Active user alert count with FCM tokens: {count}")
            return count
            
        except SQLAlchemyError as e:
            logger.error(f"Error counting active user alerts with tokens: {e}")
            raise 