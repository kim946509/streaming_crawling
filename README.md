# Streaming Platform Auto Crawling
스트리밍 플랫폼을 자동으로 크롤링해오는 레퍼지토리입니다.

### Technology Stack
1. Django Rest Framework
2. Celery, Celery Beat
3. Redis
4. BeautifulSoup
5. Selenium

### Folder Structure
```
streaming_crawling
├─ README.md
├─ config                  # django project 설정 폴더
│  ├─ __init__.py
│  ├─ asgi.py
│  ├─ settings.py
│  ├─ urls.py
│  └─ wsgi.py
├─ manage.py
├─ requirements.txt           # 패키지 기록 txt 파일
├─ streaming_site_list        # 스트리밍 조회할 사이트별 앱 관리 폴더
│  ├─ __init__.py
│  └─ youtube                 # 유튜브에서 노래 조회수 추출하는 앱
│     ├─ __init__.py
│     ├─ admin.py
│     ├─ apps.py
│     ├─ migrations
│     │  └─ __init__.py
│     ├─ models.py
│     ├─ serializers          # 각종 serializer들 모아놓은 폴더
│     │  ├─ __init__.py
│     │  └─ api_serializers.py
│     ├─ tests.py
│     ├─ urls.py
│     └─ views                # 각종 view들 모아놓은 폴더
│        ├─ api_views.py      # API 함수 포함된 view 파일
│        └─ crawler.py        # 크롤링 함수 포함된 view 파일
└─ 명령어
   ├─ command_framework.txt
   └─ install_pip_command.txt
```