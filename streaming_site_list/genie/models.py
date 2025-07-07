from django.db import models
from streaming_site_list.models import BaseModel

class GenieSongViewCount(BaseModel):
    """
    Genie 플랫폼 크롤링 결과 모델
    """
    song_id = models.CharField(max_length=32, help_text="노래 ID")
    total_person_count = models.BigIntegerField(default=0, help_text="총 청취자 수")
    view_count = models.BigIntegerField(default=0, help_text="총 재생 수")
    extracted_date = models.DateField(help_text="크롤링 실행 날짜")

    class Meta:
        db_table = 'genie_crawling_data'
        ordering = ['-extracted_date', '-created_at']
        unique_together = ['song_id', 'extracted_date']  # 같은 날 중복 크롤링 방지
        
    def __str__(self):
        return f"Genie Song {self.song_id} - {self.extracted_date}"