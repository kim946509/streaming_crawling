"""
단순화된 크롤링 매니저
크롤링 전체 흐름을 4단계로 단순화:
1. 크롤링 대상 노래 조회
2. 크롤링 실행
3. DB 저장
4. CSV 저장
"""
import logging
from datetime import date
from crawling_view.data.song_service import SongService
from crawling_view.data.db_writer import save_genie_to_db, save_youtube_to_db, save_youtube_music_to_db, save_melon_to_db
from crawling_view.data.csv_writer import save_genie_csv, save_youtube_csv, save_youtube_music_csv, save_melon_csv
from crawling_view.controller.platform_crawlers import create_crawler
from crawling_view.utils.constants import Platforms

logger = logging.getLogger(__name__)

def run_crawling(target_date=None):
    """
    크롤링 전체 프로세스 실행
        
    Args:
        target_date (date, optional): 크롤링 대상 날짜. None이면 오늘 날짜
            
    Returns:
        dict: 크롤링 결과 요약
    """
    logger.info("🚀 크롤링 프로세스 시작")
        
    try:
        # 1단계: 크롤링 대상 노래 조회
        logger.info("📋 1단계: 크롤링 대상 노래 조회")
        active_songs = SongService.get_active_songs(target_date)
        
        if not active_songs:
            logger.warning("⚠️ 크롤링 대상 노래가 없습니다.")
            return {'status': 'no_songs', 'message': '크롤링 대상 노래가 없습니다.'}
        
        # 2단계: 플랫폼별 크롤링 실행
        logger.info("🕷️ 2단계: 플랫폼별 크롤링 실행")
        crawling_results = {}
        
        # Genie 크롤링
        genie_songs = SongService.get_songs_by_platform(active_songs, 'genie')
        if genie_songs:
            logger.info(f"🎵 Genie 크롤링 시작: {len(genie_songs)}개 곡")
            genie_crawler = create_crawler('genie')
            genie_data = SongService.convert_to_crawling_format(genie_songs, 'genie')
            genie_results = genie_crawler.crawl_songs(genie_data)
            crawling_results['genie'] = genie_results
            failed_count = len(genie_songs) - len(genie_results)
            logger.info(f"✅ Genie 크롤링 완료: {len(genie_results)}개 성공, {failed_count}개 실패")
        
        # YouTube Music 크롤링
        ytmusic_songs = SongService.get_songs_by_platform(active_songs, 'youtube_music')
        if ytmusic_songs:
            logger.info(f"🎵 YouTube Music 크롤링 시작: {len(ytmusic_songs)}개 곡")
            ytmusic_crawler = create_crawler('youtube_music')
            ytmusic_data = SongService.convert_to_crawling_format(ytmusic_songs, 'youtube_music')
            ytmusic_results = ytmusic_crawler.crawl_songs(ytmusic_data)
            crawling_results['youtube_music'] = ytmusic_results
            failed_count = len(ytmusic_songs) - len(ytmusic_results)
            logger.info(f"✅ YouTube Music 크롤링 완료: {len(ytmusic_results)}개 성공, {failed_count}개 실패")
        
        # YouTube 크롤링
        youtube_songs = SongService.get_songs_by_platform(active_songs, 'youtube')
        if youtube_songs:
            logger.info(f"🎵 YouTube 크롤링 시작: {len(youtube_songs)}개 곡")
            youtube_crawler = create_crawler('youtube')
            youtube_data = SongService.convert_to_crawling_format(youtube_songs, 'youtube')
            youtube_results = youtube_crawler.crawl_songs(youtube_data)
            crawling_results['youtube'] = youtube_results
            failed_count = len(youtube_songs) - len(youtube_results)
            logger.info(f"✅ YouTube 크롤링 완료: {len(youtube_results)}개 성공, {failed_count}개 실패")
        
        # Melon 크롤링
        melon_songs = SongService.get_songs_by_platform(active_songs, 'melon')
        if melon_songs:
            logger.info(f"🍈 Melon 크롤링 시작: {len(melon_songs)}개 곡")
            melon_crawler = create_crawler('melon')
            melon_data = SongService.convert_to_crawling_format(melon_songs, 'melon')
            melon_results = melon_crawler.crawl_songs(melon_data)
            crawling_results['melon'] = melon_results
            failed_count = len(melon_songs) - len(melon_results)
            logger.info(f"✅ Melon 크롤링 완료: {len(melon_results)}개 성공, {failed_count}개 실패")
        
        # 3단계: DB 저장
        logger.info("💾 3단계: DB 저장")
        db_results = {}
        
        if 'genie' in crawling_results:
            db_results['genie'] = save_genie_to_db(crawling_results['genie'])
        
        if 'youtube_music' in crawling_results:
            db_results['youtube_music'] = save_youtube_music_to_db(crawling_results['youtube_music'])
        
        if 'youtube' in crawling_results:
            db_results['youtube'] = save_youtube_to_db(crawling_results['youtube'])
        
        if 'melon' in crawling_results:
            db_results['melon'] = save_melon_to_db(crawling_results['melon'])
        
        # 4단계: CSV 저장
        logger.info("📄 4단계: CSV 저장")
        csv_results = {}
        
        if 'genie' in crawling_results:
            csv_results['genie'] = save_genie_csv(crawling_results['genie'])
                
        if 'youtube_music' in crawling_results:
            csv_results['youtube_music'] = save_youtube_music_csv(crawling_results['youtube_music'])
        
        if 'youtube' in crawling_results:
            csv_results['youtube'] = save_youtube_csv(crawling_results['youtube'])
        
        if 'melon' in crawling_results:
            csv_results['melon'] = save_melon_csv(crawling_results['melon'])
        
        # 결과 요약
        summary = {
            'status': 'success',
            'target_date': target_date or date.today(),
            'total_songs': len(active_songs),
            'crawling_results': crawling_results,
            'db_results': db_results,
            'csv_results': csv_results
        }
        
        logger.info("✅ 크롤링 프로세스 완료")
        logger.info(f"📊 결과 요약: {len(active_songs)}개 곡, {len(crawling_results)}개 플랫폼")
        
        return summary
        
    except Exception as e:
        logger.error(f"❌ 크롤링 프로세스 실패: {e}", exc_info=True)
        return {'status': 'error', 'message': str(e)}

