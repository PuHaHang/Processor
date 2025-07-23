"""
User 도메인 서비스

이 모듈은 사용자 관련 CRUD 작업을 처리하는 서비스를 제공합니다.
새로운 ERD 구조에 따라 사용자 정보가 여러 테이블로 분산되어 있어
트랜잭션 처리가 중요합니다.
"""

import uuid
import random
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, func

from .models import User, UserProfile, UserBilling, UserAlert, UserRole, UserProvider, UserRegion, UserBillingType
from .dto import CreateUserDto, UpdateUserDto, SearchUsersDto, GetUsersByBillingDto
from .repository import UserRepository, UserProfileRepository, UserBillingRepository, UserAlertRepository
from ...common.dependency_injection import inject_session, transactional

import logging

logger = logging.getLogger(__name__)


class UserService:
    """사용자 관련 비즈니스 로직을 처리하는 서비스"""

    def __init__(self):
        self.user_repository = UserRepository()
        self.user_profile_repository = UserProfileRepository()
        self.user_billing_repository = UserBillingRepository()
        self.user_alert_repository = UserAlertRepository()

    @transactional
    def create_user(self, session: Session, dto: CreateUserDto) -> User:
        """
        새로운 사용자를 생성합니다.
        사용자 정보가 여러 테이블에 분산되어 있어 트랜잭션 처리가 필요합니다.

        Args:
            session: 데이터베이스 세션
            dto: 사용자 생성 데이터 전송 객체

        Returns:
            생성된 사용자 객체

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            # 기본 사용자 정보 생성
            user_id = str(uuid.uuid4())
            user = User(
                user_id=user_id,
                role=dto.role,
                provider=dto.provider,
                openid=dto.openid
            )
            
            # Repository를 통해 사용자 생성
            user = self.user_repository.create(session, user)
            
            # 프로필 생성
            nickname = dto.nickname
            if dto.provider == UserProvider.GUEST:
                # GUEST 사용자는 guest_랜덤숫자 형태로 닉네임 생성
                random_number = random.randint(1000000000, 9999999999)
                nickname = f"guest_{random_number}"
            
            profile = UserProfile(
                user_id=user_id,
                nickname=nickname,
                image=dto.image,
                region=dto.region
            )
            self.user_profile_repository.create(session, profile)
            
            # 결제 정보 생성
            billing = UserBilling(
                user_id=user_id,
                billing=dto.billing
            )
            self.user_billing_repository.create(session, billing)
            
            # 알림 정보 생성
            alert = UserAlert(
                user_id=user_id,
                fcm_token=dto.fcm_token,
                alert_flag=dto.alert_flag
            )
            self.user_alert_repository.create(session, alert)
            
            logger.info(f"User created: {user_id}")
            return user
            
        except SQLAlchemyError as e:
            logger.error(f"Error creating user: {e}")
            raise

    @inject_session
    def get_user_by_id(self, session: Session, user_id: str) -> Optional[User]:
        """
        ID로 사용자를 조회합니다.
        관련된 모든 정보(프로필, 결제, 알림)를 함께 로드합니다.

        Args:
            session: 데이터베이스 세션
            user_id: 사용자 ID

        Returns:
            사용자 객체 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            user = self.user_repository.find_by_id(session, user_id)
            
            if user:
                logger.debug(f"User found: {user_id}")
            else:
                logger.debug(f"User not found: {user_id}")
                
            return user
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting user by ID: {e}")
            raise

    @inject_session
    def get_user_by_openid(self, session: Session, openid: str) -> Optional[User]:
        """
        OpenID로 사용자를 조회합니다.

        Args:
            session: 데이터베이스 세션
            openid: OAuth2.0 식별자

        Returns:
            사용자 객체 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            user = self.user_repository.find_by_openid(session, openid)
            
            if user:
                logger.debug(f"User found by OpenID: {openid}")
            else:
                logger.debug(f"User not found by OpenID: {openid}")
                
            return user
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting user by OpenID: {e}")
            raise

    @transactional
    def delete_user(self, session: Session, user_id: str) -> bool:
        """
        사용자를 삭제합니다.
        CASCADE 설정으로 관련 정보들도 함께 삭제됩니다.

        Args:
            session: 데이터베이스 세션
            user_id: 사용자 ID

        Returns:
            삭제 성공 여부

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            user = self.user_repository.find_by_id(session, user_id)
            if not user:
                logger.warning(f"User not found for deletion: {user_id}")
                return False
            
            result = self.user_repository.delete(session, user)
            
            logger.info(f"User deleted: {user_id}")
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Error deleting user: {e}")
            raise

    @inject_session
    def get_users_by_billing(self, session: Session, dto: GetUsersByBillingDto) -> List[User]:
        """
        결제 플랜으로 사용자를 조회합니다.

        Args:
            session: 데이터베이스 세션
            dto: 결제 플랜별 사용자 조회 데이터 전송 객체

        Returns:
            사용자 객체 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            # UserBilling repository로부터 결제 정보 조회
            billing_records = self.user_billing_repository.find_by_billing_type(session, dto.billing, dto.limit, dto.offset)
            
            # 해당 결제 플랜 사용자들의 user_id들을 가져와서 User 조회
            user_ids = [billing.user_id for billing in billing_records]
            users = []
            for user_id in user_ids:
                user = self.user_repository.find_by_id(session, user_id)
                if user:
                    users.append(user)
            
            logger.debug(f"Found {len(users)} users with billing: {dto.billing}")
            return users
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting users by billing: {e}")
            raise

    @transactional
    def update_user(self, session: Session, dto: UpdateUserDto) -> Optional[User]:
        """
        사용자 정보를 수정합니다.
        여러 테이블에 분산된 정보를 업데이트합니다.

        Args:
            session: 데이터베이스 세션
            dto: 사용자 수정 데이터 전송 객체

        Returns:
            수정된 사용자 객체 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            user = self.user_repository.find_by_id(session, dto.user_uuid)
            
            if not user:
                logger.warning(f"User not found for update: {dto.user_uuid}")
                return None
            
            update_fields = dto.get_update_fields()
            updated_sections = []
            
            # 프로필 정보 업데이트
            if any(field in update_fields for field in ['nickname', 'image', 'region']):
                profile = self.user_profile_repository.find_by_user_id(session, dto.user_uuid)
                
                if not profile:
                    # 프로필이 없는 경우 새로 생성
                    profile = UserProfile(user_id=dto.user_uuid)
                    if 'nickname' in update_fields:
                        profile.nickname = update_fields['nickname']
                    if 'image' in update_fields:
                        profile.image = update_fields['image']
                    if 'region' in update_fields:
                        profile.region = update_fields['region']
                    self.user_profile_repository.create(session, profile)
                else:
                    # 기존 프로필 업데이트
                    if 'nickname' in update_fields:
                        profile.nickname = update_fields['nickname']
                    if 'image' in update_fields:
                        profile.image = update_fields['image']
                    if 'region' in update_fields:
                        profile.region = update_fields['region']
                    self.user_profile_repository.update(session, profile)
                
                updated_sections.append('profile')
            
            # 결제 정보 업데이트
            if 'billing' in update_fields:
                billing = self.user_billing_repository.find_by_user_id(session, dto.user_uuid)
                
                if not billing:
                    # 결제 정보가 없는 경우 새로 생성
                    billing = UserBilling(user_id=dto.user_uuid, billing=update_fields['billing'])
                    self.user_billing_repository.create(session, billing)
                else:
                    # 기존 결제 정보 업데이트
                    billing.billing = update_fields['billing']
                    self.user_billing_repository.update(session, billing)
                
                updated_sections.append('billing')
            
            # 알림 정보 업데이트
            if any(field in update_fields for field in ['fcm_token', 'alert_flag']):
                alert = self.user_alert_repository.find_by_user_id(session, dto.user_uuid)
                
                if not alert:
                    # 알림 정보가 없는 경우 새로 생성
                    alert = UserAlert(user_id=dto.user_uuid)
                    if 'fcm_token' in update_fields:
                        alert.fcm_token = update_fields['fcm_token']
                    if 'alert_flag' in update_fields:
                        alert.alert_flag = update_fields['alert_flag']
                    self.user_alert_repository.create(session, alert)
                else:
                    # 기존 알림 정보 업데이트
                    if 'fcm_token' in update_fields:
                        alert.fcm_token = update_fields['fcm_token']
                    if 'alert_flag' in update_fields:
                        alert.alert_flag = update_fields['alert_flag']
                    self.user_alert_repository.update(session, alert)
                
                updated_sections.append('alert')
            
            # 기본 사용자 정보 업데이트
            if 'role' in update_fields:
                user.role = update_fields['role']
                self.user_repository.update(session, user)
                updated_sections.append('user')
            
            if updated_sections:
                logger.info(f"User updated: {dto.user_uuid}, sections: {updated_sections}")
            else:
                logger.debug(f"No valid fields to update for user: {dto.user_uuid}")
            
            return user
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating user: {e}")
            raise

    @inject_session
    def get_all_users(self, session: Session, limit: int = 100, offset: int = 0) -> List[User]:
        """
        모든 사용자를 조회합니다.

        Args:
            session: 데이터베이스 세션
            limit: 조회 제한 수
            offset: 조회 시작 위치

        Returns:
            사용자 객체 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            users = self.user_repository.find_all(session, limit, offset)
            
            logger.debug(f"Found {len(users)} users")
            return users
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting all users: {e}")
            raise

    @inject_session
    def get_user_count(self, session: Session) -> int:
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
            count = self.user_repository.count(session)
            
            logger.debug(f"Total user count: {count}")
            return count
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting user count: {e}")
            raise

    @inject_session
    def get_user_statistics(self, session: Session) -> Dict[str, Any]:
        """
        사용자 통계 정보를 조회합니다.

        Args:
            session: 데이터베이스 세션

        Returns:
            사용자 통계 정보

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            # 총 사용자 수
            total_users = self.user_repository.count(session)
            
            # 제공자별 통계 (직접 쿼리 필요)
            provider_stats = session.query(
                User.provider,
                func.count(User.user_id).label('count')
            ).group_by(User.provider).all()
            
            # 결제 플랜별 통계 (직접 쿼리 필요)
            billing_stats = session.query(
                UserBilling.billing,
                func.count(UserBilling.user_id).label('count')
            ).group_by(UserBilling.billing).all()
            
            # 지역별 통계 (직접 쿼리 필요)
            region_stats = session.query(
                UserProfile.region,
                func.count(UserProfile.user_id).label('count')
            ).group_by(UserProfile.region).all()
            
            # 역할별 통계 (직접 쿼리 필요)
            role_stats = session.query(
                User.role,
                func.count(User.user_id).label('count')
            ).group_by(User.role).all()
            
            statistics = {
                'total_users': total_users,
                'by_provider': {stat.provider: stat.count for stat in provider_stats},
                'by_billing': {stat.billing: stat.count for stat in billing_stats},
                'by_region': {stat.region: stat.count for stat in region_stats},
                'by_role': {stat.role: stat.count for stat in role_stats}
            }
            
            logger.debug(f"User statistics calculated: {statistics}")
            return statistics
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting user statistics: {e}")
            raise

    @inject_session
    def search_users(self, session: Session, dto: SearchUsersDto) -> List[User]:
        """
        다양한 조건으로 사용자를 검색합니다.
        여러 테이블에 분산된 정보를 기반으로 검색합니다.

        Args:
            session: 데이터베이스 세션
            dto: 사용자 검색 데이터 전송 객체

        Returns:
            검색된 사용자 객체 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            # 복잡한 검색 조건이므로 직접 쿼리 사용
            query = session.query(User).options(
                joinedload(User.profile),
                joinedload(User.billing),
                joinedload(User.alert)
            )
            
            # 기본 사용자 정보 필터
            if dto.provider:
                query = query.filter(User.provider == dto.provider)
            if dto.role:
                query = query.filter(User.role == dto.role)
            
            # 프로필 정보 필터
            if dto.nickname:
                query = query.join(UserProfile).filter(
                    UserProfile.nickname.ilike(f"%{dto.nickname}%")
                )
            if dto.region:
                query = query.join(UserProfile).filter(
                    UserProfile.region == dto.region
                )
            
            # 결제 정보 필터
            if dto.billing:
                query = query.join(UserBilling).filter(
                    UserBilling.billing == dto.billing
                )
            
            users = query.offset(dto.offset).limit(dto.limit).all()
            
            logger.debug(f"Found {len(users)} users with search criteria")
            return users
            
        except SQLAlchemyError as e:
            logger.error(f"Error searching users: {e}")
            raise

    @transactional
    def update_fcm_token(self, session: Session, user_id: str, fcm_token: str) -> Optional[User]:
        """
        사용자의 FCM 토큰을 업데이트합니다.

        Args:
            session: 데이터베이스 세션
            user_id: 사용자 ID
            fcm_token: FCM 토큰

        Returns:
            업데이트된 사용자 객체 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            user = self.user_repository.find_by_id(session, user_id)
            
            if not user:
                logger.warning(f"User not found for FCM token update: {user_id}")
                return None
            
            # 기존 알림 정보 조회
            alert = self.user_alert_repository.find_by_user_id(session, user_id)
            
            if not alert:
                # 알림 정보가 없는 경우 새로 생성
                alert = UserAlert(user_id=user_id, fcm_token=fcm_token, alert_flag=False)
                self.user_alert_repository.create(session, alert)
            else:
                # 기존 알림 정보 업데이트
                alert.fcm_token = fcm_token
                self.user_alert_repository.update(session, alert)
            
            logger.info(f"FCM token updated for user: {user_id}")
            return user
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating FCM token: {e}")
            raise

    @transactional
    def update_alert_flag(self, session: Session, user_id: str, alert_flag: bool) -> Optional[User]:
        """
        사용자의 알림 플래그를 업데이트합니다.

        Args:
            session: 데이터베이스 세션
            user_id: 사용자 ID
            alert_flag: 알림 플래그

        Returns:
            업데이트된 사용자 객체 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            user = self.user_repository.find_by_id(session, user_id)
            
            if not user:
                logger.warning(f"User not found for alert flag update: {user_id}")
                return None
            
            # 기존 알림 정보 조회
            alert = self.user_alert_repository.find_by_user_id(session, user_id)
            
            if not alert:
                # 알림 정보가 없는 경우 새로 생성
                alert = UserAlert(user_id=user_id, alert_flag=alert_flag)
                self.user_alert_repository.create(session, alert)
            else:
                # 기존 알림 정보 업데이트
                alert.alert_flag = alert_flag
                self.user_alert_repository.update(session, alert)
            
            logger.info(f"Alert flag updated for user: {user_id}, flag: {alert_flag}")
            return user
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating alert flag: {e}")
            raise 