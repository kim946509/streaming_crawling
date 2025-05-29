from django.urls import path
from API_View.youtube_music_api_views import YouTubeMusicSongViewCountAPIView

urlpatterns = [
    path('youtube_music/', YouTubeMusicSongViewCountAPIView.as_view(), name='youtube_music-song-view-count'), # POST, GET
]