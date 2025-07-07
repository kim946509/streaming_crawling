import os
import sys
import django
import logging
import time
from datetime import date

# 현재 파일의 상위 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from crawling_view.crawling_manager import run_crawling
from crawling_view.common.song_service import SongService


def format_time(seconds):
    """초를 분:초 형태로 포맷팅"""
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    if minutes > 0:
        return f"{minutes}분 {remaining_seconds}초"
    else:
        return f"{remaining_seconds}초"


def test_crawling_manager():
    """새로운 크롤링 매니저 테스트"""
    print("🚀 새로운 크롤링 매니저 테스트")
    print("=" * 60)
    
    start_time = time.time()
    
    # 새로운 크롤링 매니저 사용
    results = run_crawling(
        target_date=date.today(),
        platforms=['genie', 'youtube_music', 'youtube'],  # 모든 플랫폼 포함
        save_csv=True,
        save_db=True
    )
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 결과 출력
    print("\n📊 크롤링 결과:")
    for platform, result in results.items():
        if 'error' in result:
            print(f"❌ {platform}: {result['error']}")
        else:
            crawling_result = result.get('crawling_result', [])
            platform_elapsed_time = result.get('elapsed_time', 0)
            
            if isinstance(crawling_result, list):
                success_count = len(crawling_result)
            elif isinstance(crawling_result, dict):
                success_count = len(crawling_result)
            else:
                success_count = 0
            
            print(f"✅ {platform}: {success_count}개 성공 ({format_time(platform_elapsed_time)})")
    
    print(f"\n⏱️ 전체 소요 시간: {format_time(elapsed_time)}")
    return results


def main():
    """메인 테스트 함수"""
    total_start_time = time.time()
    print(f"새로운 크롤링 매니저 테스트 시작: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        # 새로운 크롤링 매니저 사용
        results = test_crawling_manager()
        
        # 3. 전체 결과 요약
        total_end_time = time.time()
        total_elapsed_time = total_end_time - total_start_time
        
        print("\n" + "=" * 80)
        print("📊 최종 크롤링 결과 요약")
        print("=" * 80)
        
        total_success = 0
        for platform, result in results.items():
            if 'error' not in result:
                crawling_result = result.get('crawling_result', [])
                if isinstance(crawling_result, list):
                    success_count = len(crawling_result)
                elif isinstance(crawling_result, dict):
                    success_count = len(crawling_result)
                else:
                    success_count = 0
                total_success += success_count
                print(f"✅ {platform}: {success_count}개 성공")
        
        print("=" * 80)
        print(f"🎯 총 성공: {total_success}개")
        print(f"🏁 전체 테스트 완료 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️ 전체 소요 시간: {format_time(total_elapsed_time)}")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류 발생: {e}")
        logging.error(f"크롤링 매니저 테스트 실패: {e}", exc_info=True)


if __name__ == "__main__":
    main()
