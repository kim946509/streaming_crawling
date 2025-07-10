"""
단일 곡 크롤링 API 뷰
"""
import subprocess
import logging
import os
import sys
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from crawling_view.models import SongInfo
from crawling_view.utils.constants import Platforms

logger = logging.getLogger(__name__)


class CrawlSingleSongAPIView(APIView):
    """
    단일 곡 크롤링 API
    
    비동기로 크롤링을 실행하고 즉시 응답을 반환합니다.
    """
    
    def post(self, request):
        """
        단일 곡 크롤링 요청 처리
        
        Request Body:
        {
            "song_id": "곡 ID (SongInfo.id)"
        }
        
        Response:
        {
            "status": "started",
            "message": "크롤링이 시작되었습니다",
            "song_id": "곡 ID",
            "song_info": {
                "title": "곡명",
                "artist": "아티스트명",
                "available_platforms": ["genie", "youtube_music", ...]
            }
        }
        """
        try:
            # 요청 데이터 검증
            song_id = request.data.get('song_id')
            if not song_id:
                return Response({
                    'status': 'error',
                    'message': 'song_id가 필요합니다.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 곡 존재 여부 확인
            try:
                song = SongInfo.objects.get(id=song_id)
            except SongInfo.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': f'Song ID {song_id}에 해당하는 곡이 존재하지 않습니다.'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 크롤링 가능한 플랫폼 확인
            platforms = Platforms.ALL_PLATFORMS
            available_platforms = [p for p in platforms if song.is_platform_available(p)]
            
            if not available_platforms:
                return Response({
                    'status': 'error',
                    'message': '크롤링 가능한 플랫폼이 없습니다.',
                    'song_info': {
                        'title': song.title_ko,
                        'artist': song.artist_ko,
                        'available_platforms': []
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 비동기 크롤링 시작
            python_executable = self._get_python_executable()
            manage_py_path = self._get_manage_py_path()
            
            # subprocess.Popen으로 비동기 실행
            process = subprocess.Popen(
                [python_executable, manage_py_path, 'crawl_one_song', f'--song-id={song_id}'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=settings.BASE_DIR
            )
            
            logger.info(f"🚀 단일 곡 크롤링 프로세스 시작 - Song ID: {song_id}, PID: {process.pid}")
            
            # 성공 응답 반환 (크롤링이 시작되었다는 것만 알려줌)
            return Response({
                'status': 'started',
                'message': '크롤링이 시작되었습니다.',
                'song_id': song_id,
                'process_id': process.pid,
                'song_info': {
                    'title': song.title_ko,
                    'artist': song.artist_ko,
                    'available_platforms': available_platforms
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"❌ 단일 곡 크롤링 API 오류: {e}", exc_info=True)
            return Response({
                'status': 'error',
                'message': f'크롤링 시작 중 오류가 발생했습니다: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_python_executable(self):
        """
        Python 실행파일 경로 반환
        
        Returns:
            str: Python 실행파일 경로
        """
        # 현재 실행 중인 Python 경로 사용
        return sys.executable
    
    def _get_manage_py_path(self):
        """
        manage.py 파일 경로 반환
        
        Returns:
            str: manage.py 파일의 절대 경로
        """
        return os.path.join(settings.BASE_DIR, 'manage.py')


class CrawlSongStatusAPIView(APIView):
    """
    크롤링 상태 확인 API (선택사항)
    
    현재는 간단하게 로그 파일 확인만 제공
    """
    
    def get(self, request):
        """
        크롤링 상태 조회
        
        Response:
        {
            "status": "info",
            "message": "크롤링 상태는 로그 파일을 확인하세요.",
            "log_info": {
                "log_directory": "logs/",
                "pattern": "single_crawling_*.log"
            }
        }
        """
        return Response({
            'status': 'info',
            'message': '크롤링 상태는 로그 파일을 확인하세요.',
            'log_info': {
                'log_directory': 'logs/',
                'pattern': 'single_crawling_*.log',
                'description': '최신 로그 파일에서 크롤링 진행 상황을 확인할 수 있습니다.'
            }
        }, status=status.HTTP_200_OK) 