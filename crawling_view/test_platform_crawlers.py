"""
개별 플랫폼 크롤러 테스트
"""
import sys
import os
import django
from datetime import date

# Django 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from crawling_view.platform_crawlers import crawl_genie, crawl_youtube_music, crawl_youtube
from crawling_view.common.song_service import SongService
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_individual_crawlers():
    """개별 플랫폼 크롤러 테스트"""
    print("🚀 개별 플랫폼 크롤러 테스트 시작")
    print("=" * 60)
    
    # 활성화된 곡들 조회
    songs = SongService.get_active_songs(date.today())
    
    if not songs:
        print("❌ 크롤링 대상 곡이 없습니다.")
        return
    
    print(f"📋 크롤링 대상 곡: {len(songs)}개")
    
    # 1. Genie 크롤링 테스트
    print("\n🩵 Genie 크롤링 테스트")
    print("-" * 30)
    try:
        genie_result = crawl_genie(songs, save_csv=True, save_db=False)
        print(f"✅ Genie 결과: {len(genie_result.get('crawling_result', []))}개 성공")
    except Exception as e:
        print(f"❌ Genie 실패: {e}")
    
    # 2. YouTube Music 크롤링 테스트
    print("\n❤️ YouTube Music 크롤링 테스트")
    print("-" * 30)
    try:
        youtube_music_result = crawl_youtube_music(songs, save_csv=True, save_db=False)
        print(f"✅ YouTube Music 결과: {len(youtube_music_result.get('crawling_result', []))}개 성공")
    except Exception as e:
        print(f"❌ YouTube Music 실패: {e}")
    
    # 3. YouTube 크롤링 테스트
    print("\n🖤 YouTube 크롤링 테스트")
    print("-" * 30)
    try:
        youtube_result = crawl_youtube(songs, save_csv=True, save_db=False)
        print(f"✅ YouTube 결과: {len(youtube_result.get('crawling_result', {}))}개 성공")
    except Exception as e:
        print(f"❌ YouTube 실패: {e}")
    

    
    print("\n🏁 개별 크롤러 테스트 완료!")

def test_specific_platform(platform: str):
    """특정 플랫폼만 테스트"""
    print(f"🎯 {platform} 플랫폼 테스트")
    print("=" * 40)
    
    songs = SongService.get_active_songs(date.today())
    
    if not songs:
        print("❌ 크롤링 대상 곡이 없습니다.")
        return
    
    if platform == 'genie':
        result = crawl_genie(songs, save_csv=True, save_db=True)
    elif platform == 'youtube_music':
        result = crawl_youtube_music(songs, save_csv=True, save_db=True)
    elif platform == 'youtube':
        result = crawl_youtube(songs, save_csv=True, save_db=True)

    else:
        print(f"❌ 지원하지 않는 플랫폼: {platform}")
        return
    
    crawling_result = result.get('crawling_result', [])
    elapsed_time = result.get('elapsed_time', 0)
    
    if isinstance(crawling_result, list):
        success_count = len(crawling_result)
    elif isinstance(crawling_result, dict):
        success_count = len(crawling_result)
    else:
        success_count = 0
    
    print(f"✅ {platform}: {success_count}개 성공 ({elapsed_time:.2f}초)")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # 특정 플랫폼 테스트
        platform = sys.argv[1]
        test_specific_platform(platform)
    else:
        # 모든 플랫폼 테스트
        test_individual_crawlers() 