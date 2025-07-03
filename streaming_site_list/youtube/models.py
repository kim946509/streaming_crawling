from django.db import models

class YouTubeSongViewCount(models.Model):
    """
    YouTube 플랫폼 크롤링 결과 모델
    """
    id = models.AutoField(primary_key=True)
    song_id = models.IntegerField()  # SongInfo의 song_id와 연결 (FK 없이)
    video_id = models.CharField(max_length=50, help_text="YouTube 비디오 ID")
    view_count = models.BigIntegerField(default=0, help_text="조회수")
    upload_date = models.DateField(help_text="업로드 날짜")
    extracted_date = models.DateField(help_text="크롤링 실행 날짜")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-extracted_date', '-created_at']
        unique_together = ['song_id', 'extracted_date']  # 같은 날 중복 크롤링 방지
        
    def __str__(self):
        return f"YouTube Song {self.song_id} - {self.extracted_date}"