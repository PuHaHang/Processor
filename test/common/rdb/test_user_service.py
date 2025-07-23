# """
# User 도메인 Service 테스트

# 이 모듈은 User 도메인의 UserService 클래스를 테스트합니다.
# 실제 PostgreSQL 데이터베이스와 연결하여 테스트합니다.
# """

# import pytest
# import uuid
# from unittest.mock import patch

# from src.common.rdb.domain.user.models import User, UserProfile, UserBilling, UserAlert, UserRole, UserProvider, UserRegion, UserBillingType
# from src.common.rdb.domain.user.user_service import UserService
# from src.common.rdb.domain.user.dto import CreateUserDto, UpdateUserDto, SearchUsersDto, GetUsersByBillingDto


# @pytest.mark.database
# @pytest.mark.service
# class TestUserService:
#     """UserService 클래스의 기능을 테스트합니다."""
    
#     def test_create_user(self, session, clean_database):
#         """사용자 생성 테스트"""
#         service = UserService()
        
#         # 사용자 생성 DTO
#         create_dto = CreateUserDto(
#             nickname="test_user",
#             role=UserRole.USER,
#             provider=UserProvider.GOOGLE,
#             openid="google_123456",
#             image="https://example.com/image.jpg",
#             billing=UserBillingType.FREE,
#             region=UserRegion.KR,
#             fcm_token="test_fcm_token",
#             alert_flag=True
#         )
        
#         # 사용자 생성
#         created_user = service.create_user(session, create_dto)
        
#         # 결과 확인
#         assert created_user.role == UserRole.USER
#         assert created_user.provider == UserProvider.GOOGLE
#         assert created_user.openid == "google_123456"
#         assert created_user.user_id is not None
        
#         # 관련 정보가 모두 생성되었는지 확인
#         assert created_user.profile is not None
#         assert created_user.profile.nickname == "test_user"
#         assert created_user.profile.image == "https://example.com/image.jpg"
#         assert created_user.profile.region == UserRegion.KR
        
#         assert created_user.billing is not None
#         assert created_user.billing.billing == UserBillingType.FREE
        
#         assert created_user.alert is not None
#         assert created_user.alert.fcm_token == "test_fcm_token"
#         assert created_user.alert.alert_flag is True
    
#     def test_create_guest_user(self, session, clean_database):
#         """GUEST 사용자 생성 테스트"""
#         service = UserService()
        
#         # GUEST 사용자 생성 DTO
#         create_dto = CreateUserDto(
#             nickname="guest_user",  # 실제로는 자동 생성됨
#             role=UserRole.USER,
#             provider=UserProvider.GUEST,
#             billing=UserBillingType.FREE,
#             region=UserRegion.KR,
#             alert_flag=False
#         )
        
#         # 사용자 생성
#         created_user = service.create_user(session, create_dto)
        
#         # 결과 확인
#         assert created_user.provider == UserProvider.GUEST
#         assert created_user.openid is None
        
#         # GUEST 사용자는 닉네임이 "guest_숫자" 형태로 자동 생성
#         assert created_user.profile is not None
#         assert created_user.profile.nickname.startswith("guest_")
#         assert len(created_user.profile.nickname) > 6  # "guest_" + 10자리 숫자
    
#     def test_get_user_by_id(self, session, complete_user, clean_database):
#         """ID로 사용자 조회 테스트"""
#         service = UserService()
        
#         # 사용자 조회
#         found_user = service.get_user_by_id(session, complete_user.user_id)
        
#         # 결과 확인
#         assert found_user is not None
#         assert found_user.user_id == complete_user.user_id
#         assert found_user.role == complete_user.role
#         assert found_user.provider == complete_user.provider
        
#         # 관련 정보가 모두 로드되었는지 확인
#         assert found_user.profile is not None
#         assert found_user.billing is not None
#         assert found_user.alert is not None
    
#     def test_get_user_by_id_not_found(self, session, clean_database):
#         """존재하지 않는 ID로 사용자 조회 테스트"""
#         service = UserService()
        
#         # 존재하지 않는 사용자 조회
#         found_user = service.get_user_by_id(session, str(uuid.uuid4()))
        
#         # 결과 확인
#         assert found_user is None
    
#     def test_get_user_by_openid(self, session, clean_database):
#         """OpenID로 사용자 조회 테스트"""
#         service = UserService()
        
#         # 사용자 생성
#         create_dto = CreateUserDto(
#             nickname="openid_user",
#             role=UserRole.USER,
#             provider=UserProvider.GOOGLE,
#             openid="google_unique_openid",
#             billing=UserBillingType.FREE,
#             region=UserRegion.KR,
#             alert_flag=False
#         )
#         created_user = service.create_user(session, create_dto)
        
