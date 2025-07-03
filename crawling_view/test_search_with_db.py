import os
import django
import logging
import time
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from crawling_view.youtube_music.youtube_music_main import run_youtube_music_crawling
from crawling_view.genie.genie_main import run_genie_crawling
from crawling_view.youtube.youtube_main import run_youtube_crawling
from streaming_site_list.models import SongInfo, CrawlingPeriod
from user_id_and_password import youtube_music_id, youtube_music_password


def format_time(seconds):
    """초를 분:초 형태로 포맷팅"""
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    if minutes > 0:
        return f"{minutes}분 {remaining_seconds}초"
    else:
        return f"{remaining_seconds}초"


def get_active_songs():
    """
    오늘 날짜를 기준으로 활성화된 크롤링 대상 곡들을 조회
    
    Returns:
        list: SongInfo 객체 리스트
    """
    today = date.today()
    
    # 1. 오늘 날짜가 크롤링 기간에 포함되고 활성화된 song_id 조회
    active_periods = CrawlingPeriod.objects.filter(
        start_date__lte=today,
        end_date__gte=today,
        is_deleted=False
    ).values_list('song_id', flat=True)
    
    print(f"📅 오늘 날짜: {today}")
    print(f"🔍 활성 크롤링 기간에 포함된 song_id 개수: {len(active_periods)}")
    
    # 2. 해당 song_id들의 SongInfo 조회 (삭제되지 않은 것만)
    active_songs = SongInfo.objects.filter(
        id__in=active_periods,
        is_deleted=False
    )
    
    print(f"🎵 크롤링 대상 곡 개수: {len(active_songs)}")
    
    for song in active_songs:
        print(f"   - {song.id}: {song.artist_name} - {song.song_name}")
    
    return list(active_songs)


def test_genie_crawling(songs):
    """지니 크롤링 테스트"""
    if not songs:
        print("❌ 크롤링 대상 곡이 없습니다.")
        return []
    
    start_time = time.time()
    print(f"\n🩵 [Genie] 크롤링 시작 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # SongInfo 객체를 Genie 크롤링 형식으로 변환
    song_list = [
        {'song_title': song.song_name, 'artist_name': song.artist_name}
        for song in songs
    ]
    
    try:
        results = run_genie_crawling(song_list, save_csv=True, save_db=True)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print(f"[Genie] 크롤링 완료 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[Genie] 총 소요 시간: {format_time(elapsed_time)}")
        print(f"[Genie] 곡당 평균 시간: {format_time(elapsed_time / len(song_list)) if song_list else '0초'}")
        print(f"[Genie] 성공한 곡 수: {len(results)}/{len(song_list)}")
        
        return results
        
    except Exception as e:
        print(f"❌ [Genie] 크롤링 실패: {e}")
        return []


def test_youtube_music_crawling(songs):
    """유튜브 뮤직 크롤링 테스트"""
    if not songs:
        print("❌ 크롤링 대상 곡이 없습니다.")
        return []
    
    start_time = time.time()
    print(f"\n[YouTube Music] 크롤링 시작 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # SongInfo 객체를 YouTube Music 크롤링 형식으로 변환
    song_list = [
        {'song_title': song.song_name, 'artist_name': song.artist_name}
        for song in songs
    ]
    
    try:
        results = run_youtube_music_crawling(
            song_list, 
            youtube_music_id, 
            youtube_music_password, 
            save_csv=True, 
            save_db=True
        )
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print(f"[YouTube Music] 크롤링 완료 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[YouTube Music] 총 소요 시간: {format_time(elapsed_time)}")
        print(f"[YouTube Music] 곡당 평균 시간: {format_time(elapsed_time / len(song_list)) if song_list else '0초'}")
        print(f"[YouTube Music] 성공한 곡 수: {len(results)}/{len(song_list)}")
        
        return results
        
    except Exception as e:
        print(f"❌ [YouTube Music] 크롤링 실패: {e}")
        return []


def test_youtube_crawling(songs):
    """유튜브 크롤링 테스트"""
    if not songs:
        print("❌ 크롤링 대상 곡이 없습니다.")
        return []
    
    start_time = time.time()
    print(f"\n🖤 [YouTube] 크롤링 시작 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # YouTube URL이 있는 곡들만 필터링
    songs_with_url = [song for song in songs if song.youtube_url]
    
    if not songs_with_url:
        print("❌ YouTube URL이 있는 곡이 없습니다.")
        return {}
    
    # SongInfo 객체를 YouTube 크롤링 형식으로 변환
    url_artist_list = [
        (song.youtube_url, song.artist_name)
        for song in songs_with_url
    ]
    
    try:
        results = run_youtube_crawling(url_artist_list, save_csv=True, save_db=True)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print(f"[YouTube] 크롤링 완료 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[YouTube] 총 소요 시간: {format_time(elapsed_time)}")
        print(f"[YouTube] 곡당 평균 시간: {format_time(elapsed_time / len(url_artist_list)) if url_artist_list else '0초'}")
        print(f"[YouTube] 성공한 곡 수: {len(results)}/{len(url_artist_list)}")
        
        return results
        
    except Exception as e:
        print(f"❌ [YouTube] 크롤링 실패: {e}")
        return {}


def main():
    """메인 테스트 함수"""
    total_start_time = time.time()
    print(f"DB 기반 크롤링 테스트 시작: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        # 1. 활성화된 크롤링 대상 곡들 조회
        songs = get_active_songs()
        
        if not songs:
            print("❌ 크롤링 대상 곡이 없습니다. 프로그램을 종료합니다.")
            return
        
        # 2. 각 플랫폼별 크롤링 실행
        genie_results = test_genie_crawling(songs)
        youtube_music_results = test_youtube_music_crawling(songs)
        youtube_results = test_youtube_crawling(songs)
        
        # 3. 전체 결과 요약
        total_end_time = time.time()
        total_elapsed_time = total_end_time - total_start_time
        
        print("\n" + "=" * 80)
        print("📊 크롤링 결과 요약")
        print("=" * 80)
        print(f"🎯 대상 곡 수: {len(songs)}")
        print(f"🩵 Genie 성공: {len(genie_results)}")
        print(f"❤️ YouTube Music 성공: {len(youtube_music_results)}")
        print(f"🖤 YouTube 성공: {len(youtube_results)}")
        print("=" * 80)
        print(f"🏁 전체 테스트 완료 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️ 전체 소요 시간: {format_time(total_elapsed_time)}")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류 발생: {e}")
        logging.error(f"DB 기반 크롤링 테스트 실패: {e}", exc_info=True)


if __name__ == "__main__":
    main()
