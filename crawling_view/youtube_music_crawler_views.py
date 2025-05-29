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

'''===================== logging 설정 ====================='''
logger = logging.getLogger(__name__)


'''===================== ⬇️ 고객사 하위에 서비스별 폴더를 모두 생성 함수 ====================='''
def make_service_dir(company_name, service_name, base_dir='csv_folder/'):
    dir_path = Path(base_dir) / company_name / service_name
    dir_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"✅ {company_name} 하위에 {service_name} 폴더 생성 완료")
    
    
'''===================== ⬇️ CSV 파일 저장 함수 ====================='''
def save_each_to_csv(results, company_name, service_name):
    """
    각 곡별로 company_name/service_name 폴더에 CSV 저장
    """
    make_service_dir(company_name, service_name)
    filepaths = {}
    for song_id, data in results.items():
        CSV_DIR = Path('csv_folder/') / company_name / service_name

        if data.get('view_count') is not None:
            try:
                data['view_count'] = int(data['view_count'])
            except (ValueError, TypeError):
                data['view_count'] = None
                logger.error(f"❌ 조회수 변환 실패: {data['view_count']}")

        song_name = data.get('song_name', 'unknown')
        # 파일명에 사용할 수 없는 문자 제거 및 공백을 언더바로 변환
        song_name_clean = re.sub(r'[\\/:*?"<>|]', '', song_name)
        song_name_clean = song_name_clean.replace(' ', '_')
        if not song_name_clean:
            song_name_clean = 'unknown'
        filename = f"{song_name_clean}.csv" # 파일명
        filepath = CSV_DIR / filename # 파일 저장 경로

        ''' ⬇️ DataFrame 생성 (컬럼 순서 커스텀 가능)'''
        columns = ['song_name', 'view_count', 'youtube_music_url', 'upload_date', 'extracted_date']
        new_df = pd.DataFrame([{col: data.get(col) for col in columns}])

        # 기존 파일이 있으면 읽어서 누적, 없으면 새로 생성
        if filepath.exists():
            try:
                old_df = pd.read_csv(filepath)
                combined_df = pd.concat([old_df, new_df], ignore_index=True)
            except Exception as e:
                logger.error(f"❌ 기존 CSV 읽기 실패: {filepath} - {e}")
                combined_df = new_df
        else:
            combined_df = new_df

        # 저장
        combined_df.to_csv(filepath, index=False, encoding='utf-8-sig')
        logger.info(f"✅ CSV 파일 저장 완료: {filepath}")
        filepaths[song_name] = str(filepath)
    return filepaths


'''===================== ⬇️ driver 설정 ====================='''
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


'''===================== ⬇️ 조회수 텍스트를 숫자로 변환하는 함수 ====================='''
def convert_view_count(view_count_text):
    """
    예: "1.5만 회" -> 15000, "2.3천 회" -> 2300, "1,234회" -> 1234, "9회" -> 9
    """
    if not view_count_text:
        return None
        
    # 쉼표, "조회수", "회" 제거
    view_count_text = view_count_text.replace(',', '').replace('조회수', '').replace('회', '').strip()
    
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


