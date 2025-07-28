"""
User 도메인 Repository 테스트

이 모듈은 User 도메인의 모든 Repository 클래스들을 테스트합니다.
실제 PostgreSQL 데이터베이스와 연결하여 테스트합니다.
SQLModel을 최대한 활용하여 타입 안전성과 성능을 보장합니다.
"""

import pytest
from ulid import ULID
from datetime import datetime

from src.common.rdb.domain.user.models import User, UserProfile, UserBilling, UserAlert, UserRole, UserProvider, UserRegion, UserBillingType
from src.common.rdb.domain.user.repository import UserRepository, UserProfileRepository, UserBillingRepository, UserAlertRepository


@pytest.mark.database
@pytest.mark.repository
class TestUserRepository:
    """UserRepository 클래스의 기능을 테스트합니다."""
    
    def test_create_user(self, session, clean_database):
        """사용자 생성 테스트"""
        repository = UserRepository()
        
        # 사용자 생성
        user = User(
            role=UserRole.USER,
            provider=UserProvider.GOOGLE,
            openid="google_123456"
        )
        
        created_user = repository.create(session, user)
        
        # 결과 확인
        assert created_user.user_id is not None
        assert created_user.role == UserRole.USER
        assert created_user.provider == UserProvider.GOOGLE
        assert created_user.openid == "google_123456"
        assert created_user.created_at is not None
    
    def test_find_by_id(self, session, sample_user, clean_database):
        """ID로 사용자 조회 테스트"""
        repository = UserRepository()
        
        # 사용자 조회
        found_user = repository.find_by_id(session, sample_user.user_id)
        
        # 결과 확인
        assert found_user is not None
        assert found_user.user_id == sample_user.user_id
        assert found_user.role == sample_user.role
        assert found_user.provider == sample_user.provider
    
    def test_find_by_openid(self, session, clean_database):
        """OpenID로 사용자 조회 테스트"""
        repository = UserRepository()
        
        # 사용자 생성
        user = User(
            role=UserRole.USER,
            provider=UserProvider.GOOGLE,
            openid="test_openid_456"
        )
        repository.create(session, user)
        
        # OpenID로 조회
        found_user = repository.find_by_openid(session, "test_openid_456")
        
        # 결과 확인
        assert found_user is not None
        assert found_user.openid == "test_openid_456"
        assert found_user.provider == UserProvider.GOOGLE
    
    def test_find_by_provider(self, session, clean_database):
        """인증 제공자별 사용자 조회 테스트"""
        repository = UserRepository()
        
        # 여러 사용자 생성
        users = []
        for i in range(3):
            user = User(
                role=UserRole.USER,
                provider=UserProvider.GOOGLE,
                openid=f"google_openid_{i}"
            )
            users.append(repository.create(session, user))
        
        # Google 제공자로 조회
        google_users = repository.find_by_provider(session, UserProvider.GOOGLE)
        
        # 결과 확인
        assert len(google_users) == 3
        for user in google_users:
            assert user.provider == UserProvider.GOOGLE
    
    def test_find_by_role(self, session, clean_database):
        """역할별 사용자 조회 테스트"""
        repository = UserRepository()
        
        # 여러 사용자 생성
        users = []
        for i in range(3):
            user = User(
                role=UserRole.USER,
                provider=UserProvider.GUEST
            )
            users.append(repository.create(session, user))
        
        # USER 역할로 조회
        user_role_users = repository.find_by_role(session, UserRole.USER)
        
        # 결과 확인
        assert len(user_role_users) == 3
        for user in user_role_users:
            assert user.role == UserRole.USER
    
    def test_update_user(self, session, sample_user, clean_database):
        """사용자 정보 업데이트 테스트"""
        repository = UserRepository()
        
        # 사용자 정보 수정
        sample_user.role = UserRole.ADMIN
        sample_user.provider = UserProvider.APPLE
        
        updated_user = repository.update(session, sample_user)
        
        # 결과 확인
        assert updated_user.role == UserRole.ADMIN
        assert updated_user.provider == UserProvider.APPLE
        assert updated_user.updated_at is not None
    
    def test_delete_user(self, session, sample_user, clean_database):
        """사용자 삭제 테스트"""
        repository = UserRepository()
        
        # 사용자 삭제
        result = repository.delete(session, sample_user)
        
        # 결과 확인
        assert result is True
        
        # 삭제 확인
        found_user = repository.find_by_id(session, sample_user.user_id)
        assert found_user is None
    
    def test_find_all(self, session, clean_database):
        """모든 사용자 조회 테스트"""
        repository = UserRepository()
        
        # 여러 사용자 생성
        users = []
        for i in range(3):
            user = User(
                role=UserRole.USER,
                provider=UserProvider.GUEST
            )
            users.append(repository.create(session, user))
        
        # 모든 사용자 조회
        all_users = repository.find_all(session)
        
        # 결과 확인
        assert len(all_users) == 3
    
    def test_count(self, session, clean_database):
        """사용자 수 조회 테스트"""
        repository = UserRepository()
        
        # 여러 사용자 생성
        for i in range(5):
            user = User(
                role=UserRole.USER,
                provider=UserProvider.GUEST
            )
            repository.create(session, user)
        
        # 사용자 수 조회
        count = repository.count(session)
        
        # 결과 확인
        assert count == 5
    
    def test_count_by_provider(self, session, clean_database):
        """제공자별 사용자 수 조회 테스트"""
        repository = UserRepository()
        
        # Google 사용자 생성
        for i in range(3):
            user = User(
                role=UserRole.USER,
                provider=UserProvider.GOOGLE,
                openid=f"google_{i}"
            )
            repository.create(session, user)
        
        # Apple 사용자 생성
        for i in range(2):
            user = User(
                role=UserRole.USER,
                provider=UserProvider.APPLE,
                openid=f"apple_{i}"
            )
            repository.create(session, user)
        
        # Google 사용자 수 조회
        google_count = repository.count_by_provider(session, UserProvider.GOOGLE)
        assert google_count == 3
        
        # Apple 사용자 수 조회
        apple_count = repository.count_by_provider(session, UserProvider.APPLE)
        assert apple_count == 2
    
    def test_count_by_role(self, session, clean_database):
        """역할별 사용자 수 조회 테스트"""
        repository = UserRepository()
        
        # USER 역할 사용자 생성
        for i in range(4):
            user = User(
                role=UserRole.USER,
                provider=UserProvider.GUEST
            )
            repository.create(session, user)
        
        # ADMIN 역할 사용자 생성
        for i in range(2):
            user = User(
                role=UserRole.ADMIN,
                provider=UserProvider.GUEST
            )
            repository.create(session, user)
        
        # USER 역할 사용자 수 조회
        user_count = repository.count_by_role(session, UserRole.USER)
        assert user_count == 4
        
        # ADMIN 역할 사용자 수 조회
        admin_count = repository.count_by_role(session, UserRole.ADMIN)
        assert admin_count == 2
    
    def test_exists_by_id(self, session, sample_user, clean_database):
        """ID로 사용자 존재 여부 확인 테스트"""
        repository = UserRepository()
        
        # 존재하는 사용자 확인
        exists = repository.exists_by_id(session, sample_user.user_id)
        assert exists is True
        
        # 존재하지 않는 사용자 확인
        exists = repository.exists_by_id(session, str(ULID()))
        assert exists is False
    
    def test_exists_by_openid(self, session, clean_database):
        """OpenID로 사용자 존재 여부 확인 테스트"""
        repository = UserRepository()
        
        # 사용자 생성
        user = User(
            role=UserRole.USER,
            provider=UserProvider.GOOGLE,
            openid="test_openid"
        )
        repository.create(session, user)
        
        # 존재하는 OpenID 확인
        exists = repository.exists_by_openid(session, "test_openid")
        assert exists is True
        
        # 존재하지 않는 OpenID 확인
        exists = repository.exists_by_openid(session, "nonexistent_openid")
        assert exists is False
    
    def test_find_recent(self, session, clean_database):
        """최근 생성된 사용자 조회 테스트"""
        repository = UserRepository()
        
        # 여러 사용자 생성
        for i in range(5):
            user = User(
                role=UserRole.USER,
                provider=UserProvider.GUEST
            )
            repository.create(session, user)
        
        # 최근 사용자 조회 (3명)
        recent_users = repository.find_recent(session, limit=3)
        
        # 결과 확인
        assert len(recent_users) == 3
        # 생성 시간 순서 확인 (최신순)
        for i in range(len(recent_users) - 1):
            assert recent_users[i].created_at >= recent_users[i + 1].created_at


