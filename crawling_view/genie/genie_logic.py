"""
Genie 크롤링 및 파싱 로직
"""
import time
import random
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ..common.constants import GenieSelectors, GenieSettings, CommonSettings
from ..common.utils import normalize_song_name, make_soup, get_current_timestamp

logger = logging.getLogger(__name__)

class GenieCrawler:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, CommonSettings.DEFAULT_WAIT_TIME)
    
    def crawl_song(self, song_title, artist_name):
        """
        단일 곡 크롤링
        
        Args:
            song_title (str): 곡 제목
            artist_name (str): 아티스트명
            
        Returns:
            dict: 크롤링 결과 또는 None
        """
        try:
            # 검색 실행
            html = self._search_song(song_title, artist_name)
            if not html:
                return None
            
            # 파싱 실행
            result = self._parse_song_info(html, song_title, artist_name)
            return result
            
        except Exception as e:
            logger.error(f"❌ 곡 크롤링 실패 ({song_title} - {artist_name}): {e}", exc_info=True)
            return None
    
    def _search_song(self, song_title, artist_name):
        """
        Genie에서 곡 검색
        
        Args:
            song_title (str): 곡 제목
            artist_name (str): 아티스트명
            
        Returns:
            str: 곡 정보 페이지 HTML 또는 None
        """
        try:
            query = f"{artist_name} {song_title}"
            self.driver.get(GenieSettings.BASE_URL)
            
            # 검색 입력창 찾기 및 검색 실행
            for attempt in range(GenieSettings.MAX_SEARCH_ATTEMPTS):
                try:
                    # 검색 입력창 찾기
                    search_input = self._find_search_input()
                    if not search_input:
                        raise Exception("검색 입력창을 찾을 수 없습니다.")
                    
                    # 검색어 입력
                    search_input.clear()
                    time.sleep(random.uniform(CommonSettings.RANDOM_DELAY_MIN, CommonSettings.RANDOM_DELAY_MAX))
                    search_input.send_keys(query)
                    time.sleep(random.uniform(CommonSettings.RANDOM_DELAY_MIN, CommonSettings.RANDOM_DELAY_MAX))
                    search_input.send_keys(Keys.RETURN)
                    time.sleep(3)
                    
                    # 곡 정보 페이지로 이동
                    html = self._navigate_to_song_info()
                    if html:
                        return html
                    
                    break
                    
                except Exception as e:
                    logger.warning(f"검색 시도 {attempt+1}/{GenieSettings.MAX_SEARCH_ATTEMPTS} 실패: {e}")
                    if attempt < GenieSettings.MAX_SEARCH_ATTEMPTS - 1:
                        self.driver.refresh()
                        time.sleep(3)
                    else:
                        logger.error(f"검색 마지막 시도({attempt+1})도 실패: {e}")
                        raise
            
            return None
            
        except Exception as e:
            logger.error(f"❌ 곡 검색 실패: {e}", exc_info=True)
            return None
    
    def _find_search_input(self):
        """검색 입력창 찾기"""
        for selector in GenieSelectors.SEARCH_INPUT:
            try:
                search_input = self.wait.until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
                )
                return search_input
            except Exception:
                continue
        return None
    
    def _navigate_to_song_info(self):
        """검색 결과에서 직접 데이터 추출 (곡 정보 페이지로 이동하지 않음)"""
        try:
            # 검색 결과에서 직접 파싱하도록 변경
            logger.info("✅ 검색 결과에서 직접 데이터 추출")
            return self.driver.page_source
            
        except Exception as e:
            logger.error(f"❌ 검색 결과 페이지 접근 실패: {e}")
            return None
    
    def _parse_song_info(self, html, target_song, target_artist):
        """
        검색 결과 HTML 파싱 (검색 결과 테이블에서 직접 추출)
        
        Args:
            html (str): 검색 결과 페이지 HTML
            target_song (str): 검색한 곡명
            target_artist (str): 검색한 아티스트명
            
        Returns:
            dict: 파싱된 곡 정보 또는 None
        """
        for attempt in range(GenieSettings.MAX_PARSE_ATTEMPTS):
            try:
                logger.info(f"[시도 {attempt+1}/{GenieSettings.MAX_PARSE_ATTEMPTS}] '{target_artist} - {target_song}' 정보 추출 시도 중...")
                
                soup = make_soup(html)
                if not soup:
                    continue
                
                # 검색 결과 테이블에서 곡 정보 찾기
                song_rows = soup.select(GenieSelectors.RESULT_ROWS)
                
                for row in song_rows:
                    try:
                        # 곡명 추출
                        song_title_element = row.select_one(f"{GenieSelectors.TITLE_COLUMN} {GenieSelectors.ARTIST_NAME}")
                        if not song_title_element:
                            continue
                        
                        song_title = song_title_element.text.strip()
                        
                        # 곡명 매칭 확인
                        if normalize_song_name(song_title) != normalize_song_name(target_song):
                            continue
                        
                        # 아티스트명 추출
                        artist_elements = row.select(f"{GenieSelectors.ARTIST_COLUMN} {GenieSelectors.ARTIST_NAME}")
                        artist_name = target_artist
                        if len(artist_elements) > 1:
                            artist_name = artist_elements[1].text.strip()
                        
                        # 조회수 정보 추출
                        view_count = self._extract_view_count_from_row(row)
                        
                        # 결과 반환
                        result = {
                            'song_title': song_title,
                            'artist_name': artist_name,
                            'view_count': view_count,
                            'crawl_date': get_current_timestamp()
                        }
                        
                        logger.info(f"✅ '{target_song}' 파싱 성공!")
                        return result
                        
                    except Exception as e:
                        logger.warning(f"행 파싱 실패: {e}")
                        continue
                
            except Exception as e:
                logger.error(f"❌ 파싱 시도 {attempt+1}/{GenieSettings.MAX_PARSE_ATTEMPTS} 실패: {e}", exc_info=True)
                continue
        
        logger.warning(f"❌ '{target_song}' 파싱 실패 - 모든 시도 실패")
        return None
    
    def _extract_song_title(self, soup):
        """곡명 추출 (배열 셀렉터 지원)"""
        for selector in GenieSelectors.SONG_TITLE:
            song_title_tag = soup.select_one(selector)
            if song_title_tag:
                song_title = song_title_tag.text.strip()
                logger.info(f"✅ 곡명 추출 성공: {song_title}")
                return song_title
        return None
    
    def _extract_artist_name(self, soup):
        """아티스트명 추출 (배열 셀렉터 지원)"""
        for selector in GenieSelectors.ARTIST_INFO:
            artist_tag = soup.select_one(selector)
            if artist_tag:
                artist_name = artist_tag.text.strip()
                logger.info(f"✅ 아티스트명 추출 성공: {artist_name}")
                return artist_name
        return None
    
    def _extract_view_count_from_row(self, row):
        """검색 결과 행에서 조회수 정보 추출"""
        try:
            count_elements = row.select(f"{GenieSelectors.COUNT_COLUMN} {GenieSelectors.PLAY_COUNT}")
            
            if len(count_elements) >= 2:
                try:
                    # 첫 번째: 전체 청취자수, 두 번째: 전체 재생수
                    total_person_count = int(count_elements[0].text.replace(',', '').strip())
                    total_play_count = int(count_elements[1].text.replace(',', '').strip())
                    
                    return {
                        'total_person_count': total_person_count,
                        'view_count': total_play_count
                    }
                except (ValueError, TypeError, IndexError) as e:
                    logger.warning(f"❌ 조회수 변환 실패: {e}")
                    return {'total_person_count': 0, 'view_count': 0}
            
            return {'total_person_count': 0, 'view_count': 0}
            
        except Exception as e:
            logger.error(f"❌ 조회수 정보 추출 실패: {e}")
            return {'total_person_count': 0, 'view_count': 0}
    
    def _extract_view_count(self, soup):
        """조회수 정보 추출 (배열 셀렉터 지원)"""
        try:
            for selector in GenieSelectors.TOTAL_STATS:
                total_div = soup.select_one(selector)
                if total_div:
                    for p_selector in GenieSelectors.TOTAL_STATS_PARAGRAPHS:
                        p_tags = total_div.select(p_selector)
                        if len(p_tags) >= 2:
                            try:
                                # 첫 번째 <p>: 전체 청취자수
                                total_person_count = int(p_tags[0].text.replace(',', '').strip())
                                # 두 번째 <p>: 전체 재생수
                                total_play_count = int(p_tags[1].text.replace(',', '').strip())
                                
                                return {
                                    'total_person_count': total_person_count,
                                    'view_count': total_play_count
                                }
                            except (ValueError, TypeError) as e:
                                logger.warning(f"❌ 청취자수/재생수 변환 실패: {e}")
                                continue
            
            return {'total_person_count': 0, 'view_count': 0}
            
        except Exception as e:
            logger.error(f"❌ 조회수 정보 추출 실패: {e}")
            return {'total_person_count': 0, 'view_count': 0} 