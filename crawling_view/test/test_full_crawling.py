"""
전체 크롤링 프로세스 테스트 (단순화)
"""
import sys
import os
import django

# Django 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from crawling_view.controller.crawling_manager import run_crawling

def test_full_crawling():
    """전체 크롤링 프로세스 테스트"""
    print("🚀 전체 크롤링 테스트")
    
    result = run_crawling()
    print(f"결과: {result['status']}")
    
    if result['status'] == 'success':
        print(f"대상 곡: {result.get('total_songs', 0)}개")
        print(f"크롤링 플랫폼: {len(result.get('crawling_results', {}))}개")
        
        # 플랫폼별 결과
        for platform, results in result.get('crawling_results', {}).items():
            count = len(results) if isinstance(results, (list, dict)) else 0
            print(f"  - {platform}: {count}개")

if __name__ == "__main__":
    test_full_crawling() 