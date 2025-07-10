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
    # 기본 정보
    artist_ko = models.CharField(max_length=255, default="unknown", help_text="아티스트명 (국문)")
    artist_en = models.CharField(max_length=255, default="unknown", help_text="아티스트명 (영문)")
    title_ko = models.CharField(max_length=255, default="unknown", help_text="곡 제목 (국문)")
    title_en = models.CharField(max_length=255,  default="unknown",help_text="곡 제목 (영문)")
    
    # 크롤링용 필수 정보
    youtube_url = models.URLField(max_length=500, blank=True, null=True, help_text="YouTube URL (YouTube 크롤링용)")
    melon_song_id = models.CharField(max_length=100, blank=True, null=True, help_text="멜론 곡 ID (Melon 크롤링용)", unique=True)

    class Meta:
        db_table = 'song_info'
        
    def __str__(self):
        return f"[{self.id}] {self.artist_ko} - {self.title_ko}"
    
    def get_platform_info(self, platform):
        """
        플랫폼별 정보 조회
        
        Args:
            platform (str): 플랫폼명 ('melon', 'genie', 'youtube', 'youtube_music')
            
        Returns:
            dict: 플랫폼별 정보
        """
        base_info = {
            'title_ko': self.title_ko,
            'title_en': self.title_en,
            'artist_ko': self.artist_ko,
            'artist_en': self.artist_en
        }
        
        if platform == Platforms.MELON:
            return {
                **base_info,
                'song_id': self.melon_song_id
            }
        elif platform == Platforms.YOUTUBE:
            return {
                **base_info,
                'url': self.youtube_url
            }
        else:
            return base_info
    
    def is_platform_available(self, platform):
        """
        플랫폼 크롤링 가능 여부 확인
        
        Args:
            platform (str): 플랫폼명
            
        Returns:
            bool: 크롤링 가능 여부
        """
        # 기본적으로 국문 정보는 필수
        has_basic_info = bool(self.title_ko and self.artist_ko)
        
        if platform == Platforms.MELON:
            return has_basic_info and bool(self.melon_song_id)
        elif platform == Platforms.YOUTUBE:
            return has_basic_info and bool(self.youtube_url)
        else:
            return has_basic_info 