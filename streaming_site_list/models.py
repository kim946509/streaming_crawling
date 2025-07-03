from django.db import models

class CrawlingManager(models.Model):
    class Meta:
        verbose_name = "크롤링 자동 실행 버튼"
        verbose_name_plural = "크롤링 자동 실행 버튼"

class SongInfo(models.Model):
    """
    노래 기본 정보 모델
    """
    song_id = models.AutoField(primary_key=True)  # 자동 증가하는 정수 PK
    artist_name = models.CharField(max_length=255)
    song_name = models.CharField(max_length=255)
    youtube_url = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['artist_name', 'song_name']  # 아티스트+곡명 조합으로 중복 방지
        
    def __str__(self):
        return f"[{self.song_id}] {self.artist_name} - {self.song_name}"

class CrawlingPeriod(models.Model):
    """
    크롤링 기간 관리 모델
    """
    id = models.AutoField(primary_key=True)
    song_id = models.IntegerField()  # SongInfo의 song_id와 연결 (FK 없이)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Song {self.song_id}: {self.start_date} ~ {self.end_date}"