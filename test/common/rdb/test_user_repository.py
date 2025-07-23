# """
# User 도메인 Repository 테스트

# 이 모듈은 User 도메인의 모든 Repository 클래스들을 테스트합니다.
# 실제 PostgreSQL 데이터베이스와 연결하여 테스트합니다.
# """

# import pytest
# import uuid
# from datetime import datetime

# from src.common.rdb.domain.user.models import User, UserProfile, UserBilling, UserAlert, UserRole, UserProvider, UserRegion, UserBillingType
# from src.common.rdb.domain.user.repository import UserRepository, UserProfileRepository, UserBillingRepository, UserAlertRepository


# @pytest.mark.database
# @pytest.mark.repository
# class TestUserRepository:
#     """UserRepository 클래스의 기능을 테스트합니다."""
    
#     def test_create_user(self, session, clean_database):
#         """사용자 생성 테스트"""
#         repository = UserRepository()
        
#         # 사용자 생성
#         user_id = str(uuid.uuid4())
#         user = User(
#             user_id=user_id,
#             role=UserRole.USER,
#             provider=UserProvider.GOOGLE,
#             openid="google_123456"
#         )
        
#         created_user = repository.create(session, user)
        
#         # 결과 확인
#         assert created_user.user_id == user_id
#         assert created_user.role == UserRole.USER
#         assert created_user.provider == UserProvider.GOOGLE
#         assert created_user.openid == "google_123456"
#         assert created_user._time is not None
    
#     def test_find_by_id(self, session, sample_user, clean_database):
#         """ID로 사용자 조회 테스트"""
#         repository = UserRepository()
        
#         # 사용자 조회
#         found_user = repository.find_by_id(session, sample_user.user_id)
        
#         # 결과 확인
#         assert found_user is not None
#         assert found_user.user_id == sample_user.user_id
#         assert found_user.role == sample_user.role
#         assert found_user.provider == sample_user.provider
    
#     def test_find_by_id_not_found(self, session, clean_database):
#         """존재하지 않는 ID로 사용자 조회 테스트"""
#         repository = UserRepository()
        
#         # 존재하지 않는 사용자 조회
#         found_user = repository.find_by_id(session, str(uuid.uuid4()))
        
#         # 결과 확인
#         assert found_user is None
    
#     def test_find_by_openid(self, session, clean_database):
#         """OpenID로 사용자 조회 테스트"""
#         repository = UserRepository()
        
#         # 사용자 생성
#         user_id = str(uuid.uuid4())
#         user = User(
#             user_id=user_id,
#             role=UserRole.USER,
#             provider=UserProvider.GOOGLE,
#             openid="google_unique_id"
#         )
#         repository.create(session, user)
        
#         # OpenID로 조회
#         found_user = repository.find_by_openid(session, "google_unique_id")
        
#         # 결과 확인
#         assert found_user is not None
#         assert found_user.user_id == user_id
#         assert found_user.openid == "google_unique_id"
    
#     def test_find_by_provider(self, session, clean_database):
#         """제공자로 사용자 조회 테스트"""
#         repository = UserRepository()
        
#         # 여러 제공자의 사용자 생성
#         users = []
#         for i, provider in enumerate([UserProvider.GOOGLE, UserProvider.KAKAO, UserProvider.GUEST]):
#             user_id = str(uuid.uuid4())
#             user = User(
#                 user_id=user_id,
#                 role=UserRole.USER,
#                 provider=provider,
#                 openid=f"{provider.value}_id_{i}" if provider != UserProvider.GUEST else None
#             )
#             users.append(repository.create(session, user))
        
#         # Google 제공자로 조회
#         google_users = repository.find_by_provider(session, UserProvider.GOOGLE)
        
#         # 결과 확인
#         assert len(google_users) == 1
#         assert google_users[0].provider == UserProvider.GOOGLE
    
#     def test_find_by_role(self, session, clean_database):
#         """역할로 사용자 조회 테스트"""
#         repository = UserRepository()
        
#         # 여러 역할의 사용자 생성
#         for i, role in enumerate([UserRole.USER, UserRole.ADMIN, UserRole.USER]):
#             user_id = str(uuid.uuid4())
#             user = User(
#                 user_id=user_id,
#                 role=role,
#                 provider=UserProvider.GUEST
#             )
#             repository.create(session, user)
        
