"""
크롤링 기간 관리 모델
"""
from django.db import models
from .base import BaseModel

class CrawlingPeriod(BaseModel):
    """
    크롤링 기간 관리 모델
    """
    song_id = models.CharField(max_length=36, help_text="노래 ID (song_info.id 참조)")
    start_date = models.DateField(help_text="크롤링 시작일")
    end_date = models.DateField(help_text="크롤링 종료일")
    is_active = models.BooleanField(default=True, help_text="활성화화 여부")

    class Meta:
        db_table = 'crawling_period'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Song {self.song_id}: {self.start_date} ~ {self.end_date} (Active: {self.is_active})" 