def run_platform_crawling(platform, target_date=None):
    """
    특정 플랫폼만 크롤링 실행
    
    Args:
        platform (str): 플랫폼명 ('genie', 'youtube', 'youtube_music', 'melon')
        target_date (date, optional): 크롤링 대상 날짜
        
    Returns:
        dict: 크롤링 결과
    """
    logger.info(f"🚀 {platform} 플랫폼 크롤링 시작")
    
    try:
        # 1단계: 크롤링 대상 노래 조회
        active_songs = SongService.get_active_songs(target_date)
        platform_songs = SongService.get_songs_by_platform(active_songs, platform)
        
        if not platform_songs:
            logger.warning(f"⚠️ {platform} 크롤링 대상 노래가 없습니다.")
            return {'status': 'no_songs', 'platform': platform}
        
        # 2단계: 크롤링 실행
        crawler = create_crawler(platform)
        crawling_data = SongService.convert_to_crawling_format(platform_songs, platform)
        crawling_results = crawler.crawl_songs(crawling_data)
        
        # 3단계: DB 저장
        if platform == Platforms.GENIE:
            db_results = save_genie_to_db(crawling_results)
        elif platform == Platforms.YOUTUBE_MUSIC:
            db_results = save_youtube_music_to_db(crawling_results)
        elif platform == Platforms.YOUTUBE:
            db_results = save_youtube_to_db(crawling_results)
        elif platform == Platforms.MELON:
            db_results = save_melon_to_db(crawling_results)
        else:
            db_results = {'error': '지원하지 않는 플랫폼'}
        
        # 4단계: CSV 저장
        if platform == Platforms.GENIE:
            csv_results = save_genie_csv(crawling_results)
        elif platform == Platforms.YOUTUBE_MUSIC:
            csv_results = save_youtube_music_csv(crawling_results)
        elif platform == Platforms.YOUTUBE:
            csv_results = save_youtube_csv(crawling_results)
        elif platform == Platforms.MELON:
            csv_results = save_melon_csv(crawling_results)
        else:
            csv_results = {'error': '지원하지 않는 플랫폼'}
        
        summary = {
            'status': 'success',
            'platform': platform,
            'target_date': target_date or date.today(),
            'total_songs': len(platform_songs),
            'crawling_results': crawling_results,
            'db_results': db_results,
            'csv_results': csv_results
        }
        
        logger.info(f"✅ {platform} 크롤링 완료")
        return summary
        
    except Exception as e:
        logger.error(f"❌ {platform} 크롤링 실패: {e}", exc_info=True)
        return {'status': 'error', 'platform': platform, 'message': str(e)} 