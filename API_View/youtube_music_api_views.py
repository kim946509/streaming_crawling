# ---------- ⬇️ 모델 호출 ----------
from streaming_site_list.youtube_music.models import YouTubeMusicSongViewCount

# ---------- ⬇️ Serializer 호출 ----------
from streaming_site_list.youtube_music.youtube_music_serializers import YouTubeMusicSongViewCountSerializer

# ---------- ⬇️ crawler 함수 호출 ----------
from crawling_view.youtube_crawler_views import save_each_to_csv
from crawling_view.youtube_music_crawler_views import YouTubeMusicSongCrawler, save_to_db

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
            save_to_db(results)
            return Response({"message": "크롤링 작업이 즉시 실행되었습니다."}, status=status.HTTP_202_ACCEPTED)


    '''===================== ⬇️ 곡 단일 또는 전체 조회 API ====================='''
    @swagger_auto_schema(
        operation_summary="곡 단일 조회 (song_id 또는 song_name 중 하나 필요)",
        manual_parameters=[
            openapi.Parameter('song_id', openapi.IN_QUERY, description="곡의 song_id", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('song_name', openapi.IN_QUERY, description="곡의 song_name", type=openapi.TYPE_STRING, required=False),
        ]
    )
    def get(self, request):
        song_id = request.query_params.get('song_id')
        song_name = request.query_params.get('song_name')
        if not song_id and not song_name:
            # 전체 리스트 반환
            songs = YouTubeMusicSongViewCount.objects.all()
            serializer = YouTubeMusicSongViewCountSerializer(songs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        try:
            if song_id:
                song = YouTubeMusicSongViewCount.objects.get(song_id=song_id)
            else:
                song = YouTubeMusicSongViewCount.objects.filter(song_name=song_name).first()
                if not song:
                    raise YouTubeMusicSongViewCount.DoesNotExist
            serializer = YouTubeMusicSongViewCountSerializer(song)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except YouTubeMusicSongViewCount.DoesNotExist:
            return Response({'error': '해당 곡이 존재하지 않습니다.'}, status=status.HTTP_404_NOT_FOUND)


    '''===================== ⬇️ 곡 정보 수정 API ====================='''
    @swagger_auto_schema(
        operation_summary="곡 정보 수정 (song_id 또는 song_name 중 하나 필요)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'song_id': openapi.Schema(type=openapi.TYPE_STRING, description="곡의 song_id (선택)"),
                'song_name': openapi.Schema(type=openapi.TYPE_STRING, description="곡의 song_name (선택)"),
                'artist_name': openapi.Schema(type=openapi.TYPE_STRING, description="아티스트명 (수정시)"),
                'view_count': openapi.Schema(type=openapi.TYPE_INTEGER, description="조회수 (수정시)"),
                'youtube_music_url': openapi.Schema(type=openapi.TYPE_STRING, description="유튜브 뮤직 URL (수정시)"),
                'extracted_date': openapi.Schema(type=openapi.TYPE_STRING, description="추출일 (YYYY-MM-DD, 수정시)"),
                'upload_date': openapi.Schema(type=openapi.TYPE_STRING, description="업로드일 (YYYY-MM-DD, 수정시)")
            },
            required=[],
            description="song_id 또는 song_name 중 하나는 반드시 필요합니다."
        )
    )
    def put(self, request):
        song_id = request.data.get('song_id')
        song_name = request.data.get('song_name')
        if not song_id and not song_name:
            return Response({'error': 'song_id 또는 song_name 필드가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            if song_id:
                song = YouTubeMusicSongViewCount.objects.get(song_id=song_id)
            else:
                song = YouTubeMusicSongViewCount.objects.filter(song_name=song_name).first()
                if not song:
                    raise YouTubeMusicSongViewCount.DoesNotExist
        except YouTubeMusicSongViewCount.DoesNotExist:
            return Response({'error': '해당 곡이 존재하지 않습니다.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = YouTubeMusicSongViewCountSerializer(song, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    '''===================== ⬇️ 곡 삭제 API ====================='''
    @swagger_auto_schema(
        operation_summary="곡 삭제 (song_id 또는 song_name 중 하나 필요)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'song_id': openapi.Schema(type=openapi.TYPE_STRING, description="곡의 song_id (선택)"),
                'song_name': openapi.Schema(type=openapi.TYPE_STRING, description="곡의 song_name (선택)")
            },
            required=[],
            description="song_id 또는 song_name 중 하나는 반드시 필요합니다."
        )
    )
    def delete(self, request):
        song_id = request.data.get('song_id')
        song_name = request.data.get('song_name')
        if not song_id and not song_name:
            return Response({'error': 'song_id 또는 song_name 필드가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            if song_id:
                song = YouTubeMusicSongViewCount.objects.get(song_id=song_id)
            else:
                song = YouTubeMusicSongViewCount.objects.filter(song_name=song_name).first()
                if not song:
                    raise YouTubeMusicSongViewCount.DoesNotExist
            song.delete()
            return Response({'message': '삭제되었습니다.'}, status=status.HTTP_204_NO_CONTENT)
        except YouTubeMusicSongViewCount.DoesNotExist:
            return Response({'error': '해당 곡이 존재하지 않습니다.'}, status=status.HTTP_404_NOT_FOUND)