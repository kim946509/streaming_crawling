"""
개별 플랫폼 크롤러 테스트
"""
import sys
import os
import django

# Django 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from crawling_view.controller.crawling_manager import run_platform_crawling
from crawling_view.data.song_service import SongService
from datetime import date

def test_single_platform(platform):
    """단일 플랫폼 크롤링 테스트"""
    print(f"🎯 {platform} 크롤링 테스트")
    
    # 먼저 수동으로 각 단계를 확인해보자
    print("=== 1단계: 크롤링 대상 노래 조회 ===")
    active_songs = SongService.get_active_songs()
    print(f"전체 활성 곡 수: {len(active_songs)}")
    
    for song in active_songs:
        print(f"  - {song.id}: {song.artist_ko} - {song.title_ko}")
        print(f"    Genie 가능: {song.is_platform_available('genie')}")
        print(f"    YouTube Music 가능: {song.is_platform_available('youtube_music')}")
        print(f"    YouTube 가능: {song.is_platform_available('youtube')}")
    
    print(f"\n=== 2단계: {platform} 플랫폼 필터링 ===")
    platform_songs = SongService.get_songs_by_platform(active_songs, platform)
    print(f"{platform} 플랫폼 가능한 곡 수: {len(platform_songs)}")
    
    for song in platform_songs:
        info = song.get_platform_info(platform)
        print(f"  - {song.id}: {info}")
    
    print(f"\n=== 3단계: 크롤링 형식 변환 ===")
    crawling_data = SongService.convert_to_crawling_format(platform_songs, platform)
    print(f"크롤링 데이터 수: {len(crawling_data)}")
    
    for i, data in enumerate(crawling_data):
        print(f"  [{i+1}] {data}")
    
    print(f"\n=== 4단계: 실제 크롤링 실행 ===")
    result = run_platform_crawling(platform)
    print(f"결과: {result['status']}")
    
    if result['status'] == 'success':
        crawling_count = len(result.get('crawling_results', []))
        print(f"크롤링: {crawling_count}개")
        print(f"DB 저장: {result.get('db_results', {})}")
        print(f"CSV 저장: {len(result.get('csv_results', []))}개 파일")
    else:
        print(f"실패 사유: {result.get('message', '알 수 없음')}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        platform = sys.argv[1]
        test_single_platform(platform)
    else:
        print("사용법: python test_platform_crawlers.py [platform]")
        print("예시: python test_platform_crawlers.py genie")
        print("      python test_platform_crawlers.py youtube_music")
        print("      python test_platform_crawlers.py youtube") 