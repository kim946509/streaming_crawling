"""
YouTube Music 크롤링 및 파싱 로직
"""
import time
import random
import logging
import re
import pickle
import os
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from crawling_view.utils.constants import YouTubeMusicSelectors, CommonSettings
from crawling_view.utils.utils import normalize_text, make_soup, get_current_timestamp, convert_view_count

# .env 파일 로드
load_dotenv()

logger = logging.getLogger(__name__)

class YouTubeMusicCrawler:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, CommonSettings.DEFAULT_WAIT_TIME)
        self.youtube_music_id = os.getenv('YOUTUBE_MUSIC_ID', '')
        self.youtube_music_password = os.getenv('YOUTUBE_MUSIC_PASSWORD', '')
        self.is_logged_in = False
        self.cookies_file = "cookies.pkl"
    
    def _load_cookies(self):
        """저장된 쿠키 로드"""
        try:
            if os.path.exists(self.cookies_file):
                with open(self.cookies_file, 'rb') as f:
                    cookies = pickle.load(f)
                logger.info(f"🍪 저장된 쿠키 로드: {len(cookies)}개")
                return cookies
        except Exception as e:
            logger.warning(f"쿠키 로드 실패: {e}")
        return None
    
    def _is_cookie_expired(self, cookies):
        """쿠키 만료 여부 확인"""
        try:
            import time
            current_time = time.time()
            
            for cookie in cookies:
                # expires 필드가 있는 경우 확인
                if 'expiry' in cookie:
                    if cookie['expiry'] < current_time:
                        logger.info(f"🍪 쿠키 만료됨: {cookie.get('name', 'unknown')}")
                        return True
                
                # maxAge 필드가 있는 경우 확인
                if 'maxAge' in cookie and cookie['maxAge'] > 0:
                    # maxAge는 초 단위이므로 현재 시간과 비교
                    if cookie['maxAge'] < current_time:
                        logger.info(f"🍪 쿠키 만료됨: {cookie.get('name', 'unknown')}")
                        return True
            
            return False
        except Exception as e:
            logger.warning(f"쿠키 만료 확인 실패: {e}")
            return False
    
    def _save_cookies(self):
        """현재 쿠키 저장"""
        try:
            cookies = self.driver.get_cookies()
            with open(self.cookies_file, 'wb') as f:
                pickle.dump(cookies, f)
            logger.info(f"🍪 쿠키 저장 완료: {len(cookies)}개")
        except Exception as e:
            logger.error(f"쿠키 저장 실패: {e}")
    
    def _apply_cookies(self, cookies):
        """쿠키 적용"""
        try:
            # 먼저 YouTube Music 페이지로 이동
            self.driver.get("https://music.youtube.com/")
            time.sleep(2)
            
            # 쿠키 적용
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    logger.warning(f"쿠키 적용 실패: {cookie.get('name', 'unknown')} - {e}")
            
            logger.info("🍪 쿠키 적용 완료")
            return True
        except Exception as e:
            logger.error(f"쿠키 적용 실패: {e}")
            return False
    
    def _check_login_status(self):
        """로그인 상태 확인"""
        try:
            # 로그인 버튼이 있는지 확인
            login_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'a[aria-label="로그인"]')
            if not login_buttons or not login_buttons[0].is_displayed():
                logger.info("✅ 이미 로그인된 상태")
                return True
            else:
                logger.info("❌ 로그인되지 않은 상태")
                return False
        except Exception as e:
            logger.warning(f"로그인 상태 확인 실패: {e}")
            return False
    
    def login(self):
        """
        YouTube Music 로그인 (쿠키 우선 사용)
        
        로그인 순서:
        1. 저장된 쿠키가 있으면 쿠키로 로그인 시도
        2. 쿠키가 없거나 만료되었으면 일반 로그인 시도
        3. 로그인 성공 시 새로운 쿠키 저장
        
        Returns:
            bool: 로그인 성공 여부
        """
        try:
            # 1단계: 저장된 쿠키로 로그인 시도
            cookies = self._load_cookies()
            if cookies:
                # 쿠키 만료 여부 확인
                if self._is_cookie_expired(cookies):
                    logger.warning("⚠️ 쿠키가 만료되었습니다. 일반 로그인을 시도합니다.")
                else:
                    logger.info("🍪 저장된 쿠키로 로그인 시도")
                    if self._apply_cookies(cookies):
                        # 로그인 상태 확인
                        if self._check_login_status():
                            self.is_logged_in = True
                            logger.info("✅ 쿠키로 로그인 성공")
                            return True
                        else:
                            logger.warning("⚠️ 쿠키가 유효하지 않습니다. 일반 로그인을 시도합니다.")
                    else:
                        logger.warning("⚠️ 쿠키 적용에 실패했습니다. 일반 로그인을 시도합니다.")
            else:
                logger.info("📝 저장된 쿠키가 없습니다. 일반 로그인을 시도합니다.")
            
            # 2단계: 일반 로그인 시도
            logger.info("🔐 일반 로그인 시도")
            return self._perform_manual_login()
            
        except Exception as e:
            logger.error(f"❌ YouTube Music 로그인 실패: {e}", exc_info=True)
            return False
    
    def _perform_manual_login(self):
        """
        수동 로그인 수행
        
        Returns:
            bool: 로그인 성공 여부
        """
        try:
            self.driver.get("https://music.youtube.com/")
            time.sleep(2)
            
            # 로그인 버튼이 보이면(=로그인 안 된 상태)만 로그인 로직 실행
            need_login = False
            try:
                login_btn = self.driver.find_element(By.CSS_SELECTOR, 'a[aria-label="로그인"]')
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
                email_input = self.wait.until(EC.presence_of_element_located((By.ID, "identifierId")))
                time.sleep(random.uniform(CommonSettings.RANDOM_DELAY_MIN, CommonSettings.RANDOM_DELAY_MAX))
                email_input.send_keys(self.youtube_music_id)
                time.sleep(random.uniform(CommonSettings.RANDOM_DELAY_MIN, CommonSettings.RANDOM_DELAY_MAX))

                # '다음' 버튼 클릭
                next_button = self.wait.until(EC.element_to_be_clickable((By.ID, "identifierNext")))
                time.sleep(random.uniform(CommonSettings.RANDOM_DELAY_MIN, CommonSettings.RANDOM_DELAY_MAX))
                next_button.click()
                time.sleep(random.uniform(CommonSettings.RANDOM_DELAY_MIN, CommonSettings.RANDOM_DELAY_MAX))

                # 비밀번호 입력
                password_input = self.wait.until(EC.presence_of_element_located((By.NAME, "Passwd")))
                time.sleep(random.uniform(CommonSettings.RANDOM_DELAY_MIN, CommonSettings.RANDOM_DELAY_MAX))
                password_input.send_keys(self.youtube_music_password)
                time.sleep(random.uniform(CommonSettings.RANDOM_DELAY_MIN, CommonSettings.RANDOM_DELAY_MAX))

                # 로그인 버튼 클릭
                login_button = self.wait.until(EC.element_to_be_clickable((By.ID, "passwordNext")))
                time.sleep(random.uniform(CommonSettings.RANDOM_DELAY_MIN, CommonSettings.RANDOM_DELAY_MAX))
                login_button.click()
                time.sleep(random.uniform(CommonSettings.RANDOM_DELAY_MIN, CommonSettings.RANDOM_DELAY_MAX))

                # 본인 인증 화면 감지 및 대기
                time.sleep(2)
                page_source = self.driver.page_source
                if any(keyword in page_source for keyword in ["보안", "코드", "인증", "확인", "전화", "기기", "추가 확인"]):
                    logger.warning("⚠️ 본인 인증(추가 인증) 화면이 감지되었습니다. 자동화가 중단될 수 있습니다.")
                    time.sleep(60)

                # 로그인 완료 대기
                self.wait.until_not(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[aria-label="로그인"]')))
                time.sleep(2)
                
                # 로그인 성공 시 쿠키 저장
                self._save_cookies()
                
            # 유튜브 뮤직 페이지로 이동
            self.driver.get("https://music.youtube.com/")
            time.sleep(2)
            
            # 최종 로그인 상태 확인
            if self._check_login_status():
                self.is_logged_in = True
                logger.info("✅ 일반 로그인 성공")
                return True
            else:
                logger.error("❌ 일반 로그인 실패")
                return False
                
        except Exception as e:
            logger.error(f"❌ 수동 로그인 실패: {e}", exc_info=True)
            return False
    
    def crawl_song(self, song_title, artist_name, song_id=None):
        """
        단일 곡 크롤링
        
        Args:
            song_title (str): 곡 제목
            artist_name (str): 아티스트명
            song_id (str, optional): SongInfo의 pk값
            
        Returns:
            dict: 크롤링 결과 또는 None
        """
        try:
            if not self.is_logged_in:
                logger.error("❌ 로그인이 필요합니다.")
                return None
            
            # 검색 실행
            html = self._search_song(song_title, artist_name)
            if not html:
                return None
            
            # 파싱 실행
            result = self._parse_song_info(html, song_title, artist_name, song_id)
            return result
            
        except Exception as e:
            logger.error(f"❌ 곡 크롤링 실패 ({song_title} - {artist_name}): {e}", exc_info=True)
            return None
    
    def _search_song(self, song_title, artist_name):
        """
        YouTube Music에서 곡 검색
        
        Args:
            song_title (str): 곡 제목
            artist_name (str): 아티스트명
            
        Returns:
            str: 검색 결과 HTML 또는 None
        """
        try:
            # 줄바꿈 제거 및 공백 정리
            clean_artist = artist_name.strip().replace('\n', ' ').replace('\r', ' ')
            clean_song = song_title.strip().replace('\n', ' ').replace('\r', ' ')
            query = f"{clean_artist} {clean_song}"
            logger.info(f"🔍 YouTube Music 검색어: '{query}'")
            max_attempts = 3
            
            for attempt in range(max_attempts):
                try:
                    logger.info(f"🔍 검색 시도 {attempt+1}/{max_attempts}")
                    
                    # 페이지 로딩 대기
                    self._wait_for_page_load()
                    
                    # 검색 버튼 찾기 및 클릭
                    search_button = self._find_search_button()
                    if not search_button:
                        raise Exception("검색 버튼을 찾을 수 없습니다.")
                    
                    # 검색 버튼이 화면에 보이는지 확인
                    if not search_button.is_displayed():
                        raise Exception("검색 버튼이 화면에 보이지 않습니다.")
                    
                    # JavaScript로 클릭 시도 (더 안정적)
                    try:
                        self.driver.execute_script("arguments[0].click();", search_button)
                        logger.info("✅  검색 버튼 클릭 성공")
                    except Exception as e:
                        logger.warning(f"⚠️ 클릭 실패, 일반 클릭 시도: {e}")
                        search_button.click()
                    
                    time.sleep(1)  
                    
                    # 검색어 입력
                    search_input = self._find_search_input()
                    if not search_input:
                        raise Exception("검색 입력창을 찾을 수 없습니다.")
                    
                    # 검색 입력창이 활성화될 때까지 대기
                    try:
                        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, search_input.tag_name)))
                    except Exception as e:
                        logger.warning(f"⚠️ 검색 입력창 활성화 대기 실패: {e}")
                    
                    # 검색어 입력 전에 입력창 상태 확인
                    try:
                        # 입력창이 비어있는지 확인
                        current_value = search_input.get_attribute('value') or ''
                        if current_value:
                            logger.info(f"🔍 기존 검색어 제거: '{current_value}'")
                            search_input.clear()
                            time.sleep(1)
                    except Exception as e:
                        logger.warning(f"⚠️ 기존 검색어 제거 실패: {e}")
                    
                    # 검색어 입력 (더 안전한 방법)
                    try:
                        # JavaScript로 값 설정 시도
                        self.driver.execute_script("arguments[0].value = arguments[1];", search_input, query)
                        logger.info("✅ JavaScript로 검색어 입력 성공")
                    except Exception as e:
                        logger.warning(f"⚠️ JavaScript 입력 실패, 일반 입력 시도: {e}")
                        search_input.send_keys(query)
                    
                    time.sleep(2)
                    
                    # Enter 키 입력 (더 안전한 방법)
                    try:
                        # JavaScript로 Enter 이벤트 발생
                        self.driver.execute_script("""
                            var event = new KeyboardEvent('keydown', {
                                key: 'Enter',
                                code: 'Enter',
                                keyCode: 13,
                                which: 13,
                                bubbles: true,
                                cancelable: true
                            });
                            arguments[0].dispatchEvent(event);
                        """, search_input)
                        logger.info("✅ JavaScript로 Enter 키 이벤트 발생 성공")
                    except Exception as e:
                        logger.warning(f"⚠️ JavaScript Enter 이벤트 실패, 일반 Enter 시도: {e}")
                        search_input.send_keys(Keys.RETURN)
                    
                    time.sleep(1)  # 원래 대기 시간으로 복원
                    
                    # "노래" 탭 클릭 (다국어 지원)
                    song_tab_clicked = False
                    for song_tab_selector in YouTubeMusicSelectors.SONG_TAB:
                        try:
                            logger.debug(f"🔍 노래 탭 셀렉터 시도: {song_tab_selector}")
                            song_tab = self.wait.until(
                                EC.element_to_be_clickable((
                                    By.XPATH,
                                    song_tab_selector
                                ))
                            )
                            
                            # 탭이 화면에 보이는지 확인
                            if not song_tab.is_displayed():
                                logger.debug(f"❌ 노래 탭이 화면에 보이지 않음: {song_tab_selector}")
                                continue
                            
                            # JavaScript로 클릭 시도
                            self.driver.execute_script("arguments[0].click();", song_tab)
                            logger.info(f"✅ JavaScript로 노래 탭 클릭 성공: {song_tab_selector}")
                            song_tab_clicked = True
                            break
                            
                        except Exception as e:
                            logger.debug(f"❌ 노래 탭 셀렉터 실패: {song_tab_selector} - {str(e)}")
                            continue
                    
                    if not song_tab_clicked:
                        logger.warning("⚠️ 모든 노래 탭 셀렉터 실패, 탭 클릭 없이 계속 진행")
                    
                    time.sleep(1)  # 원래 대기 시간으로 복원
                    
                    # HTML 반환
                    html = self.driver.page_source
                    logger.info(f"✅ 검색 성공: {artist_name} - {song_title}")
                    return html
                    
                except Exception as e:
                    logger.warning(f"검색 시도 {attempt+1} 실패: {e}")
                    if attempt < max_attempts - 1:
                        # 유튜브 뮤직 메인 페이지로 돌아가기
                        self.driver.get("https://music.youtube.com/")
                        time.sleep(2)
                    else:
                        logger.error(f"❌ 모든 검색 시도 실패: {artist_name} - {song_title}")
                        
            return None
            
        except Exception as e:
            logger.error(f"❌ 곡 검색 실패: {e}", exc_info=True)
            return None
    
    def _find_search_button(self):
        """검색 버튼 찾기"""
        for selector in YouTubeMusicSelectors.SEARCH_BUTTON:
            try:
                logger.debug(f"🔍 검색 버튼 셀렉터 시도: {selector}")
                search_button = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                logger.info(f"✅ 검색 버튼 찾기 성공: {selector}")
                return search_button
            except Exception as e:
                logger.debug(f"❌ 검색 버튼 셀렉터 실패: {selector} - {str(e)}")
                continue
        
        # 모든 셀렉터 실패 시 현재 페이지 상태 로깅
        logger.error("❌ 모든 검색 버튼 셀렉터 실패")
        self._log_page_state()
        return None
    
    def _find_search_input(self):
        """검색 입력창 찾기"""
        for selector in YouTubeMusicSelectors.SEARCH_INPUT:
            try:
                logger.debug(f"🔍 검색 입력창 셀렉터 시도: {selector}")
                
                # 먼저 요소가 존재하는지 확인
                search_input = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                
                # 요소가 화면에 보이는지 확인
                if not search_input.is_displayed():
                    logger.debug(f"❌ 검색 입력창이 화면에 보이지 않음: {selector}")
                    continue
                
                # 요소가 상호작용 가능한지 확인
                if not search_input.is_enabled():
                    logger.debug(f"❌ 검색 입력창이 비활성화됨: {selector}")
                    continue
                
                # 입력창의 속성 확인
                input_type = search_input.get_attribute('type') or ''
                if input_type == 'hidden':
                    logger.debug(f"❌ 검색 입력창이 숨겨진 상태: {selector}")
                    continue
                
                logger.info(f"✅ 검색 입력창 찾기 성공: {selector}")
                return search_input
                
            except Exception as e:
                logger.debug(f"❌ 검색 입력창 셀렉터 실패: {selector} - {str(e)}")
                continue
        
        # 모든 셀렉터 실패 시 현재 페이지 상태 로깅
        logger.error("❌ 모든 검색 입력창 셀렉터 실패")
        self._log_page_state()
        return None
    
    def _parse_song_info(self, html, target_song, target_artist, song_id=None):
        """
        검색 결과 HTML 파싱
        
        Args:
            html (str): 검색 결과 HTML
            target_song (str): 검색한 곡명
            target_artist (str): 검색한 아티스트명
            song_id (str, optional): SongInfo의 pk값
            
        Returns:
            dict: 파싱된 곡 정보 또는 None
        """
        try:
            logger.info(f"[파싱] '{target_artist} - {target_song}' 정보 추출 시도 중...")
            
            soup = make_soup(html)
            if not soup:
                return None
            
            song_items = soup.select(YouTubeMusicSelectors.SONG_ITEMS)
            logger.info(f"🔍 YouTube Music 검색 결과: {len(song_items)}개 곡 발견")
            
            for i, item in enumerate(song_items):
                logger.info(f"🔍 검사 중인 곡 {i+1}/{len(song_items)}")
                try:
                    # 곡명 추출
                    song_title = self._extract_song_title(item)
                    if not song_title:
                        continue

                    # 아티스트명 추출
                    artist_name = self._extract_artist_name(item)
                    if not artist_name:
                        continue
                        
                    logger.info(f"🔍 발견된 곡: '{song_title}' - '{artist_name}'")

                    # 조회수 추출
                    view_count = self._extract_view_count(item)

                    # 디버그 로깅
                    normalized_song = normalize_text(song_title)
                    normalized_target = normalize_text(target_song)
                    normalized_artist = normalize_text(artist_name)
                    normalized_target_artist = normalize_text(target_artist)
                    
                    logger.debug(f"검사 중: 제목='{song_title}' → '{normalized_song}' vs '{target_song}' → '{normalized_target}'")
                    logger.debug(f"검사 중: 아티스트='{artist_name}' → '{normalized_artist}' vs '{target_artist}' → '{normalized_target_artist}'")

                    # 정규화된 문자열로 비교
                    title_match = normalized_song == normalized_target
                    artist_match = normalized_artist == normalized_target_artist
                    
                    logger.debug(f"일치 검사: 제목 일치={title_match}, 아티스트 일치={artist_match}")
                    
                    if title_match and artist_match:
                        result = {
                            'song_title': song_title,
                            'artist_name': artist_name,
                            'views': convert_view_count(view_count),
                            'listeners': -1,  # YouTube Music은 청취자 수 제공 안함
                            'crawl_date': get_current_timestamp(),
                            'song_id': song_id
                        }
                        logger.info(f"[성공] 일치하는 곡 발견: {song_title} - {artist_name} ({view_count})")
                        return result
                    else:
                        if not title_match:
                            logger.debug(f"제목 불일치: '{normalized_song}' != '{normalized_target}'")
                        if not artist_match:
                            logger.debug(f"아티스트 불일치: '{normalized_artist}' != '{normalized_target_artist}'")

                except Exception as e:
                    logger.warning(f"개별 곡 파싱 중 예외 발생: {e}")
                    continue

            # 일치하는 곡을 찾지 못한 경우
            logger.warning(f"[실패] '{target_artist} - {target_song}'와 일치하는 곡을 찾지 못함")
            return None
            
        except Exception as e:
            logger.error(f"❌ 파싱 실패: {e}", exc_info=True)
            return None
    
    def _extract_song_title(self, item):
        """곡명 추출"""
        song_name_tag = item.select_one(YouTubeMusicSelectors.SONG_TITLE)
        if song_name_tag:
            song_title = song_name_tag.get_text(strip=True)
            logger.debug(f"✅ 곡명 추출 성공: {song_title}")
            return song_title
        return None
    
    def _extract_artist_name(self, item):
        """아티스트명 추출"""
        artist_column = item.select_one(YouTubeMusicSelectors.ARTIST_COLUMN)
        if artist_column:
            artist_a = artist_column.select_one(YouTubeMusicSelectors.ARTIST_LINK)
            if artist_a:
                artist_name = artist_a.get_text(strip=True)
                logger.debug(f"✅ 아티스트명 추출 성공: {artist_name}")
                return artist_name
        return None
    
    def _extract_view_count(self, item):
        """조회수 추출"""
        try:
            flex_columns = item.select(YouTubeMusicSelectors.VIEW_COUNT_FLEX)
            
            for flex_col in flex_columns:
                aria_label = flex_col.get('aria-label', '')
                if '회' in aria_label and '재생' in aria_label:
                    view_count = aria_label.replace('회', '').replace('재생', '').strip()
                    logger.debug(f"✅ 조회수 추출 성공: {view_count}")
                    return view_count
            
            return None
            
        except Exception as e:
            logger.error(f"❌ 조회수 추출 실패: {e}")
            return None
    
    def _log_page_state(self):
        """현재 페이지 상태 로깅 (디버깅용)"""
        try:
            current_url = self.driver.current_url
            page_title = self.driver.title
            logger.info(f"📄 현재 URL: {current_url}")
            logger.info(f"📄 페이지 제목: {page_title}")
            
            # 검색 관련 요소들 확인
            search_elements = self.driver.find_elements(By.CSS_SELECTOR, '[aria-label*="검색"], [aria-label*="Search"], yt-icon-button, button#button')
            logger.info(f"🔍 검색 관련 요소 개수: {len(search_elements)}")
            
            for i, elem in enumerate(search_elements[:5]):  # 처음 5개만 로깅
                try:
                    aria_label = elem.get_attribute('aria-label') or 'N/A'
                    tag_name = elem.tag_name
                    is_displayed = elem.is_displayed()
                    is_enabled = elem.is_enabled()
                    logger.info(f"  요소 {i+1}: {tag_name} - aria-label: {aria_label} - 표시: {is_displayed} - 활성: {is_enabled}")
                except Exception:
                    logger.info(f"  요소 {i+1}: 정보 추출 실패")
            
            # 검색 입력창 관련 요소들 확인
            input_elements = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="search"], input[aria-autocomplete], input[role="combobox"]')
            logger.info(f"🔍 검색 입력창 관련 요소 개수: {len(input_elements)}")
            
            for i, elem in enumerate(input_elements[:3]):  # 처음 3개만 로깅
                try:
                    input_type = elem.get_attribute('type') or 'N/A'
                    aria_autocomplete = elem.get_attribute('aria-autocomplete') or 'N/A'
                    role = elem.get_attribute('role') or 'N/A'
                    placeholder = elem.get_attribute('placeholder') or 'N/A'
                    is_displayed = elem.is_displayed()
                    is_enabled = elem.is_enabled()
                    logger.info(f"  입력창 {i+1}: type={input_type}, aria-autocomplete={aria_autocomplete}, role={role}, placeholder={placeholder}, 표시: {is_displayed}, 활성: {is_enabled}")
                except Exception:
                    logger.info(f"  입력창 {i+1}: 정보 추출 실패")
            
            # 페이지 소스 일부 저장 (디버깅용)
            page_source = self.driver.page_source
            if len(page_source) > 1000:
                logger.debug(f"📄 페이지 소스 (처음 1000자): {page_source[:1000]}...")
            else:
                logger.debug(f"📄 페이지 소스: {page_source}")
                
        except Exception as e:
            logger.error(f"❌ 페이지 상태 로깅 실패: {e}")
    
    def _wait_for_page_load(self, timeout=10):
        """페이지 로딩 완료 대기"""
        try:
            # DOM이 준비될 때까지 대기
            self.wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
            logger.debug("✅ 페이지 로딩 완료")
            return True
        except Exception as e:
            logger.warning(f"⚠️ 페이지 로딩 대기 실패: {e}")
            return False
