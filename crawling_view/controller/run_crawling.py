"""
전체 크롤링 프로세스 실행 스크립트 (운영용)
"""
import sys
import os
import django
import logging
import time
from datetime import datetime, date
from collections import defaultdict

# Django 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from crawling_view.controller.crawling_manager import run_crawling, run_platform_crawling
from crawling_view.data.song_service import SongService
from crawling_view.utils.constants import Platforms

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/crawling_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_full_crawling(target_date=None):
    """
    전체 크롤링 프로세스 실행 (운영용)
    
    Args:
        target_date (date, optional): 크롤링 대상 날짜. None이면 오늘 날짜
        
    Returns:
        dict: 상세한 크롤링 결과
    """
    start_time = time.time()
    start_datetime = datetime.now()
    
    logger.info("🚀 전체 크롤링 프로세스 시작")
    logger.info(f"📅 크롤링 대상 날짜: {target_date or date.today()}")
    logger.info(f"⏰ 시작 시간: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 크롤링 실행
        result = run_crawling(target_date)
        
        # 실행 시간 계산
        end_time = time.time()
        end_datetime = datetime.now()
        elapsed_time = end_time - start_time
        
        # 결과 분석
        analysis = analyze_crawling_result(result, elapsed_time, start_datetime, end_datetime)
        
        # 상세 로그 출력
        log_detailed_results(analysis)
        
        return analysis
        
    except Exception as e:
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        logger.error(f"❌ 크롤링 프로세스 실행 중 오류 발생: {e}", exc_info=True)
        
        error_result = {
            'status': 'error',
            'error_message': str(e),
            'start_time': start_datetime,
            'end_time': datetime.now(),
            'elapsed_time': elapsed_time,
            'target_date': target_date or date.today()
        }
        
        return error_result

def analyze_crawling_result(result, elapsed_time, start_datetime, end_datetime):
    """
    크롤링 결과 상세 분석
    
    Args:
        result (dict): 크롤링 결과
        elapsed_time (float): 실행 시간 (초)
        start_datetime (datetime): 시작 시간
        end_datetime (datetime): 종료 시간
        
    Returns:
        dict: 분석된 결과
    """
    analysis = {
        'status': result.get('status', 'unknown'),
        'start_time': start_datetime,
        'end_time': end_datetime,
        'elapsed_time': elapsed_time,
        'target_date': result.get('target_date'),
        'total_songs': result.get('total_songs', 0),
        'platforms': {},
        'summary': {}
    }
    
    if result['status'] == 'success':
        # 플랫폼별 상세 분석
        crawling_results = result.get('crawling_results', {})
        db_results = result.get('db_results', {})
        csv_results = result.get('csv_results', {})
        
        total_crawled = 0
        total_saved_db = 0
        total_saved_csv = 0
        total_failed = 0
        
        for platform in Platforms.ALL_PLATFORMS:
            platform_data = {
                'crawled_count': 0,
                'db_saved': 0,
                'db_updated': 0,
                'db_failed': 0,
                'db_skipped': 0,
                'csv_saved': 0,
                'status': 'not_executed'
            }
            
            # 크롤링 결과 분석
            if platform in crawling_results:
                platform_data['status'] = 'success'
                crawled_data = crawling_results[platform]
                
                if isinstance(crawled_data, list):
                    platform_data['crawled_count'] = len(crawled_data)
                elif isinstance(crawled_data, dict):
                    platform_data['crawled_count'] = len(crawled_data)
                
                total_crawled += platform_data['crawled_count']
            
            # DB 저장 결과 분석
            if platform in db_results:
                db_result = db_results[platform]
                if isinstance(db_result, dict):
                    platform_data['db_saved'] = db_result.get('saved_count', 0)
                    platform_data['db_updated'] = db_result.get('updated_count', 0)
                    platform_data['db_failed'] = db_result.get('failed_count', 0)
                    platform_data['db_skipped'] = db_result.get('skipped_count', 0)
                    
                    total_saved_db += platform_data['db_saved'] + platform_data['db_updated']
                    total_failed += platform_data['db_failed']
            
            # CSV 저장 결과 분석
            if platform in csv_results:
                csv_result = csv_results[platform]
                if isinstance(csv_result, list):
                    platform_data['csv_saved'] = len(csv_result)
                    total_saved_csv += platform_data['csv_saved']
            
            analysis['platforms'][platform] = platform_data
        
        # 전체 요약
        # 총 크롤링 시도: 곡 수 × 플랫폼 수
        total_attempts = analysis['total_songs'] * len(Platforms.ALL_PLATFORMS)
        
        # 실제 성공: CSV 저장이 성공한 것이 실제 성공
        actual_success = total_saved_csv
        
        # 실패: 총 시도 - 실제 성공
        total_failed = total_attempts - actual_success
        
        # 성공률: 실제 성공 / 총 시도
        success_rate = (actual_success / max(total_attempts, 1)) * 100
        
        analysis['summary'] = {
            'total_crawled': total_crawled,
            'total_saved_db': total_saved_db,
            'total_saved_csv': total_saved_csv,
            'total_failed': total_failed,
            'success_rate': success_rate
        }
    
    return analysis

def log_detailed_results(analysis):
    """
    상세한 결과를 로그로 출력
    
    Args:
        analysis (dict): 분석된 결과
    """
    logger.info("=" * 80)
    logger.info("📊 크롤링 결과 상세 분석")
    logger.info("=" * 80)
    
    # 기본 정보
    logger.info(f"📅 대상 날짜: {analysis['target_date']}")
    logger.info(f"⏰ 시작 시간: {analysis['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"⏰ 종료 시간: {analysis['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"⏱️  총 실행 시간: {analysis['elapsed_time']:.2f}초 ({analysis['elapsed_time']/60:.2f}분)")
    
    if analysis['status'] == 'success':
        logger.info(f"🎵 전체 대상 곡: {analysis['total_songs']}개")
        
        # 플랫폼별 결과
        logger.info("\n📈 플랫폼별 상세 결과:")
        logger.info("-" * 60)
        
        for platform, data in analysis['platforms'].items():
            status_emoji = "✅" if data['status'] == 'success' else "❌" if data['status'] == 'error' else "⚠️"
            logger.info(f"{status_emoji} {platform.upper()}:")
            logger.info(f"   크롤링: {data['crawled_count']}개")
            logger.info(f"   DB 저장: {data['db_saved']}개 생성, {data['db_updated']}개 교체, {data['db_failed']}개 실패, {data['db_skipped']}개 스킵")
            logger.info(f"   CSV 저장: {data['csv_saved']}개 파일")
        
        # 전체 요약
        summary = analysis['summary']
        total_attempts = analysis['total_songs'] * len(Platforms.ALL_PLATFORMS)
        
        logger.info("\n📊 전체 요약:")
        logger.info("-" * 60)
        logger.info(f"🎵 대상 곡: {analysis['total_songs']}개")
        logger.info(f"🌐 플랫폼: {len(Platforms.ALL_PLATFORMS)}개")
        logger.info(f"🎯 총 크롤링 시도: {total_attempts}개")
        logger.info(f"💾 DB 저장: {summary['total_saved_db']}개")
        logger.info(f"📄 CSV 저장: {summary['total_saved_csv']}개 파일")
        logger.info(f"❌ 실패: {summary['total_failed']}개")
        logger.info(f"📈 성공률: {summary['success_rate']:.1f}%")
        
        # 성능 분석
        if summary['total_crawled'] > 0:
            avg_time_per_song = analysis['elapsed_time'] / summary['total_crawled']
            logger.info(f"⚡ 곡당 평균 처리 시간: {avg_time_per_song:.2f}초")
    
    elif analysis['status'] == 'no_songs':
        logger.warning("⚠️ 크롤링 대상 곡이 없습니다.")
    
    elif analysis['status'] == 'error':
        logger.error(f"❌ 크롤링 실패: {analysis.get('error_message', '알 수 없는 오류')}")
    
    logger.info("=" * 80)

def run_single_platform_crawling(platform, target_date=None):
    """
    단일 플랫폼 크롤링 실행
    
    Args:
        platform (str): 플랫폼명 ('genie', 'youtube', 'youtube_music', 'melon')
        target_date (date, optional): 크롤링 대상 날짜
        
    Returns:
        dict: 크롤링 결과
    """
    start_time = time.time()
    start_datetime = datetime.now()
    
    logger.info(f"🚀 {platform.upper()} 플랫폼 크롤링 시작")
    logger.info(f"📅 크롤링 대상 날짜: {target_date or date.today()}")
    logger.info(f"⏰ 시작 시간: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        result = run_platform_crawling(platform, target_date)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        logger.info(f"✅ {platform.upper()} 크롤링 완료")
        logger.info(f"⏱️  실행 시간: {elapsed_time:.2f}초")
        
        if result['status'] == 'success':
            crawling_count = len(result.get('crawling_results', []))
            logger.info(f"🎯 크롤링 성공: {crawling_count}개")
            
            db_result = result.get('db_results', {})
            if isinstance(db_result, dict):
                saved_count = db_result.get('saved_count', 0)
                updated_count = db_result.get('updated_count', 0)
                failed_count = db_result.get('failed_count', 0)
                logger.info(f"💾 DB 저장: {saved_count}개 생성, {updated_count}개 교체, {failed_count}개 실패")
            
            csv_result = result.get('csv_results', [])
            if isinstance(csv_result, list):
                logger.info(f"📄 CSV 저장: {len(csv_result)}개 파일")
        
        return result
        
    except Exception as e:
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        logger.error(f"❌ {platform.upper()} 크롤링 실패: {e}", exc_info=True)
        logger.info(f"⏱️  실행 시간: {elapsed_time:.2f}초")
        
        return {'status': 'error', 'platform': platform, 'error_message': str(e)}

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='크롤링 프로세스 실행')
    parser.add_argument('--platform', choices=Platforms.ALL_PLATFORMS, 
                       help='특정 플랫폼만 크롤링')
    parser.add_argument('--date', type=str, help='크롤링 대상 날짜 (YYYY-MM-DD 형식)')
    
    args = parser.parse_args()
    
    # 날짜 파싱
    target_date = None
    if args.date:
        try:
            target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
        except ValueError:
            logger.error("❌ 날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식을 사용하세요.")
            sys.exit(1)
    
    # 크롤링 실행
    if args.platform:
        # 단일 플랫폼 크롤링
        result = run_single_platform_crawling(args.platform, target_date)
    else:
        # 전체 크롤링
        result = run_full_crawling(target_date)
    
    # 종료 코드 설정
    if result.get('status') == 'success':
        sys.exit(0)
    else:
        sys.exit(1) 