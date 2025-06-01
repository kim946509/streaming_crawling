# 🎶 Streaming Platform Auto Crawling
스트리밍 플랫폼(YouTube, YouTube Music, Genie)을 자동으로 크롤링해오는 레퍼지토리입니다.

### ⚙️ Technology Stack
1. Django Rest Framework
2. Celery, Celery Beat
3. Redis
4. BeautifulSoup
5. Selenium
---
### 🤷🏻‍♀️ How to use this repository
⬇️ Download Repository
```
git clone https://github.com/minkyungbae/streaming_crawling.git
```
⬇️ Make Env
```
python -m venv env
```
⬇️ Activate Env
```
source env/bin/activate
```
⬇️ install Package
```
pip install -r requirements.txt
```

---
### 📁 Folder Structure
```
streaming_crawling
├─ 명령어/                                 # pip, 실행 명령어 txt를 저장한 폴더
├─ API_View/                             # API 함수 관리 폴더
│  ├─ __init__.py
│  ├─ genie_api_views.py                 # Genie API 함수 파일
│  ├─ youtube_api_views.py               # YouTube API 함수 파일
│  └─ youtube_music_api_views.py         # YouTube Music API 함수 파일
├─ celery_setup                          # celery 설정 폴더(크롤링 자동화)
│  ├─ __init__.py
│  ├─ schedule_celery_beat.py            # 크롤링을 반복할 날짜 및 시간 설정한 파일
│  └─ task_setup                         # 자동 크롤링 할 함수 등록 관리 폴더
│     ├─ genie_tasks.py                  # Genie 크롤링 작업 실행 코드 파일
│     ├─ youtube_music_tasks.py          # YouTube Music 크롤링 작업 실행 코드 파일
│     └─ youtube_tasks.py                # YouTube 크롤링 작업 실행 코드 파일
├─ crawling_view                         # 크롤링 함수 관리 폴더
│  ├─ __init__.py
│  ├─ test_serch.py                      # 개발자용 크롤링 즉시 확인 파일
│  ├─ genie_crawler_views.py             # Genie 크롤링 항목 설정 코드 파일
│  ├─ youtube_crawler_views.py           # YouTube 크롤링 항목 설정 코드 파일
│  └─ youtube_music_crawler_views.py     # YouTube Music 크롤링 항목 설정 코드 파일
├─ config                                # django project 설정 폴더
│  ├─ __init__.py                        # celery 등록한 파일
│  ├─ celery.py                          # celery 설정한 파일
│  ├─ settings.py
│  ├─ urls.py
├─ streaming_site_list                   # 크롤링할 스트리밍 플랫폼 관리 app 폴더
│  ├─ __init__.py
│  ├─ genie/                             # 지니에서 노래 조회수 추출 설정하는 앱
│  ├─ youtube/                           # 유튜브에서 노래 조회수 추출 설정하는 앱
│  └─ youtube_music/                     # 유튜브 뮤직에서 노래 조회수 추출 설정하는 앱
├─ logging_setting.py                    # logging 기본 설정
├─ manage.py
├─ README.md
└─requirements.txt                       # 패키지 기록 txt 파일
```