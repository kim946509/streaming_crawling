from django.db import models

class CrawlingManager(models.Model):
    class Meta:
        verbose_name = "크롤링 자동 실행 버튼"
        verbose_name_plural = "크롤링 자동 실행 버튼"