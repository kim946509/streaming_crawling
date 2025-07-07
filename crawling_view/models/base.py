"""
기본 모델 및 유틸리티
"""
from django.db import models
import uuid

def generate_uuid():
    """UUID를 생성하는 함수"""
    return uuid.uuid4().hex

class BaseModel(models.Model):
    """
    모든 모델의 공통 베이스 클래스
    """
    id = models.CharField(max_length=32, primary_key=True, default=generate_uuid, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, help_text="생성시간")
    updated_at = models.DateTimeField(auto_now=True, help_text="수정시간")

    class Meta:
        abstract = True  # 추상 모델로 설정 (테이블 생성 안함) 