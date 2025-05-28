# ---------- model 호출 ----------
from streaming_site_list.youtube.models import YouTubeSongViewCount
# ---------- selenium에서 import한 목록 ----------
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# ---------- webdriver에서 import한 목록 ----------
from webdriver_manager.chrome import ChromeDriverManager
from contextlib import contextmanager
# ---------- 크롤링을 위해 필요한 모듈 ----------
from bs4 import BeautifulSoup
from datetime import datetime
import logging, time, re
import pandas as pd
from pathlib import Path

# ---------- CSV 파일 저장 경로 설정 ----------
CSV_DIR = Path("song_crawling_result_csv/youtube")
CSV_DIR.mkdir(exist_ok=True)

# ---------- logging 설정 ----------
logger = logging.getLogger(__name__)


# ---------- ⬇️ driver 설정 ----------
@contextmanager
def setup_driver():
    options = Options()
    # options.add_argument('--headless') # 브라우저 창 비활성화 : 주석처리하면 브라우저 활성화
    options.add_argument('--no-sandbox') # 샌드박스 비활성화 (보안 기능 해제)
    options.add_argument('--disable-dev-shm-usage')# 공유 메모리 사용 비활성화
    options.add_argument('--disable-gpu') # GPU 비활성화
    options.add_argument('--disable-blink-features=AutomationControlled') # 자동화 방지 기능 비활성화
    options.add_argument('--window-size=1920,1080')  # 브라우저 창 크기 고정으로 일관된 크롤링 환경 제공
    options.add_argument('--start-maximized')  # 브라우저 최대화
    options.add_argument('--incognito')  # 시크릿 모드(캐시나 쿠키의 영향을 받지 않음)
    options.add_argument('--disable-extensions')  # 확장 프로그램 비활성화(성능 향상용)
    options.add_argument('--disable-popup-blocking')  # 팝업 차단 비활성화(필요한 경우 팝업 허용 <- 주석 처리하면 허용)
    options.add_argument('--disable-notifications')  # 알림 비활성화
    options.add_argument('--lang=ko_KR')  # 브라우저 한국어 설정
    options.add_argument('--log-level=3')  # 불필요한 로그 출력을 줄임
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')  # User-Agent 설정(일반 브라우저처럼 보이도록)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    logger.info("🟢 Chrome 브라우저 실행 완료")

    try:
        yield driver
    except Exception as e:
        logger.error(f"❌ Chrome 브라우저 실행 실패: {e}", exc_info=True)
        raise
    finally:
        driver.quit()
        logger.info("🔴 Chrome 브라우저 종료")

# ---------- ⬇️ CSV 파일 저장 함수 ----------
def save_to_csv(results, filename=None):
    """
    크롤링 결과를 CSV 파일로 저장합니다.
    """
    if filename is None:
        filename = f"youtube_crawling_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    filepath = CSV_DIR / filename
    
    # 결과를 DataFrame으로 변환
    df = pd.DataFrame.from_dict(results, orient='index')
    df.index.name = 'song_id'
    df.reset_index(inplace=True)
    
    # CSV 파일로 저장
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    logger.info(f"✅ CSV 파일 저장 완료: {filepath}")
    return filepath

# ---------- ⬇️ DB 저장 함수 ----------
def save_to_db(results):
    """
    크롤링 결과를 DB에 저장합니다.
    """
    for song_id, data in results.items():
        try:
            YouTubeSongViewCount.objects.create(
                song_id=song_id,
                song_name=data['song_name'],
                view_count=data['view_count'],
                youtube_url=f"https://www.youtube.com/watch?v={song_id}",
                upload_date=data['upload_date'],
                extracted_date=data['extracted_date']
            )
        except Exception as e:
            logger.error(f"❌ DB 저장 실패 (song_id: {song_id}): {e}")


# ---------- ⬇️ 조회수 텍스트를 숫자로 변환하는 함수 ----------
def convert_view_count(view_count_text):
    """
    예: "1.5만 회" -> 15000, "2.3천 회" -> 2300, "1,234회" -> 1234
    """
    if not view_count_text:
        return None
        
    # 쉼표와 "회" 제거
    view_count_text = view_count_text.replace(',', '').replace('조회수', '').strip()
    
    try:
        # "만" 단위 처리
        if '만' in view_count_text:
            number = float(view_count_text.replace('만', ''))
            return int(number * 10000)
        # "천" 단위 처리
        elif '천' in view_count_text:
            number = float(view_count_text.replace('천', ''))
            return int(number * 1000)
        # 일반 숫자 처리
        else:
            return int(view_count_text)
    except (ValueError, TypeError):
        logger.error(f"조회수 변환 실패: {view_count_text}")
        return None


