"""
단일 곡 크롤링 Django Management Command
"""
import logging
import time
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from crawling_view.models import SongInfo
from crawling_view.controller.crawling_manager import run_platform_crawling
from crawling_view.data.song_service import SongService
from crawling_view.utils.constants import Platforms

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/single_crawling_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '단일 곡에 대해 모든 플랫폼 크롤링 실행'

    def add_arguments(self, parser):
        parser.add_argument(
            '--song-id',
            type=str,
            required=True,
            help='크롤링할 곡의 ID (SongInfo.id)'
        )

    def handle(self, *args, **options):
        song_id = options['song_id']
        
        try:
            # 1. 곡 정보 조회
            logger.info(f"🎵 단일 곡 크롤링 시작 - Song ID: {song_id}")
            
            try:
                song = SongInfo.objects.get(id=song_id)
            except SongInfo.DoesNotExist:
                logger.error(f"❌ 곡을 찾을 수 없습니다. Song ID: {song_id}")
                raise CommandError(f"Song ID {song_id}에 해당하는 곡이 존재하지 않습니다.")
            
            logger.info(f"📋 곡 정보: {song.artist_ko} - {song.title_ko}")
            
            # 2. 플랫폼별 크롤링 가능 여부 확인
            platforms = Platforms.ALL_PLATFORMS
            available_platforms = []
            
            for platform in platforms:
                if song.is_platform_available(platform):
                    available_platforms.append(platform)
                    logger.info(f"✅ {platform} 크롤링 가능")
                else:
                    logger.info(f"❌ {platform} 크롤링 불가능 (필수 정보 부족)")
            
            if not available_platforms:
                logger.warning("⚠️ 크롤링 가능한 플랫폼이 없습니다.")
                return
            
            # 3. 각 플랫폼별로 크롤링 실행
            total_results = {}
            
            for platform in available_platforms:
                logger.info(f"🚀 {platform} 크롤링 시작...")
                
                try:
                    # 임시로 해당 곡만을 대상으로 크롤링 실행
                    result = self.crawl_single_song_platform(song, platform)
                    total_results[platform] = result
                    
                    if result.get('status') == 'success':
                        logger.info(f"✅ {platform} 크롤링 완료")
                    else:
                        logger.warning(f"⚠️ {platform} 크롤링 실패: {result.get('error', '알 수 없는 오류')}")
                        
                except Exception as e:
                    logger.error(f"❌ {platform} 크롤링 중 오류: {e}", exc_info=True)
                    total_results[platform] = {'status': 'error', 'error': str(e)}
            
            # 4. 전체 결과 요약
            success_count = len([r for r in total_results.values() if r.get('status') == 'success'])
            total_count = len(total_results)
            
            logger.info("=" * 50)
            logger.info("📊 단일 곡 크롤링 완료")
            logger.info(f"🎵 대상 곡: {song.artist_ko} - {song.title_ko}")
            logger.info(f"✅ 성공: {success_count}/{total_count} 플랫폼")
            logger.info(f"📈 성공률: {(success_count/total_count*100):.1f}%")
            
            for platform, result in total_results.items():
                status_emoji = "✅" if result.get('status') == 'success' else "❌"
                logger.info(f"   {status_emoji} {platform}: {result.get('status', 'unknown')}")
            
            logger.info("=" * 50)
            
        except Exception as e:
            logger.error(f"❌ 단일 곡 크롤링 실행 중 전체 오류: {e}", exc_info=True)
            raise CommandError(f"크롤링 실행 중 오류가 발생했습니다: {e}")

    def crawl_single_song_platform(self, song, platform):
        """
        단일 곡의 특정 플랫폼 크롤링
        
        Args:
            song (SongInfo): 크롤링할 곡 객체
            platform (str): 플랫폼명
            
        Returns:
            dict: 크롤링 결과
        """
        try:
            # SongService를 사용하여 크롤링 데이터 포맷 변환
            crawling_data = SongService.convert_to_crawling_format([song], platform)
            
            if not crawling_data:
                return {'status': 'error', 'error': f'{platform} 크롤링 데이터 변환 실패'}
            
            # 플랫폼별 크롤링 실행 (기존 로직 활용)
            from crawling_view.controller.platform_crawlers import create_crawler
            from crawling_view.data.db_writer import save_genie_to_db, save_youtube_to_db, save_youtube_music_to_db, save_melon_to_db
            from crawling_view.data.csv_writer import save_genie_csv, save_youtube_csv, save_youtube_music_csv, save_melon_csv
            
            # 크롤러 생성 및 실행
            crawler = create_crawler(platform)
            crawling_results = crawler.crawl_songs(crawling_data)
            
            if not crawling_results:
                return {'status': 'error', 'error': '크롤링 결과가 비어있음'}
            
            # DB 저장
            if platform == Platforms.GENIE:
                db_result = save_genie_to_db(crawling_results)
                csv_result = save_genie_csv(crawling_results)
            elif platform == Platforms.YOUTUBE_MUSIC:
                db_result = save_youtube_music_to_db(crawling_results)
                csv_result = save_youtube_music_csv(crawling_results)
            elif platform == Platforms.YOUTUBE:
                db_result = save_youtube_to_db(crawling_results)
                csv_result = save_youtube_csv(crawling_results)
            elif platform == Platforms.MELON:
                db_result = save_melon_to_db(crawling_results)
                csv_result = save_melon_csv(crawling_results)
            else:
                return {'status': 'error', 'error': f'지원하지 않는 플랫폼: {platform}'}
            
            return {
                'status': 'success',
                'crawling_count': len(crawling_results),
                'db_result': db_result,
                'csv_result': csv_result
            }
            
        except Exception as e:
            logger.error(f"플랫폼 {platform} 크롤링 중 오류: {e}", exc_info=True)
            return {'status': 'error', 'error': str(e)} 