#         # USER 역할로 조회
#         user_role_users = repository.find_by_role(session, UserRole.USER)
        
#         # 결과 확인
#         assert len(user_role_users) == 2
#         for user in user_role_users:
#             assert user.role == UserRole.USER
    
#     def test_update_user(self, session, sample_user, clean_database):
#         """사용자 업데이트 테스트"""
#         repository = UserRepository()
        
#         # 사용자 정보 변경
#         sample_user.role = UserRole.ADMIN
#         sample_user.openid = "updated_openid"
        
#         # 업데이트 실행
#         updated_user = repository.update(session, sample_user)
        
#         # 결과 확인
#         assert updated_user.role == UserRole.ADMIN
#         assert updated_user.openid == "updated_openid"
        
#         # 데이터베이스에서 재조회하여 확인
#         found_user = repository.find_by_id(session, sample_user.user_id)
#         assert found_user.role == UserRole.ADMIN
#         assert found_user.openid == "updated_openid"
    
#     def test_delete_user(self, session, sample_user, clean_database):
#         """사용자 삭제 테스트"""
#         repository = UserRepository()
        
#         # 사용자 삭제
#         result = repository.delete(session, sample_user)
        
#         # 결과 확인
#         assert result is True
        
#         # 삭제 확인
#         found_user = repository.find_by_id(session, sample_user.user_id)
#         assert found_user is None
    
#     def test_find_all(self, session, clean_database):
#         """모든 사용자 조회 테스트"""
#         repository = UserRepository()
        
#         # 여러 사용자 생성
#         users = []
#         for i in range(3):
#             user_id = str(uuid.uuid4())
#             user = User(
#                 user_id=user_id,
#                 role=UserRole.USER,
#                 provider=UserProvider.GUEST
#             )
#             users.append(repository.create(session, user))
        
#         # 모든 사용자 조회
#         all_users = repository.find_all(session)
        
#         # 결과 확인
#         assert len(all_users) == 3
    
#     def test_count(self, session, clean_database):
#         """사용자 수 조회 테스트"""
#         repository = UserRepository()
        
#         # 여러 사용자 생성
#         for i in range(5):
#             user_id = str(uuid.uuid4())
#             user = User(
#                 user_id=user_id,
#                 role=UserRole.USER,
#                 provider=UserProvider.GUEST
#             )
#             repository.create(session, user)
        
#         # 사용자 수 조회
#         count = repository.count(session)
        
#         # 결과 확인
#         assert count == 5
    
#     def test_exists_by_id(self, session, sample_user, clean_database):
#         """ID로 사용자 존재 여부 확인 테스트"""
#         repository = UserRepository()
        
#         # 존재하는 사용자 확인
#         exists = repository.exists_by_id(session, sample_user.user_id)
#         assert exists is True
        
#         # 존재하지 않는 사용자 확인
#         exists = repository.exists_by_id(session, str(uuid.uuid4()))
#         assert exists is False
    
#     def test_exists_by_openid(self, session, clean_database):
#         """OpenID로 사용자 존재 여부 확인 테스트"""
#         repository = UserRepository()
        
#         # 사용자 생성
#         user_id = str(uuid.uuid4())
#         user = User(
#             user_id=user_id,
#             role=UserRole.USER,
#             provider=UserProvider.GOOGLE,
#             openid="test_openid"
#         )
#         repository.create(session, user)
        
#         # 존재하는 OpenID 확인
#         exists = repository.exists_by_openid(session, "test_openid")
#         assert exists is True
        
#         # 존재하지 않는 OpenID 확인
#         exists = repository.exists_by_openid(session, "nonexistent_openid")
#         assert exists is False


# @pytest.mark.database
# @pytest.mark.repository
# class TestUserProfileRepository:
#     """UserProfileRepository 클래스의 기능을 테스트합니다."""
    
#     def test_create_profile(self, session, sample_user, clean_database):
#         """사용자 프로필 생성 테스트"""
#         repository = UserProfileRepository()
        
#         # 프로필 생성
#         profile = UserProfile(
#             user_id=sample_user.user_id,
#             nickname="test_nickname",
#             image="https://example.com/image.jpg",
#             region=UserRegion.KR
#         )
        
