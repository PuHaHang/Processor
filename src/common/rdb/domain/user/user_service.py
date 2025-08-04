"""
User 도메인 서비스

이 모듈은 사용자 관련 CRUD 작업을 처리하는 서비스를 제공합니다.
SQLModel을 최대한 활용하여 타입 안전성과 데이터 검증을 제공합니다.
새로운 ERD 구조에 따라 사용자 정보가 여러 테이블로 분산되어 있어
트랜잭션 처리가 중요합니다.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from sqlmodel import Session, select, func
from sqlalchemy.exc import SQLAlchemyError

from .models import User, UserProfile, UserBilling, UserAlert, UserRole, UserProvider, UserRegion, UserBillingType
from .dto import CreateUserDto, UpdateUserDto, SearchUsersDto, GetUsersByBillingDto
from .repository import UserRepository, UserProfileRepository, UserBillingRepository, UserAlertRepository

import logging

logger = logging.getLogger(__name__)


class UserService:
    """사용자 관련 비즈니스 로직을 처리하는 SQLModel 최적화 서비스"""

    def __init__(self):
        self.user_repository = UserRepository()
        self.user_profile_repository = UserProfileRepository()
        self.user_billing_repository = UserBillingRepository()
        self.user_alert_repository = UserAlertRepository()

    def create_user(self, session: Session, dto: CreateUserDto) -> User:
        """
        새로운 사용자를 생성합니다.
        여러 테이블에 분산된 정보를 트랜잭션 내에서 생성합니다.

        Args:
            session: SQLModel 세션
            dto: 사용자 생성 데이터 전송 객체

        Returns:
            생성된 사용자 객체

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            # 기본 사용자 생성
            user = User(
                role=dto.role,
                provider=dto.provider,
                openid=dto.openid
            )
            
            # Repository를 통해 사용자 생성
            user = self.user_repository.create(session, user)
            
            # 사용자 프로필 생성
            profile = UserProfile(
                user_id=user.user_id,
                nickname=dto.nickname,
                image=dto.image,
                region=dto.region
            )
            self.user_profile_repository.create(session, profile)
            
            # 사용자 결제 정보 생성
            billing = UserBilling(
                user_id=user.user_id,
                billing=dto.billing
            )
            self.user_billing_repository.create(session, billing)
            
            # 사용자 알림 정보 생성
            alert = UserAlert(
                user_id=user.user_id,
                fcm_token=dto.fcm_token,
                is_alerted=dto.is_alerted
            )
            self.user_alert_repository.create(session, alert)
            
            logger.info(f"User created with all related data: {user.user_id}")
            return user
            
        except SQLAlchemyError as e:
            logger.error(f"Error creating user: {e}")
            raise

    def get_user_by_id(self, session: Session, user_id: str) -> Optional[User]:
        """
        ID로 사용자를 조회합니다.
        관련된 모든 정보를 함께 로드합니다.

        Args:
            session: SQLModel 세션
            user_id: 사용자 ID

        Returns:
            사용자 객체 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            user = self.user_repository.find_by_id(session, user_id)
            
            if user:
                logger.debug(f"User found by ID: {user_id}")
            else:
                logger.debug(f"User not found by ID: {user_id}")
                
            return user
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting user by ID: {e}")
            raise

    def get_user_by_openid(self, session: Session, openid: str) -> Optional[User]:
        """
        OpenID로 사용자를 조회합니다.

        Args:
            session: SQLModel 세션
            openid: OAuth OpenID

        Returns:
            사용자 객체 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            user = self.user_repository.find_by_openid(session, openid)
            
            if user:
                logger.debug(f"User found by openid: {openid}")
            else:
                logger.debug(f"User not found by openid: {openid}")
                
            return user
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting user by openid: {e}")
            raise

    def delete_user(self, session: Session, user_id: str) -> bool:
        """
        사용자를 삭제합니다.
        관련된 모든 정보를 함께 삭제합니다.

        Args:
            session: SQLModel 세션
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
            
            # 사용자 삭제 (관련 데이터는 CASCADE로 자동 삭제)
            result = self.user_repository.delete(session, user)
            
            if result:
                logger.info(f"User deleted successfully: {user_id}")
            else:
                logger.error(f"Failed to delete user: {user_id}")
                
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Error deleting user: {e}")
            raise

    def get_users_by_billing(self, session: Session, dto: GetUsersByBillingDto) -> List[User]:
        """
        결제 플랜별로 사용자를 조회합니다.

        Args:
            session: SQLModel 세션
            dto: 결제 플랜별 사용자 조회 DTO

        Returns:
            사용자 객체 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            # 결제 정보로 사용자 ID 목록 조회
            billings = self.user_billing_repository.find_by_billing_type(
                session, dto.billing, dto.limit, dto.offset
            )
            
            # 사용자 ID 목록 추출
            user_ids = [billing.user_id for billing in billings]
            
            # 사용자 정보 조회
            users = []
            for user_id in user_ids:
                user = self.user_repository.find_by_id(session, user_id)
                if user:
                    users.append(user)
            
            logger.debug(f"Found {len(users)} users for billing type: {dto.billing}")
            return users
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting users by billing: {e}")
            raise

    def update_user(self, session: Session, dto: UpdateUserDto) -> Optional[User]:
        """
        사용자 정보를 업데이트합니다.

        Args:
            session: SQLModel 세션
            dto: 사용자 업데이트 DTO

        Returns:
            업데이트된 사용자 객체 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            # 사용자 조회
            user = self.user_repository.find_by_id(session, dto.user_id)
            
            if not user:
                logger.warning(f"User not found for update: {dto.user_id}")
                return None
            
            # 기본 사용자 정보 업데이트
            if dto.role is not None:
                user.role = dto.role
            
            if dto.provider is not None:
                user.provider = dto.provider
            
            if dto.openid is not None:
                user.openid = dto.openid
            
            # 사용자 정보 업데이트
            user = self.user_repository.update(session, user)
            
            # 프로필 정보 업데이트
            profile = self.user_profile_repository.find_by_user_id(session, user.user_id)
            if profile:
                if dto.nickname is not None:
                    profile.nickname = dto.nickname
                if dto.image is not None:
                    profile.image = dto.image
                if dto.region is not None:
                    profile.region = dto.region
                
                self.user_profile_repository.update(session, profile)
            
            # 결제 정보 업데이트
            billing = self.user_billing_repository.find_by_user_id(session, user.user_id)
            if billing and dto.billing is not None:
                billing.billing = dto.billing
                self.user_billing_repository.update(session, billing)
            
            # 알림 정보 업데이트
            alert = self.user_alert_repository.find_by_user_ids(session, [user.user_id])
            if alert and len(alert) > 0:
                if dto.fcm_token is not None:
                    alert[0].fcm_token = dto.fcm_token
                if dto.is_alerted is not None:
                    alert[0].is_alerted = dto.is_alerted
                
                self.user_alert_repository.update(session, alert[0])
            
            logger.info(f"User updated successfully: {user.user_id}")
            return user
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating user: {e}")
            raise

    def get_all_users(self, session: Session, limit: int = 100, offset: int = 0) -> List[User]:
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
            users = self.user_repository.find_all(session, limit, offset)
            
            logger.debug(f"Found {len(users)} users")
            return users
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting all users: {e}")
            raise

    def get_user_count(self, session: Session) -> int:
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
            count = self.user_repository.count(session)
            
            logger.debug(f"Total user count: {count}")
            return count
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting user count: {e}")
            raise

    def get_user_statistics(self, session: Session) -> Dict[str, Any]:
        """
        사용자 통계 정보를 조회합니다.

        Args:
            session: SQLModel 세션

        Returns:
            통계 정보 딕셔너리

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            # 전체 사용자 수
            total_users = self.user_repository.count(session)
            
            # 제공자별 사용자 수
            provider_stats = {}
            for provider in UserProvider:
                count = self.user_repository.count_by_provider(session, provider)
                provider_stats[provider.value] = count
            
            # 역할별 사용자 수
            role_stats = {}
            for role in UserRole:
                count = self.user_repository.count_by_role(session, role)
                role_stats[role.value] = count
            
            # 결제 플랜별 사용자 수
            billing_stats = {}
            for billing_type in UserBillingType:
                count = self.user_billing_repository.count_by_billing_type(session, billing_type)
                billing_stats[billing_type.value] = count
            
            # 지역별 사용자 수
            region_stats = {}
            for region in UserRegion:
                profiles = self.user_profile_repository.find_by_region(session, region, limit=1000)
                region_stats[region.value] = len(profiles)
            
            # 알림 활성화 사용자 수
            alert_enabled_count = self.user_alert_repository.count_by_alert_enabled(session, True)
            alert_disabled_count = self.user_alert_repository.count_by_alert_enabled(session, False)
            
            statistics = {
                "total_users": total_users,
                "by_provider": provider_stats,
                "by_role": role_stats,
                "by_billing": billing_stats,
                "by_region": region_stats,
                "alert_enabled": alert_enabled_count,
                "alert_disabled": alert_disabled_count
            }
            
            logger.debug(f"User statistics generated: {statistics}")
            return statistics
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting user statistics: {e}")
            raise

    def search_users(self, session: Session, dto: SearchUsersDto) -> List[User]:
        """
        사용자를 검색합니다.

        Args:
            session: SQLModel 세션
            dto: 사용자 검색 DTO

        Returns:
            사용자 객체 리스트

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            # 검색 조건에 따른 사용자 조회
            if dto.nickname:
                # 닉네임으로 프로필 검색
                profiles = self.user_profile_repository.search_by_nickname(
                    session, dto.nickname, dto.limit, dto.offset
                )
                user_ids = [profile.user_id for profile in profiles]
            else:
                # 기본 사용자 조회
                users = self.user_repository.find_all(session, dto.limit, dto.offset)
                user_ids = [user.user_id for user in users]
            
            # 사용자 정보 조회 및 필터링
            filtered_users = []
            for user_id in user_ids:
                user = self.user_repository.find_by_id(session, user_id)
                if user and self._matches_search_criteria(user, dto):
                    filtered_users.append(user)
            
            logger.debug(f"Found {len(filtered_users)} users matching search criteria")
            return filtered_users
            
        except SQLAlchemyError as e:
            logger.error(f"Error searching users: {e}")
            raise

    def _matches_search_criteria(self, user: User, dto: SearchUsersDto) -> bool:
        """
        사용자가 검색 조건에 맞는지 확인합니다.
        
        Args:
            user: 검사할 사용자
            dto: 검색 조건
            
        Returns:
            조건에 맞으면 True, 아니면 False
        """
        # Provider 필터링
        if dto.provider and user.provider != dto.provider:
            return False
        
        # Role 필터링
        if dto.role and user.role != dto.role:
            return False
        
        # Billing 필터링
        if dto.billing and (not user.billing or user.billing.billing != dto.billing):
            return False
        
        # Region 필터링
        if dto.region and (not user.profile or user.profile.region != dto.region):
            return False
        
        return True

    def update_fcm_token(self, session: Session, user_id: str, fcm_token: str) -> Optional[User]:
        """
        사용자의 FCM 토큰을 업데이트합니다.

        Args:
            session: SQLModel 세션
            user_id: 사용자 ID
            fcm_token: 새로운 FCM 토큰

        Returns:
            업데이트된 사용자 객체 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            # 사용자 조회
            user = self.user_repository.find_by_id(session, user_id)
            
            if not user:
                logger.warning(f"User not found for FCM token update: {user_id}")
                return None
            
            # 알림 정보 조회 또는 생성
            alert = self.user_alert_repository.find_by_user_ids(session, [user_id])
            
            if alert and len(alert) > 0:
                # 기존 알림 정보 업데이트
                alert[0].fcm_token = fcm_token
                self.user_alert_repository.update(session, alert[0])
            else:
                # 새로운 알림 정보 생성
                alert = UserAlert(
                    user_id=user_id,
                    fcm_token=fcm_token,
                    is_alerted=False  # FCM 토큰만 업데이트할 때는 기본값 사용
                )
                self.user_alert_repository.create(session, alert)
            
            logger.info(f"FCM token updated for user: {user_id}")
            return user
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating FCM token: {e}")
            raise

    def update_is_alerted(self, session: Session, user_id: str, is_alerted: bool) -> Optional[User]:
        """
        사용자의 알림 플래그를 업데이트합니다.

        Args:
            session: SQLModel 세션
            user_id: 사용자 ID
            is_alerted: 새로운 알림 플래그

        Returns:
            업데이트된 사용자 객체 또는 None

        Raises:
            SQLAlchemyError: 데이터베이스 오류 발생 시
        """
        try:
            # 사용자 조회
            user = self.user_repository.find_by_id(session, user_id)
            
            if not user:
                logger.warning(f"User not found for alert flag update: {user_id}")
                return None
            
            # 알림 정보 조회 또는 생성
            alert = self.user_alert_repository.find_by_user_ids(session, [user_id])
            
            if alert and len(alert) > 0:
                # 기존 알림 정보 업데이트
                alert[0].is_alerted = is_alerted
                self.user_alert_repository.update(session, alert[0])
            else:
                # 새로운 알림 정보 생성
                alert = UserAlert(
                    user_id=user_id,
                    fcm_token=None,
                    is_alerted=is_alerted
                )
                self.user_alert_repository.create(session, alert)
            
            logger.info(f"Alert flag updated for user: {user_id} -> {is_alerted}")
            return user
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating alert flag: {e}")
            raise

    def get_user_alerts_by_user_ids(self, session: Session, user_ids: List[str]) -> List[UserAlert]:
        """
        사용자의 알림 정보를 조회합니다.
        """
        try:
            alerts = self.user_alert_repository.find_by_user_ids(session, user_ids)
            return alerts
        except SQLAlchemyError as e:
            logger.error(f"Error getting user alert by ID: {e}")
            raise