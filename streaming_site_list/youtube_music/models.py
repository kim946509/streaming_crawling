from django.db import models
from streaming_site_list.models import BaseModel

class YouTubeMusicSongViewCount(BaseModel):
    """
    YouTube Music 플랫폼 크롤링 결과 모델
    """
    song_id = models.CharField(max_length=32, help_text="노래 ID")
    view_count = models.BigIntegerField(default=0, help_text="조회수")
    extracted_date = models.DateField(help_text="크롤링 실행 날짜")

    class Meta:
        ordering = ['-extracted_date', '-created_at']
        unique_together = ['song_id', 'extracted_date']  # 같은 날 중복 크롤링 방지
        
    def __str__(self):
        return f"YouTube Music Song {self.song_id} - {self.extracted_date}"