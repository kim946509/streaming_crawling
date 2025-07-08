"""
URL configuration for config project.

크롤링 전용 Django 애플리케이션
"""
from django.urls import path, include

urlpatterns = [
    path('api/v1/', include('crawling_view.api.urls')),
]