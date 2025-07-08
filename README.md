# 🎶 Streaming Platform Auto Crawling System

스트리밍 플랫폼(YouTube, YouTube Music, Genie)을 자동으로 크롤링하여 음악 데이터를 수집하는 Django 기반 시스템입니다.

## 🎯 프로젝트 개요

이 시스템은 다음과 같은 특징을 가집니다:

- **명령어 기반 크롤링**: Django 웹서버 없이 CLI 명령어로 크롤링 실행
- **다중 플랫폼 지원**: YouTube, YouTube Music, Genie 플랫폼 동시 크롤링
- **모듈화된 구조**: 데이터, 뷰, 컨트롤러 계층으로 명확한 역할 분리

## ⚙️ 기술 스택

- **Backend**: Django 4.2.21, Django REST Framework
- **Database**: SQLite (개발), MySQL (운영)
- **Web Scraping**: Selenium 4.33.0, BeautifulSoup4 4.13.4
- **Data Processing**: Pandas 2.2.3, NumPy 2.0.2

## 🚀 설치 및 실행

### 1. 저장소 클론

```bash
git clone https://github.com/minkyungbae/streaming_crawling.git
cd streaming_crawling
```

### 2. 가상환경 생성 및 활성화

```bash
# 가상환경 생성
python -m venv env

# 가상환경 활성화 (Windows)
env\Scripts\activate

# 가상환경 활성화 (Linux/Mac)
source env/bin/activate
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. 데이터베이스 마이그레이션

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. 개발 서버 실행

```bash
python manage.py runserver
```

## 📁 프로젝트 구조

```
streaming_crawling/
├── 📁 crawling_view/                    # 메인 크롤링 앱
│   ├── 📁 models/                       # 데이터 모델
│   │   ├── base.py                      # 기본 모델 클래스
│   │   ├── song_info.py                 # 노래 정보 모델
│   │   ├── crawling_data.py             # 크롤링 데이터 모델
│   │   └── crawling_period.py           # 크롤링 기간 모델
│   ├── 📁 data/                         # 데이터 처리 계층
│   │   ├── song_service.py              # 노래 정보 서비스
│   │   ├── db_writer.py                 # 데이터베이스 저장
│   │   └── csv_writer.py                # CSV 파일 저장
│   ├── 📁 view/                         # 플랫폼별 크롤링 로직
│   │   ├── 📁 genie/                    # Genie 크롤링
│   │   ├── 📁 youtube/                  # YouTube 크롤링
│   │   └── 📁 youtube_music/            # YouTube Music 크롤링
│   ├── 📁 controller/                   # 크롤링 관리 계층
│   │   ├── crawling_manager.py          # 전체 크롤링 관리
│   │   └── platform_crawlers.py         # 플랫폼별 크롤러
│   ├── 📁 utils/                        # 유틸리티 함수
│   └── 📁 test/                         # 테스트 파일
│       ├── test_full_crawling.py        # 전체 크롤링 테스트
│       └── test_platform_crawlers.py    # 플랫폼별 크롤링 테스트
├── 📁 config/                           # Django 설정
│   ├── settings.py                      # 프로젝트 설정
│   ├── urls.py                          # URL 설정
│   └── wsgi.py                          # WSGI 설정
├── 📁 csv_folder/                       # CSV 파일 저장소
├── 📁 명령어/                           # 실행 명령어 모음
├── manage.py                            # Django 관리 명령어
├── requirements.txt                     # Python 패키지 목록
└── README.md                            # 프로젝트 문서
```

## 🔧 사용법

### 1. 전체 크롤링 실행

```bash
# 모든 활성 노래에 대해 모든 플랫폼 크롤링
python manage.py run_crawling_job
```

### 2. 특정 플랫폼 크롤링

```bash
# Genie 플랫폼만 크롤링
python crawling_view/test/test_platform_crawlers.py genie

# YouTube Music 플랫폼만 크롤링
python crawling_view/test/test_platform_crawlers.py youtube_music

# YouTube 플랫폼만 크롤링
python crawling_view/test/test_platform_crawlers.py youtube
```

### 3. 테스트 실행

```bash
# 전체 크롤링 테스트
python crawling_view/test/test_full_crawling.py

# 플랫폼별 크롤링 테스트
python crawling_view/test/test_platform_crawlers.py [platform]
```

## 📊 데이터 모델

### SongInfo (노래 정보)

- `genie_title`, `genie_artist`: Genie 플랫폼 정보
- `youtube_music_title`, `youtube_music_artist`: YouTube Music 플랫폼 정보
- `youtube_url`: YouTube 영상 URL
- `melon_song_id`: Melon 곡 ID

### CrawlingData (크롤링 데이터)

- `song_id`: 노래 ID (SongInfo 참조)
- `views`: 조회수 (정상: 숫자, 미지원: -1, 오류: -999)
- `listeners`: 청취자 수 (정상: 숫자, 미지원: -1, 오류: -999)
- `platform`: 플랫폼명 (genie, youtube, youtube_music)

### CrawlingPeriod (크롤링 기간)

- `song_id`: 노래 ID
- `start_date`, `end_date`: 크롤링 기간
- `is_active`: 활성화 여부

## 🔄 크롤링 프로세스

1. **활성 노래 조회**: `CrawlingPeriod.is_active = True`인 노래들 조회
2. **플랫폼별 필터링**: 각 플랫폼에서 크롤링 가능한 노래 필터링
3. **크롤링 실행**: Selenium을 사용한 웹 스크래핑
4. **데이터 저장**: 데이터베이스 및 CSV 파일 저장

## 🚨 예외 처리

| 상황          | views/listeners 값 | 설명                               |
| ------------- | ------------------ | ---------------------------------- |
| 정상 수집     | 정수 (예: 123456)  | 정상적으로 크롤링된 데이터         |
| 플랫폼 미지원 | -1                 | 해당 플랫폼에서 지원하지 않는 필드 |
| 크롤링 실패   | -999               | 오류 발생 또는 응답 없음           |

## 📝 로그 설정

로그는 `logging_setting.py`에서 관리되며, 크롤링 과정의 모든 활동이 기록됩니다.

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해 주세요.
