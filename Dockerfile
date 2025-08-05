# Python 3.12 slim 이미지 사용
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치 (ffmpeg, redis-tools 등)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    redis-tools \
    curl \
    awscli \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치를 위한 requirements.txt 복사
COPY requirements.txt .

# Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -U yt-dlp

# 애플리케이션 코드 복사
COPY . .

# Python 경로에 src 디렉토리 추가
ENV PYTHONPATH="${PYTHONPATH}:/app/src"

# 포트 설정 (필요에 따라 수정)
EXPOSE ${SERVER_PORT}

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 애플리케이션 실행
ENTRYPOINT ["/entrypoint.sh"] 