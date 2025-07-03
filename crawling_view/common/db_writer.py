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

def save_genie_to_db(results):
    """
    Genie 크롤링 결과를 DB에 저장
    
    Args:
        results (list): 크롤링 결과 리스트
        
    Returns:
        int: 저장된 레코드 수
    """
    if not results:
        return 0
    
    saved_count = 0
    
    for result in results:
        try:
            view_count = result.get('view_count', {})
            if isinstance(view_count, dict):
                total_person_count = view_count.get('total_person_count', 0)
                total_play_count = view_count.get('total_play_count', 0)
            else:
                total_person_count = 0
                total_play_count = 0
            
            GenieSongViewCount.objects.update_or_create(
                song_name=result.get('song_title'),
                artist_name=result.get('artist_name'),
                defaults={
                    'total_person_count': total_person_count,
                    'total_play_count': total_play_count,
                    'extracted_date': result.get('crawl_date')
                }
            )
            saved_count += 1
            logger.debug(f"✅ Genie DB 저장 완료: {result.get('song_title')} - {result.get('artist_name')}")
            
        except Exception as e:
            logger.error(f"❌ Genie DB 저장 실패: {result} - {e}")
    
    logger.info(f"✅ Genie DB 저장 완료: {saved_count}개 레코드")
    return saved_count

def save_youtube_music_to_db(results):
    """
    YouTube Music 크롤링 결과를 DB에 저장
    
    Args:
        results (list): 크롤링 결과 리스트
        
    Returns:
        int: 저장된 레코드 수
    """
    if not results:
        return 0
    
    saved_count = 0
    
    for result in results:
        try:
            YouTubeMusicSongViewCount.objects.update_or_create(
                song_name=result.get('song_title'),
                artist_name=result.get('artist_name'),
                defaults={
                    'view_count': result.get('view_count'),
                    'extracted_date': result.get('crawl_date')
                }
            )
            saved_count += 1
            logger.debug(f"✅ YouTube Music DB 저장 완료: {result.get('song_title')} - {result.get('artist_name')}")
            
        except Exception as e:
            logger.error(f"❌ YouTube Music DB 저장 실패: {result} - {e}")
    
    logger.info(f"✅ YouTube Music DB 저장 완료: {saved_count}개 레코드")
    return saved_count

def save_youtube_to_db(results):
    """
    YouTube 크롤링 결과를 DB에 저장
    
    Args:
        results (dict): 크롤링 결과 딕셔너리
        
    Returns:
        int: 저장된 레코드 수
    """
    if not results:
        return 0
    
    saved_count = 0
    
    for song_id, result in results.items():
        try:
            YouTubeSongViewCount.objects.update_or_create(
                song_id=song_id,
                defaults={
                    'song_name': result.get('song_name'),
                    'artist_name': result.get('artist_name'),
                    'view_count': result.get('view_count'),
                    'youtube_url': result.get('youtube_url'),
                    'upload_date': result.get('upload_date'),
                    'extracted_date': result.get('extracted_date')
                }
            )
            saved_count += 1
            logger.debug(f"✅ YouTube DB 저장 완료: {result.get('song_name')} - {result.get('artist_name')}")
            
        except Exception as e:
            logger.error(f"❌ YouTube DB 저장 실패: {result} - {e}")
    
    logger.info(f"✅ YouTube DB 저장 완료: {saved_count}개 레코드")
    return saved_count 