#         created_profile = repository.create(session, profile)
        
#         # 결과 확인
#         assert created_profile.user_id == sample_user.user_id
#         assert created_profile.nickname == "test_nickname"
#         assert created_profile.image == "https://example.com/image.jpg"
#         assert created_profile.region == UserRegion.KR
#         assert created_profile.created_at is not None
#         assert created_profile.updated_at is not None
    
#     def test_find_by_user_id(self, session, sample_user_profile, clean_database):
#         """사용자 ID로 프로필 조회 테스트"""
#         repository = UserProfileRepository()
        
#         # 프로필 조회
#         found_profile = repository.find_by_user_id(session, sample_user_profile.user_id)
        
#         # 결과 확인
#         assert found_profile is not None
#         assert found_profile.user_id == sample_user_profile.user_id
#         assert found_profile.nickname == sample_user_profile.nickname
    
#     def test_find_by_nickname(self, session, sample_user_profile, clean_database):
#         """닉네임으로 프로필 조회 테스트"""
#         repository = UserProfileRepository()
        
#         # 닉네임으로 조회
#         found_profile = repository.find_by_nickname(session, sample_user_profile.nickname)
        
#         # 결과 확인
#         assert found_profile is not None
#         assert found_profile.nickname == sample_user_profile.nickname
#         assert found_profile.user_id == sample_user_profile.user_id
    
#     def test_find_by_region(self, session, sample_user, clean_database):
#         """지역으로 프로필 조회 테스트"""
#         repository = UserProfileRepository()
        
#         # 여러 지역의 프로필 생성
#         regions = [UserRegion.KR, UserRegion.US, UserRegion.KR]
#         for i, region in enumerate(regions):
#             user_id = str(uuid.uuid4())
#             user = User(user_id=user_id, role=UserRole.USER, provider=UserProvider.GUEST)
#             session.add(user)
#             session.flush()
            
#             profile = UserProfile(
#                 user_id=user_id,
#                 nickname=f"user_{i}",
#                 region=region
#             )
#             repository.create(session, profile)
        
#         # KR 지역으로 조회
#         kr_profiles = repository.find_by_region(session, UserRegion.KR)
        
#         # 결과 확인
#         assert len(kr_profiles) == 2
#         for profile in kr_profiles:
#             assert profile.region == UserRegion.KR
    
#     def test_search_by_nickname(self, session, sample_user, clean_database):
#         """닉네임 패턴으로 프로필 검색 테스트"""
#         repository = UserProfileRepository()
        
#         # 여러 닉네임의 프로필 생성
#         nicknames = ["test_user", "test_admin", "user_test", "admin"]
#         for i, nickname in enumerate(nicknames):
#             user_id = str(uuid.uuid4())
#             user = User(user_id=user_id, role=UserRole.USER, provider=UserProvider.GUEST)
#             session.add(user)
#             session.flush()
            
#             profile = UserProfile(
#                 user_id=user_id,
#                 nickname=nickname,
#                 region=UserRegion.KR
#             )
#             repository.create(session, profile)
        
#         # "test" 패턴으로 검색
#         search_results = repository.search_by_nickname(session, "test")
        
#         # 결과 확인
#         assert len(search_results) == 3
#         for profile in search_results:
#             assert "test" in profile.nickname
    
#     def test_update_profile(self, session, sample_user_profile, clean_database):
#         """프로필 업데이트 테스트"""
#         repository = UserProfileRepository()
        
#         # 프로필 정보 변경
#         sample_user_profile.nickname = "updated_nickname"
#         sample_user_profile.image = "https://example.com/updated.jpg"
#         sample_user_profile.region = UserRegion.US
        
#         # 업데이트 실행
#         updated_profile = repository.update(session, sample_user_profile)
        
#         # 결과 확인
#         assert updated_profile.nickname == "updated_nickname"
#         assert updated_profile.image == "https://example.com/updated.jpg"
#         assert updated_profile.region == UserRegion.US
#         assert updated_profile.updated_at is not None
    
#     def test_delete_profile(self, session, sample_user_profile, clean_database):
#         """프로필 삭제 테스트"""
#         repository = UserProfileRepository()
        
