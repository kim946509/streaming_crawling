from django.contrib import admin
from streaming_site_list.genie.models import GenieSongViewCount

@admin.register(GenieSongViewCount)
class GenieSongViewCountAdmin(admin.ModelAdmin):
    list_display = ('song_id', 'total_person_count', 'view_count', 'extracted_date', 'created_at')
    search_fields = ('song_id',)
    list_filter = ('extracted_date', 'created_at')
    readonly_fields = ('created_at',)