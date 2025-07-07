"""
DB 저장 관련 함수들
"""
from django.db import transaction
from streaming_site_list.models import SongInfo, CrawlingData, PlatformType
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
    
    if not song_id:
        logger.warning(f"❌ {platform} 필수 데이터 누락: song_id={song_id}")
        return None
    
    # views 처리 (필수 데이터)
    views = data.get('views')
    if views is None or views == 'None':
        views = -999  # 오류 (필수 데이터 누락)
        logger.error(f"❌ {platform} 조회수 데이터 누락: song_id={song_id}")
    else:
        try:
            views = int(views) if views else -999  # 0도 오류로 처리 (데이터가 있어야 함)
        except (ValueError, TypeError):
            original_views = views  # 원래 값 보존
            views = -999  # 오류
            logger.error(f"❌ {platform} 조회수 변환 실패: song_id={song_id}, 원래값={original_views} (type: {type(original_views)}), 변환후=-999")
    
    # listeners 처리 (필수 데이터)
    listeners = data.get('listeners')
    if listeners is None or listeners == 'None':
        listeners = -999  # 오류 (필수 데이터 누락)
        logger.error(f"❌ {platform} 청취자 수 데이터 누락: song_id={song_id}")
    else:
        try:
            listeners = int(listeners) if listeners else -999  # 0도 오류로 처리 (데이터가 있어야 함)
        except (ValueError, TypeError):
            original_listeners = listeners  # 원래 값 보존
            listeners = -999  # 오류
            logger.error(f"❌ {platform} 청취자 수 변환 실패: song_id={song_id}, 원래값={original_listeners} (type: {type(original_listeners)}), 변환후=-999")
    
    return {
        'song_id': song_id,
        'views': views,
        'listeners': listeners
    }

def get_song_info_id(artist_name, song_name):
    """
    SongInfo 테이블에서 artist와 title로 id 조회
    
    Args:
        artist_name (str): 아티스트명
        song_name (str): 곡명
        
    Returns:
        str: SongInfo의 id 또는 None
    """
    try:
        song_info = SongInfo.objects.get(
            artist=artist_name,
            title=song_name
        )
        logger.debug(f"✅ SongInfo 조회 성공: {song_info.id} - {artist_name} - {song_name}")
        return song_info.id
    except SongInfo.DoesNotExist:
        logger.warning(f"❌ SongInfo 찾을 수 없음: {artist_name} - {song_name}")
        return None
    except Exception as e:
        logger.error(f"❌ SongInfo 조회 실패: {artist_name} - {song_name} - {e}")
        return None

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
            # song_id가 있는지 확인
            song_id = result.get('song_id')
            
            if not song_id:
                logger.warning(f"❌ song_id 누락으로 스킵: {result}")
                skipped_count += 1
                continue
            
            # 데이터 검증 및 정리
            clean_data = _validate_and_clean_data(result, 'Genie')
            if not clean_data:
                skipped_count += 1
                continue
            
            CrawlingData.objects.create(
                song_id=clean_data['song_id'],
                views=clean_data['views'],
                listeners=clean_data['listeners'],
                platform=PlatformType.GENIE
            )
            saved_count += 1
            logger.debug(f"✅ Genie DB 저장 완료: {clean_data['song_id']}")
            
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
            # song_id가 있는지 확인
            song_id = result.get('song_id')
            
            if not song_id:
                logger.warning(f"❌ song_id 누락으로 스킵: {result}")
                skipped_count += 1
                continue
            
            # 데이터 검증 및 정리
            clean_data = _validate_and_clean_data(result, 'YouTube Music')
            if not clean_data:
                skipped_count += 1
                continue
            
            CrawlingData.objects.create(
                song_id=clean_data['song_id'],
                views=clean_data['views'],
                listeners=clean_data['listeners'],
                platform=PlatformType.YOUTUBE_MUSIC
            )
            saved_count += 1
            logger.debug(f"✅ YouTube Music DB 저장 완료: {clean_data['song_id']}")
            
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
            # song_id가 있는지 확인
            if not song_id:
                logger.warning(f"❌ song_id 누락으로 스킵: {result}")
                skipped_count += 1
                continue
            
            # 데이터 검증 및 정리
            clean_data = _validate_and_clean_data(result, 'YouTube')
            if not clean_data:
                skipped_count += 1
                continue
            
            CrawlingData.objects.create(
                song_id=clean_data['song_id'],
                views=clean_data['views'],
                listeners=clean_data['listeners'],
                platform=PlatformType.YOUTUBE
            )
            saved_count += 1
            logger.debug(f"✅ YouTube DB 저장 완료: {clean_data['song_id']}")
            
        except Exception as e:
            failed_count += 1
            logger.error(f"❌ YouTube DB 저장 실패: {result} - {e}")
    
    logger.info(f"✅ YouTube DB 저장 완료: {saved_count}개 성공, {failed_count}개 실패, {skipped_count}개 스킵")
    return {'saved_count': saved_count, 'failed_count': failed_count, 'skipped_count': skipped_count} 