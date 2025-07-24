"""
User 도메인 패키지

이 패키지는 사용자 도메인 관련 모델, 서비스, DTO를 포함합니다.
새로운 ERD 구조에 따라 사용자 정보가 여러 테이블로 분산되어 있습니다.
"""

from .models import User, UserProfile, UserBilling, UserAlert, UserRole, UserProvider, UserRegion, UserBillingType
from .user_service import UserService
from .dto import CreateUserDto, UpdateUserDto, SearchUsersDto, GetUsersByBillingDto
from .repository import UserRepository, UserProfileRepository, UserBillingRepository, UserAlertRepository

__all__ = [
    # Models
    'User',
    'UserProfile',
    'UserBilling',
    'UserAlert',
    
    # Enums
    'UserRole',
    'UserProvider',
    'UserRegion',
    'UserBillingType',
    
    # Services
    'UserService',
    
    # DTOs
    'CreateUserDto',
    'UpdateUserDto',
    'SearchUsersDto',
    'GetUsersByBillingDto',
    
    # Repositories
    'UserRepository',
    'UserProfileRepository',
    'UserBillingRepository',
    'UserAlertRepository'
] 