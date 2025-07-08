# Ubuntu 22.04 기반
FROM ubuntu:22.04

# 환경변수 설정
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99

# 시스템 패키지 업데이트 및 필수 패키지 설치 (MySQL 빌드 도구 포함)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    wget \
    curl \
    gnupg \
    unzip \
    cron \
    nano \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    libmysqlclient-dev \
    locales \
    && rm -rf /var/lib/apt/lists/*

# Chrome 설치
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 생성
WORKDIR /app

# Python 의존성 파일 복사
COPY requirements.txt .

# Python 패키지 설치
RUN pip3 install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사 (.env 제외 - 보안상 서버의 .env 파일 사용)
COPY crawling_view/ ./crawling_view/
COPY config/ ./config/
COPY manage.py .
COPY logging_setting.py .

# 로그 디렉토리 생성
RUN mkdir -p logs csv_folder

# cron 작업 설정 (30분마다 실행)
# cron에서 환경변수를 사용하기 위해 환경변수를 cron 환경에 추가
RUN echo "SHELL=/bin/bash" > /etc/cron.d/crawling-cron \
    && echo "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" >> /etc/cron.d/crawling-cron \
    && echo "*/30 * * * * /app/scripts/run_crawling.sh >> /app/logs/cron.log 2>&1" >> /etc/cron.d/crawling-cron \
    && chmod 0644 /etc/cron.d/crawling-cron \
    && crontab /etc/cron.d/crawling-cron

# 실행 스크립트 생성
RUN echo '#!/bin/bash\n\
# cron 서비스 시작\n\
service cron start\n\
\n\
# Django 설정\n\
export DJANGO_SETTINGS_MODULE=config.settings\n\
\n\
# 환경변수를 cron에 전달하기 위해 cron 환경 파일 업데이트\n\
env | grep -v "^_" | grep -v "^\\." | sed "s/^/export /" > /etc/environment\n\
\n\
# 첫 번째 크롤링 실행 (테스트용)\n\
echo "Starting initial crawling test..."\n\
python3 crawling_view/controller/run_crawling.py\n\
\n\
# 컨테이너 계속 실행 (cron이 백그라운드에서 동작)\n\
echo "Container is running. Cron will execute crawling at 00:00, 03:00, 06:00, 09:00, 12:00, 15:00, 18:00, 21:00 daily."\n\
tail -f /dev/null' > /app/start.sh \
    && chmod +x /app/start.sh

# 시작 명령
CMD ["/app/start.sh"]