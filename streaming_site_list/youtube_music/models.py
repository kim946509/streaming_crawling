from django.db import models

class YouTubeMusicSongViewCount(models.Model):
    artist_name = models.CharField(max_length=255)
    song_name = models.CharField(max_length=255)
    view_count = models.BigIntegerField(default=0)
    extracted_date = models.DateField()

    def __str__(self):
        return f"{self.artist_name} - {self.song_name}"