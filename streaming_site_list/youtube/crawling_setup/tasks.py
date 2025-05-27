from celery import shared_task
import logging
from streaming_site_list.youtube.views.crawler import YouTubeSongCrawler
from streaming_site_list.youtube.models import YouTubeSongViewCount
from datetime import datetime

# 로거 설정
logger = logging.getLogger(__name__)

@shared_task(
    name='streaming_site_list.youtube.crawling_setup.tasks.YouTubeViewCountTask',
    bind=True,
    max_retries=3,
    default_retry_delay=300  # 5분 후 재시도
)
def YouTubeSingCrawlingTask(self, song_ids):
    """
    유튜브 조회수 크롤링을 실행하는 Celery 태스크

    Args:
        song_ids (list): 크롤링할 유튜브 동영상 ID 리스트

    Returns:
        dict: 크롤링 결과
    """
    try:
        logger.info(f"유튜브 조회수 크롤링 시작 - {len(song_ids)}개 동영상")
        start_time = datetime.now()

        # 크롤링 실행
        results = YouTubeSongCrawler(song_ids)
        
        # 크롤링 완료 시간 기록
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"크롤링 완료 - 소요시간: {duration:.2f}초")
        return {
            'status': 'success',
            'song_count': len(song_ids),
            'duration': duration,
            'results': results
        }

    except Exception as e:
        logger.error(f"크롤링 중 오류 발생: {str(e)}", exc_info=True)
        # 재시도 횟수가 남아있으면 재시도
        if self.request.retries < self.max_retries:
            logger.info(f"크롤링 재시도 ({self.request.retries + 1}/{self.max_retries})")
            raise self.retry(exc=e)
        return {
            'status': 'error',
            'error_message': str(e)
        }