@pytest.mark.database
@pytest.mark.repository
class TestUserProfileRepository:
    """UserProfileRepository 클래스의 기능을 테스트합니다."""
    
    def test_create_profile(self, session, sample_user, clean_database):
        """사용자 프로필 생성 테스트"""
        repository = UserProfileRepository()
        
        # 프로필 생성
        profile = UserProfile(
            user_id=sample_user.user_id,
            nickname="test_nickname",
            image="https://example.com/image.jpg",
            region=UserRegion.KR
        )
        
        created_profile = repository.create(session, profile)
        
        # 결과 확인
        assert created_profile.user_id == sample_user.user_id
        assert created_profile.nickname == "test_nickname"
        assert created_profile.image == "https://example.com/image.jpg"
        assert created_profile.region == UserRegion.KR
        assert created_profile.created_at is not None
        assert created_profile.updated_at is not None
    
    def test_find_by_user_id(self, session, sample_user_profile, clean_database):
        """사용자 ID로 프로필 조회 테스트"""
        repository = UserProfileRepository()
        
        # 프로필 조회
        found_profile = repository.find_by_user_id(session, sample_user_profile.user_id)
        
        # 결과 확인
        assert found_profile is not None
        assert found_profile.user_id == sample_user_profile.user_id
        assert found_profile.nickname == sample_user_profile.nickname
    
    def test_find_by_nickname(self, session, clean_database):
        """닉네임으로 프로필 조회 테스트"""
        repository = UserProfileRepository()
        
        # 사용자와 프로필 생성
        from src.common.rdb.domain.user.models import User
        user = User(role=UserRole.USER, provider=UserProvider.GUEST)
        session.add(user)
        session.flush()
        
        profile = UserProfile(
            user_id=user.user_id,
            nickname="unique_nickname",
            region=UserRegion.KR
        )
        repository.create(session, profile)
        
        # 닉네임으로 조회
        found_profile = repository.find_by_nickname(session, "unique_nickname")
        
        # 결과 확인
        assert found_profile is not None
        assert found_profile.nickname == "unique_nickname"
    
    def test_find_by_region(self, session, clean_database):
        """지역별 프로필 조회 테스트"""
        repository = UserProfileRepository()
        
        # 여러 사용자와 프로필 생성
        for i in range(3):
            user = User(role=UserRole.USER, provider=UserProvider.GUEST)
            session.add(user)
            session.flush()
            
            profile = UserProfile(
                user_id=user.user_id,
                nickname=f"user_{i}",
                region=UserRegion.KR
            )
            repository.create(session, profile)
        
        # KR 지역 프로필 조회
        kr_profiles = repository.find_by_region(session, UserRegion.KR)
        
        # 결과 확인
        assert len(kr_profiles) == 3
        for profile in kr_profiles:
            assert profile.region == UserRegion.KR
    
    def test_search_by_nickname(self, session, clean_database):
        """닉네임 패턴으로 프로필 검색 테스트"""
        repository = UserProfileRepository()
        
        # 여러 사용자와 프로필 생성
        nicknames = ["test_user", "test_admin", "guest_user", "admin_test"]
        for nickname in nicknames:
            user = User(role=UserRole.USER, provider=UserProvider.GUEST)
            session.add(user)
            session.flush()
            
            profile = UserProfile(
                user_id=user.user_id,
                nickname=nickname,
                region=UserRegion.KR
            )
            repository.create(session, profile)
        
        # "test"로 검색
        test_profiles = repository.search_by_nickname(session, "test")
        
        # 결과 확인
        assert len(test_profiles) == 3
        for profile in test_profiles:
            assert "test" in profile.nickname
    
    def test_update_profile(self, session, sample_user_profile, clean_database):
        """프로필 업데이트 테스트"""
        repository = UserProfileRepository()
        
        # 프로필 정보 수정
        sample_user_profile.nickname = "updated_nickname"
        sample_user_profile.image = "https://example.com/updated_image.jpg"
        sample_user_profile.region = UserRegion.US
        
        updated_profile = repository.update(session, sample_user_profile)
        
        # 결과 확인
        assert updated_profile.nickname == "updated_nickname"
        assert updated_profile.image == "https://example.com/updated_image.jpg"
        assert updated_profile.region == UserRegion.US
        assert updated_profile.updated_at is not None
    
    def test_delete_profile(self, session, sample_user_profile, clean_database):
        """프로필 삭제 테스트"""
        repository = UserProfileRepository()
        
        # 프로필 삭제
        result = repository.delete(session, sample_user_profile)
        
        # 결과 확인
        assert result is True
        
        # 삭제 확인
        found_profile = repository.find_by_user_id(session, sample_user_profile.user_id)
        assert found_profile is None
    
    def test_find_all(self, session, clean_database):
        """모든 프로필 조회 테스트"""
        repository = UserProfileRepository()
        
        # 여러 사용자와 프로필 생성
        for i in range(3):
            user = User(role=UserRole.USER, provider=UserProvider.GUEST)
            session.add(user)
            session.flush()
            
            profile = UserProfile(
                user_id=user.user_id,
                nickname=f"user_{i}",
                region=UserRegion.KR
            )
            repository.create(session, profile)
        
        # 모든 프로필 조회
        all_profiles = repository.find_all(session)
        
        # 결과 확인
        assert len(all_profiles) == 3
    
    def test_count(self, session, clean_database):
        """프로필 수 조회 테스트"""
        repository = UserProfileRepository()
        
        # 여러 사용자와 프로필 생성
        for i in range(5):
            user = User(role=UserRole.USER, provider=UserProvider.GUEST)
            session.add(user)
            session.flush()
            
            profile = UserProfile(
                user_id=user.user_id,
                nickname=f"user_{i}",
                region=UserRegion.KR
            )
            repository.create(session, profile)
        
        # 프로필 수 조회
        count = repository.count(session)
        
        # 결과 확인
        assert count == 5
    
    def test_exists_by_nickname(self, session, clean_database):
        """닉네임으로 프로필 존재 여부 확인 테스트"""
        repository = UserProfileRepository()
        
        # 사용자와 프로필 생성
        user = User(role=UserRole.USER, provider=UserProvider.GUEST)
        session.add(user)
        session.flush()
        
        profile = UserProfile(
            user_id=user.user_id,
            nickname="unique_nickname",
            region=UserRegion.KR
        )
        repository.create(session, profile)
        
        # 존재하는 닉네임 확인
        exists = repository.exists_by_nickname(session, "unique_nickname")
        assert exists is True
        
        # 존재하지 않는 닉네임 확인
        exists = repository.exists_by_nickname(session, "nonexistent_nickname")
        assert exists is False