#         # 프로필 삭제
#         result = repository.delete(session, sample_user_profile)
        
#         # 결과 확인
#         assert result is True
        
#         # 삭제 확인
#         found_profile = repository.find_by_user_id(session, sample_user_profile.user_id)
#         assert found_profile is None
    
#     def test_exists_by_nickname(self, session, sample_user_profile, clean_database):
#         """닉네임으로 프로필 존재 여부 확인 테스트"""
#         repository = UserProfileRepository()
        
#         # 존재하는 닉네임 확인
#         exists = repository.exists_by_nickname(session, sample_user_profile.nickname)
#         assert exists is True
        
#         # 존재하지 않는 닉네임 확인
#         exists = repository.exists_by_nickname(session, "nonexistent_nickname")
#         assert exists is False


# @pytest.mark.database
# @pytest.mark.repository
# class TestUserBillingRepository:
#     """UserBillingRepository 클래스의 기능을 테스트합니다."""
    
#     def test_create_billing(self, session, sample_user, clean_database):
#         """사용자 결제 정보 생성 테스트"""
#         repository = UserBillingRepository()
        
#         # 결제 정보 생성
#         billing = UserBilling(
#             user_id=sample_user.user_id,
#             billing=UserBillingType.PLUS
#         )
        
#         created_billing = repository.create(session, billing)
        
#         # 결과 확인
#         assert created_billing.user_id == sample_user.user_id
#         assert created_billing.billing == UserBillingType.PLUS
#         assert created_billing.created_at is not None
#         assert created_billing.updated_at is not None
    
#     def test_find_by_user_id(self, session, sample_user_billing, clean_database):
#         """사용자 ID로 결제 정보 조회 테스트"""
#         repository = UserBillingRepository()
        
#         # 결제 정보 조회
#         found_billing = repository.find_by_user_id(session, sample_user_billing.user_id)
        
#         # 결과 확인
#         assert found_billing is not None
#         assert found_billing.user_id == sample_user_billing.user_id
#         assert found_billing.billing == sample_user_billing.billing
    
#     def test_find_by_billing_type(self, session, sample_user, clean_database):
#         """결제 플랜으로 결제 정보 조회 테스트"""
#         repository = UserBillingRepository()
        
#         # 여러 결제 플랜의 결제 정보 생성
#         billing_types = [UserBillingType.FREE, UserBillingType.PLUS, UserBillingType.FREE]
#         for i, billing_type in enumerate(billing_types):
#             user_id = str(uuid.uuid4())
#             user = User(user_id=user_id, role=UserRole.USER, provider=UserProvider.GUEST)
#             session.add(user)
#             session.flush()
            
#             billing = UserBilling(
#                 user_id=user_id,
#                 billing=billing_type
#             )
#             repository.create(session, billing)
        
#         # FREE 플랜으로 조회
#         free_billings = repository.find_by_billing_type(session, UserBillingType.FREE)
        
#         # 결과 확인
#         assert len(free_billings) == 2
#         for billing in free_billings:
#             assert billing.billing == UserBillingType.FREE
    
#     def test_update_billing(self, session, sample_user_billing, clean_database):
#         """결제 정보 업데이트 테스트"""
#         repository = UserBillingRepository()
        
#         # 결제 정보 변경
#         sample_user_billing.billing = UserBillingType.PRO
        
#         # 업데이트 실행
#         updated_billing = repository.update(session, sample_user_billing)
        
#         # 결과 확인
#         assert updated_billing.billing == UserBillingType.PRO
#         assert updated_billing.updated_at is not None
    
#     def test_delete_billing(self, session, sample_user_billing, clean_database):
#         """결제 정보 삭제 테스트"""
#         repository = UserBillingRepository()
        
#         # 결제 정보 삭제
#         result = repository.delete(session, sample_user_billing)
        
#         # 결과 확인
#         assert result is True
        
#         # 삭제 확인
#         found_billing = repository.find_by_user_id(session, sample_user_billing.user_id)
#         assert found_billing is None
    
#     def test_count_by_billing_type(self, session, sample_user, clean_database):
#         """결제 플랜별 사용자 수 조회 테스트"""
#         repository = UserBillingRepository()
        
