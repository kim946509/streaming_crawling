"""
크롤링 매니저 테스트
"""
import sys
import os
import django
from datetime import date

# Django 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from crawling_view.crawling_manager import CrawlingManager, run_crawling
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_crawling_manager():
    """크롤링 매니저 테스트"""
    print("🚀 크롤링 매니저 테스트 시작")
    print("=" * 60)
    
    # 1. 매니저 생성
    manager = CrawlingManager(target_date=date.today())
    print(f"📅 대상 날짜: {manager.target_date}")
    
    # 2. 전체 크롤링 실행 (CSV만 저장, DB는 저장하지 않음)
    print("\n🔄 전체 크롤링 실행 중...")
    results = manager.run_full_crawling(
        platforms=['genie', 'youtube_music', 'youtube'],  # 모든 플랫폼 포함
        save_csv=True,
        save_db=False  # 테스트용으로 DB 저장 비활성화
    )
    
    # 3. 결과 출력
    print("\n📊 크롤링 결과:")
    for platform, result in results.items():
        if 'error' in result:
            print(f"❌ {platform}: {result['error']}")
        else:
            crawling_result = result.get('crawling_result', [])
            elapsed_time = result.get('elapsed_time', 0)
            
            if isinstance(crawling_result, list):
                success_count = len(crawling_result)
            elif isinstance(crawling_result, dict):
                success_count = len(crawling_result)
            else:
                success_count = 0
            
            print(f"✅ {platform}: {success_count}개 성공 ({elapsed_time:.2f}초)")
    
    print("\n🏁 테스트 완료!")

def test_run_crawling_function():
    """편의 함수 테스트"""
    print("\n🔄 편의 함수 테스트")
    print("=" * 60)
    
    # 편의 함수 사용
    results = run_crawling(
        target_date=date.today(),
        platforms=['genie', 'youtube_music', 'youtube'],  # 모든 플랫폼 테스트
        save_csv=True,
        save_db=False
    )
    
    print(f"📊 결과: {results}")

if __name__ == "__main__":
    try:
        test_crawling_manager()
        test_run_crawling_function()
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc() 