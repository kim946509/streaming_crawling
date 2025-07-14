"""
단일 곡 크롤링/저장 매니저
"""
import logging
from datetime import date
from crawling_view.data.song_service import SongService
from crawling_view.utils.constants import Platforms
from crawling_view.controller.crawling_manager import create_crawler
from crawling_view.data.db_writer import (
    save_genie_to_db, save_youtube_music_to_db, save_youtube_to_db, save_melon_to_db
)
from crawling_view.data.csv_writer import (
    save_genie_csv, save_youtube_music_csv, save_youtube_csv, save_melon_csv
)

logger = logging.getLogger(__name__)

def run_single_song_crawling(song_dict, save_csv=True, save_db=True, platform=None):
    """
    단일 곡 크롤링 및 저장 (여러 곡과 동일한 로직, 곡 리스트만 1개)
    Args:
        song_dict (dict): {'song_id', 'song_title', 'artist_name', 'title_en', 'artist_en'}
        save_csv (bool): CSV 저장 여부
        save_db (bool): DB 저장 여부
        platform (str or None): 특정 플랫폼만 실행 (None이면 전체)
    Returns:
        dict: 결과 요약
    """
    logger.info("🚀 단일 곡 크롤링 프로세스 시작")

    crawling_results = {}
    db_results = {}
    csv_results = {}

    platforms_to_run = [platform] if platform else Platforms.ALL_PLATFORMS

    for plat in platforms_to_run:
        if plat == Platforms.GENIE:
            # Genie용 데이터 형식
            genie_data = [{
                'song_id': song_dict['song_id'],
                'song_title': song_dict['song_title'],
                'artist_name': song_dict['artist_name']
            }]
            
            genie_crawler = create_crawler('genie')
            genie_results = genie_crawler.crawl_songs(genie_data)
            crawling_results['genie'] = genie_results
            if save_db:
                db_results['genie'] = save_genie_to_db(genie_results)
            if save_csv:
                csv_results['genie'] = save_genie_csv(genie_results)
                
        elif plat == Platforms.YOUTUBE_MUSIC:
            # YouTube Music용 데이터 형식
            ytmusic_data = [{
                'song_id': song_dict['song_id'],
                'song_title': song_dict['song_title'],
                'artist_name': song_dict['artist_name']
            }]
            
            ytmusic_crawler = create_crawler('youtube_music')
            ytmusic_results = ytmusic_crawler.crawl_songs(ytmusic_data)
            crawling_results['youtube_music'] = ytmusic_results
            if save_db:
                db_results['youtube_music'] = save_youtube_music_to_db(ytmusic_results)
            if save_csv:
                csv_results['youtube_music'] = save_youtube_music_csv(ytmusic_results)
                
        elif plat == Platforms.YOUTUBE:
            # YouTube는 song_dict에서 직접 URL 정보 사용
            youtube_url = song_dict.get('youtube_url')
            logger.info(f"🔍 YouTube 크롤링 시작: song_id={song_dict['song_id']}")
            logger.info(f"🔗 YouTube URL: {youtube_url}")
            
            if youtube_url:
                youtube_data = [(youtube_url, song_dict['artist_name'], song_dict['song_id'])]
                logger.info(f"📝 YouTube 데이터 준비: {youtube_data}")
                
                youtube_crawler = create_crawler('youtube')
                youtube_results = youtube_crawler.crawl_songs(youtube_data)
                crawling_results['youtube'] = youtube_results
                if save_db:
                    db_results['youtube'] = save_youtube_to_db(youtube_results)
                if save_csv:
                    csv_results['youtube'] = save_youtube_csv(youtube_results)
            else:
                logger.warning(f"⚠️ YouTube URL이 비어있는 곡: {song_dict['song_id']}")
                
        elif plat == Platforms.MELON:
            # Melon은 song_dict에서 직접 melon_song_id 사용
            melon_song_id = song_dict.get('melon_song_id')
            logger.info(f"🔍 Melon 크롤링 시작: song_id={song_dict['song_id']}")
            logger.info(f"🎵 Melon song_id: {melon_song_id}")
            
            if melon_song_id:
                melon_data = [{
                    'song_id': song_dict['song_id'],
                    'melon_song_id': melon_song_id
                }]
                
                melon_crawler = create_crawler('melon')
                melon_results = melon_crawler.crawl_songs(melon_data)
                crawling_results['melon'] = melon_results
                if save_db:
                    db_results['melon'] = save_melon_to_db(melon_results)
                if save_csv:
                    csv_results['melon'] = save_melon_csv(melon_results)
            else:
                logger.warning(f"⚠️ Melon song_id가 비어있는 곡: {song_dict['song_id']}")

    summary = {
        'status': 'success',
        'crawling_results': crawling_results,
        'db_results': db_results,
        'csv_results': csv_results
    }
    logger.info("✅ 단일 곡 크롤링 프로세스 완료")
    return summary 