@pytest.mark.database
@pytest.mark.repository
class TestUserBillingRepository:
    """UserBillingRepository 클래스의 기능을 테스트합니다."""
    
    def test_create_billing(self, session, sample_user, clean_database):
        """사용자 결제 정보 생성 테스트"""
        repository = UserBillingRepository()
        
        # 결제 정보 생성
        billing = UserBilling(
            user_id=sample_user.user_id,
            billing=UserBillingType.PLUS
        )
        
        created_billing = repository.create(session, billing)
        
        # 결과 확인
        assert created_billing.user_id == sample_user.user_id
        assert created_billing.billing == UserBillingType.PLUS
        assert created_billing.created_at is not None
        assert created_billing.updated_at is not None
    
    def test_find_by_user_id(self, session, sample_user_billing, clean_database):
        """사용자 ID로 결제 정보 조회 테스트"""
        repository = UserBillingRepository()
        
        # 결제 정보 조회
        found_billing = repository.find_by_user_id(session, sample_user_billing.user_id)
        
        # 결과 확인
        assert found_billing is not None
        assert found_billing.user_id == sample_user_billing.user_id
        assert found_billing.billing == sample_user_billing.billing
    
    def test_find_by_billing_type(self, session, clean_database):
        """결제 플랜별 사용자 조회 테스트"""
        repository = UserBillingRepository()
        
        # 여러 사용자와 결제 정보 생성
        for i in range(3):
            user = User(role=UserRole.USER, provider=UserProvider.GUEST)
            session.add(user)
            session.flush()
            
            billing = UserBilling(
                user_id=user.user_id,
                billing=UserBillingType.PLUS
            )
            repository.create(session, billing)
        
        # PLUS 플랜 사용자 조회
        plus_users = repository.find_by_billing_type(session, UserBillingType.PLUS)
        
        # 결과 확인
        assert len(plus_users) == 3
        for billing in plus_users:
            assert billing.billing == UserBillingType.PLUS
    
    def test_update_billing(self, session, sample_user_billing, clean_database):
        """결제 정보 업데이트 테스트"""
        repository = UserBillingRepository()
        
        # 결제 정보 수정
        sample_user_billing.billing = UserBillingType.PRO
        
        updated_billing = repository.update(session, sample_user_billing)
        
        # 결과 확인
        assert updated_billing.billing == UserBillingType.PRO
        assert updated_billing.updated_at is not None
    
    def test_delete_billing(self, session, sample_user_billing, clean_database):
        """결제 정보 삭제 테스트"""
        repository = UserBillingRepository()
        
        # 결제 정보 삭제
        result = repository.delete(session, sample_user_billing)
        
        # 결과 확인
        assert result is True
        
        # 삭제 확인
        found_billing = repository.find_by_user_id(session, sample_user_billing.user_id)
        assert found_billing is None
    
    def test_find_all(self, session, clean_database):
        """모든 결제 정보 조회 테스트"""
        repository = UserBillingRepository()
        
        # 여러 사용자와 결제 정보 생성
        for i in range(3):
            user = User(role=UserRole.USER, provider=UserProvider.GUEST)
            session.add(user)
            session.flush()
            
            billing = UserBilling(
                user_id=user.user_id,
                billing=UserBillingType.FREE
            )
            repository.create(session, billing)
        
        # 모든 결제 정보 조회
        all_billings = repository.find_all(session)
        
        # 결과 확인
        assert len(all_billings) == 3
    
    def test_count(self, session, clean_database):
        """결제 정보 수 조회 테스트"""
        repository = UserBillingRepository()
        
        # 여러 사용자와 결제 정보 생성
        for i in range(5):
            user = User(role=UserRole.USER, provider=UserProvider.GUEST)
            session.add(user)
            session.flush()
            
            billing = UserBilling(
                user_id=user.user_id,
                billing=UserBillingType.FREE
            )
            repository.create(session, billing)
        
        # 결제 정보 수 조회
        count = repository.count(session)
        
        # 결과 확인
        assert count == 5
    
    def test_count_by_billing_type(self, session, clean_database):
        """결제 플랜별 사용자 수 조회 테스트"""
        repository = UserBillingRepository()
        
        # FREE 플랜 사용자 생성
        for i in range(3):
            user = User(role=UserRole.USER, provider=UserProvider.GUEST)
            session.add(user)
            session.flush()
            
            billing = UserBilling(
                user_id=user.user_id,
                billing=UserBillingType.FREE
            )
            repository.create(session, billing)
        
        # PLUS 플랜 사용자 생성
        for i in range(2):
            user = User(role=UserRole.USER, provider=UserProvider.GUEST)
            session.add(user)
            session.flush()
            
            billing = UserBilling(
                user_id=user.user_id,
                billing=UserBillingType.PLUS
            )
            repository.create(session, billing)
        
        # FREE 플랜 사용자 수 조회
        free_count = repository.count_by_billing_type(session, UserBillingType.FREE)
        assert free_count == 3
        
        # PLUS 플랜 사용자 수 조회
        plus_count = repository.count_by_billing_type(session, UserBillingType.PLUS)
        assert plus_count == 2


