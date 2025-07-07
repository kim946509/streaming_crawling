"""
플랫폼별 크롤링 클래스들
"""
import logging
import time
from typing import List, Dict, Any

from crawling_view.common.song_service import SongService
from crawling_view.common.db_writer import save_genie_to_db, save_youtube_music_to_db, save_youtube_to_db
from crawling_view.genie.genie_main import run_genie_crawling
from crawling_view.youtube.youtube_main import run_youtube_crawling
from crawling_view.youtube_music.youtube_music_main import run_youtube_music_crawling
from streaming_site_list.models import SongInfo



logger = logging.getLogger(__name__)


class BasePlatformCrawler:
    """플랫폼 크롤링 기본 클래스"""
    
    def __init__(self, songs: List[SongInfo]):
        self.songs = songs
        self.platform_name = "base"
    
    def crawl(self, save_csv: bool = True, save_db: bool = True) -> Dict[str, Any]:
        """크롤링 실행"""
        raise NotImplementedError
    
    def _log_start(self):
        """크롤링 시작 로그"""
        logger.info(f"🎯 {self.platform_name} 크롤링 시작...")
    
    def _log_complete(self, elapsed_time: float, result_count: int):
        """크롤링 완료 로그"""
        logger.info(f"✅ {self.platform_name} 크롤링 완료: {result_count}개 성공 ({elapsed_time:.2f}초)")


class GenieCrawler(BasePlatformCrawler):
    """Genie 크롤링 클래스"""
    
    def __init__(self, songs: List[SongInfo]):
        super().__init__(songs)
        self.platform_name = "genie"
    
    def crawl(self, save_csv: bool = True, save_db: bool = True) -> Dict[str, Any]:
        """Genie 크롤링 실행"""
        self._log_start()
        start_time = time.time()
        
        # 크롤링 형식으로 변환
        song_list = SongService.convert_to_crawling_format(self.songs, 'genie')
        
        if not song_list:
            logger.warning("⚠️ Genie 크롤링 대상 곡이 없습니다.")
            return {'crawling_result': [], 'elapsed_time': 0, 'success': True}
        
        # 크롤링 실행
        crawling_results = run_genie_crawling(song_list, save_csv=save_csv, save_db=False)
        
        # DB 저장 (크롤링과 분리)
        if save_db and crawling_results:
            db_result = save_genie_to_db(crawling_results)
            logger.info(f"💾 Genie DB 저장: {db_result}")
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        self._log_complete(elapsed_time, len(crawling_results))
        
        return {
            'crawling_result': crawling_results,
            'elapsed_time': elapsed_time,
            'success': True
        }


class YouTubeMusicCrawler(BasePlatformCrawler):
    """YouTube Music 크롤링 클래스"""
    
    def __init__(self, songs: List[SongInfo]):
        super().__init__(songs)
        self.platform_name = "youtube_music"
    
    def crawl(self, save_csv: bool = True, save_db: bool = True) -> Dict[str, Any]:
        """YouTube Music 크롤링 실행"""
        self._log_start()
        start_time = time.time()
        
        from user_id_and_password import youtube_music_id, youtube_music_password
        
        # 크롤링 형식으로 변환
        song_list = SongService.convert_to_crawling_format(self.songs, 'youtube_music')
        
        if not song_list:
            logger.warning("⚠️ YouTube Music 크롤링 대상 곡이 없습니다.")
            return {'crawling_result': [], 'elapsed_time': 0, 'success': True}
        
        # 크롤링 실행
        crawling_results = run_youtube_music_crawling(
            song_list, 
            youtube_music_id, 
            youtube_music_password, 
            save_csv=save_csv, 
            save_db=False
        )
        
        # DB 저장 (크롤링과 분리)
        if save_db and crawling_results:
            db_result = save_youtube_music_to_db(crawling_results)
            logger.info(f"💾 YouTube Music DB 저장: {db_result}")
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        self._log_complete(elapsed_time, len(crawling_results))
        
        return {
            'crawling_result': crawling_results,
            'elapsed_time': elapsed_time,
            'success': True
        }


class YouTubeCrawler(BasePlatformCrawler):
    """YouTube 크롤링 클래스"""
    
    def __init__(self, songs: List[SongInfo]):
        super().__init__(songs)
        self.platform_name = "youtube"
    
    def crawl(self, save_csv: bool = True, save_db: bool = True) -> Dict[str, Any]:
        """YouTube 크롤링 실행"""
        self._log_start()
        start_time = time.time()
        
        # YouTube URL이 있는 곡들만 필터링
        youtube_songs = SongService.get_songs_by_platform(self.songs, 'youtube')
        
        if not youtube_songs:
            logger.warning("⚠️ YouTube URL이 있는 곡이 없습니다.")
            return {'crawling_result': {}, 'elapsed_time': 0, 'success': True}
        
        # 크롤링 형식으로 변환
        url_artist_song_id_list = SongService.convert_to_crawling_format(youtube_songs, 'youtube')
        
        if not url_artist_song_id_list:
            logger.warning("⚠️ YouTube 크롤링 대상 곡이 없습니다.")
            return {'crawling_result': {}, 'elapsed_time': 0, 'success': True}
        
        # 크롤링 실행
        crawling_results = run_youtube_crawling(url_artist_song_id_list, save_csv=save_csv, save_db=False)
        
        # DB 저장 (크롤링과 분리)
        if save_db and crawling_results:
            db_result = save_youtube_to_db(crawling_results)
            logger.info(f"💾 YouTube DB 저장: {db_result}")
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        self._log_complete(elapsed_time, len(crawling_results))
        
        return {
            'crawling_result': crawling_results,
            'elapsed_time': elapsed_time,
            'success': True
        }





def create_crawler(platform: str, songs: List[SongInfo]) -> BasePlatformCrawler:
    """
    플랫폼별 크롤러 생성
    
    Args:
        platform: 플랫폼명 ('genie', 'youtube_music', 'youtube')
        songs: 크롤링할 곡 목록
        
    Returns:
        BasePlatformCrawler: 해당 플랫폼의 크롤러
    """
    if platform == 'genie':
        return GenieCrawler(songs)
    elif platform == 'youtube_music':
        return YouTubeMusicCrawler(songs)
    elif platform == 'youtube':
        return YouTubeCrawler(songs)
    else:
        raise ValueError(f"지원하지 않는 플랫폼: {platform}")


# 편의 함수들
def crawl_genie(songs: List[SongInfo], save_csv: bool = True, save_db: bool = True) -> Dict[str, Any]:
    """Genie 크롤링 편의 함수"""
    crawler = GenieCrawler(songs)
    return crawler.crawl(save_csv, save_db)


def crawl_youtube_music(songs: List[SongInfo], save_csv: bool = True, save_db: bool = True) -> Dict[str, Any]:
    """YouTube Music 크롤링 편의 함수"""
    crawler = YouTubeMusicCrawler(songs)
    return crawler.crawl(save_csv, save_db)


def crawl_youtube(songs: List[SongInfo], save_csv: bool = True, save_db: bool = True) -> Dict[str, Any]:
    """YouTube 크롤링 편의 함수"""
    crawler = YouTubeCrawler(songs)
    return crawler.crawl(save_csv, save_db)


 