class SearchSong:
    def __init__(self, youtube_music_id, youtube_music_password):
        self.youtube_music_id = youtube_music_id
        self.youtube_music_password = youtube_music_password

    def search(self, artist_name, song_name):
        """
        YouTube Music에서 '아티스트명 곡 명'으로 검색 (여러 셀렉터 시도, 로그인 포함)
        """
        try:
            query = f"{artist_name} {song_name}"
            with setup_driver() as driver:
                driver.get("https://music.youtube.com/")
                wait = WebDriverWait(driver, 10)

                # ------------------------------ 로그인 버튼 클릭 ------------------------------
                try:
                    login_a_tag = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[aria-label="로그인"]')))
                    login_a_tag.click()
                    time.sleep(2)
                except Exception as e:
                    logger.warning("로그인 버튼(a[aria-label='로그인']) 클릭 실패 또는 이미 로그인 페이지입니다.")

                # ------------------------------ 로그인 ------------------------------
                # 이메일 입력 필드가 나타날 때까지 대기
                email_input = wait.until(EC.presence_of_element_located((By.ID, "identifierId")))
                email_input.send_keys(self.youtube_music_id)

                # '다음' 버튼이 클릭 가능할 때까지 대기 후 클릭
                next_button = wait.until(EC.element_to_be_clickable((By.ID, "identifierNext")))
                next_button.click()

                # 비밀번호 입력 필드가 나타날 때까지 대기
                password_input = wait.until(EC.presence_of_element_located((By.NAME, "Passwd")))
                password_input.send_keys(self.youtube_music_password)

                # 로그인 버튼 클릭
                login_button = wait.until(EC.element_to_be_clickable((By.ID, "passwordNext")))
                login_button.click()

                # ------------------------------ 검색 ------------------------------
                # 여러 검색 버튼 셀렉터 시도
                search_button_selectors = [
                    'button#button[aria-label="검색 시작"]',
                    'ytmusic-search-box button#button[aria-label="검색 시작"]',
                    'tp-yt-paper-icon-button[title="검색"]',
                    'ytmusic-search-box button',
                    'button[aria-label="검색"]',
                    'button[aria-label="Search"]',
                    'tp-yt-paper-icon-button[aria-label="검색"]',
                    'tp-yt-paper-icon-button[aria-label="Search"]',
                ]
                search_button = None
                for selector in search_button_selectors:
                    try:
                        search_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                        break
                    except Exception:
                        continue
                if not search_button:
                    raise Exception("검색 버튼을 찾을 수 없습니다.")

                search_button.click()
                time.sleep(2)

                # ------------------------------ 입력창 찾기 ------------------------------
                # 여러 입력창 셀렉터 시도
                search_input_selectors = [
                    'input#input',
                    'input[aria-label="검색"]',
                    'input[aria-label="Search"]',
                    'input[type="text"]',
                    'input[placeholder="검색"]',
                    'input[placeholder="Search"]',
                    'ytmusic-search-box input',
                    'tp-yt-paper-input input',
                    'input[name="search_query"]',
                    'input.ytSearchboxComponentInput',
                    'input.yt-searchbox-input',
                    'input[role="combobox"]',
                    'input[class*="searchbox"]',
                    'input',
                ]
                search_input = None
                for selector in search_input_selectors:
                    try:
                        search_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
                        break
                    except Exception:
                        continue
                if not search_input:
                    raise Exception("검색 입력창을 찾을 수 없습니다.")

                search_input.clear()
                search_input.send_keys(query)
                search_input.send_keys(u'\ue007')  # 엔터키 전송
                time.sleep(2)  # 검색 결과 로딩 대기

                html = driver.page_source
                return html
        except Exception as e:
            logger.error(f"❌ SearchSong.search() 에러: {e}", exc_info=True)
            return None

    def search_multiple(self, artist_song_list):
        results = []
        for artist, song in artist_song_list:
            html = self.search(artist, song)
            results.append({
                "artist": artist,
                "song": song,
                "html": html
            })
        return results

class YouTubeMusicSongCrawler():
    @staticmethod
    def extract_song_info_list(html_list, artist_song_list):
        """
        여러 곡의 HTML 결과와 (아티스트, 곡명) 리스트를 받아 각각의 곡 정보(곡명, 아티스트, 조회수)를 추출
        """
        results = []
        for html, (target_artist, target_song) in zip(html_list, artist_song_list):
            try:
                soup = BeautifulSoup(html, 'html.parser')
                song_items = soup.select('ytmusic-shelf-renderer ytmusic-responsive-list-item-renderer')
                found = False
                for item in song_items:
                    try:
                        # 곡명, 아티스트명 추출 (실제 구조에 맞게 selector 수정)
                        song_name_tag = item.select_one('yt-formatted-string.title')
                        artist_name_tag = item.select_one('yt-formatted-string.subtitle')
                        song_name = song_name_tag.get_text(strip=True) if song_name_tag else None
                        artist_name = artist_name_tag.get_text(strip=True) if artist_name_tag else None
                        # 정확히 일치하는 곡 찾기
                        if song_name and artist_name and song_name.lower() == target_song.lower() and target_artist.lower() in artist_name.lower():
                            # 조회수 추출 (실제 구조에 맞게 selector 수정)
                            view_count_tag = item.select_one('span[title*="조회수"], span[title*="views"]')
                            view_count = view_count_tag.get_text(strip=True) if view_count_tag else None
                            results.append({
                                'song_name': song_name,
                                'artist_name': artist_name,
                                'view_count': view_count
                            })
                            found = True
                            break
                    except Exception as e:
                        continue
                if not found:
                    results.append({'song_name': target_song, 'artist_name': target_artist, 'view_count': None})
            except Exception as e:
                results.append({'song_name': target_song, 'artist_name': target_artist, 'view_count': None})
        return results