#         # 여러 결제 플랜의 결제 정보 생성
#         billing_types = [UserBillingType.FREE, UserBillingType.PLUS, UserBillingType.FREE, UserBillingType.PRO]
#         for i, billing_type in enumerate(billing_types):
#             user_id = str(uuid.uuid4())
#             user = User(user_id=user_id, role=UserRole.USER, provider=UserProvider.GUEST)
#             session.add(user)
#             session.flush()
            
#             billing = UserBilling(
#                 user_id=user_id,
#                 billing=billing_type
#             )
#             repository.create(session, billing)
        
#         # FREE 플랜 사용자 수 조회
#         free_count = repository.count_by_billing_type(session, UserBillingType.FREE)
        
#         # 결과 확인
#         assert free_count == 2


# @pytest.mark.database
# @pytest.mark.repository
# class TestUserAlertRepository:
#     """UserAlertRepository 클래스의 기능을 테스트합니다."""
    
#     def test_create_alert(self, session, sample_user, clean_database):
#         """사용자 알림 정보 생성 테스트"""
#         repository = UserAlertRepository()
        
#         # 알림 정보 생성
#         alert = UserAlert(
#             user_id=sample_user.user_id,
#             fcm_token="test_fcm_token_123",
#             alert_flag=True
#         )
        
#         created_alert = repository.create(session, alert)
        
#         # 결과 확인
#         assert created_alert.user_id == sample_user.user_id
#         assert created_alert.fcm_token == "test_fcm_token_123"
#         assert created_alert.alert_flag is True
#         assert created_alert.created_at is not None
#         assert created_alert.updated_at is not None
    
#     def test_find_by_user_id(self, session, sample_user_alert, clean_database):
#         """사용자 ID로 알림 정보 조회 테스트"""
#         repository = UserAlertRepository()
        
#         # 알림 정보 조회
#         found_alert = repository.find_by_user_id(session, sample_user_alert.user_id)
        
#         # 결과 확인
#         assert found_alert is not None
#         assert found_alert.user_id == sample_user_alert.user_id
#         assert found_alert.fcm_token == sample_user_alert.fcm_token
#         assert found_alert.alert_flag == sample_user_alert.alert_flag
    
#     def test_find_by_fcm_token(self, session, sample_user_alert, clean_database):
#         """FCM 토큰으로 알림 정보 조회 테스트"""
#         repository = UserAlertRepository()
        
#         # FCM 토큰으로 조회
#         found_alert = repository.find_by_fcm_token(session, sample_user_alert.fcm_token)
        
#         # 결과 확인
#         assert found_alert is not None
#         assert found_alert.fcm_token == sample_user_alert.fcm_token
#         assert found_alert.user_id == sample_user_alert.user_id
    
#     def test_find_by_alert_enabled(self, session, sample_user, clean_database):
#         """알림 활성화 여부로 알림 정보 조회 테스트"""
#         repository = UserAlertRepository()
        
#         # 여러 알림 설정의 알림 정보 생성
#         alert_flags = [True, False, True, False]
#         for i, alert_flag in enumerate(alert_flags):
#             user_id = str(uuid.uuid4())
#             user = User(user_id=user_id, role=UserRole.USER, provider=UserProvider.GUEST)
#             session.add(user)
#             session.flush()
            
#             alert = UserAlert(
#                 user_id=user_id,
#                 fcm_token=f"token_{i}",
#                 alert_flag=alert_flag
#             )
#             repository.create(session, alert)
        
#         # 활성화된 알림 정보 조회
#         enabled_alerts = repository.find_by_alert_enabled(session, True)
        
#         # 결과 확인
#         assert len(enabled_alerts) == 2
#         for alert in enabled_alerts:
#             assert alert.alert_flag is True
    
#     def test_find_active_alerts_with_tokens(self, session, sample_user, clean_database):
#         """활성화된 알림 정보 중 FCM 토큰이 있는 것 조회 테스트"""
#         repository = UserAlertRepository()
        
#         # 다양한 상태의 알림 정보 생성
#         test_cases = [
#             (True, "token_1"),  # 활성화 + 토큰 있음
#             (True, None),       # 활성화 + 토큰 없음
#             (False, "token_2"), # 비활성화 + 토큰 있음
#             (True, "token_3"),  # 활성화 + 토큰 있음
#         ]
        
