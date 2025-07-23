"""
데이터베이스 연결 및 세션 관리를 위한 SQLAlchemy 설정 모듈

이 모듈은 PostgreSQL 데이터베이스와의 연결을 관리하고,
SQLAlchemy 세션을 통한 데이터베이스 작업을 지원합니다.
"""

import os
import logging
from typing import Generator, Optional
from contextlib import contextmanager

from sqlalchemy import create_engine, MetaData, event
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import QueuePool

# 로깅 설정
logger = logging.getLogger(__name__)

# 메타데이터 설정 (naming_convention을 통한 제약조건 이름 자동 생성)
metadata = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
})


class Base(DeclarativeBase):
    """SQLAlchemy 모델의 베이스 클래스"""
    metadata = metadata


class DatabaseManager:
    """데이터베이스 연결과 세션 관리를 담당하는 클래스"""

    def __init__(self):
        self.engine = None
        self.session_factory = None
        self._is_initialized = False

    def initialize(
        self,
        database_url: Optional[str] = None,
        echo: bool = False,
        pool_size: int = 10,
        max_overflow: int = 20,
        pool_timeout: int = 30,
        pool_recycle: int = 3600
    ) -> None:
        """
        데이터베이스 연결을 초기화합니다.

        Args:
            database_url: 데이터베이스 URL (기본값: 환경변수에서 읽음)
            echo: SQL 쿼리 로깅 여부
            pool_size: 커넥션 풀 기본 크기
            max_overflow: 커넥션 풀 최대 추가 연결 수
            pool_timeout: 커넥션 대기 시간(초)
            pool_recycle: 커넥션 재활용 시간(초)
        """
        if self._is_initialized:
            logger.warning("Database is already initialized")
            return

        # 데이터베이스 URL 설정
        if database_url is None:
            database_url = self._get_database_url()

        try:
            # 엔진 생성
            self.engine = create_engine(
                database_url,
                echo=echo,
                poolclass=QueuePool,
                pool_size=pool_size,
                max_overflow=max_overflow,
                pool_timeout=pool_timeout,
                pool_recycle=pool_recycle,
                pool_pre_ping=True,  # 연결 상태 확인
            )

            # 세션 팩토리 생성
            self.session_factory = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False
            )

            # 연결 이벤트 리스너 등록
            self._setup_event_listeners()

            self._is_initialized = True
            logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def _get_database_url(self) -> str:
        """환경변수로부터 데이터베이스 URL을 구성합니다."""
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        database = os.getenv("POSTGRES_DB", "puhahang")
        username = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PW", "")
        return f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"

    def _setup_event_listeners(self) -> None:
        """SQLAlchemy 이벤트 리스너를 설정합니다."""
        
        if self.engine is None:
            return
            
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """연결 시 설정을 적용합니다."""
            if self.engine is not None and self.engine.dialect.name == "postgresql":
                # PostgreSQL 특화 설정
                with dbapi_connection.cursor() as cursor:
                    cursor.execute("SET timezone = 'UTC'")

    def create_tables(self) -> None:
        """모든 테이블을 생성합니다."""
        if not self._is_initialized or self.engine is None:
            raise RuntimeError("Database not initialized")

        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise

    def drop_tables(self) -> None:
        """모든 테이블을 삭제합니다."""
        if not self._is_initialized or self.engine is None:
            raise RuntimeError("Database not initialized")

        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info("Tables dropped successfully")
        except Exception as e:
            logger.error(f"Failed to drop tables: {e}")
            raise

    def get_session(self) -> Session:
        """새로운 데이터베이스 세션을 생성합니다."""
        if not self._is_initialized or self.session_factory is None:
            raise RuntimeError("Database not initialized")

        return self.session_factory()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        자동 커밋/롤백이 적용되는 세션 컨텍스트 매니저

        Usage:
            with db_manager.session_scope() as session:
                # 데이터베이스 작업 수행
                session.add(user)
                # 자동으로 커밋됨
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session rolled back due to: {e}")
            raise
        finally:
            session.close()

    def close(self) -> None:
        """데이터베이스 연결을 종료합니다."""
        if self.engine:
            self.engine.dispose()
            self._is_initialized = False
            logger.info("Database connection closed")


# 글로벌 데이터베이스 매니저 인스턴스
db_manager = DatabaseManager()


def get_database_manager() -> DatabaseManager:
    """데이터베이스 매니저 인스턴스를 반환합니다."""
    return db_manager


def get_session() -> Session:
    """새로운 데이터베이스 세션을 생성합니다."""
    return db_manager.get_session()


def initialize_database(
    database_url: Optional[str] = None,
    echo: bool = False,
    create_tables: bool = True
) -> None:
    """
    데이터베이스를 초기화합니다.

    Args:
        database_url: 데이터베이스 URL
        echo: SQL 쿼리 로깅 여부
        create_tables: 테이블 생성 여부
    """
    db_manager.initialize(database_url=database_url, echo=echo)
    
    if create_tables:
        db_manager.create_tables() 