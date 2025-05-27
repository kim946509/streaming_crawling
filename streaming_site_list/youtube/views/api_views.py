# ---------- ⬇️ 모델 호출 ----------
from streaming_site_list.youtube.models import YouTubeSongViewCount

# ---------- ⬇️ Serializer 호출 ----------
from streaming_site_list.youtube.serializers.api_serializers import YouTubeSongViewCountSerializer

# ---------- ⬇️ crawler 함수 호출 ----------
from streaming_site_list.youtube.views.crawler import song_view_count

# ---------- ⬇️ Swagger를 위하여 ----------
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# ---------- ⬇️ DRF 패키지 호출 ----------
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


# ---------- ⬇️ API 함수 정의 ----------
class YouTubeSongViewCountAPIView(APIView):
    @swagger_auto_schema(
        operation_summary="유튜브 노래 조회수 추출",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'song_id': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING),description="크롤링할 유튜브 노래 ID 목록을 입력해주세요."),
            },
            required=['song_id'],
            example={
                'song_id': ['Sv2mIvMwrSY', 'dQw4w9WgXcQ']
            }
        ),
        responses={202: '크롤링이 시작되었습니다.', 400: '잘못된 요청입니다.'}
    )
    def post(self, request):
        song_ids = request.data.get('song_id', [])
        if not song_ids:
            return Response({'error': 'song_id 필드가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 노래 ID 리스트를 문자열로 변환
        song_ids_str = ','.join(song_ids)

        # 크롤링 작업 큐에 추가
        song_view_count.delay(song_ids_str)

    def get(self, request):
        queryset = YouTubeSongViewCount.objects.all().order_by('-extracted_date') # 크롤링 한 날짜의 최신순으로 정렬
        serializer = YouTubeSongViewCountSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)