from django.urls import path
from API_View.genie_api_views import GenieSongViewCountAPIView

urlpatterns = [
    path('genie/', GenieSongViewCountAPIView.as_view(), name='genie-song-view-count'), # POST, GET, PUT, DELETE
]