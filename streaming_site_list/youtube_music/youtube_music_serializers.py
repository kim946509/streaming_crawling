from rest_framework import serializers
from streaming_site_list.youtube_music.models import YouTubeMusicSongViewCount

class YouTubeMusicSongViewCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = YouTubeMusicSongViewCount
        fields = ['song_id', 'song_name', 'view_count', 'extracted_date']