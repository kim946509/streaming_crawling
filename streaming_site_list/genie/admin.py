from django.contrib import admin
from streaming_site_list.genie.models import GenieSongViewCount

@admin.register(GenieSongViewCount)
class GenieSongViewCountAdmin(admin.ModelAdmin):
    list_display = ('artist_name', 'song_name', 'total_person_count', 'total_play_count', 'extracted_date') # admin 페이지에 표시할 필드
    search_fields = ('artist_name', 'song_name', 'extracted_date') # 검색 가능한 필드