#         for i, (alert_flag, fcm_token) in enumerate(test_cases):
#             user_id = str(uuid.uuid4())
#             user = User(user_id=user_id, role=UserRole.USER, provider=UserProvider.GUEST)
#             session.add(user)
#             session.flush()
            
#             alert = UserAlert(
#                 user_id=user_id,
#                 fcm_token=fcm_token,
#                 alert_flag=alert_flag
#             )
#             repository.create(session, alert)
        
#         # 활성화된 알림 정보 중 FCM 토큰이 있는 것 조회
#         active_alerts_with_tokens = repository.find_active_alerts_with_tokens(session)
        
#         # 결과 확인
#         assert len(active_alerts_with_tokens) == 2
#         for alert in active_alerts_with_tokens:
#             assert alert.alert_flag is True
#             assert alert.fcm_token is not None
    
#     def test_update_alert(self, session, sample_user_alert, clean_database):
#         """알림 정보 업데이트 테스트"""
#         repository = UserAlertRepository()
        
#         # 알림 정보 변경
#         sample_user_alert.fcm_token = "updated_fcm_token"
#         sample_user_alert.alert_flag = False
        
#         # 업데이트 실행
#         updated_alert = repository.update(session, sample_user_alert)
        
#         # 결과 확인
#         assert updated_alert.fcm_token == "updated_fcm_token"
#         assert updated_alert.alert_flag is False
#         assert updated_alert.updated_at is not None
    
#     def test_delete_alert(self, session, sample_user_alert, clean_database):
#         """알림 정보 삭제 테스트"""
#         repository = UserAlertRepository()
        
#         # 알림 정보 삭제
#         result = repository.delete(session, sample_user_alert)
        
#         # 결과 확인
#         assert result is True
        
#         # 삭제 확인
#         found_alert = repository.find_by_user_id(session, sample_user_alert.user_id)
#         assert found_alert is None
    
#     def test_count_by_alert_enabled(self, session, sample_user, clean_database):
#         """알림 활성화 여부별 사용자 수 조회 테스트"""
#         repository = UserAlertRepository()
        
#         # 여러 알림 설정의 알림 정보 생성
#         alert_flags = [True, False, True, False, True]
#         for i, alert_flag in enumerate(alert_flags):
#             user_id = str(uuid.uuid4())
#             user = User(user_id=user_id, role=UserRole.USER, provider=UserProvider.GUEST)
#             session.add(user)
#             session.flush()
            
#             alert = UserAlert(
#                 user_id=user_id,
#                 fcm_token=f"token_{i}",
#                 alert_flag=alert_flag
#             )
#             repository.create(session, alert)
        
#         # 활성화된 알림 사용자 수 조회
#         enabled_count = repository.count_by_alert_enabled(session, True)
        
#         # 결과 확인
#         assert enabled_count == 3
    
#     def test_count_active_with_tokens(self, session, sample_user, clean_database):
#         """활성화된 알림 정보 중 FCM 토큰이 있는 사용자 수 조회 테스트"""
#         repository = UserAlertRepository()
        
#         # 다양한 상태의 알림 정보 생성
#         test_cases = [
#             (True, "token_1"),  # 활성화 + 토큰 있음
#             (True, None),       # 활성화 + 토큰 없음
#             (False, "token_2"), # 비활성화 + 토큰 있음
#             (True, "token_3"),  # 활성화 + 토큰 있음
#             (True, "token_4"),  # 활성화 + 토큰 있음
#         ]
        
#         for i, (alert_flag, fcm_token) in enumerate(test_cases):
#             user_id = str(uuid.uuid4())
#             user = User(user_id=user_id, role=UserRole.USER, provider=UserProvider.GUEST)
#             session.add(user)
#             session.flush()
            
#             alert = UserAlert(
#                 user_id=user_id,
#                 fcm_token=fcm_token,
#                 alert_flag=alert_flag
#             )
#             repository.create(session, alert)
        
#         # 활성화된 알림 정보 중 FCM 토큰이 있는 사용자 수 조회
#         active_count_with_tokens = repository.count_active_with_tokens(session)
        
#         # 결과 확인
#         assert active_count_with_tokens == 3 