from django.urls import path
from streaming_site_list.youtube.views.api_views import YouTubeSongViewCountAPIView

urlpatterns = [
    path('youtube/', YouTubeSongViewCountAPIView.as_view(), name='youtube-song-view-count'), # POST, GET
]