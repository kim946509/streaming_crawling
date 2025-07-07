"""
플랫폼별 크롤링 클래스들 (단순화)
"""
import logging
import time
from typing import List, Dict, Any

from crawling_view.view.genie.genie_main import run_genie_crawling
from crawling_view.view.youtube.youtube_main import run_youtube_crawling
from crawling_view.view.youtube_music.youtube_music_main import run_youtube_music_crawling
from crawling_view.models import SongInfo

logger = logging.getLogger(__name__)


class BasePlatformCrawler:
    """플랫폼 크롤링 기본 클래스"""
    
    def __init__(self):
        self.platform_name = "base"
    
    def crawl_songs(self, song_data: List[Dict]) -> List[Dict]:
        """크롤링 실행"""
        raise NotImplementedError
    
    def _log_start(self, song_count: int):
        """크롤링 시작 로그"""
        logger.info(f"🎯 {self.platform_name} 크롤링 시작: {song_count}개 곡")
    
    def _log_complete(self, elapsed_time: float, result_count: int):
        """크롤링 완료 로그"""
        logger.info(f"✅ {self.platform_name} 크롤링 완료: {result_count}개 성공 ({elapsed_time:.2f}초)")


class GenieCrawler(BasePlatformCrawler):
    """Genie 크롤링 클래스"""
    
    def __init__(self):
        super().__init__()
        self.platform_name = "genie"
    
    def crawl_songs(self, song_data: List[Dict]) -> List[Dict]:
        """Genie 크롤링 실행"""
        if not song_data:
            logger.warning("⚠️ Genie 크롤링 대상 곡이 없습니다.")
            return []
        
        self._log_start(len(song_data))
        start_time = time.time()
        
        # 크롤링 실행 (CSV, DB 저장은 분리)
        crawling_results = run_genie_crawling(song_data, save_csv=False, save_db=False)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        self._log_complete(elapsed_time, len(crawling_results))
        
        return crawling_results


class YouTubeMusicCrawler(BasePlatformCrawler):
    """YouTube Music 크롤링 클래스"""
    
    def __init__(self):
        super().__init__()
        self.platform_name = "youtube_music"
    
    def crawl_songs(self, song_data: List[Dict]) -> List[Dict]:
        """YouTube Music 크롤링 실행"""
        if not song_data:
            logger.warning("⚠️ YouTube Music 크롤링 대상 곡이 없습니다.")
            return []
        
        self._log_start(len(song_data))
        start_time = time.time()
        
        # 크롤링 실행 (CSV, DB 저장은 분리)
        crawling_results = run_youtube_music_crawling(
            song_data, 
            save_csv=False, 
            save_db=False
        )
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        self._log_complete(elapsed_time, len(crawling_results))
        
        return crawling_results


class YouTubeCrawler(BasePlatformCrawler):
    """YouTube 크롤링 클래스"""
    
    def __init__(self):
        super().__init__()
        self.platform_name = "youtube"
    
    def crawl_songs(self, song_data: List[tuple]) -> Dict[str, Dict]:
        """YouTube 크롤링 실행"""
        if not song_data:
            logger.warning("⚠️ YouTube 크롤링 대상 곡이 없습니다.")
            return {}
        
        self._log_start(len(song_data))
        start_time = time.time()
        
        # 크롤링 실행 (CSV, DB 저장은 분리)
        crawling_results = run_youtube_crawling(song_data, save_csv=False, save_db=False)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        self._log_complete(elapsed_time, len(crawling_results))
        
        return crawling_results


def create_crawler(platform: str):
    """
    플랫폼별 크롤러 생성
    
    Args:
        platform: 플랫폼명 ('genie', 'youtube_music', 'youtube')
        
    Returns:
        BasePlatformCrawler: 해당 플랫폼의 크롤러
    """
    if platform == 'genie':
        return GenieCrawler()
    elif platform == 'youtube_music':
        return YouTubeMusicCrawler()
    elif platform == 'youtube':
        return YouTubeCrawler()
    else:
        raise ValueError(f"지원하지 않는 플랫폼: {platform}")


# 편의 함수들
def crawl_genie(songs: List[SongInfo], save_csv: bool = True, save_db: bool = True) -> Dict[str, Any]:
    """Genie 크롤링 편의 함수"""
    crawler = GenieCrawler()
    return crawler.crawl_songs(songs)


def crawl_youtube_music(songs: List[SongInfo], save_csv: bool = True, save_db: bool = True) -> Dict[str, Any]:
    """YouTube Music 크롤링 편의 함수"""
    crawler = YouTubeMusicCrawler()
    return crawler.crawl_songs(songs)


def crawl_youtube(songs: List[SongInfo], save_csv: bool = True, save_db: bool = True) -> Dict[str, Any]:
    """YouTube 크롤링 편의 함수"""
    crawler = YouTubeCrawler()
    return crawler.crawl_songs(songs)


 