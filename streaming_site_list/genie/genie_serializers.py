from rest_framework import serializers
from streaming_site_list.genie.models import GenieSongViewCount

class GenieSongViewCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenieSongViewCount
        fields = ['id', 'song_id', 'song_name', 'view_count', 'extracted_date']
