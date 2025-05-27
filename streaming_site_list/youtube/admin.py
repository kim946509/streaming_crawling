from django.contrib import admin
from streaming_site_list.youtube.models import YouTubeSongViewCount

@admin.register(YouTubeSongViewCount)
class YouTubeSongViewCountAdmin(admin.ModelAdmin):
    list_display = ('song_id', 'view_count', 'upload_date', 'extracted_date') # admin 페이지에 표시할 필드
    search_fields = ('song_id', 'upload_date', 'extracted_date') # 검색 가능한 필드
    

