# ---------- ⬇️ 모델 호출 ----------
from streaming_site_list.youtube_music.models import YouTubeMusicSongViewCount

# ---------- ⬇️ Serializer 호출 ----------
from streaming_site_list.youtube_music.serializers.youtube_music_serializers import YouTubeMusicSongViewCountSerializer

# ---------- ⬇️ crawler 함수 호출 ----------
from crawling_view.youtube_crawler_views import save_each_to_csv
from crawling_view.youtube_music_crawler_views import YouTubeMusicSongCrawler

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
class YouTubeMusicSongViewCountAPIView(APIView):
    @swagger_auto_schema(
        operation_summary="고객사별 유튜브 뮤직 노래 조회수 및 업로드일 크롤링",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'artist_name': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="크롤링할 유튜브 뮤직 노래 아티스트 명"
                ),
                'song_names': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING),
                    description="크롤링할 유튜브 뮤직 노래 제목 목록"
                ),
                'company_name': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="크롤링할 고객사 명(영어로 입력해주세요. 예: rhoonart)"
                ),
                'service_name': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="크롤링할 서비스 명(영어로 입력해주세요. 예: youtube_music)"
                ),
                'immediate': openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description="즉시 크롤링 실행 여부 (기본값: False)",
                    default=False
                )
            },
            required=['artist_name', 'song_names', 'company_name', 'service_name'],
            example={
                'artist_name': "Jaerium",
                'song_names': ["song 1", "song 2", "song 3"],
                'company_name': "rhoonart",
                'service_name': "youtube_music",
                'immediate': False
            }
        ),
    )
    def post(self, request):
        artist_name = request.data.get('artist_name', 'default')
        song_names = request.data.get('song_names', [])
        company_name = request.data.get('company_name', 'default')
        service_name = request.data.get('service_name', 'youtube_music')
        immediate = request.data.get('immediate', False)

        if not song_names:
            return Response(
                {'error': 'song_names 필드가 필요합니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if immediate:
            results = YouTubeMusicSongCrawler(artist_name, song_names)
            save_each_to_csv(results, company_name, service_name)
            return Response({"message": "크롤링 작업이 즉시 실행되었습니다."}, status=status.HTTP_202_ACCEPTED)