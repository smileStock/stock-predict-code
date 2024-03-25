# 기본 이미지 선택
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 파일만 복사
COPY requirements.txt .

# 시스템 패키지 업데이트 및 필요한 라이브러리 및 컴파일 도구 설치
RUN apt-get update && apt-get install -y \
    pkg-config \
    libmariadb-dev \
    gcc \
    python3-dev

# 필요한 패키지 설치
RUN pip3 install --no-cache-dir -r requirements.txt

# 나머지 애플리케이션 파일 복사
COPY . .

# Flask 앱 실행
# 포트는 환경 변수로 설정하는 것이 좋으나, 기본값으로 5000을 사용
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
# 가상 환경 설정이 여전히 필요한 경우, 활성화 명령을 ENTRYPOINT 전에 추가할 수 있으나, Dockerfile에서는 필요 없음

# ENTRYPOINT 대신 CMD 사용, Flask 서버 실행
CMD ["flask", "run"]
