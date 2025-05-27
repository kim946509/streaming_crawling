import logging
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from datetime import datetime
import pytz

# 로거 설정
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def YouTubeSongViewCountCrawlingSchedule():
    """
    유튜브 크롤링 스케줄을 생성하는 함수
    매일 한국 시간 오후 5시(17:00 KST)에 실행되도록 설정
    """
    try:
        # 현재 시간을 KST로 확인
        kst = pytz.timezone('Asia/Seoul')
        current_time = datetime.now(kst)
        logger.info(f"현재 서버 시간: {current_time}")

        schedule, created = CrontabSchedule.objects.get_or_create(
            minute='0',
            # === ⬇️ 이거 수정하면 돼유 ===
            hour='8',  # UTC 8시 = KST 17시
            day_of_week='*', # 매일 -> 0 ~ 6 (일 ~ 토). 예) '0'은 일요일, '1'은 월요일
            day_of_month='*', # 매일 -> 1 ~ 31. 예) '1'은 1일, '31'은 31일
            month_of_year='*', # 매월 -> 1 ~ 12. 예) '1'은 1월, '12'은 12월
            timezone=pytz.timezone('Asia/Seoul')
        )
        
        if created:
            logger.info("새로운 Crontab 스케줄이 생성되었습니다. (KST 17:00 실행)")
        else:
            logger.info("기존 Crontab 스케줄을 사용합니다. (KST 17:00 실행)")

        task, task_created = PeriodicTask.objects.get_or_create(
            name='매일 오후 5시에 시작되는 크롤링',
            defaults={
                'crontab': schedule,
                'task': 'streaming_site_list.youtube.crawling_setup.tasks.SongViewCountTask',
            }
        )

        if task_created:
            logger.info("새로운 Periodic Task가 생성되었습니다.")
        else:
            logger.info("기존 Periodic Task가 존재합니다.")

        return True

    except Exception as e:
        logger.error(f"스케줄 생성 중 오류 발생: {str(e)}")
        return False

if __name__ == "__main__":
    YouTubeSongViewCountCrawlingSchedule()