@pytest.mark.database
@pytest.mark.repository
class TestUserAlertRepository:
    """UserAlertRepository 클래스의 기능을 테스트합니다."""
    
    def test_create_alert(self, session, sample_user, clean_database):
        """사용자 알림 정보 생성 테스트"""
        repository = UserAlertRepository()
        
        # 알림 정보 생성
        alert = UserAlert(
            user_id=sample_user.user_id,
            fcm_token="test_fcm_token_123",
            is_alerted=True
        )
        
        created_alert = repository.create(session, alert)
        
        # 결과 확인
        assert created_alert.user_id == sample_user.user_id
        assert created_alert.fcm_token == "test_fcm_token_123"
        assert created_alert.is_alerted is True
        assert created_alert.created_at is not None
        assert created_alert.updated_at is not None
    
    def test_find_by_user_id(self, session, sample_user_alert, clean_database):
        """사용자 ID로 알림 정보 조회 테스트"""
        repository = UserAlertRepository()
        
        # 알림 정보 조회
        found_alert = repository.find_by_user_ids(session, [sample_user_alert.user_id])
        
        # 결과 확인
        assert found_alert is not None
        assert found_alert[0].user_id == sample_user_alert.user_id
        assert found_alert[0].fcm_token == sample_user_alert.fcm_token
        assert found_alert[0].is_alerted == sample_user_alert.is_alerted
    
    def test_find_by_fcm_token(self, session, sample_user_alert, clean_database):
        """FCM 토큰으로 알림 정보 조회 테스트"""
        repository = UserAlertRepository()
        
        # FCM 토큰으로 조회
        found_alert = repository.find_by_fcm_token(session, sample_user_alert.fcm_token)
        
        # 결과 확인
        assert found_alert is not None
        assert found_alert.fcm_token == sample_user_alert.fcm_token
        assert found_alert.user_id == sample_user_alert.user_id
    
    def test_find_by_alert_enabled(self, session, clean_database):
        """알림 활성화된 사용자 조회 테스트"""
        repository = UserAlertRepository()
        
        # 여러 사용자와 알림 정보 생성
        for i in range(3):
            user = User(role=UserRole.USER, provider=UserProvider.GUEST)
            session.add(user)
            session.flush()
            
            alert = UserAlert(
                user_id=user.user_id,
                fcm_token=f"fcm_token_{i}",
                is_alerted=True
            )
            repository.create(session, alert)
        
        # 알림 비활성화 사용자 생성
        user = User(role=UserRole.USER, provider=UserProvider.GUEST)
        session.add(user)
        session.flush()
        
        alert = UserAlert(
            user_id=user.user_id,
            fcm_token="disabled_fcm_token",
            is_alerted=False
        )
        repository.create(session, alert)
        
        # 알림 활성화된 사용자 조회
        enabled_alerts = repository.find_by_alert_enabled(session, alert_enabled=True)
        
        # 결과 확인
        assert len(enabled_alerts) == 3
        for alert in enabled_alerts:
            assert alert.is_alerted is True
    
    def test_find_active_alerts_with_tokens(self, session, clean_database):
        """FCM 토큰이 있는 활성 알림 조회 테스트"""
        repository = UserAlertRepository()
        
        # FCM 토큰이 있는 활성 알림 생성
        for i in range(3):
            user = User(role=UserRole.USER, provider=UserProvider.GUEST)
            session.add(user)
            session.flush()
            
            alert = UserAlert(
                user_id=user.user_id,
                fcm_token=f"active_fcm_token_{i}",
                is_alerted=True
            )
            repository.create(session, alert)
        
        # FCM 토큰이 없는 활성 알림 생성
        user = User(role=UserRole.USER, provider=UserProvider.GUEST)
        session.add(user)
        session.flush()
        
        alert = UserAlert(
            user_id=user.user_id,
            fcm_token=None,
            is_alerted=True
        )
        repository.create(session, alert)
        
        # FCM 토큰이 있는 활성 알림 조회
        active_alerts = repository.find_active_alerts_with_tokens(session)
        
        # 결과 확인
        assert len(active_alerts) == 3
        for alert in active_alerts:
            assert alert.is_alerted is True
            assert alert.fcm_token is not None
    
    def test_update_alert(self, session, sample_user_alert, clean_database):
        """알림 정보 업데이트 테스트"""
        repository = UserAlertRepository()
        
        # 알림 정보 수정
        sample_user_alert.fcm_token = "updated_fcm_token"
        sample_user_alert.is_alerted = False
        
        updated_alert = repository.update(session, sample_user_alert)
        
        # 결과 확인
        assert updated_alert.fcm_token == "updated_fcm_token"
        assert updated_alert.is_alerted is False
        assert updated_alert.updated_at is not None
    
    def test_delete_alert(self, session, sample_user_alert, clean_database):
        """알림 정보 삭제 테스트"""
        repository = UserAlertRepository()
        
        # 알림 정보 삭제
        result = repository.delete(session, sample_user_alert)
        
        # 결과 확인
        assert result is True
        
        # 삭제 확인
        found_alert = repository.find_by_user_ids(session, [sample_user_alert.user_id])
        assert len(found_alert) == 0
    
    def test_find_all(self, session, clean_database):
        """모든 알림 정보 조회 테스트"""
        repository = UserAlertRepository()
        
        # 여러 사용자와 알림 정보 생성
        for i in range(3):
            user = User(role=UserRole.USER, provider=UserProvider.GUEST)
            session.add(user)
            session.flush()
            
            alert = UserAlert(
                user_id=user.user_id,
                fcm_token=f"fcm_token_{i}",
                is_alerted=True
            )
            repository.create(session, alert)
        
        # 모든 알림 정보 조회
        all_alerts = repository.find_all(session)
        
        # 결과 확인
        assert len(all_alerts) == 3
    
    def test_count(self, session, clean_database):
        """알림 정보 수 조회 테스트"""
        repository = UserAlertRepository()
        
        # 여러 사용자와 알림 정보 생성
        for i in range(5):
            user = User(role=UserRole.USER, provider=UserProvider.GUEST)
            session.add(user)
            session.flush()
            
            alert = UserAlert(
                user_id=user.user_id,
                fcm_token=f"fcm_token_{i}",
                is_alerted=True
            )
            repository.create(session, alert)
        
        # 알림 정보 수 조회
        count = repository.count(session)
        
        # 결과 확인
        assert count == 5
    
    def test_count_by_alert_enabled(self, session, clean_database):
        """알림 활성화 상태별 사용자 수 조회 테스트"""
        repository = UserAlertRepository()
        
        # 알림 활성화 사용자 생성
        for i in range(4):
            user = User(role=UserRole.USER, provider=UserProvider.GUEST)
            session.add(user)
            session.flush()
            
            alert = UserAlert(
                user_id=user.user_id,
                fcm_token=f"enabled_fcm_token_{i}",
                is_alerted=True
            )
            repository.create(session, alert)
        
        # 알림 비활성화 사용자 생성
        for i in range(2):
            user = User(role=UserRole.USER, provider=UserProvider.GUEST)
            session.add(user)
            session.flush()
            
            alert = UserAlert(
                user_id=user.user_id,
                fcm_token=f"disabled_fcm_token_{i}",
                is_alerted=False
            )
            repository.create(session, alert)
        
        # 알림 활성화 사용자 수 조회
        enabled_count = repository.count_by_alert_enabled(session, is_alerted=True)
        assert enabled_count == 4
        
        # 알림 비활성화 사용자 수 조회
        disabled_count = repository.count_by_alert_enabled(session, is_alerted=False)
        assert disabled_count == 2
    
    def test_count_active_with_tokens(self, session, clean_database):
        """FCM 토큰이 있는 활성 알림 수 조회 테스트"""
        repository = UserAlertRepository()
        
        # FCM 토큰이 있는 활성 알림 생성
        for i in range(3):
            user = User(role=UserRole.USER, provider=UserProvider.GUEST)
            session.add(user)
            session.flush()
            
            alert = UserAlert(
                user_id=user.user_id,
                fcm_token=f"active_fcm_token_{i}",
                is_alerted=True
            )
            repository.create(session, alert)
        
        # FCM 토큰이 없는 활성 알림 생성
        user = User(role=UserRole.USER, provider=UserProvider.GUEST)
        session.add(user)
        session.flush()
        
        alert = UserAlert(
            user_id=user.user_id,
            fcm_token=None,
            is_alerted=True
        )
        repository.create(session, alert)
        
        # FCM 토큰이 있는 활성 알림 수 조회
        active_count = repository.count_active_with_tokens(session)
        
        # 결과 확인
        assert active_count == 3 