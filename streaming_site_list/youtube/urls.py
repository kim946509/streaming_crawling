from django.urls import path
from API_View.youtube_api_views import YouTubeSongViewCountAPIView

urlpatterns = [
    path('youtube/', YouTubeSongViewCountAPIView.as_view(), name='youtube-song-view-count'), # POST, GET, PUT, DELETE
]