# ---------- ⬇️ 유튜브 URL에서 song_id 추출하는 함수 ----------
def extract_song_id(youtube_url):
    """
    유튜브 URL에서 song_id 추출
    """
    # 일반적인 유튜브 URL 패턴
    match = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", youtube_url)
    if match:
        return match.group(1)
    return None


# ---------- ⬇️ 크롤링 함수 ----------
def YouTubeSongCrawler(urls):
    """
    유튜브 URL 리스트를 받아 각 동영상의 정보를 크롤링
    Returns:
        dict: {
            song_id: {
                'song_name': str,  # 동영상 제목
                'view_count': int,  # 조회수 (숫자형)
                'youtube_url': str, # 유튜브 URL
                'upload_date': str, # 업로드 날짜 (YYYY.MM.DD 형식)
                'extracted_date': str   # 크롤링한 날짜와 시간 (YYYY.MM.DD 형식)
            }
        }
    """
    results = {}
    url_id_map = {}

    # 각 url에서 song_id 추출
    for url in urls:
        song_id = extract_song_id(url)
        if song_id:
            url_id_map[song_id] = url
        else:
            # 유효하지 않은 URL 처리
            results[url] = {
                'song_name': None,
                'view_count': None,
                'youtube_url': url,
                'upload_date': None,
                'extracted_date': datetime.now().strftime('%Y-%m-%d'),
                'error': '유효하지 않은 유튜브 URL'
            }

    try:
        with setup_driver() as driver:
            wait = WebDriverWait(driver, 10)
            for song_id, url in url_id_map.items():
                try:
                    # 현재 크롤링 시간 기록
                    extracted_date = datetime.now().strftime('%Y.%m.%d')
                    youtube_url = url  # 입력받은 원본 URL 사용

                    # 페이지 로드
                    driver.get(youtube_url)

                    # 동적 로딩을 위한 대기
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, "ytd-watch-metadata")))
                    time.sleep(2)  # 추가 대기 시간

                    # HTML 파싱
                    html = driver.page_source
                    soup = BeautifulSoup(html, 'html.parser')

                    # 동영상 제목 추출
                    title_element = soup.find('h1', {'class': 'style-scope ytd-watch-metadata'})
                    song_name = title_element.text.strip() if title_element else None

                    # 조회수 추출
                    view_count_element = soup.find('span', class_='view-count')
                    view_count_text = view_count_element.text.strip() if view_count_element else None
                    view_count = convert_view_count(view_count_text)

                    # 업로드 날짜 추출
                    info_text = soup.find('div', {'id': 'info-strings'})
                    upload_date = None
                    if info_text:
                        date_text = info_text.find('yt-formatted-string').text
                        # "YYYY. MM. DD." 형식을 "YYYY-MM-DD" 형식으로 변환
                        date_match = re.search(r'(\d{4})\. (\d{1,2})\. (\d{1,2})\.', date_text)
                        if date_match:
                            year, month, day = date_match.groups()
                            upload_date = f"{year}.{month:0>2}.{day:0>2}"

                    # 결과 저장
                    results[song_id] = {
                        'song_name': song_name,
                        'view_count': view_count,
                        'youtube_url': youtube_url,
                        'upload_date': upload_date,
                        'extracted_date': extracted_date
                    }

                    logger.info(f"✅ {song_id} 크롤링 성공 - 제목: {song_name}, 조회수: {view_count}, 업로드일: {upload_date}")

                except Exception as e:
                    logger.error(f"❌ {song_id} 크롤링 실패: {e}", exc_info=True)
                    results[song_id] = {
                        'song_name': None,
                        'view_count': None,
                        'youtube_url': url,
                        'upload_date': None,
                        'extracted_date': datetime.now().strftime('%Y-%m-%d'),
                        'error': str(e)
                    }
                    continue

        # 크롤링 결과를 DB와 CSV 파일에 저장
        save_to_db(results)
        csv_filepath = save_to_csv(results)
        logger.info(f"✅ 크롤링 결과 저장 완료 - CSV: {csv_filepath}")

        return results
    except Exception as e:
        logger.error(f"❌ 크롤러 실행 중 오류 발생: {e}", exc_info=True)
        return results
