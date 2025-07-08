"""
노래 정보 모델
"""
from django.db import models
from .base import BaseModel
from crawling_view.utils.constants import Platforms

class SongInfo(BaseModel):
    """
    노래 기본 정보 모델
    """
    # 플랫폼별 정보 (필수 정보만)
    genie_title = models.CharField(max_length=255, blank=True, null=True, help_text="지니 곡 제목")
    genie_artist = models.CharField(max_length=255, blank=True, null=True, help_text="지니 아티스트명")
    youtube_music_title = models.CharField(max_length=255, blank=True, null=True, help_text="유튜브 뮤직 곡 제목")
    youtube_music_artist = models.CharField(max_length=255, blank=True, null=True, help_text="유튜브 뮤직 아티스트명")
    
    # 크롤링용 필수 정보
    youtube_url = models.URLField(max_length=500, blank=True, null=True, help_text="YouTube URL (YouTube 크롤링용)")
    melon_song_id = models.CharField(max_length=100, blank=True, null=True, help_text="멜론 곡 ID (Melon 크롤링용)", unique=True)

    class Meta:
        db_table = 'song_info'
        
    def __str__(self):
        return f"[{self.id}] {self.genie_artist} - {self.genie_title}"
    
    def get_platform_info(self, platform):
        """
        플랫폼별 정보 조회
        
        Args:
            platform (str): 플랫폼명 ('melon', 'genie', 'youtube', 'youtube_music')
            
        Returns:
            dict: 플랫폼별 정보
        """
        if platform == Platforms.MELON:
            return {
                'song_id': self.melon_song_id,
                'title': self.youtube_music_title,  # YouTube Music 정보로 대체
                'artist': self.youtube_music_artist  # YouTube Music 정보로 대체
            }
        elif platform == Platforms.GENIE:
            return {
                'title': self.genie_title,
                'artist': self.genie_artist
            }
        elif platform == Platforms.YOUTUBE:
            return {
                'url': self.youtube_url,
                'title': self.youtube_music_title,  # YouTube Music 정보로 대체
                'artist': self.youtube_music_artist  # YouTube Music 정보로 대체
            }
        elif platform == Platforms.YOUTUBE_MUSIC:
            return {
                'title': self.youtube_music_title,
                'artist': self.youtube_music_artist
            }
        else:
            return {
                'title': self.genie_title,
                'artist': self.genie_artist
            }
    
    def is_platform_available(self, platform):
        """
        플랫폼 크롤링 가능 여부 확인
        
        Args:
            platform (str): 플랫폼명
            
        Returns:
            bool: 크롤링 가능 여부
        """
        if platform == Platforms.MELON:
            return bool(self.melon_song_id)
        elif platform == Platforms.GENIE:
            return bool(self.genie_title and self.genie_artist)
        elif platform == Platforms.YOUTUBE:
            return bool(self.youtube_url)
        elif platform == Platforms.YOUTUBE_MUSIC:
            return bool(self.youtube_music_title and self.youtube_music_artist)
        else:
            return False 