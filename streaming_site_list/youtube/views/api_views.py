# ---------- ⬇️ 모델 호출 ----------
from streaming_site_list.youtube.models import YouTubeSongViewCount

# ---------- ⬇️ Serializer 호출 ----------
from streaming_site_list.youtube.serializers.api_serializers import YouTubeSongViewCountSerializer

# ---------- ⬇️ crawler 함수 호출 ----------
from streaming_site_list.youtube.views.crawler import YouTubeSongCrawler
from streaming_site_list.youtube.celery_setup.tasks import YouTubeSongCrawlingTask

# ---------- ⬇️ Swagger를 위하여 ----------
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# ---------- ⬇️ DRF 패키지 호출 ----------
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging, time

logger = logging.getLogger(__name__)

# ---------- ⬇️ API 함수 정의 ----------
class YouTubeSongViewCountAPIView(APIView):
    @swagger_auto_schema(
        operation_summary="유튜브 노래 조회수 및 업로드일 크롤링",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'urls': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING),
                    description="크롤링할 유튜브 동영상 ID 목록"
                ),
                'immediate': openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description="즉시 크롤링 실행 여부 (기본값: False)",
                    default=False
                )
            },
            required=['urls'],
            example={
                'urls': [
                    "https://www.youtube.com/watch?v=Sv2mIvMwrSY", "https://www.youtube.com/watch?v=R1CZTJ8hW0s", 
                    "https://www.youtube.com/watch?v=T4gsXNcF4Z0", "https://www.youtube.com/watch?v=-VQx4dePV5I", 
                    "https://www.youtube.com/watch?v=ecTQx5JNZBA", "https://www.youtube.com/watch?v=NiTwT05VgPA", 
                    "https://www.youtube.com/watch?v=nZpOGr1C8es", "https://www.youtube.com/watch?v=M1MFK5rWUpU", 
                    "https://www.youtube.com/watch?v=xpSJnLMCRxc", "https://www.youtube.com/watch?v=6hhhleiuaJA", 
                    "https://www.youtube.com/watch?v=jKY7pm7xlLk", "https://www.youtube.com/watch?v=C36Y5fmPnrQ", 
                    "https://www.youtube.com/watch?v=cpfFpC5xrrY", "https://www.youtube.com/watch?v=TlkHKmjha3U", 
                    "https://www.youtube.com/watch?v=M1MFK5rWUpU", "https://www.youtube.com/watch?v=LDJAuOW-_-4", 
                    "https://www.youtube.com/watch?v=z7WJw6SY0m0", "https://www.youtube.com/watch?v=ecTQx5JNZBA", 
                    "https://www.youtube.com/watch?v=2r0Wh1uEiuE", "https://www.youtube.com/watch?v=R6VH1qB-Hlg", 
                    "https://www.youtube.com/watch?v=HSUgcYisbmw", "https://www.youtube.com/watch?v=fi-QYKZP1d0", 
                    "https://www.youtube.com/watch?v=uIcpEprBKUA", "https://www.youtube.com/watch?v=LDJAuOW-_-4", 
                    "https://www.youtube.com/watch?v=r8clc_Vwahs", "https://www.youtube.com/watch?v=z7WJw6SY0m0", 
                    "https://www.youtube.com/watch?v=jn__gJ-7-vE", "https://www.youtube.com/watch?v=61yiWvXwB74", 
                    "https://www.youtube.com/watch?v=Dz8dI9G-kMk"
                    ],
                'immediate': False
            }
        ),
        responses={
            202: openapi.Response(
                description="크롤링 요청이 성공적으로 처리됨",
                examples={
                    "application/json": {
                        "message": "크롤링 작업이 성공적으로 예약되었습니다.",
                        "task_info": {
                            "scheduled_time": "2025-05-27 17:00:00 KST",
                            "song_count": 2
                        }
                    }
                }
            ),
            400: "잘못된 요청"
        }
    )
    def post(self, request):
        urls = request.data.get('urls', [])
        immediate = request.data.get('immediate', False)

        if not urls:
            return Response(
                {'error': 'urls 필드가 필요합니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if immediate:
                # 즉시 실행
                results = YouTubeSongCrawler(urls)
                return Response({
                    'message': '크롤링이 즉시 실행되었습니다.',
                    'results': results
                }, status=status.HTTP_200_OK)
            else:
                # Celery task로 예약
                task = YouTubeSongCrawlingTask.delay(urls)
                return Response({
                    'message': '크롤링 작업이 성공적으로 예약되었습니다.',
                    'task_info': {
                        'task_id': task.id,
                        'song_count': len(urls)
                    }
                }, status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            return Response({
                'error': f'크롤링 작업 처리 중 오류가 발생했습니다: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="유튜브 노래 조회수 조회",
        responses={200: YouTubeSongViewCountSerializer(many=True)}
    )
    def get(self, request):
        queryset = YouTubeSongViewCount.objects.all().order_by('-extracted_date') # 크롤링 한 날짜의 최신순으로 정렬
        serializer = YouTubeSongViewCountSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)