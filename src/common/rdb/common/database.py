"""
데이터베이스 연결 및 세션 관리를 위한 SQLModel 설정 모듈

이 모듈은 PostgreSQL 데이터베이스와의 연결을 관리하고,
SQLModel 세션을 통한 데이터베이스 작업을 지원합니다.
SQLModel 프레임워크를 최대한 활용하여 타입 안전성과 성능을 보장합니다.
"""

import os
import logging
from typing import Generator, Optional
from contextlib import contextmanager
import logfire

from sqlalchemy.dialects.postgresql import psycopg2 as psycopg2_dialect
import psycopg2
from sqlmodel import create_engine, Session, SQLModel, text
from sqlalchemy import event, MetaData
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import QueuePool
from aws_secretsmanager_caching import SecretCache, SecretCacheConfig
import botocore.session

# 로깅 설정
logger = logging.getLogger(__name__)

# SQLModel 메타데이터 설정 (naming_convention을 통한 제약조건 이름 자동 생성)
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

cached_secret = None
def get_secret():
    global cached_secret
    if cached_secret is not None:
        return cached_secret

    import json
    import boto3
    from botocore.exceptions import ClientError

    secret_name = os.getenv("AWS_RDS_SECRETS_MANAGER", "")
    region_name = os.getenv("AWS_REGION", "ap-northeast-2")

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    secret = get_secret_value_response['SecretString']
    secret_dict = json.loads(secret)
    cached_secret = secret_dict
    return secret_dict

class DatabaseManager:
    """SQLModel 기반 데이터베이스 연결과 세션 관리를 담당하는 클래스"""

    def __init__(self):
        self.engine = None
        self._is_initialized = False
        self._secret_cache = None

    def initialize(
        self,
        echo: bool = False,
        pool_size: int = 10,
        max_overflow: int = 20,
        pool_timeout: int = 30,
        pool_recycle: int = 3600
    ) -> None:
        """
        SQLModel 데이터베이스 연결을 초기화합니다.

        Args:
            database_url: 데이터베이스 URL (기본값: 환경변수에서 읽음)
            echo: SQL 쿼리 로깅 여부
            pool_size: 커넥션 풀 기본 크기
            max_overflow: 커넥션 풀 최대 추가 연결 수
            pool_timeout: 커넥션 대기 시간(초)
            pool_recycle: 커넥션 재활용 시간(초)
        """
        if self._is_initialized:
            logfire.warn('데이터베이스가 이미 초기화됨')
            return
        
        try:
                # Secrets Manager 캐시 준비 (선택: refresh interval 조정)
            if os.getenv("AWS_SECRETS_MANAGER_ENABLED", ""):
                sm_client = botocore.session.get_session().create_client(
                    'secretsmanager',
                    region_name=os.getenv("AWS_REGION", "ap-northeast-2"),
                )
                cache_cfg = SecretCacheConfig(
                    # 기본값: secret_refresh_interval=3600.0
                    # 필요 시 더 짧게: secret_refresh_interval=900.0
                )
                self._secret_cache = SecretCache(config=cache_cfg, client=sm_client)

            self.engine = create_engine(
                "postgresql+psycopg2://",
                creator=self._connect,        # 연결 시점마다 최신 시크릿 사용
                echo=echo,
                poolclass=QueuePool,
                pool_size=pool_size,
                max_overflow=max_overflow,
                pool_timeout=pool_timeout,
                pool_recycle=pool_recycle,    # 회전 이후 새 연결은 최신 비번으로
                pool_pre_ping=True,           # 죽은 커넥션 감지
                future=True,
            )

            # 메타데이터 naming convention 설정
            if SQLModel.metadata.naming_convention != naming_convention:
                SQLModel.metadata.naming_convention = naming_convention

            # 연결 이벤트 리스너 등록
            self._setup_event_listeners()

            self._is_initialized = True
            logfire.info('SQLModel 데이터베이스 초기화 성공')

        except Exception as e:
            logfire.error('데이터베이스 초기화 실패 {error}', error=str(e))
            raise

    def _connect(self):
        """환경변수로부터 데이터베이스 URL을 구성합니다."""
        secret = {}
        if os.getenv("AWS_SECRETS_MANAGER_ENABLED", "false") == "true":
            secret = get_secret()
        else:
            secret = {
                "username": os.getenv("POSTGRES_USER", ""),
                "password": os.getenv("POSTGRES_PW", ""),
            }
        
        username = secret['username']
        password = secret['password']

        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        database = os.getenv("POSTGRES_DB", "postgres")

        return psycopg2.connect(
            host=host,
            port=port,
            dbname=database,
            user=username,
            password=password,
            sslmode='require'
        )

    def _setup_event_listeners(self) -> None:
        """SQLAlchemy 이벤트 리스너를 설정합니다."""
        
        if self.engine is None:
            return
            
        @event.listens_for(self.engine, "connect")
        def set_postgresql_settings(dbapi_connection, connection_record):
            """연결 시 PostgreSQL 설정을 적용합니다."""
            if self.engine is not None and self.engine.dialect.name == "postgresql":
                # PostgreSQL 특화 설정
                with dbapi_connection.cursor() as cursor:
                    cursor.execute("SET timezone = 'UTC'")
                    cursor.execute("SET statement_timeout = '300s'")

    def create_tables(self) -> None:
        """모든 SQLModel 테이블을 생성합니다."""
        if not self._is_initialized or self.engine is None:
            raise RuntimeError("Database not initialized")

        try:
            SQLModel.metadata.create_all(bind=self.engine)
            logfire.info('SQLModel 테이블 생성 성공')
        except Exception as e:
            logfire.error('테이블 생성 실패 {error}', error=str(e))
            raise

    def drop_tables(self) -> None:
        """모든 SQLModel 테이블을 삭제합니다."""
        if not self._is_initialized or self.engine is None:
            raise RuntimeError("Database not initialized")

        try:
            SQLModel.metadata.drop_all(bind=self.engine)
            logfire.info('SQLModel 테이블 삭제 성공')
        except Exception as e:
            logfire.error('테이블 삭제 실패 {error}', error=str(e))
            raise

    def get_session(self) -> Session:
        """새로운 SQLModel 세션을 생성합니다."""
        if not self._is_initialized or self.engine is None:
            raise RuntimeError("Database not initialized")

        return Session(self.engine)

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        자동 커밋/롤백이 적용되는 SQLModel 세션 컨텍스트 매니저

        Usage:
            with db_manager.session_scope() as session:
                # SQLModel 데이터베이스 작업 수행
                session.add(user)
                session.commit()
                # 자동으로 커백됨
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logfire.error('세션 롤백 발생 {error}', error=str(e))
            raise
        finally:
            session.close()

    def close(self) -> None:
        """데이터베이스 연결을 종료합니다."""
        if self.engine:
            self.engine.dispose()
            self._is_initialized = False
            logfire.info('데이터베이스 연결 종료')
    def health_check(self) -> bool:
        """데이터베이스 연결 상태를 확인합니다."""
        if not self._is_initialized or self.engine is None:
            return False
        
        try:
            with self.session_scope() as session:
                session.exec(text("SELECT 1"))
                return True
        except Exception as e:
            logfire.error('데이터베이스 헬스 체크 실패 {error}', error=str(e))
            return False
