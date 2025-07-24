"""
DatabaseManager 테스트

이 모듈은 DatabaseManager 클래스의 기능을 테스트합니다.
"""

import pytest
import tempfile
import os
from sqlmodel import Session, text

from src.common.rdb.common.database import DatabaseManager


@pytest.mark.database
class TestDatabaseManager:
    """DatabaseManager 테스트 클래스"""

    def test_database_manager_initialization(self, test_database_url):
        """DatabaseManager 초기화 테스트"""
        db_manager = DatabaseManager()
        assert db_manager.engine is None
        
        db_manager.initialize(test_database_url)
        assert db_manager.engine is not None
        
        db_manager.close()

    def test_database_connection(self, db_manager):
        """데이터베이스 연결 테스트"""
        assert db_manager.engine is not None
        
        # 연결 테스트
        with db_manager.session_scope() as session:
            result = session.exec(text("SELECT 1")).first()
            assert result == (1, )

    def test_session_creation(self, db_manager):
        """세션 생성 테스트"""
        session = db_manager.get_session()
        assert isinstance(session, Session)
        session.close()

    def test_session_scope_context_manager(self, db_manager):
        """세션 컨텍스트 매니저 테스트"""
        with db_manager.session_scope() as session:
            result = session.exec(text("SELECT 1")).first()
            assert result == (1, )
            # 자동 커밋 확인

    def test_session_rollback_on_error(self, db_manager):
        """에러 시 롤백 테스트"""
        with pytest.raises(Exception):
            with db_manager.session_scope() as session:
                session.exec(text("SELECT * FROM non_existent_table"))
                # 에러 발생 시 자동 롤백

    def test_table_creation_and_drop(self, test_database_url):
        """테이블 생성 및 삭제 테스트"""
        db_manager = DatabaseManager()
        db_manager.initialize(test_database_url)
        
        # 테이블 생성
        db_manager.create_tables()
        
        # 테이블이 생성되었는지 확인
        with db_manager.session_scope() as session:
            result = session.exec(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")).all()
            assert len(result) > 0
        
        db_manager.close()

    def test_database_close(self, test_database_url):
        """데이터베이스 연결 종료 테스트"""
        db_manager = DatabaseManager()
        db_manager.initialize(test_database_url)
        
        assert db_manager.engine is not None
        db_manager.close()
        
        # 연결이 종료되었는지 확인
        assert db_manager.health_check() is False

    def test_database_concurrent_access(self, db_manager):
        """동시 접근 테스트"""
        import threading
        import time
        
        results = []
        
        def worker(worker_id):
            try:
                with db_manager.session_scope() as session:
                    result = session.exec(text("SELECT 1")).first()
                    results.append((worker_id, result))
                    time.sleep(0.1)  # 약간의 지연
            except Exception as e:
                results.append((worker_id, f"Error: {e}"))
        
        # 여러 스레드에서 동시 접근
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 모든 스레드 완료 대기
        for thread in threads:
            thread.join()

        # 모든 스레드가 성공적으로 완료되었는지 확인
        assert len(results) == 5
        for worker_id, result in results:
            assert result == (1, ), f"Worker {worker_id} failed with result: {result}"

    def test_database_transaction_commit(self, db_manager):
        """트랜잭션 커밋 테스트"""
        with db_manager.session_scope() as session:
            # 테스트 데이터 삽입
            session.exec(text("CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY, name TEXT)"))
            session.exec(text("INSERT INTO test_table (id, name) VALUES (1, 'test')"))
            # 자동 커밋 확인
        
        # 데이터가 저장되었는지 확인
        with db_manager.session_scope() as session:
            result = session.exec(text("SELECT name FROM test_table WHERE id = 1")).first()
            assert result == ("test", )

        with db_manager.session_scope() as session:
            session.exec(text("DROP TABLE IF EXISTS test_table"))

    # @pytest.mark.slow
    # def test_database_performance(self, db_manager):
    #     """데이터베이스 성능 테스트"""
    #     import time
        
    #     start_time = time.time()
        
    #     # 여러 세션 생성 및 사용
    #     for _ in range(100):
    #         with db_manager.session_scope() as session:
    #             session.exec(text("SELECT 1")).first()
        
    #     end_time = time.time()
    #     execution_time = end_time - start_time
        
    #     # 성능 기준: 100번의 쿼리가 5초 이내에 완료되어야 함
    #     assert execution_time < 5.0, f"Performance test failed: {execution_time:.2f} seconds" 
