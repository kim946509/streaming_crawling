from django.db import models
import uuid
from datetime import datetime

def generate_uuid():
    """UUID를 생성하는 함수"""
    return uuid.uuid4().hex

class PlatformType(models.TextChoices):
    """
    플랫폼 타입 Enum
    """
    MELON = 'melon', 'Melon'
    GENIE = 'genie', 'Genie'
    YOUTUBE = 'youtube', 'YouTube'
    YOUTUBE_MUSIC = 'youtube_music', 'YouTube Music'


class BaseModel(models.Model):
    """
    모든 모델의 공통 베이스 클래스
    """
    id = models.CharField(max_length=32, primary_key=True, default=generate_uuid, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, help_text="생성시간")
    updated_at = models.DateTimeField(auto_now=True, help_text="수정시간")

    class Meta:
        abstract = True  # 추상 모델로 설정 (테이블 생성 안함)

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
        if platform == 'melon':
            return {
                'song_id': self.melon_song_id,
                'title': self.youtube_music_title,  # YouTube Music 정보로 대체
                'artist': self.youtube_music_artist  # YouTube Music 정보로 대체
            }
        elif platform == 'genie':
            return {
                'title': self.genie_title,
                'artist': self.genie_artist
            }
        elif platform == 'youtube':
            return {
                'url': self.youtube_url,
                'title': self.youtube_music_title,  # YouTube Music 정보로 대체
                'artist': self.youtube_music_artist  # YouTube Music 정보로 대체
            }
        elif platform == 'youtube_music':
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
        if platform == 'melon':
            return bool(self.melon_song_id)
        elif platform == 'genie':
            return bool(self.genie_title and self.genie_artist)
        elif platform == 'youtube':
            return bool(self.youtube_url)
        elif platform == 'youtube_music':
            return bool(self.youtube_music_title and self.youtube_music_artist)
        else:
            return False


class CrawlingPeriod(BaseModel):
    """
    크롤링 기간 관리 모델
    """

    song_id = models.CharField(max_length=32, help_text="노래 ID (song_info.id 참조)")
    start_date = models.DateField(help_text="크롤링 시작일")
    end_date = models.DateField(help_text="크롤링 종료일")
    is_active = models.BooleanField(default=True, help_text="활성화화 여부")

    class Meta:
        db_table = 'crawling_period'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Song {self.song_id}: {self.start_date} ~ {self.end_date} (Active: {self.is_active})"


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
