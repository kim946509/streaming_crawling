"""
YouTube Music 크롤링 및 파싱 로직
"""
import time
import random
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ..common.constants import YouTubeMusicSelectors, CommonSettings
from ..common.utils import normalize_text, make_soup, get_current_timestamp, convert_view_count

logger = logging.getLogger(__name__)

class YouTubeMusicCrawler:
    def __init__(self, driver, youtube_music_id, youtube_music_password):
        self.driver = driver
        self.wait = WebDriverWait(driver, CommonSettings.DEFAULT_WAIT_TIME)
        self.youtube_music_id = youtube_music_id
        self.youtube_music_password = youtube_music_password
        self.is_logged_in = False
    
    def login(self):
        """
        YouTube Music 로그인
        
        Returns:
            bool: 로그인 성공 여부
        """
        try:
            self.driver.get("https://music.youtube.com/")
            
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
                
            # 유튜브 뮤직 페이지로 이동
            self.driver.get("https://music.youtube.com/")
            time.sleep(2)
            
            self.is_logged_in = True
            logger.info("✅ YouTube Music 로그인 성공")
            return True
            
        except Exception as e:
            logger.error(f"❌ YouTube Music 로그인 실패: {e}", exc_info=True)
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
                    # 검색 버튼 찾기 및 클릭
                    search_button = self._find_search_button()
                    if not search_button:
                        raise Exception("검색 버튼을 찾을 수 없습니다.")
                    
                    search_button.click()
                    time.sleep(2)
                    
                    # 검색어 입력
                    search_input = self._find_search_input()
                    if not search_input:
                        raise Exception("검색 입력창을 찾을 수 없습니다.")
                    
                    search_input.clear()
                    time.sleep(0.5)
                    search_input.send_keys(query)
                    time.sleep(1)
                    search_input.send_keys(Keys.RETURN)
                    time.sleep(2)
                    
                    # "노래" 탭 클릭
                    song_tab = self.wait.until(
                        EC.element_to_be_clickable((
                            By.XPATH,
                            YouTubeMusicSelectors.SONG_TAB
                        ))
                    )
                    song_tab.click()
                    time.sleep(1)
                    
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
                search_button = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                return search_button
            except Exception:
                continue
        return None
    
    def _find_search_input(self):
        """검색 입력창 찾기"""
        for selector in YouTubeMusicSelectors.SEARCH_INPUT:
            try:
                search_input = self.wait.until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
                )
                return search_input
            except Exception:
                continue
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
