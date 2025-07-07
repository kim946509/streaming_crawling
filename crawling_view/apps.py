"""
크롤링 시스템 Django 앱 설정
"""
from django.apps import AppConfig

class CrawlingViewConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crawling_view'
    verbose_name = '크롤링 시스템' 