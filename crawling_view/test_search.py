import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from crawling_view.youtube_music.youtube_music_main import run_youtube_music_crawling
from user_id_and_password import youtube_music_id, youtube_music_password
from crawling_view.genie.genie_main import run_genie_crawling
from crawling_view.youtube.youtube_main import run_youtube_crawling


'''===================== 유튜브 뮤직 테스트(jaerium) ====================='''
def test_jaerium_youtube_music():
    artist_name = "Jaerium"
    song_names = [
        "Cheers to the Future",
        "Softness in the Snow",
        # "The Frost of Dreams",
        # "Beneath the Frozen Sky",
        # "The Wisp of Winter",
        # "Sparkles of the Night",
        # "Soft Breezes in Winter",
        "The New Year's Moment",
        # "Cheers to the Future",
        # "Softness in the Snow",
        # "The Frost of Dreams",
    ]
    
    # 새로운 구조에 맞게 데이터 변환
    song_list = [
        {'song_title': song, 'artist_name': artist_name}
        for song in song_names
    ]
    
    # 새로운 크롤링 함수 호출
    results = run_youtube_music_crawling(
        song_list, 
        youtube_music_id, 
        youtube_music_password, 
        save_csv=True, 
        save_db=True
    )
    
    logging.info(f"[❤️ YouTube Music(Jaerium)] 크롤링 곡 개수: {len(results)}개")
    for result in results:
        print(f"[YouTubeMusic] 아티스트: {result['artist_name']}, 곡명: {result['song_title']}, "
              f"조회수: {result['view_count']}, 크롤링 날짜: {result['crawl_date']}")


'''===================== 유튜브 뮤직 테스트(anonatsue) ====================='''
def test_anonatsue_youtube_music():
    artist_name = "anonatsue"
    song_names = [
        "Dreamy Orchards",
        "Emerald Symphony",
        "Sunbeam Reflections",
        "Warm Breeze Serenade",
        "Velvet Dawn",
        "Enchanted Bloom",
        "Lush Springtime",
        "Cascading Waterfall",
        "Fragrant Twilight",
        "Cherry Blossom Serenade",
        "Soft Petal Waltz",
        "Garden of Serenity",
        "Wind's Caress",
        "Secret Garden Lullaby",
        "Azure Morning",
        "Lush Green Fields",
        "Meadow Whispers",
    ]
    
    # 새로운 구조에 맞게 데이터 변환
    song_list = [
        {'song_title': song, 'artist_name': artist_name}
        for song in song_names
    ]
    
    # 새로운 크롤링 함수 호출
    results = run_youtube_music_crawling(
        song_list, 
        youtube_music_id, 
        youtube_music_password, 
        save_csv=True, 
        save_db=True
    )
    
    logging.info(f"[❤️ YouTube Music(Anonatsue)] 크롤링 곡 개수: {len(results)}개")
    for result in results:
        print(f"[YouTubeMusic] 아티스트: {result['artist_name']}, 곡명: {result['song_title']}, "
              f"조회수: {result['view_count']}, 크롤링 날짜: {result['crawl_date']}")


'''===================== 지니 테스트(jaerium) ====================='''
def test_genie_jaerium():
    artist_name = "Jaerium"
    song_names = [
        "Beneath the Frozen Sky",
        "The Wisp of Winter",
        "Sparkles of the Night",
        "Soft Breezes in Winter",
        "The New Year's Moment",
        "Cheers to the Future",
        "Softness in the Snow", 
        "The Frost of Dreams" 
        ]
    
    # 새로운 구조에 맞게 데이터 변환
    song_list = [
        {'song_title': song, 'artist_name': artist_name}
        for song in song_names
    ]
    
    # 새로운 크롤링 함수 호출
    results = run_genie_crawling(song_list, save_csv=True, save_db=True)
    
    logging.info(f"[🩵 Genie(Jaerium)] 크롤링 곡 개수: {len(results)}개")
    for result in results:
        view_count = result.get('view_count', {})
        if isinstance(view_count, dict):
            print(f"[Genie] 아티스트: {result['artist_name']}, 곡명: {result['song_title']}, "
                  f"전체 청취자수: {view_count.get('total_person_count', 0)}, "
                  f"전체 재생수: {view_count.get('total_play_count', 0)}, "
                  f"추출일: {result['crawl_date']}")
        else:
            print(f"[Genie] 아티스트: {result['artist_name']}, 곡명: {result['song_title']}, "
                  f"조회수: {view_count}, 추출일: {result['crawl_date']}")


