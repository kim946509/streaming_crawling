"""
크롤링 API URL 패턴
"""
from django.urls import path
from .views import CrawlSingleSongAPIView, CrawlSongStatusAPIView

app_name = 'crawling_api'

urlpatterns = [
    path('crawl-song/', CrawlSingleSongAPIView.as_view(), name='crawl_single_song'),
    path('crawl-status/', CrawlSongStatusAPIView.as_view(), name='crawl_status'),
] 