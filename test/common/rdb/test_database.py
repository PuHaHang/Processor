# """
# 데이터베이스 연결 모듈 테스트

# 이 모듈은 DatabaseManager 클래스와 관련 기능들을 테스트합니다.
# 실제 PostgreSQL 데이터베이스와 연결하여 테스트합니다.
# """

# import pytest
# import os
# from sqlalchemy import create_engine, text
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import SQLAlchemyError

# from src.common.rdb.common.database import DatabaseManager, Base


# @pytest.mark.database
# class TestDatabaseManager:
#     """DatabaseManager 클래스의 기능을 테스트합니다."""
    
#     def test_database_manager_initialization(self, test_database_url):
#         """데이터베이스 매니저 초기화 테스트"""
#         manager = DatabaseManager()
        
#         # 초기 상태 확인
#         assert manager.engine is None
#         assert manager.session_factory is None
#         assert manager._is_initialized is False
        
#         # 초기화 수행
#         manager.initialize(database_url=test_database_url)
        
#         # 초기화 후 상태 확인
#         assert manager.engine is not None
#         assert manager.session_factory is not None
#         assert manager._is_initialized is True
        
#         # 정리
#         manager.close()
    
#     def test_database_connection(self, db_manager):
#         """데이터베이스 연결 테스트"""
#         # 연결 상태 확인
#         assert db_manager.engine is not None
#         assert db_manager.session_factory is not None
#         assert db_manager._is_initialized is True
        
#         # 기본 쿼리 실행 테스트
#         with db_manager.session_scope() as session:
#             result = session.execute(text("SELECT 1")).scalar()
#             assert result == 1
    
#     def test_session_creation(self, db_manager):
#         """세션 생성 테스트"""
#         # 세션 생성
#         session = db_manager.get_session()
        
#         # 세션 타입 확인
#         assert isinstance(session, Session)
        
#         # 세션 사용 테스트
#         result = session.execute(text("SELECT 1")).scalar()
#         assert result == 1
        
#         # 세션 정리
#         session.close()
    
#     def test_session_scope_context_manager(self, db_manager):
#         """세션 컨텍스트 매니저 테스트"""
#         with db_manager.session_scope() as session:
#             # 세션 타입 확인
#             assert isinstance(session, Session)
            
#             # 테스트 데이터 생성
#             session.execute(text("CREATE TEMPORARY TABLE test_table (id INTEGER)"))
#             session.execute(text("INSERT INTO test_table VALUES (1)"))
            
#             # 데이터 조회
#             result = session.execute(text("SELECT id FROM test_table")).scalar()
#             assert result == 1
        
#         # 컨텍스트 종료 후 자동 커밋 확인
#         with db_manager.session_scope() as session:
#             # 임시 테이블은 세션이 닫히면 사라짐
#             pass
    
#     def test_session_rollback_on_error(self, db_manager):
#         """에러 발생시 세션 롤백 테스트"""
#         with pytest.raises(SQLAlchemyError):
#             with db_manager.session_scope() as session:
#                 # 유효하지 않은 SQL 실행
#                 session.execute(text("INVALID SQL STATEMENT"))
    
#     def test_table_creation_and_drop(self, test_database_url):
#         """테이블 생성 및 삭제 테스트"""
#         manager = DatabaseManager()
#         manager.initialize(database_url=test_database_url)
        
#         # 테이블 생성
#         manager.create_tables()
        
#         # 테이블 존재 확인
#         with manager.session_scope() as session:
#             result = session.execute(text("""
#                 SELECT table_name 
#                 FROM information_schema.tables 
#                 WHERE table_schema = 'public' 
#                 AND table_name = 'users'
#             """)).scalar()
#             assert result == 'users'
        
#         # 테이블 삭제
#         manager.drop_tables()
        
#         # 테이블 삭제 확인
#         with manager.session_scope() as session:
#             result = session.execute(text("""
#                 SELECT table_name 
#                 FROM information_schema.tables 
#                 WHERE table_schema = 'public' 
#                 AND table_name = 'users'
#             """)).scalar()
#             assert result is None
        
#         # 정리
#         manager.close()
    
#     def test_database_url_from_environment(self, monkeypatch):
#         """환경변수로부터 데이터베이스 URL 구성 테스트"""
#         manager = DatabaseManager()
        
#         # 환경변수 설정
#         monkeypatch.setenv("DB_HOST", "testhost")
#         monkeypatch.setenv("DB_PORT", "5433")
#         monkeypatch.setenv("DB_NAME", "testdb")
#         monkeypatch.setenv("DB_USER", "testuser")
#         monkeypatch.setenv("DB_PASSWORD", "testpass")
        
#         # 환경변수로부터 URL 구성 테스트
#         url = manager._get_database_url()
#         expected_url = "postgresql+psycopg2://testuser:testpass@testhost:5433/testdb"
#         assert url == expected_url
    
