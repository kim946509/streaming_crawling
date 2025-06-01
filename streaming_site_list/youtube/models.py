from django.db import models

class YouTubeSongViewCount(models.Model):
    song_id = models.CharField(max_length=255, unique=True)
    song_name = models.CharField(max_length=255)
    view_count = models.BigIntegerField(default=0)
    youtube_url = models.URLField(max_length=255)
    extracted_date = models.DateField()
    upload_date = models.DateField()

    def __str__(self):
        return f"{self.artist_name} - {self.song_name}"