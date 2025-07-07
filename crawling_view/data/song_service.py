"""
크롤링 대상 곡 조회 서비스
"""
from datetime import date
from streaming_site_list.models import SongInfo, CrawlingPeriod
import logging

logger = logging.getLogger(__name__)


class SongService:
    """
    크롤링 대상 곡 조회 및 관리 서비스
    """
    
    @staticmethod
    def get_active_songs(target_date=None):
        """
        특정 날짜를 기준으로 활성화된 크롤링 대상 곡들을 조회
        
        Args:
            target_date (date, optional): 기준 날짜. None이면 오늘 날짜 사용
            
        Returns:
            list: SongInfo 객체 리스트
        """
        if target_date is None:
            target_date = date.today()
        
        # 1. 해당 날짜가 크롤링 기간에 포함되고 활성화된 song_id 조회
        active_periods = CrawlingPeriod.objects.filter(
            start_date__lte=target_date,
            end_date__gte=target_date,
            is_active=True
        ).values_list('song_id', flat=True)
        
        logger.info(f"📅 기준 날짜: {target_date}")
        logger.info(f"🔍 활성 크롤링 기간에 포함된 song_id 개수: {len(active_periods)}")
        
        # 2. 해당 song_id들의 SongInfo 조회
        active_songs = SongInfo.objects.filter(
            id__in=active_periods
        )
        
        logger.info(f"🎵 크롤링 대상 곡 개수: {len(active_songs)}")
        
        for song in active_songs:
            logger.debug(f"   - {song.id}: {song.genie_artist} - {song.genie_title}")
        
        return list(active_songs)
    
    @staticmethod
    def get_active_crawling_songs(target_date=None):
        """
        get_active_songs의 별칭 (기존 코드 호환성)
        """
        return SongService.get_active_songs(target_date)
    
    @staticmethod
    def get_songs_by_platform(songs, platform):
        """
        플랫폼별로 필터링된 곡 목록 반환
        
        Args:
            songs (list): SongInfo 객체 리스트
            platform (str): 플랫폼명 ('youtube', 'genie', 'youtube_music')
            
        Returns:
            list: 필터링된 SongInfo 객체 리스트
        """
        if platform == 'youtube':
            # YouTube URL이 있는 곡들만 필터링
            return [song for song in songs if song.is_platform_available('youtube')]
        elif platform in ['genie', 'youtube_music']:
            # 해당 플랫폼 정보가 있는 곡들만 필터링
            return [song for song in songs if song.is_platform_available(platform)]
        else:
            logger.warning(f"❌ 알 수 없는 플랫폼: {platform}")
            return []
    
    @staticmethod
    def convert_to_crawling_format(songs, platform):
        """
        SongInfo 객체들을 크롤링 형식으로 변환
        
        Args:
            songs (list): SongInfo 객체 리스트
            platform (str): 플랫폼명
            
        Returns:
            list: 크롤링 형식의 데이터 리스트
        """
        if platform == 'genie':
            return [
                {
                    'song_id': song.id,
                    'song_title': song.get_platform_info('genie')['title'],
                    'artist_name': song.get_platform_info('genie')['artist']
                }
                for song in songs
                if song.is_platform_available('genie')
            ]
        elif platform == 'youtube_music':
            return [
                {
                    'song_id': song.id,
                    'song_title': song.get_platform_info('youtube_music')['title'],
                    'artist_name': song.get_platform_info('youtube_music')['artist']
                }
                for song in songs
                if song.is_platform_available('youtube_music')
            ]
        elif platform == 'youtube':
            return [
                (song.get_platform_info('youtube')['url'], song.get_platform_info('youtube')['artist'], song.id)
                for song in songs
                if song.is_platform_available('youtube')
            ]
        else:
            logger.warning(f"❌ 알 수 없는 플랫폼: {platform}")
            return [] 