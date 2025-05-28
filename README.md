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
├─명령어/                                 # pip, 실행 명령어 txt를 저장한 폴더
├─ config                               # django project 설정 폴더
│  ├─ __init__.py                       # celery 등록한 파일
│  ├─ celery.py                         # celery 설정한 파일
│  ├─ settings.py
│  ├─ urls.py
├─ csv_folder                           # 크롤링 결과 csv를 저장 폴더
│  └─ rhoonart                          # 고객사명으로 구분
│     ├─ genie/
│     ├─ youtube/
│     └─ youtube_music/
├─ streaming_site_list                  # 크롤링할 스트리밍 플랫폼 관리 app 폴더
│  ├─ __init__.py
│  └─ youtube                           # 유튜브에서 노래 조회수 추출 설정하는 앱
│     ├─ __init__.py
│     ├─ admin.py                       # admin page 설정한 파일
│     ├─ celery_setup                   # celery 설정 폴더
│     │  ├─ schedule_celery_beat.py     # 크롤링을 반복할 날짜 및 시간 설정한 파일
│     │  └─ tasks.py                    # 어떤 작업을 자동화 할 건지 설정한 파일
│     ├─ migrations/
│     ├─ models.py                      # DB 컬럼 설정한 파일
│     ├─ serializers/                   # 각종 serializer들 모아놓은 폴더
│     ├─ urls.py
│     └─ views                          # 각종 view들 모아놓은 폴더
│        ├─ api_views.py                # API 함수 포함된 view 파일
│        └─ crawler.py                  # 크롤링 함수 포함된 view 파일
├─ logging_setting.py
├─ manage.py
├─ README.md
└─ requirements.txt                     # 패키지 기록 txt 파일

```