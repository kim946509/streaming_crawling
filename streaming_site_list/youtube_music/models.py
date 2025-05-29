from django.db import models

class YouTubeMusicSongViewCount(models.Model):
    song_id = models.CharField(max_length=255, unique=True)
    artist_name = models.CharField(max_length=255)
    song_name = models.CharField(max_length=255)
    view_count = models.BigIntegerField(default=0)
    youtube_music_url = models.URLField(max_length=255)
    extracted_date = models.DateField()
    upload_date = models.DateField()

    def __str__(self):
        return f"{self.song_id} - {self.view_count}"