#     def test_connection_pooling(self, db_manager):
#         """커넥션 풀링 테스트"""
#         # 여러 세션 생성
#         sessions = []
#         for i in range(3):
#             session = db_manager.get_session()
#             sessions.append(session)
            
#             # 각 세션에서 쿼리 실행
#             result = session.execute(text("SELECT 1")).scalar()
#             assert result == 1
        
#         # 모든 세션 정리
#         for session in sessions:
#             session.close()
    
#     # def test_database_initialization_error(self):
#     #     """데이터베이스 초기화 에러 테스트"""
#     #     manager = DatabaseManager()
        
#     #     # 잘못된 URL로 초기화 시도
#     #     with pytest.raises(Exception):
#     #         manager.initialize(database_url="postgresql+psycopg2://invalid:invalid@invalid:0000/invalid")
    
#     def test_database_not_initialized_error(self):
#         """초기화되지 않은 데이터베이스 사용 시 에러 테스트"""
#         manager = DatabaseManager()
        
#         # 초기화하지 않고 테이블 생성 시도
#         with pytest.raises(RuntimeError):
#             manager.create_tables()
        
#         # 초기화하지 않고 세션 생성 시도
#         with pytest.raises(RuntimeError):
#             manager.get_session()
    
#     def test_database_close(self, test_database_url):
#         """데이터베이스 연결 종료 테스트"""
#         manager = DatabaseManager()
#         manager.initialize(database_url=test_database_url)
        
#         # 초기화 상태 확인
#         assert manager._is_initialized is True
#         assert manager.engine is not None
        
#         # 연결 종료
#         manager.close()
        
#         # 종료 후 상태 확인
#         assert manager._is_initialized is False
    
#     def test_database_concurrent_access(self, db_manager):
#         """동시 접근 테스트"""
#         import threading
#         import time
        
#         results = []
        
#         def worker(worker_id):
#             with db_manager.session_scope() as session:
#                 # 간단한 지연 시뮬레이션
#                 time.sleep(0.1)
#                 result = session.execute(text("SELECT :id"), {"id": worker_id}).scalar()
#                 results.append(result)
        
#         # 여러 스레드에서 동시 접근
#         threads = []
#         for i in range(5):
#             thread = threading.Thread(target=worker, args=(i,))
#             threads.append(thread)
#             thread.start()
        
#         # 모든 스레드 완료 대기
#         for thread in threads:
#             thread.join()
        
#         # 결과 확인
#         assert len(results) == 5
#         assert sorted(results) == [0, 1, 2, 3, 4]
    
#     def test_database_transaction_rollback(self, db_manager):
#         """트랜잭션 롤백 테스트"""
#         # 임시 테이블 생성
#         with db_manager.session_scope() as session:
#             session.execute(text("CREATE TEMPORARY TABLE test_rollback (id INTEGER)"))
        
#         # 트랜잭션 롤백 테스트
#         try:
#             with db_manager.session_scope() as session:
#                 session.execute(text("INSERT INTO test_rollback VALUES (1)"))
#                 # 강제로 예외 발생
#                 raise Exception("Test exception")
#         except Exception:
#             pass
        
#         # 롤백 확인
#         with db_manager.session_scope() as session:
#             result = session.execute(text("SELECT COUNT(*) FROM test_rollback")).scalar()
#             assert result == 0
    
#     def test_database_transaction_commit(self, db_manager):
#         """트랜잭션 커밋 테스트"""
#         # 임시 테이블 생성
#         with db_manager.session_scope() as session:
#             session.execute(text("CREATE TEMPORARY TABLE test_commit (id INTEGER)"))
        
#         # 데이터 삽입
#         with db_manager.session_scope() as session:
#             session.execute(text("INSERT INTO test_commit VALUES (1)"))
        
#         # 커밋 확인
#         with db_manager.session_scope() as session:
#             result = session.execute(text("SELECT COUNT(*) FROM test_commit")).scalar()
#             assert result == 1
    
#     def test_database_metadata_naming_convention(self, db_manager):
#         """데이터베이스 메타데이터 네이밍 컨벤션 테스트"""
#         from src.common.rdb.common.database import metadata
        
#         # 네이밍 컨벤션 확인
#         assert "ix" in metadata.naming_convention
#         assert "uq" in metadata.naming_convention
#         assert "ck" in metadata.naming_convention
#         assert "fk" in metadata.naming_convention
#         assert "pk" in metadata.naming_convention
    
#     @pytest.mark.slow
#     def test_database_performance(self, db_manager):
#         """데이터베이스 성능 테스트"""
#         import time
        
#         # 대량 쿼리 실행 시간 측정
#         start_time = time.time()
        
#         with db_manager.session_scope() as session:
#             for i in range(100):
#                 session.execute(text("SELECT :id"), {"id": i})
        
#         end_time = time.time()
#         execution_time = end_time - start_time
        
#         # 1초 이내에 완료되어야 함
#         assert execution_time < 1.0 