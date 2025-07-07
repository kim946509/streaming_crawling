# 크롤링 테스트 가이드

## 테스트 파일들

### 1. test_platform_crawlers.py

플랫폼별 크롤링 테스트

```bash
# 모든 플랫폼 테스트
python test_platform_crawlers.py

# 특정 플랫폼 테스트
python test_platform_crawlers.py genie
python test_platform_crawlers.py youtube_music
python test_platform_crawlers.py youtube

# 전체 크롤링 테스트
python test_platform_crawlers.py full
```

### 2. test_full_crawling.py

전체 크롤링 프로세스 테스트

```bash
python test_full_crawling.py
```

## 테스트 결과

각 테스트는 다음 정보를 출력합니다:

- 크롤링 결과 개수
- DB 저장 결과
- CSV 파일 저장 개수

## 저장 기능

모든 테스트는 자동으로 DB와 CSV에 저장됩니다:

- **DB 저장**: CrawlingData 테이블에 저장
- **CSV 저장**: csv_folder에 플랫폼별로 파일 생성
