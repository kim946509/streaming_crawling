"""
Melon 크롤링 테스트
"""
import sys
import os
import django

# Django 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from crawling_view.view.melon.melon_logic import MelonCrawler
from crawling_view.view.melon.melon_main import run_melon_crawling
from crawling_view.controller.crawling_manager import run_platform_crawling
from crawling_view.data.song_service import SongService
from datetime import date

def test_melon_api():
    """멜론 API 직접 테스트"""
    print("🍈 Melon API 직접 테스트")
    
    crawler = MelonCrawler()
    
    # 테스트용 멜론 곡 ID (FAMOUS - ALLDAY PROJECT)
    test_song_id = "39156202"
    
    print(f"🎵 API 호출: songId={test_song_id}")
    result = crawler.crawl_song(test_song_id, "test_song_1")
    
    if result:
        print("✅ API 호출 성공!")
        print(f"   곡명: {result['song_title']}")
        print(f"   아티스트: {result['artist_name']}")
        print(f"   조회수: {result['views']:,}")
        print(f"   청취자수: {result['listeners']:,}")
        print(f"   크롤링 시간: {result['crawl_date']}")
    else:
        print("❌ API 호출 실패")

def test_melon_crawling():
    """멜론 크롤링 전체 테스트"""
    print("\n🍈 Melon 크롤링 전체 테스트")
    
    # 테스트용 데이터
    test_songs = [
        {'melon_song_id': '39156202', 'song_id': 'test_1'},  # FAMOUS - ALLDAY PROJECT
        {'melon_song_id': '39156203', 'song_id': 'test_2'},  # 다른 곡 (실패 테스트)
    ]
    
    print(f"🎵 크롤링 대상: {len(test_songs)}곡")
    
    # 크롤링 실행 (CSV, DB 저장 포함)
    results = run_melon_crawling(test_songs, save_csv=True, save_db=True)
    
    print(f"✅ 크롤링 완료: {len(results)}곡 성공")
    
    for i, result in enumerate(results, 1):
        print(f"  [{i}] {result['song_title']} - {result['artist_name']}")
        print(f"      조회수: {result['views']:,}, 청취자: {result['listeners']:,}")

def test_platform_crawling():
    """플랫폼 크롤링 매니저 테스트"""
    print("\n🍈 플랫폼 크롤링 매니저 테스트")
    
    # 먼저 수동으로 각 단계를 확인해보자
    print("=== 1단계: 크롤링 대상 노래 조회 ===")
    active_songs = SongService.get_active_songs()
    print(f"전체 활성 곡 수: {len(active_songs)}")
    
    for song in active_songs:
        print(f"  - {song.id}: {song.genie_artist} - {song.genie_title}")
        print(f"    Melon 가능: {song.is_platform_available('melon')}")
        if song.is_platform_available('melon'):
            print(f"    Melon ID: {song.melon_song_id}")
    
    print(f"\n=== 2단계: Melon 플랫폼 필터링 ===")
    melon_songs = SongService.get_songs_by_platform(active_songs, 'melon')
    print(f"Melon 플랫폼 가능한 곡 수: {len(melon_songs)}")
    
    for song in melon_songs:
        info = song.get_platform_info('melon')
        print(f"  - {song.id}: {info}")
    
    print(f"\n=== 3단계: 크롤링 형식 변환 ===")
    crawling_data = SongService.convert_to_crawling_format(melon_songs, 'melon')
    print(f"크롤링 데이터 수: {len(crawling_data)}")
    
    for i, data in enumerate(crawling_data):
        print(f"  [{i+1}] {data}")
    
    print(f"\n=== 4단계: 실제 크롤링 실행 ===")
    result = run_platform_crawling('melon')
    print(f"결과: {result['status']}")
    
    if result['status'] == 'success':
        crawling_count = len(result.get('crawling_results', []))
        print(f"크롤링: {crawling_count}개")
        print(f"DB 저장: {result.get('db_results', {})}")
        print(f"CSV 저장: {len(result.get('csv_results', []))}개 파일")
    else:
        print(f"실패 사유: {result.get('message', '알 수 없음')}")

if __name__ == "__main__":
    print("🚀 Melon 크롤링 테스트 시작")
    
    # 1. API 직접 테스트
    test_melon_api()
    
    # 2. 크롤링 전체 테스트
    test_melon_crawling()
    
    # 3. 플랫폼 크롤링 매니저 테스트
    test_platform_crawling()
    
    print("\n✅ Melon 크롤링 테스트 완료") 