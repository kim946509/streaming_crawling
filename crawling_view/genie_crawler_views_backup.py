from streaming_site_list.genie.models import GenieSongViewCount
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
import logging, time, re, random
import pandas as pd
from pathlib import Path


'''===================== logging 설정 ====================='''
logger = logging.getLogger(__name__)


'''===================== ⬇️ 고객사 하위에 서비스별 폴더를 모두 생성 함수 ====================='''
def make_service_dir(company_name, service_name, base_dir='csv_folder/'):
    dir_path = Path(base_dir) / company_name / service_name
    dir_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"✅ {company_name} 하위에 {service_name} 폴더 생성 완료")


'''===================== ⬇️ DB 저장 함수 ====================='''
def save_to_db(results):
    for song_name, data in results.items():
        GenieSongViewCount.objects.update_or_create(
            artist_name=data.get('artist_name'),
            song_name=data.get('song_name'),
            defaults={
                'total_person_count': data.get('total_person_count'),
                'total_play_count': data.get('total_play_count'),
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

        if data.get('total_person_count') is not None:
            try:
                data['total_person_count'] = int(data['total_person_count'])
            except (ValueError, TypeError):
                data['total_person_count'] = None
                logger.error(f"❌ 조회수 변환 실패: {data['total_person_count']}")

        song_name = data.get('song_name', 'unknown')

        if data.get('total_play_count') is not None:
            try:
                data['total_play_count'] = int(data['total_play_count'])
            except (ValueError, TypeError):
                data['total_play_count'] = None
                logger.error(f"❌ 조회수 변환 실패: {data['total_play_count']}")

        # ------------------------------ 파일명에 사용할 수 없는 문자 제거 및 공백을 언더바로 변환 ------------------------------
        song_name_clean = re.sub(r'[\\/:*?"<>|]', '', song_name)
        song_name_clean = song_name_clean.replace(' ', '_')
        if not song_name_clean:
            song_name_clean = 'unknown'
        
        # ------------------------------ 파일명 생성 ------------------------------
        filename = f"{song_name_clean}.csv" # 파일명
        filepath = CSV_DIR / filename # 파일 저장 경로

        # ------------------------------ DataFrame 생성 (컬럼 순서 커스텀 가능) ------------------------------
        columns = ['song_name', 'artist_name', 'total_person_count', 'total_play_count', 'extracted_date']
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
    

'''===================== ⬇️ 지니 노래 검색 함수 ====================='''
class GenieSearchSong:
    def search(self, artist_name, song_name):
        try:
            query = f"{artist_name} {song_name}"
            with setup_driver() as driver:
                driver.get("https://www.genie.co.kr/")
                wait = WebDriverWait(driver, 10)
                max_attempts = 5 # 재시도 횟수
            
                # ------------------------------ 검색 입력창 찾기 ------------------------------
                for attempt in range(max_attempts):
                        try:
                            search_input_selectors = [
                                'input#sc-fd',
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
                            time.sleep(random.uniform(0.7, 1.5))
                            search_input.send_keys(query)
                            time.sleep(random.uniform(0.7, 1.5))
                            search_input.send_keys(u'\ue007')  # 엔터키 전송
                            time.sleep(3)

                            # ---------------------- 검색 결과 로딩 대기 후, 곡 정보 버튼 클릭 ----------------------
                            try:
                                # 곡 정보 버튼 찾기 (여러 개 있을 수 있으니 첫 번째 것 클릭)
                                song_info_button = wait.until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.btn-basic.btn-info[onclick^="fnViewSongInfo"]'))
                                )
                                song_info_button.click()
                                logger.info("✅ 곡 정보 페이지 버튼 클릭 완료")

                                # 곡 정보 페이지의 곡명(h2.name)이 나타날 때까지 wait
                                try:
                                    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'h2.name')))
                                    logger.info("✅ 곡 정보 페이지 로딩 완료")
                                except Exception as e:
                                    logger.warning(f"곡 정보 페이지 로딩 대기 실패: {e}")

                                # 곡 정보 페이지의 html 반환
                                return driver.page_source
                            except Exception as e:
                                logger.error(f"❌ 곡 정보 버튼 클릭 실패: {e}")
                                return None
                            break
                        except Exception as e:
                            logger.warning(f"검색 입력창 입력 실패(시도 {attempt+1}): {e}")
                            if attempt < max_attempts - 1:
                                driver.refresh()
                                time.sleep(3)
                            else:
                                logger.error(f"검색 입력창 입력 마지막 시도({attempt+1})도 실패: {e}")
                                raise
        except Exception as e:
            logger.error(f"❌ GenieSearchSong.search() 에러: {e}", exc_info=True)
            return None


    '''===================== ⬇️ 지니 노래 검색 함수 (여러 곡) ====================='''
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


