from rest_framework import serializers
from streaming_site_list.youtube.models import YouTubeSongViewCount

class YouTubeSongViewCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = YouTubeSongViewCount
        fields = ['id', 'song_id', 'song_name', 'view_count', 'youtube_url', 'extracted_date', 'upload_date']
