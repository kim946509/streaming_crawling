"""
DB 저장 관련 함수들
"""
from django.db import transaction
from streaming_site_list.genie.models import GenieSongViewCount
from streaming_site_list.youtube.models import YouTubeSongViewCount
from streaming_site_list.youtube_music.models import YouTubeMusicSongViewCount
from streaming_site_list.models import SongInfo
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
    
    # view_count 처리
    view_count = data.get('view_count', 0)
    if view_count is None or view_count == 'None':
        view_count = 0
        logger.warning(f"⚠️ {platform} 조회수 데이터가 None: song_id={song_id}")
    
    try:
        view_count = int(view_count) if view_count else 0
    except (ValueError, TypeError):
        view_count = 0
        logger.warning(f"⚠️ {platform} 조회수 변환 실패: song_id={song_id}")
    
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
        'view_count': view_count,
        'extracted_date': extracted_date
    }

def get_song_info_id(artist_name, song_name):
    """
    SongInfo 테이블에서 artist_name과 song_name으로 id 조회
    
    Args:
        artist_name (str): 아티스트명
        song_name (str): 곡명
        
    Returns:
        str: SongInfo의 id 또는 None
    """
    try:
        song_info = SongInfo.objects.get(
            artist_name=artist_name,
            song_name=song_name,
            is_deleted=False
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
            # SongInfo ID 조회
            song_name = result.get('song_name') or result.get('song_title')
            artist_name = result.get('artist_name')
            
            if not song_name or not artist_name:
                logger.warning(f"❌ 필수 정보 누락: artist_name={artist_name}, song_name={song_name}")
                skipped_count += 1
                continue
                
            # 기존 SongInfo에서 ID 조회
            song_id = get_song_info_id(artist_name, song_name)
            if not song_id:
                logger.warning(f"❌ SongInfo를 찾을 수 없음: {artist_name} - {song_name}")
                skipped_count += 1
                continue
            
            result['song_id'] = song_id
            
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
            
            GenieSongViewCount.objects.update_or_create(
                song_id=clean_data['song_id'],
                extracted_date=clean_data['extracted_date'],
                defaults={
                    'total_person_count': total_person_count,
                    'view_count': view_count,
                }
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
            # SongInfo ID 조회
            song_name = result.get('song_name') or result.get('song_title')
            artist_name = result.get('artist_name')
            
            if not song_name or not artist_name:
                logger.warning(f"❌ 필수 정보 누락: artist_name={artist_name}, song_name={song_name}")
                skipped_count += 1
                continue
                
            # 기존 SongInfo에서 ID 조회
            song_id = get_song_info_id(artist_name, song_name)
            if not song_id:
                logger.warning(f"❌ SongInfo를 찾을 수 없음: {artist_name} - {song_name}")
                skipped_count += 1
                continue
            
            result['song_id'] = song_id
            
            # 데이터 검증 및 정리
            clean_data = _validate_and_clean_data(result, 'YouTube Music')
            if not clean_data:
                skipped_count += 1
                continue
            
            YouTubeMusicSongViewCount.objects.update_or_create(
                song_id=clean_data['song_id'],
                extracted_date=clean_data['extracted_date'],
                defaults={
                    'view_count': clean_data['view_count'],
                }
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
        results (dict): 크롤링 결과 딕셔너리 {video_id: data}
        
    Returns:
        dict: 저장 결과 (saved_count, failed_count, skipped_count)
    """
    if not results:
        return {'saved_count': 0, 'failed_count': 0, 'skipped_count': 0}
    
    saved_count = 0
    failed_count = 0
    skipped_count = 0
    
    for video_id, result in results.items():
        try:
            # SongInfo ID 조회
            song_name = result.get('song_name') or result.get('song_title')
            artist_name = result.get('artist_name')
            
            if not song_name or not artist_name:
                logger.warning(f"❌ 필수 정보 누락: artist_name={artist_name}, song_name={song_name}")
                skipped_count += 1
                continue
                
            # 기존 SongInfo에서 ID 조회
            song_id = get_song_info_id(artist_name, song_name)
            if not song_id:
                logger.warning(f"❌ SongInfo를 찾을 수 없음: {artist_name} - {song_name}")
                skipped_count += 1
                continue
            
            result['song_id'] = song_id
            
            # 데이터 검증 및 정리
            clean_data = _validate_and_clean_data(result, 'YouTube')
            if not clean_data:
                skipped_count += 1
                continue
            
            # upload_date 처리 (YYYY.MM.DD → YYYY-MM-DD 형식 변환)
            upload_date = result.get('upload_date')
            if isinstance(upload_date, str):
                try:
                    # 'YYYY.MM.DD' 형식을 'YYYY-MM-DD'로 변환
                    if '.' in upload_date:
                        upload_date = upload_date.replace('.', '-')
                    # 시간 부분이 있으면 제거
                    if ' ' in upload_date:
                        upload_date = upload_date.split(' ')[0]
                except Exception:
                    upload_date = datetime.now().date()
            
            YouTubeSongViewCount.objects.update_or_create(
                song_id=clean_data['song_id'],
                extracted_date=clean_data['extracted_date'],
                defaults={
                    'video_id': video_id,
                    'view_count': clean_data['view_count'],
                    'upload_date': upload_date,
                }
            )
            saved_count += 1
            logger.debug(f"✅ YouTube DB 저장 완료: {clean_data['song_id']}")
            
        except Exception as e:
            failed_count += 1
            logger.error(f"❌ YouTube DB 저장 실패: {result} - {e}")
    
    logger.info(f"✅ YouTube DB 저장 완료: {saved_count}개 성공, {failed_count}개 실패, {skipped_count}개 스킵")
    return {'saved_count': saved_count, 'failed_count': failed_count, 'skipped_count': skipped_count} 