#         # OpenID로 조회
#         found_user = service.get_user_by_openid(session, "google_unique_openid")
        
#         # 결과 확인
#         assert found_user is not None
#         assert found_user.user_id == created_user.user_id
#         assert found_user.openid == "google_unique_openid"
    
#     def test_delete_user(self, session, complete_user, clean_database):
#         """사용자 삭제 테스트"""
#         service = UserService()
        
#         # 사용자 삭제
#         result = service.delete_user(session, complete_user.user_id)
        
#         # 결과 확인
#         assert result is True
        
#         # 삭제 확인
#         found_user = service.get_user_by_id(session, complete_user.user_id)
#         assert found_user is None
    
#     def test_delete_user_not_found(self, session, clean_database):
#         """존재하지 않는 사용자 삭제 테스트"""
#         service = UserService()
        
#         # 존재하지 않는 사용자 삭제
#         result = service.delete_user(session, str(uuid.uuid4()))
        
#         # 결과 확인
#         assert result is False
    
#     def test_get_users_by_billing(self, session, clean_database):
#         """결제 플랜별 사용자 조회 테스트"""
#         service = UserService()
        
#         # 여러 결제 플랜의 사용자 생성
#         billing_types = [UserBillingType.FREE, UserBillingType.PLUS, UserBillingType.FREE]
#         created_users = []
        
#         for i, billing_type in enumerate(billing_types):
#             create_dto = CreateUserDto(
#                 nickname=f"user_{i}",
#                 role=UserRole.USER,
#                 provider=UserProvider.GUEST,
#                 billing=billing_type,
#                 region=UserRegion.KR,
#                 alert_flag=False
#             )
#             created_users.append(service.create_user(session, create_dto))
        
#         # FREE 플랜 사용자 조회
#         billing_dto = GetUsersByBillingDto(
#             billing=UserBillingType.FREE,
#             limit=10,
#             offset=0
#         )
#         free_users = service.get_users_by_billing(session, billing_dto)
        
#         # 결과 확인
#         assert len(free_users) == 2
#         for user in free_users:
#             assert user.billing is not None
#             assert user.billing.billing == UserBillingType.FREE
    
#     def test_update_user(self, session, complete_user, clean_database):
#         """사용자 정보 수정 테스트"""
#         service = UserService()
        
#         # 사용자 수정 DTO
#         update_dto = UpdateUserDto(
#             user_uuid=complete_user.user_id,
#             nickname="updated_nickname",
#             image="https://example.com/updated_image.jpg",
#             billing=UserBillingType.PLUS,
#             region=UserRegion.US,
#             role=UserRole.ADMIN,
#             fcm_token="updated_fcm_token",
#             alert_flag=False
#         )
        
#         # 사용자 수정
#         updated_user = service.update_user(session, update_dto)
        
#         # 결과 확인
#         assert updated_user is not None
#         assert updated_user.user_id == complete_user.user_id
#         assert updated_user.role == UserRole.ADMIN
        
#         # 관련 정보 업데이트 확인
#         assert updated_user.profile is not None
#         assert updated_user.profile.nickname == "updated_nickname"
#         assert updated_user.profile.image == "https://example.com/updated_image.jpg"
#         assert updated_user.profile.region == UserRegion.US
        
#         assert updated_user.billing is not None
#         assert updated_user.billing.billing == UserBillingType.PLUS
        
#         assert updated_user.alert is not None
#         assert updated_user.alert.fcm_token == "updated_fcm_token"
#         assert updated_user.alert.alert_flag is False
    
#     def test_update_user_partial(self, session, complete_user, clean_database):
#         """사용자 부분 수정 테스트"""
#         service = UserService()
        
#         # 원본 닉네임 저장
#         original_nickname = complete_user.profile.nickname
        
#         # 일부 필드만 수정
#         update_dto = UpdateUserDto(
#             user_uuid=complete_user.user_id,
#             billing=UserBillingType.PRO  # 결제 플랜만 수정
#         )
        
#         # 사용자 수정
#         updated_user = service.update_user(session, update_dto)
        
#         # 결과 확인
#         assert updated_user is not None
#         assert updated_user.billing is not None
#         assert updated_user.billing.billing == UserBillingType.PRO
        
#         # 다른 정보는 그대로 유지
#         assert updated_user.profile is not None
#         assert updated_user.profile.nickname == original_nickname
    
#     def test_update_user_not_found(self, session, clean_database):
#         """존재하지 않는 사용자 수정 테스트"""
#         service = UserService()
        
