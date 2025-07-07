"""
크롤링 데이터 모델
"""
from django.db import models
from .base import BaseModel

class PlatformType(models.TextChoices):
    """
    플랫폼 타입 Enum
    """
    MELON = 'melon', 'Melon'
    GENIE = 'genie', 'Genie'
    YOUTUBE = 'youtube', 'YouTube'
    YOUTUBE_MUSIC = 'youtube_music', 'YouTube Music'

class CrawlingData(BaseModel):
    """
    통합 크롤링 결과 모델
    """
    song_id = models.CharField(max_length=32, help_text="노래 ID (song_info.id 참조)")
    views = models.BigIntegerField(help_text="조회수 (정상값: 숫자, 미지원: -1, 오류: -999)")
    listeners = models.BigIntegerField(help_text="청취자 수 (정상값: 숫자, 미지원: -1, 오류: -999)")
    platform = models.CharField(
        max_length=20,
        choices=PlatformType.choices,
        help_text="플랫폼명"
    )

    class Meta:
        db_table = 'crawling_data'
        ordering = ['-created_at']
        unique_together = ['song_id', 'platform', 'created_at']  # 같은 곡, 같은 플랫폼, 같은 시간 중복 방지
        
    def __str__(self):
        return f"{self.platform} - Song {self.song_id}: Views={self.views}, Listeners={self.listeners}" 