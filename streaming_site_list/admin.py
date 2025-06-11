from django.contrib import admin, messages
from .models import CrawlingManager
# ------------------------------ Celery Tasks ------------------------------
from celery_setup.task_setup.genie_tasks import genie_crawl_jaerium_test, genie_crawl_anonatsue_test
from celery_setup.task_setup.youtube_tasks import youtube_crawl_rhoonart
from celery_setup.task_setup.youtube_music_tasks import youtube_music_crawl_jaerium_test, youtube_music_crawl_anonatsue_test

@admin.action(description='Genie, YouTube, YouTube Music 자동 크롤링 실행')
def run_all_crawling(modeladmin, request, queryset):
    genie_crawl_jaerium_test.delay()
    genie_crawl_anonatsue_test.delay()
    youtube_crawl_rhoonart.delay()
    youtube_music_crawl_jaerium_test.delay()
    youtube_music_crawl_anonatsue_test.delay()
    modeladmin.message_user(request, "다섯 가지 크롤링 작업이 Celery로 실행되었습니다.", messages.SUCCESS)

class CrawlingManagerAdmin(admin.ModelAdmin):
    actions = [run_all_crawling]

# ------------------------------ 자동 크롤링 버튼 추가 ------------------------------
admin.site.register(CrawlingManager, CrawlingManagerAdmin)