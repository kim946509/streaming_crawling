"""
Melon 크롤링 및 파싱 로직 (API 기반)
"""
import time
import random
import logging
import requests
import json
from crawling_view.utils.utils import get_current_timestamp

logger = logging.getLogger(__name__)

class MelonCrawler:
    def __init__(self):
        self.api_base_url = "https://m2.melon.com/m6/v5/song/info.json"
        self.session = requests.Session()
        # User-Agent 설정
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Referer': 'https://m2.melon.com/',
            'Origin': 'https://m2.melon.com'
        })
    
    def crawl_song(self, melon_song_id, song_id=None):
        """
        단일 곡 크롤링 (API 호출)
        
        Args:
            melon_song_id (str): 멜론 곡 ID
            song_id (str, optional): SongInfo의 pk값
            
        Returns:
            dict: 크롤링 결과 또는 None
        """
        try:
            if not melon_song_id:
                logger.error("❌ melon_song_id가 필요합니다.")
                return None
            
            logger.debug(f"🎵 Melon API 호출: songId={melon_song_id}")
            
            # API 호출
            api_url = f"{self.api_base_url}?songId={melon_song_id}"
            response = self.session.get(api_url, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"❌ API 호출 실패: HTTP {response.status_code}")
                return None
            
            # JSON 파싱
            data = response.json()
            
            # 응답 구조 확인
            if 'response' not in data or 'SONGINFO' not in data['response']:
                logger.error("❌ API 응답 구조가 올바르지 않습니다.")
                return None
            
            song_info = data['response']['SONGINFO']
            stream_info = data['response'].get('STREAMREPORTINFO', {})
            
            # 곡 정보 추출
            song_name = song_info.get('SONGNAME', '')
            artist_list = song_info.get('ARTISTLIST', [])
            artist_name = artist_list[0].get('ARTISTNAME', '') if artist_list else ''
            
            # 조회수 및 청취자수 추출
            total_listen_count = stream_info.get('TOTALLISTENCNT', '0')
            total_listener_count = stream_info.get('TOTALLISTENERCNT', '0')
            
            # 숫자 변환 (쉼표 제거)
            views = self._convert_to_number(total_listen_count)
            listeners = self._convert_to_number(total_listener_count)
            
            result = {
                'song_title': song_name,
                'artist_name': artist_name,
                'views': views,
                'listeners': listeners,
                'crawl_date': get_current_timestamp(),
                'song_id': song_id,
                'melon_song_id': melon_song_id
            }
            
            logger.info(f"✅ Melon 크롤링 성공: {song_name} - {artist_name} (조회수: {views}, 청취자: {listeners})")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API 요청 실패: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON 파싱 실패: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Melon 크롤링 실패: {e}", exc_info=True)
            return None
    
    def _convert_to_number(self, value):
        """
        문자열을 숫자로 변환 (쉼표 제거)
        
        Args:
            value (str): 변환할 문자열
            
        Returns:
            int: 변환된 숫자
                - 정상값: 양수
                - 0: 실제로 0인 경우
                - -1: 해당 플랫폼에서 제공하지 않는 데이터
                - -999: 크롤링 실패/오류
        """
        try:
            if not value:
                return -999  # 데이터가 없음 (크롤링 실패)
            
            # 쉼표 제거 후 숫자 변환
            clean_value = str(value).replace(',', '')
            result = int(clean_value)
            
            # 0인 경우 실제 0으로 처리 (멜론에서는 0이 나올 수 있음)
            return result
            
        except (ValueError, TypeError):
            logger.warning(f"숫자 변환 실패: {value}")
            return -999  # 변환 오류 