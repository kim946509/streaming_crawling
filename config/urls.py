"""
URL configuration for config project.

크롤링 전용 Django 애플리케이션
"""
from django.urls import path, include

urlpatterns = [
    # 크롤링 전용 - API는 별도 서버에서 관리
    path('', include('streaming_site_list.youtube.urls')),
    path('', include('streaming_site_list.youtube_music.urls')),
    path('', include('streaming_site_list.genie.urls')),
]