'''===================== 지니 테스트(anonatsue) ====================='''
def test_genie_anonatsue():
    artist_name = "anonatsue"
    song_names = [
        "Dreamy Orchards",
        "Emerald Symphony",
        "Sunbeam Reflections",
        "Warm Breeze Serenade",
        "Velvet Dawn",
        "Enchanted Bloom",
        "Lush Springtime",
        "Cascading Waterfall",
        "Fragrant Twilight",
        "Cherry Blossom Serenade",
        "Soft Petal Waltz",
        "Garden of Serenity",
        "Wind's Caress",
        "Secret Garden Lullaby",
        "Azure Morning",
        "Lush Green Fields",
        "Meadow Whispers"
    ]
    
    # 새로운 구조에 맞게 데이터 변환
    song_list = [
        {'song_title': song, 'artist_name': artist_name}
        for song in song_names
    ]
    
    # 새로운 크롤링 함수 호출
    results = run_genie_crawling(song_list, save_csv=True, save_db=True)
    
    logging.info(f"[🩵 Genie(Anonatsue)] 크롤링 곡 개수: {len(results)}개")
    for result in results:
        view_count = result.get('view_count', {})
        if isinstance(view_count, dict):
            print(f"[Genie] 아티스트: {result['artist_name']}, 곡명: {result['song_title']}, "
                  f"전체 청취자수: {view_count.get('total_person_count', 0)}, "
                  f"전체 재생수: {view_count.get('total_play_count', 0)}, "
                  f"추출일: {result['crawl_date']}")
        else:
            print(f"[Genie] 아티스트: {result['artist_name']}, 곡명: {result['song_title']}, "
                  f"조회수: {view_count}, 추출일: {result['crawl_date']}")


'''===================== 유튜브 테스트 ====================='''
def test_youtube():
    artist_name = "Jaerium"
    song_urls = [
        "https://www.youtube.com/watch?v=Sv2mIvMwrSY",
        "https://www.youtube.com/watch?v=R1CZTJ8hW0s",
        "https://www.youtube.com/watch?v=T4gsXNcF4Z0",
        "https://www.youtube.com/watch?v=-VQx4dePV5I",
        "https://www.youtube.com/watch?v=ecTQx5JNZBA",
        # "https://www.youtube.com/watch?v=NiTwT05VgPA",
        # "https://www.youtube.com/watch?v=nZpOGr1C8es",
        # "https://www.youtube.com/watch?v=xpSJnLMCRxc",
        # "https://www.youtube.com/watch?v=6hhhleiuaJA",
        # "https://www.youtube.com/watch?v=jKY7pm7xlLk",
        # "https://www.youtube.com/watch?v=C36Y5fmPnrQ",
        # "https://www.youtube.com/watch?v=cpfFpC5xrrY",
        # "https://www.youtube.com/watch?v=TlkHKmjha3U",
        # "https://www.youtube.com/watch?v=M1MFK5rWUpU",
        # "https://www.youtube.com/watch?v=LDJAuOW-_-4",
        # "https://www.youtube.com/watch?v=z7WJw6SY0m0",
        # "https://www.youtube.com/watch?v=2r0Wh1uEiuE",
        # "https://www.youtube.com/watch?v=R6VH1qB-Hlg",
        # "https://www.youtube.com/watch?v=HSUgcYisbmw",
        # "https://www.youtube.com/watch?v=fi-QYKZP1d0",
        # "https://www.youtube.com/watch?v=uIcpEprBKUA",
        # "https://www.youtube.com/watch?v=r8clc_Vwahs",
        # "https://www.youtube.com/watch?v=jn__gJ-7-vE",
        # "https://www.youtube.com/watch?v=61yiWvXwB74",
        # "https://www.youtube.com/watch?v=Dz8dI9G-kMk"
    ]
    
    # URL과 artist_name을 함께 전달
    url_artist_list = [(url, artist_name) for url in song_urls]
    
    # 새로운 크롤링 함수 호출
    results = run_youtube_crawling(url_artist_list, save_csv=True, save_db=True)
  
    logging.info(f"[🖤 YouTube] 크롤링 곡 개수: {len(results)}개")
    for song_id, info in results.items():
        print(f"[YouTube] 아티스트: {info['artist_name']}, 곡명: {info['song_name']}, "
              f"조회수: {info['view_count']}, URL: {info['youtube_url']}, "
              f"업로드일: {info['upload_date']}, 추출일: {info['extracted_date']}")


if __name__ == "__main__":
    # print("\n===== YouTubeMusic(Jaerium) 테스트 =====")
    # test_jaerium_youtube_music()
    # print("\n===== YouTubeMusic(Anonatsue) 테스트 =====")
    # test_anonatsue_youtube_music()

    # print("\n===== Genie(Jaerium) 테스트 =====")
    # test_genie_jaerium()
    # print("\n===== Genie(Anonatsue) 테스트 =====")
    # test_genie_anonatsue()

    print("\n===== YouTube 테스트 =====")
    test_youtube()