"""
DB 저장 관련 함수들
"""
from django.db import transaction
from streaming_site_list.genie.models import GenieSongViewCount
from streaming_site_list.youtube.models import YouTubeSongViewCount
from streaming_site_list.youtube_music.models import YouTubeMusicSongViewCount
from datetime import datetime
from .constants import CommonSettings
import logging

logger = logging.getLogger(__name__)

def save_genie_to_db(data):
    """
    Genie 크롤링 데이터를 DB에 저장
    
    Args:
        data (list): 저장할 데이터 리스트
    
    Returns:
        int: 저장된 레코드 수
    """
    if not data:
        logger.warning("저장할 데이터가 없습니다.")
        return 0
    
    saved_count = 0
    
    try:
        with transaction.atomic():
            for item in data:
                # view_count 정보 처리
                view_count = item.get('view_count', {})
                total_person_count = 0
                total_play_count = 0
                
                if isinstance(view_count, dict):
                    total_person_count = view_count.get('total_person_count', 0)
                    total_play_count = view_count.get('total_play_count', 0)
                
                # 중복 체크 (song_name과 artist_name으로 체크)
                crawl_date = datetime.strptime(item['crawl_date'], CommonSettings.DATE_FORMAT).date()
                existing = GenieSongViewCount.objects.filter(
                    song_name=item['song_title'],
                    artist_name=item['artist_name'],
                    extracted_date=crawl_date
                ).first()
                
                if not existing:
                    GenieSongViewCount.objects.create(
                        song_name=item['song_title'],
                        artist_name=item['artist_name'],
                        total_person_count=total_person_count,
                        total_play_count=total_play_count,
                        extracted_date=crawl_date
                    )
                    saved_count += 1
                else:
                    logger.debug(f"중복 데이터 스킵: {item['song_title']} - {item['artist_name']}")
        
        logger.info(f"✅ Genie DB 저장 완료: {saved_count}개 레코드")
        return saved_count
        
    except Exception as e:
        logger.error(f"❌ Genie DB 저장 실패: {e}", exc_info=True)
        return 0

def save_youtube_music_to_db(data):
    """
    YouTube Music 크롤링 데이터를 DB에 저장
    
    Args:
        data (list): 저장할 데이터 리스트
    
    Returns:
        int: 저장된 레코드 수
    """
    if not data:
        logger.warning("저장할 데이터가 없습니다.")
        return 0
    
    saved_count = 0
    
    try:
        with transaction.atomic():
            for item in data:
                # 중복 체크 (song_name과 artist_name으로 체크)
                crawl_date = datetime.strptime(item['crawl_date'], CommonSettings.DATE_FORMAT).date()
                existing = YouTubeMusicSongViewCount.objects.filter(
                    song_name=item['song_title'],
                    artist_name=item['artist_name'],
                    extracted_date=crawl_date
                ).first()
                
                if not existing:
                    YouTubeMusicSongViewCount.objects.create(
                        song_name=item['song_title'],
                        artist_name=item['artist_name'],
                        view_count=item['view_count'],
                        extracted_date=crawl_date
                    )
                    saved_count += 1
                else:
                    logger.debug(f"중복 데이터 스킵: {item['song_title']} - {item['artist_name']}")
        
        logger.info(f"✅ YouTube Music DB 저장 완료: {saved_count}개 레코드")
        return saved_count
        
    except Exception as e:
        logger.error(f"❌ YouTube Music DB 저장 실패: {e}", exc_info=True)
        return 0

def save_youtube_to_db(data):
    """
    YouTube 크롤링 데이터를 DB에 저장
    
    Args:
        data (list): 저장할 데이터 리스트
    
    Returns:
        int: 저장된 레코드 수
    """
    if not data:
        logger.warning("저장할 데이터가 없습니다.")
        return 0
    
    saved_count = 0
    
    try:
        with transaction.atomic():
            for item in data:
                # 중복 체크 (song_name과 youtube_url로 체크)
                crawl_date = datetime.strptime(item['crawl_date'], CommonSettings.DATE_FORMAT).date()
                existing = YouTubeSongViewCount.objects.filter(
                    song_name=item['song_title'],
                    youtube_url=item.get('youtube_url', ''),
                    extracted_date=crawl_date
                ).first()
                
                if not existing:
                    # song_id 생성 (YouTube URL에서 비디오 ID 추출)
                    youtube_url = item.get('youtube_url', '')
                    song_id = youtube_url.split('v=')[-1].split('&')[0] if 'v=' in youtube_url else ''
                    
                    # upload_date 처리
                    upload_date = None
                    if item.get('upload_date'):
                        try:
                            upload_date = datetime.strptime(item['upload_date'], '%Y.%m.%d').date()
                        except ValueError:
                            upload_date = crawl_date
                    
                    YouTubeSongViewCount.objects.create(
                        song_id=song_id,
                        song_name=item['song_title'],
                        view_count=item['view_count'],
                        youtube_url=youtube_url,
                        extracted_date=crawl_date,
                        upload_date=upload_date or crawl_date
                    )
                    saved_count += 1
                else:
                    logger.debug(f"중복 데이터 스킵: {item['song_title']} - {item.get('youtube_url', '')}")
        
        logger.info(f"✅ YouTube DB 저장 완료: {saved_count}개 레코드")
        return saved_count
        
    except Exception as e:
        logger.error(f"❌ YouTube DB 저장 실패: {e}", exc_info=True)
        return 0 