#         # 존재하지 않는 사용자 수정
#         update_dto = UpdateUserDto(
#             user_uuid=str(uuid.uuid4()),
#             nickname="updated_nickname"
#         )
        
#         # 사용자 수정
#         updated_user = service.update_user(session, update_dto)
        
#         # 결과 확인
#         assert updated_user is None
    
#     def test_get_all_users(self, session, clean_database):
#         """모든 사용자 조회 테스트"""
#         service = UserService()
        
#         # 여러 사용자 생성
#         for i in range(3):
#             create_dto = CreateUserDto(
#                 nickname=f"user_{i}",
#                 role=UserRole.USER,
#                 provider=UserProvider.GUEST,
#                 billing=UserBillingType.FREE,
#                 region=UserRegion.KR,
#                 alert_flag=False
#             )
#             service.create_user(session, create_dto)
        
#         # 모든 사용자 조회
#         all_users = service.get_all_users(session)
        
#         # 결과 확인
#         assert len(all_users) == 3
#         for user in all_users:
#             assert user.profile is not None
#             assert user.billing is not None
#             assert user.alert is not None
    
#     def test_get_user_count(self, session, clean_database):
#         """사용자 수 조회 테스트"""
#         service = UserService()
        
#         # 여러 사용자 생성
#         for i in range(5):
#             create_dto = CreateUserDto(
#                 nickname=f"user_{i}",
#                 role=UserRole.USER,
#                 provider=UserProvider.GUEST,
#                 billing=UserBillingType.FREE,
#                 region=UserRegion.KR,
#                 alert_flag=False
#             )
#             service.create_user(session, create_dto)
        
#         # 사용자 수 조회
#         user_count = service.get_user_count(session)
        
#         # 결과 확인
#         assert user_count == 5
    
#     def test_get_user_statistics(self, session, clean_database):
#         """사용자 통계 조회 테스트"""
#         service = UserService()
        
#         # 다양한 사용자 생성
#         test_users = [
#             (UserProvider.GOOGLE, UserBillingType.FREE, UserRegion.KR, UserRole.USER),
#             (UserProvider.KAKAO, UserBillingType.PLUS, UserRegion.US, UserRole.USER),
#             (UserProvider.GOOGLE, UserBillingType.FREE, UserRegion.KR, UserRole.ADMIN),
#         ]
        
#         for provider, billing, region, role in test_users:
#             create_dto = CreateUserDto(
#                 nickname=f"user_{provider.value}",
#                 role=role,
#                 provider=provider,
#                 openid=f"{provider.value}_id" if provider != UserProvider.GUEST else None,
#                 billing=billing,
#                 region=region,
#                 alert_flag=False
#             )
#             service.create_user(session, create_dto)
        
#         # 통계 조회
#         statistics = service.get_user_statistics(session)
        
#         # 결과 확인
#         assert statistics['total_users'] == 3
#         assert statistics['by_provider'][UserProvider.GOOGLE] == 2
#         assert statistics['by_provider'][UserProvider.KAKAO] == 1
#         assert statistics['by_billing'][UserBillingType.FREE] == 2
#         assert statistics['by_billing'][UserBillingType.PLUS] == 1
#         assert statistics['by_region'][UserRegion.KR] == 2
#         assert statistics['by_region'][UserRegion.US] == 1
#         assert statistics['by_role'][UserRole.USER] == 2
#         assert statistics['by_role'][UserRole.ADMIN] == 1
    
#     def test_search_users(self, session, clean_database):
#         """사용자 검색 테스트"""
#         service = UserService()
        
#         # 검색할 사용자들 생성
#         test_users = [
#             ("김철수", UserProvider.GOOGLE, UserBillingType.FREE, UserRegion.KR, UserRole.USER),
#             ("이영희", UserProvider.KAKAO, UserBillingType.PLUS, UserRegion.US, UserRole.USER),
#             ("박김치", UserProvider.GOOGLE, UserBillingType.FREE, UserRegion.KR, UserRole.ADMIN),
#         ]
        
#         for nickname, provider, billing, region, role in test_users:
#             create_dto = CreateUserDto(
#                 nickname=nickname,
#                 role=role,
#                 provider=provider,
#                 openid=f"{provider.value}_id" if provider != UserProvider.GUEST else None,
#                 billing=billing,
#                 region=region,
#                 alert_flag=False
#             )
#             service.create_user(session, create_dto)
        
#         # 닉네임으로 검색
#         search_dto = SearchUsersDto(
#             nickname="김",
#             limit=10,
#             offset=0
#         )
#         search_results = service.search_users(session, search_dto)
        
