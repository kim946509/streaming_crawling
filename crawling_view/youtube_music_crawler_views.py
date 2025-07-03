from streaming_site_list.youtube_music.models import YouTubeMusicSongViewCount
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
import random
'''===================== logging 설정 ====================='''
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # 로거 레벨을 DEBUG로 설정

# 파일 핸들러 설정
file_handler = logging.FileHandler('youtube_music_crawler.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# 콘솔 핸들러 설정
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 포맷터 설정
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 핸들러 추가
logger.addHandler(file_handler)
logger.addHandler(console_handler)


'''===================== ⬇️ 고객사 하위에 서비스별 폴더를 모두 생성 함수 ====================='''
def make_service_dir(company_name, service_name, base_dir='csv_folder/'):
    dir_path = Path(base_dir) / company_name / service_name
    dir_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"✅ {company_name} 하위에 {service_name} 폴더 생성 완료")


'''===================== ⬇️ DB 저장 함수 ====================='''
def save_to_db(results):
    for song_name, data in results.items():
        YouTubeMusicSongViewCount.objects.update_or_create(
            song_id=data.get('song_id'),
            song_name=data.get('song_name'),
            defaults={
                'artist_name': data.get('artist_name'),
                'view_count': data.get('view_count'),
                'extracted_date': data.get('extracted_date')
            }
        )
    

'''===================== ⬇️ CSV 파일 저장 함수 ====================='''
def save_each_to_csv(results, company_name, service_name):
    """
    각 곡별로 company_name/service_name 폴더에 CSV 저장
    """
    make_service_dir(company_name, service_name)
    filepaths = {}
    for song_name, data in results.items():
        CSV_DIR = Path('csv_folder/') / company_name / service_name

        if data.get('view_count') is not None:
            try:
                data['view_count'] = int(data['view_count'])
            except (ValueError, TypeError):
                data['view_count'] = None
                logger.error(f"❌ 조회수 변환 실패: {data['view_count']}")

        song_name = data.get('song_name', 'unknown')

        # ------------------------------ 파일명에 사용할 수 없는 문자 제거 및 공백을 언더바로 변환 ------------------------------
        song_name_clean = re.sub(r'[\\/:*?"<>|]', '', song_name)
        song_name_clean = song_name_clean.replace(' ', '_')
        if not song_name_clean:
            song_name_clean = 'unknown'
        
        # ------------------------------ 파일명 생성 ------------------------------
        filename = f"{song_name_clean}.csv" # 파일명
        filepath = CSV_DIR / filename # 파일 저장 경로

        # ------------------------------ DataFrame 생성 (컬럼 순서 커스텀 가능) ------------------------------
        columns = ['song_name', 'artist_name', 'view_count', 'extracted_date']
        new_df = pd.DataFrame([{col: data.get(col) for col in columns}])

        # ------------------------------ 기존 파일이 있으면 읽어서 누적, 없으면 새로 생성 ------------------------------
        if filepath.exists():
            try:
                old_df = pd.read_csv(filepath)
                combined_df = pd.concat([old_df, new_df], ignore_index=True)
            except Exception as e:
                logger.error(f"❌ 기존 CSV 읽기 실패: {filepath} - {e}")
                combined_df = new_df
        else:
            combined_df = new_df

        # ------------------------------ 저장 ------------------------------
        combined_df = combined_df.sort_values(by="extracted_date", ascending=False)
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
    # options.add_argument('--incognito')  # 시크릿 모드(캐시나 쿠키의 영향을 받지 않음)
    options.add_argument('--disable-extensions')  # 확장 프로그램 비활성화(성능 향상용)
    options.add_argument('--disable-popup-blocking')  # 팝업 차단 비활성화(필요한 경우 팝업 허용 <- 주석 처리하면 허용)
    options.add_argument('--disable-notifications')  # 알림 비활성화
    options.add_argument('--lang=ko_KR')  # 브라우저 한국어 설정
    options.add_argument('--log-level=3')  # 불필요한 로그 출력을 줄임
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')  # User-Agent 설정(일반 브라우저처럼 보이도록)
    
    # 자동화 탐지 방지 추가 옵션
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # 자동화 탐지 방지 스크립트 실행
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
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