'''===================== 곡명 정규화 함수 ====================='''
def normalize_song_name(text):
    return re.sub(r'[\W_]+', '', text).lower() if text else ''


'''===================== ⬇️ 지니 노래 크롤링 함수 ====================='''
class GenieSongCrawler:
    @staticmethod
    def crawl(html_list, artist_song_list):
        results = []
        max_attempts = 6
        for html, (target_artist, target_song) in zip(html_list, artist_song_list):
            if html is None:
                logger.error(f"❌ HTML이 None입니다: {target_artist} - {target_song}")
                continue
            
            # 각 곡마다 변수 초기화
            song_name = None
            artist_name = None
            total_person_count = 0
            total_play_count = 0
            success = False
            
            for attempt in range(max_attempts):
                try:
                    logger.info(f"[시도 {attempt+1}/{max_attempts}] '{target_artist} - {target_song}' 정보 추출 시도 중...")
                    soup = BeautifulSoup(html, 'html.parser')

                    # song_name 추출
                    current_song_name = None
                    song_name_tag = soup.find('h2', class_='name')
                    if song_name_tag:
                        current_song_name = song_name_tag.text.strip()
                        logger.info(f"✅ song_name 추출 성공: {current_song_name}")
                    else:
                        logger.warning("❌ song_name 태그(h2.name) 추출 실패")
                        continue

                    # 곡명 검증
                    if not current_song_name or normalize_song_name(current_song_name) != normalize_song_name(target_song):
                        logger.warning(f"❌ 검색 곡명과 파싱된 곡명이 다릅니다. 재시도합니다. 검색 '{target_song}' → 파싱 '{current_song_name}'")
                        continue

                    # 검증 통과 - 변수에 저장
                    song_name = current_song_name

                    # artist_name 추출 (info-data의 첫 번째 li의 value)
                    current_artist_name = None
                    artist_li = soup.select_one('ul.info-data li:nth-of-type(1) span.value')
                    if artist_li:
                        current_artist_name = artist_li.text.strip()
                        logger.info(f"✅ artist_name 추출 성공: {current_artist_name}")
                    else:
                        logger.warning("❌ artist_name 태그(ul.info-data > li:nth-of-type(1) > span.value) 추출 실패")
                    
                    # 아티스트명 설정 (추출된 값이 없으면 타겟 아티스트명 사용)
                    artist_name = current_artist_name if current_artist_name else target_artist

                    # 청취자수, 재생수 추출
                    total_div = soup.find('div', class_='total')
                    if total_div:
                        p_tags = total_div.find_all('p')
                        if len(p_tags) >= 2:
                            try:
                                # 첫 번째 <p>: 전체 청취자수
                                total_person_count = int(p_tags[0].text.replace(',', '').strip())
                                # 두 번째 <p>: 전체 재생수
                                total_play_count = int(p_tags[1].text.replace(',', '').strip())
                            except (ValueError, TypeError) as e:
                                logger.warning(f"❌ 청취자수/재생수 변환 실패: {e}")
                                total_person_count = 0
                                total_play_count = 0
                        else:
                            total_person_count = 0
                            total_play_count = 0
                    else:
                        total_person_count = 0
                        total_play_count = 0

                    # 성공적으로 파싱 완료
                    success = True
                    logger.info(f"✅ '{target_song}' 파싱 성공!")
                    break  # 성공하면 재시도 루프 종료

                except Exception as e:
                    logger.error(f"❌ GenieSongCrawler.crawl() 에러 (시도 {attempt+1}/{max_attempts}): {e}", exc_info=True)
                    continue

            # 성공한 경우만 결과에 추가
            if success and song_name:
                results.append({
                    "service_name": "genie",
                    "artist_name": artist_name,
                    "song_name": song_name,
                    "total_person_count": total_person_count,
                    "total_play_count": total_play_count,
                    "extracted_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                logger.info(f"✅ '{target_song}' 데이터 저장 완료")
            else:
                logger.warning(f"❌ '{target_song}' 파싱 실패 - 데이터 저장하지 않음")
        
        return results