#         # 결과 확인
#         assert len(search_results) == 2
#         for user in search_results:
#             assert "김" in user.profile.nickname
        
#         # 제공자로 검색
#         search_dto = SearchUsersDto(
#             provider=UserProvider.GOOGLE,
#             limit=10,
#             offset=0
#         )
#         google_users = service.search_users(session, search_dto)
        
#         # 결과 확인
#         assert len(google_users) == 2
#         for user in google_users:
#             assert user.provider == UserProvider.GOOGLE
        
#         # 복합 검색 (지역 + 결제 플랜)
#         search_dto = SearchUsersDto(
#             region=UserRegion.KR,
#             billing=UserBillingType.FREE,
#             limit=10,
#             offset=0
#         )
#         kr_free_users = service.search_users(session, search_dto)
        
#         # 결과 확인
#         assert len(kr_free_users) == 2
#         for user in kr_free_users:
#             assert user.profile.region == UserRegion.KR
#             assert user.billing.billing == UserBillingType.FREE
    
#     def test_update_fcm_token(self, session, complete_user, clean_database):
#         """FCM 토큰 업데이트 테스트"""
#         service = UserService()
        
#         # FCM 토큰 업데이트
#         updated_user = service.update_fcm_token(session, complete_user.user_id, "new_fcm_token")
        
#         # 결과 확인
#         assert updated_user is not None
#         assert updated_user.alert.fcm_token == "new_fcm_token"
    
#     def test_update_fcm_token_new_alert(self, session, sample_user, clean_database):
#         """알림 정보가 없는 사용자의 FCM 토큰 업데이트 테스트"""
#         service = UserService()
        
#         # FCM 토큰 업데이트 (알림 정보 없음)
#         updated_user = service.update_fcm_token(session, sample_user.user_id, "new_fcm_token")
        
#         # 결과 확인
#         assert updated_user is not None
#         assert updated_user.alert.fcm_token == "new_fcm_token"
#         assert updated_user.alert.alert_flag is False  # 기본값
    
#     def test_update_fcm_token_not_found(self, session, clean_database):
#         """존재하지 않는 사용자의 FCM 토큰 업데이트 테스트"""
#         service = UserService()
        
#         # 존재하지 않는 사용자의 FCM 토큰 업데이트
#         updated_user = service.update_fcm_token(session, str(uuid.uuid4()), "new_fcm_token")
        
#         # 결과 확인
#         assert updated_user is None
    
#     def test_update_alert_flag(self, session, complete_user, clean_database):
#         """알림 플래그 업데이트 테스트"""
#         service = UserService()
        
#         # 알림 플래그 업데이트
#         updated_user = service.update_alert_flag(session, complete_user.user_id, False)
        
#         # 결과 확인
#         assert updated_user is not None
#         assert updated_user.alert.alert_flag is False
    
#     def test_update_alert_flag_new_alert(self, session, sample_user, clean_database):
#         """알림 정보가 없는 사용자의 알림 플래그 업데이트 테스트"""
#         service = UserService()
        
#         # 알림 플래그 업데이트 (알림 정보 없음)
#         updated_user = service.update_alert_flag(session, sample_user.user_id, True)
        
#         # 결과 확인
#         assert updated_user is not None
#         assert updated_user.alert.alert_flag is True
#         assert updated_user.alert.fcm_token is None  # 기본값
    
#     def test_update_alert_flag_not_found(self, session, clean_database):
#         """존재하지 않는 사용자의 알림 플래그 업데이트 테스트"""
#         service = UserService()
        
#         # 존재하지 않는 사용자의 알림 플래그 업데이트
#         updated_user = service.update_alert_flag(session, str(uuid.uuid4()), True)
        
#         # 결과 확인
#         assert updated_user is None
    
#     @pytest.mark.slow
#     def test_create_user_performance(self, session, clean_database):
#         """사용자 생성 성능 테스트"""
#         service = UserService()
#         import time
        
#         # 여러 사용자 생성 시간 측정
#         start_time = time.time()
        
#         for i in range(10):
#             create_dto = CreateUserDto(
#                 nickname=f"perf_user_{i}",
#                 role=UserRole.USER,
#                 provider=UserProvider.GUEST,
#                 billing=UserBillingType.FREE,
#                 region=UserRegion.KR,
#                 alert_flag=False
#             )
#             service.create_user(session, create_dto)
        
#         end_time = time.time()
#         execution_time = end_time - start_time
        
#         # 10개 사용자 생성이 2초 이내에 완료되어야 함
#         assert execution_time < 2.0
        
#         # 생성된 사용자 수 확인
#         user_count = service.get_user_count(session)
#         assert user_count == 10 