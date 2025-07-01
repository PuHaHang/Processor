"""
pytest 설정 모듈

이 모듈은 pytest 실행 시 필요한 경로 설정을 처리합니다.
src 디렉토리와 프로젝트 루트를 Python 경로에 추가하여
테스트에서 모듈을 정상적으로 import할 수 있도록 합니다.
"""

# conftest.py (프로젝트 루트에 생성)
import sys
import os
from pathlib import Path

def pytest_config(config):
    """
    pytest 설정 시 실행되는 함수
    
    Args:
        config: pytest 설정 객체
    """
    # 프로젝트 루트 경로 계산
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    
    # sys.path에 src 디렉토리 추가
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    # 프로젝트 루트도 Python 경로에 추가
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # 설정 완료 메시지 출력
    print(f"✅ pytest에서 Python path 설정 완료:")
    print(f"   - src: {src_path}")
    print(f"   - root: {project_root}")