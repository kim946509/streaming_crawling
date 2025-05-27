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
├─ config
│  ├─ __init__.py
│  ├─ asgi.py
│  ├─ settings.py
│  ├─ urls.py
│  └─ wsgi.py
├─ manage.py
├─ requirements.txt
└─ streaming_site_list
   ├─ youtube
   │  ├─ __init__.py
   │  ├─ admin.py
   │  ├─ apps.py
   │  ├─ migrations
   │  │  └─ __init__.py
   │  ├─ models.py
   │  ├─ tests.py
   │  └─ views.py
   └─ youtube_music
      ├─ __init__.py
      ├─ admin.py
      ├─ apps.py
      ├─ migrations
      │  └─ __init__.py
      ├─ models.py
      ├─ tests.py
      └─ views.py

```