'''===================== ⬇️ 유튜브 뮤직 로그인, 검색 함수 ====================='''
class YouTubeMusicSearchSong:
    def __init__(self, youtube_music_id, youtube_music_password):
        self.youtube_music_id = youtube_music_id
        self.youtube_music_password = youtube_music_password

    def search(self, artist_name, song_name):
        """
        단일 곡 검색 (하위 호환성을 위해 유지)
        여러 곡 검색시에는 search_multiple 사용 권장
        """
        try:
            with setup_driver() as driver:
                wait = WebDriverWait(driver, 10)
                
                # 로그인 및 검색
                if not self._login_once(driver, wait):
                    logger.error("❌ 로그인 실패")
                    return None
                    
                html = self._search_in_session(driver, wait, artist_name, song_name)
                return html
                
        except Exception as e:
            logger.error(f"❌ SearchSong.search() 에러: {e}", exc_info=True)
            return None

    '''===================== ⬇️ 유튜브 뮤직 노래 검색 함수 (여러 곡) - 한 세션에서 연속 검색 ====================='''
    def search_multiple(self, artist_song_list):
        """
        한 번 로그인한 후 같은 세션에서 여러 곡을 연속으로 검색
        """
        results = []
        try:
            with setup_driver() as driver:
                wait = WebDriverWait(driver, 10)
                
                # 한 번만 로그인 수행
                if not self._login_once(driver, wait):
                    logger.error("❌ 로그인 실패")
                    return results
                
                # 여러 곡을 같은 세션에서 연속 검색
                for artist, song in artist_song_list:
                    logger.info(f"🔍 검색 시작: {artist} - {song}")
                    html = self._search_in_session(driver, wait, artist, song)
                    results.append({
                        "artist": artist,
                        "song": song,
                        "html": html
                    })
                    time.sleep(random.uniform(1, 2))  # 검색 간 랜덤 대기
                    
        except Exception as e:
            logger.error(f"❌ search_multiple 에러: {e}", exc_info=True)
            
        return results

    def _login_once(self, driver, wait):
        """
        한 번만 로그인을 수행하는 메서드
        """
        try:
            driver.get("https://music.youtube.com/")
            
            # 로그인 버튼이 보이면(=로그인 안 된 상태)만 로그인 로직 실행
            need_login = False
            try:
                login_btn = driver.find_element(By.CSS_SELECTOR, 'a[aria-label="로그인"]')
                if login_btn.is_displayed():
                    need_login = True
            except Exception:
                # 로그인 버튼이 없으면 이미 로그인된 상태
                need_login = False

            if need_login:
                # 로그인 프로세스 실행
                login_btn.click()
                time.sleep(2)

                # 이메일 입력
                email_input = wait.until(EC.presence_of_element_located((By.ID, "identifierId")))
                time.sleep(random.uniform(0.7, 1.5))
                email_input.send_keys(self.youtube_music_id)
                time.sleep(random.uniform(0.7, 1.5))

                # '다음' 버튼 클릭
                next_button = wait.until(EC.element_to_be_clickable((By.ID, "identifierNext")))
                time.sleep(random.uniform(0.7, 1.5))
                next_button.click()
                time.sleep(random.uniform(0.7, 1.5))

                # 비밀번호 입력
                password_input = wait.until(EC.presence_of_element_located((By.NAME, "Passwd")))
                time.sleep(random.uniform(0.7, 1.5))
                password_input.send_keys(self.youtube_music_password)
                time.sleep(random.uniform(0.7, 1.5))

                # 로그인 버튼 클릭
                login_button = wait.until(EC.element_to_be_clickable((By.ID, "passwordNext")))
                time.sleep(random.uniform(0.7, 1.5))
                login_button.click()
                time.sleep(random.uniform(0.7, 1.5))

                # 본인 인증 화면 감지 및 대기
                time.sleep(2)
                page_source = driver.page_source
                if any(keyword in page_source for keyword in ["보안", "코드", "인증", "확인", "전화", "기기", "추가 확인"]):
                    logger.warning("⚠️ 본인 인증(추가 인증) 화면이 감지되었습니다. 자동화가 중단될 수 있습니다.")
                    time.sleep(60)

                # 로그인 완료 대기
                wait.until_not(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[aria-label="로그인"]')))
                time.sleep(2)
                
            # 유튜브 뮤직 페이지로 이동
            driver.get("https://music.youtube.com/")
            time.sleep(2)
            logger.info("✅ 로그인 성공 및 유튜브 뮤직 페이지 진입")
            return True
            
        except Exception as e:
            logger.error(f"❌ 로그인 실패: {e}")
            return False

    def _search_in_session(self, driver, wait, artist_name, song_name):
        """
        이미 로그인된 세션에서 곡을 검색하는 메서드
        """
        try:
            query = f"{artist_name} {song_name}"
            max_attempts = 3
            
            for attempt in range(max_attempts):
                try:
                    # 검색 버튼 찾기 및 클릭
                    search_button_selectors = [
                        'button#button[aria-label="검색 시작"]', 
                        'button[aria-label="검색"]',
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
                    
                    # 검색어 입력
                    search_input_selectors = [
                        'input#input',
                        'input[aria-label="검색"]',
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
                    time.sleep(0.5)
                    search_input.send_keys(query)
                    time.sleep(1)
                    search_input.send_keys(u'\ue007')  # 엔터키
                    time.sleep(2)
                    
                    # "노래" 탭 클릭
                    song_chip = wait.until(
                        EC.element_to_be_clickable((
                            By.XPATH,
                            '//iron-selector[@id="chips"]//ytmusic-chip-cloud-chip-renderer//yt-formatted-string[text()="노래"]/ancestor::a'
                        ))
                    )
                    song_chip.click()
                    time.sleep(1)
                    
                    # HTML 반환
                    html = driver.page_source
                    logger.info(f"✅ 검색 성공: {artist_name} - {song_name}")
                    return html
                    
                except Exception as e:
                    logger.warning(f"검색 시도 {attempt+1} 실패: {e}")
                    if attempt < max_attempts - 1:
                        # 유튜브 뮤직 메인 페이지로 돌아가기
                        driver.get("https://music.youtube.com/")
                        time.sleep(2)
                    else:
                        logger.error(f"❌ 모든 검색 시도 실패: {artist_name} - {song_name}")
                        
            return None
            
        except Exception as e:
            logger.error(f"❌ _search_in_session 에러: {e}")
            return None

'''===================== ⬇️ 유튜브 뮤직 노래 크롤링 함수 ====================='''
class YouTubeMusicSongCrawler():
    @staticmethod
    def normalize_text(text):
        """특수문자와 공백을 정규화"""
        if not text:
            return ''
        # 유니코드 정규화 (아포스트로피, 따옴표 등을 통일)
        import unicodedata
        text = unicodedata.normalize('NFKC', text)
        # 모든 아포스트로피를 ' 로 통일
        text = text.replace('\u2018', "'").replace('\u2019', "'").replace('\u0060', "'").replace('\u00B4', "'")
        # 공백 정규화 및 소문자 변환
        return ' '.join(text.lower().split())

    @staticmethod
    def extract_song_info_list(html_list, artist_song_list):
        """
        여러 곡의 HTML 결과와 (아티스트, 곡명) 리스트를 받아 각각의 곡 정보(곡명, 아티스트, 조회수)를 추출
        """
        results = []
        for html, (target_artist, target_song) in zip(html_list, artist_song_list):
            try:
                logger.info(f"[시도] '{target_artist} - {target_song}' 정보 추출 시도 중...")
                soup = BeautifulSoup(html, 'html.parser')
                song_items = soup.select('ytmusic-shelf-renderer ytmusic-responsive-list-item-renderer')
                
                found_song = None  # 찾은 곡 정보를 저장할 변수

                for item in song_items:
                    try:
                        # 곡명 추출
                        song_name_tag = item.select_one('yt-formatted-string.title a')
                        song_name = song_name_tag.get_text(strip=True) if song_name_tag else None

                        # 아티스트명 추출
                        artist_column = item.select_one('.secondary-flex-columns')
                        artist_name = None
                        if artist_column:
                            artist_a = artist_column.select_one('a')
                            artist_name = artist_a.get_text(strip=True) if artist_a else None

                        # 조회수 추출
                        view_count = None
                        flex_columns = item.select('yt-formatted-string.flex-column')
                        
                        for flex_col in flex_columns:
                            aria_label = flex_col.get('aria-label', '')
                            if '회' in aria_label and '재생' in aria_label:
                                view_count = aria_label.replace('회', '').replace('재생', '').strip()
                                break

                        # 디버그 로깅
                        if song_name and artist_name:
                            normalized_song = YouTubeMusicSongCrawler.normalize_text(song_name)
                            normalized_target = YouTubeMusicSongCrawler.normalize_text(target_song)
                            normalized_artist = YouTubeMusicSongCrawler.normalize_text(artist_name)
                            normalized_target_artist = YouTubeMusicSongCrawler.normalize_text(target_artist)
                            
                            logger.debug(f"검사 중: 제목='{song_name}' → '{normalized_song}' vs '{target_song}' → '{normalized_target}'")
                            logger.debug(f"검사 중: 아티스트='{artist_name}' → '{normalized_artist}' vs '{target_artist}' → '{normalized_target_artist}'")

                            # 정규화된 문자열로 비교
                            title_match = normalized_song == normalized_target
                            artist_match = normalized_artist == normalized_target_artist
                            
                            logger.debug(f"일치 검사: 제목 일치={title_match}, 아티스트 일치={artist_match}")
                            
                            if title_match and artist_match:
                                found_song = {
                                    'service_name': 'youtube_music',
                                    'song_name': song_name,
                                    'artist_name': artist_name,
                                    'view_count': view_count,
                                    'extracted_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                }
                                logger.info(f"[성공] 일치하는 곡 발견: {song_name} - {artist_name} ({view_count}회)")
                                results.append(found_song)
                                logger.info(f"[결과 추가] {found_song['song_name']} - {found_song['artist_name']}")
                                break  # 일치하는 곡을 찾으면 내부 루프 종료
                            else:
                                if not title_match:
                                    logger.debug(f"제목 불일치: '{normalized_song}' != '{normalized_target}'")
                                if not artist_match:
                                    logger.debug(f"아티스트 불일치: '{normalized_artist}' != '{normalized_target_artist}'")

                    except Exception as e:
                        logger.warning(f"개별 곡 파싱 중 예외 발생: {e}")
                        continue

                # 검색 결과 처리 - found_song이 없을 때만 기본값 추가
                if not found_song:
                    # 일치하는 곡을 찾지 못한 경우 기본값 추가
                    default_result = {
                        'service_name': 'youtube_music',
                        'song_name': target_song,
                        'artist_name': target_artist,
                        'view_count': None,
                        'extracted_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    results.append(default_result)
                    logger.warning(f"[실패] '{target_artist} - {target_song}'와 일치하는 곡을 찾지 못함")

            except Exception as e:
                logger.error(f"전체 파싱 중 예외 발생: {e}")
                # 예외 발생 시 기본값 추가
                results.append({
                    'service_name': 'youtube_music',
                    'song_name': target_song,
                    'artist_name': target_artist,
                    'view_count': None,
                    'extracted_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

        return results
