from django.db import models
import uuid
from datetime import datetime

def generate_uuid():
    """UUID를 생성하는 함수"""
    return uuid.uuid4().hex

class BaseModel(models.Model):
    """
    모든 모델의 공통 베이스 클래스
    """
    id = models.CharField(max_length=32, primary_key=True, default=generate_uuid, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, help_text="생성시간")
    updated_at = models.DateTimeField(auto_now=True, help_text="수정시간")
    deleted_at = models.DateTimeField(null=True, blank=True, help_text="삭제시간")
    is_deleted = models.BooleanField(default=False, help_text="삭제여부")

    class Meta:
        abstract = True  # 추상 모델로 설정 (테이블 생성 안함)

    def soft_delete(self):
        """소프트 삭제 메서드"""
        self.is_deleted = True
        self.deleted_at = datetime.now()
        self.save()

    def restore(self):
        """삭제 복구 메서드"""
        self.is_deleted = False
        self.deleted_at = None
        self.save()

class SongInfo(BaseModel):
    """
    노래 기본 정보 모델
    """
    song_id = models.CharField(max_length=32, unique=True, help_text="노래 고유 ID")
    artist_name = models.CharField(max_length=255, help_text="아티스트명")
    song_name = models.CharField(max_length=255, help_text="곡명")
    youtube_url = models.URLField(max_length=500, blank=True, null=True, help_text="YouTube URL")

    class Meta:
        db_table = 'song_info'
        unique_together = ['artist_name', 'song_name']  # 아티스트+곡명 조합으로 중복 방지
        
    def __str__(self):
        return f"[{self.song_id}] {self.artist_name} - {self.song_name}"

class CrawlingPeriod(BaseModel):
    """
    크롤링 기간 관리 모델
    """
    song_id = models.CharField(max_length=32, help_text="노래 ID")
    start_date = models.DateField(help_text="크롤링 시작일")
    end_date = models.DateField(help_text="크롤링 종료일")
    is_active = models.BooleanField(default=True, help_text="활성화 여부")
    
    class Meta:
        db_table = 'crawling_period'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Song {self.song_id}: {self.start_date} ~ {self.end_date}"