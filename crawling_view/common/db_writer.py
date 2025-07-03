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

def _validate_and_clean_data(data, platform):
    """
    크롤링 데이터 검증 및 정리
    
    Args:
        data (dict): 크롤링 결과 데이터
        platform (str): 플랫폼명 (genie, youtube, youtube_music)
        
    Returns:
        dict: 정리된 데이터 또는 None (데이터가 유효하지 않은 경우)
    """
    if not data:
        return None
        
    # 필수 필드 검증
    song_id = data.get('song_id')
    song_name = data.get('song_name') or data.get('song_title')
    artist_name = data.get('artist_name')
    
    if not all([song_id, song_name, artist_name]):
        logger.warning(f"❌ {platform} 필수 데이터 누락: song_id={song_id}, song_name={song_name}, artist_name={artist_name}")
        return None
    
    # view_count 처리
    view_count = data.get('view_count', 0)
    if view_count is None or view_count == 'None':
        view_count = 0
        logger.warning(f"⚠️ {platform} 조회수 데이터가 None: {song_name} - {artist_name}")
    
    try:
        view_count = int(view_count) if view_count else 0
    except (ValueError, TypeError):
        view_count = 0
        logger.warning(f"⚠️ {platform} 조회수 변환 실패: {song_name} - {artist_name}")
    
    # 추출 날짜 처리
    extracted_date = data.get('extracted_date') or data.get('crawl_date')
    if isinstance(extracted_date, str):
        try:
            if ' ' in extracted_date:
                extracted_date = extracted_date.split(' ')[0]  # datetime에서 date만 추출
        except Exception:
            extracted_date = datetime.now().date()
    
    return {
        'song_id': song_id,
        'song_name': song_name,
        'artist_name': artist_name,
        'view_count': view_count,
        'extracted_date': extracted_date
    }

def save_genie_to_db(results):
    """
    Genie 크롤링 결과를 DB에 저장
    
    Args:
        results (list): 크롤링 결과 리스트
        
    Returns:
        dict: 저장 결과 (saved_count, failed_count, skipped_count)
    """
    if not results:
        return {'saved_count': 0, 'failed_count': 0, 'skipped_count': 0}
    
    saved_count = 0
    failed_count = 0
    skipped_count = 0
    
    for result in results:
        try:
            # 데이터 검증 및 정리
            clean_data = _validate_and_clean_data(result, 'Genie')
            if not clean_data:
                skipped_count += 1
                continue
            
            # Genie 특별 필드 처리
            view_count_data = result.get('view_count', {})
            if isinstance(view_count_data, dict):
                total_person_count = view_count_data.get('total_person_count', 0)
                view_count = view_count_data.get('view_count', 0)
            else:
                total_person_count = 0
                view_count = clean_data['view_count']
            
            # song_id 생성 (Genie는 아티스트명+곡명 조합으로 고유 ID 생성)
            song_id = f"genie_{clean_data['artist_name']}_{clean_data['song_name']}".lower().replace(' ', '_')
            
            GenieSongViewCount.objects.update_or_create(
                song_id=song_id,
                defaults={
                    'song_name': clean_data['song_name'],
                    'artist_name': clean_data['artist_name'],
                    'total_person_count': total_person_count,
                    'view_count': view_count,
                    'extracted_date': clean_data['extracted_date']
                }
            )
            saved_count += 1
            logger.debug(f"✅ Genie DB 저장 완료: {clean_data['song_name']} - {clean_data['artist_name']}")
            
        except Exception as e:
            failed_count += 1
            logger.error(f"❌ Genie DB 저장 실패: {result} - {e}")
    
    logger.info(f"✅ Genie DB 저장 완료: {saved_count}개 성공, {failed_count}개 실패, {skipped_count}개 스킵")
    return {'saved_count': saved_count, 'failed_count': failed_count, 'skipped_count': skipped_count}

def save_youtube_music_to_db(results):
    """
    YouTube Music 크롤링 결과를 DB에 저장
    
    Args:
        results (list): 크롤링 결과 리스트
        
    Returns:
        dict: 저장 결과 (saved_count, failed_count, skipped_count)
    """
    if not results:
        return {'saved_count': 0, 'failed_count': 0, 'skipped_count': 0}
    
    saved_count = 0
    failed_count = 0
    skipped_count = 0
    
    for result in results:
        try:
            # 데이터 검증 및 정리
            clean_data = _validate_and_clean_data(result, 'YouTube Music')
            if not clean_data:
                skipped_count += 1
                continue
            
            # song_id 생성 (YouTube Music은 아티스트명+곡명 조합으로 고유 ID 생성)
            song_id = f"ytmusic_{clean_data['artist_name']}_{clean_data['song_name']}".lower().replace(' ', '_')
            
            YouTubeMusicSongViewCount.objects.update_or_create(
                song_id=song_id,
                defaults={
                    'song_name': clean_data['song_name'],
                    'artist_name': clean_data['artist_name'],
                    'view_count': clean_data['view_count'],
                    'extracted_date': clean_data['extracted_date']
                }
            )
            saved_count += 1
            logger.debug(f"✅ YouTube Music DB 저장 완료: {clean_data['song_name']} - {clean_data['artist_name']}")
            
        except Exception as e:
            failed_count += 1
            logger.error(f"❌ YouTube Music DB 저장 실패: {result} - {e}")
    
    logger.info(f"✅ YouTube Music DB 저장 완료: {saved_count}개 성공, {failed_count}개 실패, {skipped_count}개 스킵")
    return {'saved_count': saved_count, 'failed_count': failed_count, 'skipped_count': skipped_count}

def save_youtube_to_db(results):
    """
    YouTube 크롤링 결과를 DB에 저장
    
    Args:
        results (dict): 크롤링 결과 딕셔너리 {song_id: data}
        
    Returns:
        dict: 저장 결과 (saved_count, failed_count, skipped_count)
    """
    if not results:
        return {'saved_count': 0, 'failed_count': 0, 'skipped_count': 0}
    
    saved_count = 0
    failed_count = 0
    skipped_count = 0
    
    for song_id, result in results.items():
        try:
            # 데이터 검증 및 정리
            result['song_id'] = song_id  # YouTube는 이미 고유한 video ID를 가지고 있음
            clean_data = _validate_and_clean_data(result, 'YouTube')
            if not clean_data:
                skipped_count += 1
                continue
            
            # upload_date 처리
            upload_date = result.get('upload_date')
            if isinstance(upload_date, str):
                try:
                    if ' ' in upload_date:
                        upload_date = upload_date.split(' ')[0]
                except Exception:
                    upload_date = datetime.now().date()
            
            YouTubeSongViewCount.objects.update_or_create(
                song_id=song_id,
                defaults={
                    'song_name': clean_data['song_name'],
                    'artist_name': clean_data['artist_name'],
                    'view_count': clean_data['view_count'],
                    'youtube_url': result.get('youtube_url', ''),
                    'upload_date': upload_date,
                    'extracted_date': clean_data['extracted_date']
                }
            )
            saved_count += 1
            logger.debug(f"✅ YouTube DB 저장 완료: {clean_data['song_name']} - {clean_data['artist_name']}")
            
        except Exception as e:
            failed_count += 1
            logger.error(f"❌ YouTube DB 저장 실패: {result} - {e}")
    
    logger.info(f"✅ YouTube DB 저장 완료: {saved_count}개 성공, {failed_count}개 실패, {skipped_count}개 스킵")
    return {'saved_count': saved_count, 'failed_count': failed_count, 'skipped_count': skipped_count} 