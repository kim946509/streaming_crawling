"""
크롤링 전체 프로세스 관리
"""
import logging
from datetime import date
from typing import List, Dict, Any

from crawling_view.common.song_service import SongService
from crawling_view.platform_crawlers import create_crawler
from streaming_site_list.models import SongInfo

logger = logging.getLogger(__name__)


class CrawlingManager:
    """
    크롤링 전체 프로세스를 관리하는 클래스
    """
    
    def __init__(self, target_date: date = None):
        """
        크롤링 매니저 초기화
        
        Args:
            target_date: 크롤링 대상 날짜 (None이면 오늘)
        """
        self.target_date = target_date or date.today()
        self.active_songs: List[SongInfo] = []
        
    def run_full_crawling(self, platforms: List[str] = None, save_csv: bool = True, save_db: bool = True) -> Dict[str, Any]:
        """
        전체 크롤링 프로세스 실행
        
        Args:
            platforms: 크롤링할 플랫폼 리스트 (None이면 모든 플랫폼)
            save_csv: CSV 저장 여부
            save_db: DB 저장 여부
            
        Returns:
            Dict: 각 플랫폼별 크롤링 결과
        """
        logger.info(f"🚀 크롤링 시작: {self.target_date}")
        
        # 1단계: 활성화된 노래들 조회
        self._load_active_songs()
        
        if not self.active_songs:
            logger.warning("❌ 크롤링 대상 곡이 없습니다.")
            return {}
        
        # 2단계: 플랫폼별 크롤링 실행
        results = self._execute_platform_crawling(platforms, save_csv, save_db)
        
        # 3단계: 결과 요약
        self._log_summary(results)
        
        return results
    
    def _load_active_songs(self):
        """1단계: 활성화된 노래들 조회"""
        logger.info("📋 1단계: 활성화된 노래들 조회 중...")
        
        self.active_songs = SongService.get_active_songs(self.target_date)
        
        logger.info(f"✅ 조회 완료: {len(self.active_songs)}개 곡")
        for song in self.active_songs:
            logger.debug(f"   - {song.id}: {song.genie_artist} - {song.genie_title}")
    
    def _execute_platform_crawling(self, platforms: List[str], save_csv: bool, save_db: bool) -> Dict[str, Any]:
        """2단계: 플랫폼별 크롤링 실행"""
        logger.info("🔄 2단계: 플랫폼별 크롤링 실행 중...")
        
        # 기본 플랫폼 설정
        if platforms is None:
            platforms = ['genie', 'youtube_music', 'youtube']
        
        results = {}
        
        for platform in platforms:
            if platform not in ['genie', 'youtube_music', 'youtube']:
                logger.warning(f"⚠️ 지원하지 않는 플랫폼: {platform}")
                continue
            
            try:
                # 플랫폼별 크롤러 생성 및 실행
                crawler = create_crawler(platform, self.active_songs)
                platform_result = crawler.crawl(save_csv, save_db)
                results[platform] = platform_result
                
            except Exception as e:
                logger.error(f"❌ {platform} 크롤링 실패: {e}")
                results[platform] = {'error': str(e)}
        
        return results
    
    def _log_summary(self, results: Dict[str, Any]):
        """3단계: 결과 요약 로그"""
        logger.info("📊 3단계: 크롤링 결과 요약")
        logger.info("=" * 60)
        logger.info(f"🎯 대상 곡 수: {len(self.active_songs)}")
        
        for platform, result in results.items():
            if 'error' in result:
                logger.error(f"❌ {platform}: 오류 발생 - {result['error']}")
            else:
                crawling_result = result.get('crawling_result', [])
                elapsed_time = result.get('elapsed_time', 0)
                
                if isinstance(crawling_result, list):
                    success_count = len(crawling_result)
                elif isinstance(crawling_result, dict):
                    success_count = len(crawling_result)
                else:
                    success_count = 0
                
                logger.info(f"✅ {platform}: {success_count}개 성공 ({elapsed_time:.2f}초)")
        
        logger.info("=" * 60)
        logger.info("🏁 크롤링 완료!")


def run_crawling(target_date: date = None, platforms: List[str] = None, save_csv: bool = True, save_db: bool = True) -> Dict[str, Any]:
    """
    크롤링 실행 함수 (편의 함수)
    
    Args:
        target_date: 크롤링 대상 날짜
        platforms: 크롤링할 플랫폼 리스트
        save_csv: CSV 저장 여부
        save_db: DB 저장 여부
        
    Returns:
        Dict: 크롤링 결과
    """
    manager = CrawlingManager(target_date)
    return manager.run_full_crawling(platforms, save_csv, save_db) 