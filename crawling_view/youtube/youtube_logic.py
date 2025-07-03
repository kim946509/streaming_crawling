"""
YouTube 크롤링 및 파싱 로직
"""
import time
import re
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ..common.constants import YouTubeSelectors, CommonSettings
from ..common.utils import make_soup, get_current_timestamp, convert_view_count

logger = logging.getLogger(__name__)

class YouTubeCrawler:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, CommonSettings.DEFAULT_WAIT_TIME)
    
    def crawl_multiple(self, url_artist_list):
        """
        여러 YouTube URL을 크롤링
        
        Args:
            url_artist_list (list): [('url', 'artist_name'), ...] 형태의 리스트
            
        Returns:
            dict: 크롤링 결과 딕셔너리
        """
        results = {}
        url_id_artist_map = {}

        # 각 (url, artist_name)에서 song_id 추출
        for url, artist_name in url_artist_list:
            song_id = self._extract_song_id(url)
            if song_id:
                url_id_artist_map[song_id] = {'url': url, 'artist_name': artist_name}
            else:
                # 유효하지 않은 URL 처리
                results[url] = {
                    'song_name': None,
                    'artist_name': artist_name,
                    'view_count': None,
                    'youtube_url': url,
                    'upload_date': None,
                    'extracted_date': get_current_timestamp(),
                    'error': '유효하지 않은 유튜브 URL'
                }

        # 각 URL 크롤링
        for song_id, data in url_id_artist_map.items():
            url = data['url']
            artist_name = data['artist_name']
            
            try:
                result = self._crawl_single_video(song_id, url, artist_name)
                if result:
                    results[song_id] = result
                    logger.info(f"✅ 크롤링 성공 - 아티스트: {artist_name}, 제목: {result['song_name']}, "
                              f"조회수: {result['view_count']}, 업로드일: {result['upload_date']}")
                else:
                    logger.error(f"❌ 크롤링 실패: {artist_name} - {url}")
                    
            except Exception as e:
                logger.error(f"❌ {artist_name} 크롤링 실패: {e}", exc_info=True)
                results[song_id] = {
                    'song_name': None,
                    'artist_name': artist_name,
                    'view_count': None,
                    'youtube_url': url,
                    'upload_date': None,
                    'extracted_date': get_current_timestamp(),
                }

        return results
    
    def _crawl_single_video(self, song_id, url, artist_name):
        """
        단일 YouTube 동영상 크롤링
        
        Args:
            song_id (str): YouTube 비디오 ID
            url (str): YouTube URL
            artist_name (str): 아티스트명
            
        Returns:
            dict: 크롤링 결과 또는 None
        """
        try:
            # 페이지 로드
            self.driver.get(url)

            # 동적 로딩을 위한 대기
            if not self._wait_for_title_load():
                raise Exception("제목 selector를 찾지 못함")
            
            time.sleep(2)  # 추가 대기 시간

            # HTML 파싱
            html = self.driver.page_source
            soup = make_soup(html)
            if not soup:
                return None

            # 동영상 제목 추출
            song_name = self._extract_title(soup)
            if not song_name:
                song_name = "제목 없음"
                logger.warning("동영상 제목을 찾지 못했습니다.")
            
            # 조회수 추출
            view_count = self._extract_view_count(soup)

            # 업로드 날짜 추출
            upload_date = self._extract_upload_date(soup)

            # 결과 반환
            return {
                'song_id': song_id,
                'song_name': song_name,
                'artist_name': artist_name,
                'view_count': view_count,
                'youtube_url': url,
                'upload_date': upload_date,
                'extracted_date': get_current_timestamp()
            }

        except Exception as e:
            logger.error(f"❌ 단일 비디오 크롤링 실패: {e}", exc_info=True)
            return None
    
    def _extract_song_id(self, youtube_url):
        """
        유튜브 URL에서 song_id 추출
        
        Args:
            youtube_url (str): YouTube URL
            
        Returns:
            str: 비디오 ID 또는 None
        """
        # 일반적인 유튜브 URL 패턴
        match = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", youtube_url)
        if match:
            return match.group(1)
        return None
    
    def _wait_for_title_load(self):
        """
        제목 로딩 대기
        
        Returns:
            bool: 로딩 성공 여부
        """
        selectors = [
            "h1.style-scope.ytd-watch-metadata",
            "h1.style-scope.ytd-watch-metadata > yt-formatted-string",
            "yt-formatted-string.style-scope.ytd-watch-metadata"
        ]
        
        for sel in selectors:
            try:
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, sel)))
                return True
            except:
                continue
        
        return False
    
    def _extract_title(self, soup):
        """
        동영상 제목 추출
        
        Args:
            soup (BeautifulSoup): 파싱된 HTML
            
        Returns:
            str: 동영상 제목 또는 None
        """
        title_selectors = [
            {'type': 'css', 'value': 'h1.style-scope.ytd-watch-metadata'},
            {'type': 'css', 'value': 'h1.style-scope.ytd-watch-metadata > yt-formatted-string'},
            {'type': 'css', 'value': 'yt-formatted-string.style-scope.ytd-watch-metadata'},
            {'type': 'css', 'value': 'h1.title'},
            {'type': 'css', 'value': 'h1.ytd-watch-metadata'},
            {'type': 'css', 'value': 'h1#title'},
        ]
        
        return self._find_with_selectors(soup, title_selectors)
    
    def _extract_view_count(self, soup):
        """
        조회수 추출
        
        Args:
            soup (BeautifulSoup): 파싱된 HTML
            
        Returns:
            int: 조회수 또는 None
        """
        view_count_selectors = [
            {'type': 'css', 'value': 'span.view-count'},
            {'type': 'css', 'value': 'span#view-count'},
            {'type': 'css', 'value': 'div#count span.view-count'},
            {'type': 'css', 'value': 'div#info span.view-count'},
            {'type': 'css', 'value': 'span.ytd-video-view-count-renderer'},
            {'type': 'css', 'value': 'yt-view-count-renderer span.view-count'},
        ]
        
        view_count_text = self._find_with_selectors(soup, view_count_selectors)
        return convert_view_count(view_count_text)
    
    def _extract_upload_date(self, soup):
        """
        업로드 날짜 추출
        
        Args:
            soup (BeautifulSoup): 파싱된 HTML
            
        Returns:
            str: 업로드 날짜 또는 None
        """
        upload_date_selectors = [
            {'type': 'css', 'value': 'div#info-strings yt-formatted-string'},
            {'type': 'css', 'value': 'div#date yt-formatted-string'},
            {'type': 'css', 'value': 'span.date'},
            {'type': 'css', 'value': 'div#info-strings'},
            {'type': 'css', 'value': 'yt-formatted-string#info-strings'},
        ]
        
        date_text = self._find_with_selectors(soup, upload_date_selectors)
        if date_text:
            # "YYYY. MM. DD." 또는 "YYYY.MM.DD" 형식을 "YYYY.MM.DD" 형식으로 변환
            date_match = re.search(r'(\d{4})[.\-\/\s]*(\d{1,2})[.\-\/\s]*(\d{1,2})', date_text)
            if date_match:
                year, month, day = date_match.groups()
                return f"{year}.{int(month):02d}.{int(day):02d}"
            else:
                return date_text.strip()
        
        return None
    
    def _find_with_selectors(self, soup, selectors, get_text=True):
        """
        여러 selector를 순차적으로 시도하여 첫 번째로 찾은 element(또는 text)를 반환
        
        Args:
            soup (BeautifulSoup): 파싱된 HTML
            selectors (list): 셀렉터 리스트
            get_text (bool): 텍스트 반환 여부
            
        Returns:
            str: 찾은 텍스트 또는 None
        """
        for selector in selectors:
            if selector.get('type') == 'css':
                el = soup.select_one(selector['value'])
            elif selector.get('type') == 'tag_class':
                el = soup.find(selector['tag'], class_=selector['class'])
            elif selector.get('type') == 'tag_id':
                el = soup.find(selector['tag'], id=selector['id'])
            else:
                continue
            
            if el:
                return el.text.strip() if get_text else el
        
        return None 