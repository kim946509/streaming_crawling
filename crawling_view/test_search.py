import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from crawling_view.youtube_music_crawler_views import YouTubeMusicSearchSong, YouTubeMusicSongCrawler, save_each_to_csv as save_each_to_csv_ytmusic
from user_id_and_password import youtube_music_id, youtube_music_password
from crawling_view.genie_crawler_views import GenieSearchSong, GenieSongCrawler, save_each_to_csv as save_each_to_csv_genie
from crawling_view.youtube_crawler_views import YouTubeSongCrawler, save_each_to_csv as save_each_to_csv_youtube


'''===================== 유튜브 뮤직 테스트(jaerium) ====================='''
def test_jaerium_youtube_music():
    search_song_youtube_music_jaerium = YouTubeMusicSearchSong(youtube_music_id, youtube_music_password)
    artist_name = "Jaerium"
    company_name = "rhoonart"
    song_names = [
        "Cheers to the Future",
        "Softness in the Snow",
        "The Frost of Dreams",
        "Beneath the Frozen Sky",
        "The Wisp of Winter",
        "Sparkles of the Night",
        "Soft Breezes in Winter",
        "The New Year's Moment",
        "Cheers to the Future",
        "Softness in the Snow",
        "The Frost of Dreams",
    ]
    artist_song_list = [(artist_name, song) for song in song_names]
    results = search_song_youtube_music_jaerium.search_multiple(artist_song_list)
    logging.info(f"[❤️ YouTube Music(Jaerium)] 크롤링 곡 개수: {len(results)}개")

    html_list = [result['html'] for result in results]
    info_list = YouTubeMusicSongCrawler.extract_song_info_list(html_list, artist_song_list)
    for info in info_list:
        print(f"[YouTubeMusic] 아티스트: {info['artist_name']}, 곡명: {info['song_name']}, 조회수: {info['view_count']}, 추출일: {info['extracted_date']}")
    filepaths = save_each_to_csv_ytmusic({info['song_name']: info for info in info_list}, company_name, 'youtube_music')
    print("저장된 파일 경로:")
    for song, path in filepaths.items():
        print(f"{song}: {path}")


'''===================== 유튜브 뮤직 테스트(anonatsue) ====================='''
def test_anonatsue_youtube_music():
    search_song_youtube_music_anonatsue = YouTubeMusicSearchSong(youtube_music_id, youtube_music_password)
    artist_name = "anonatsue"
    company_name = "rhoonart"
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
    artist_song_list = [(artist_name, song) for song in song_names]
    results = search_song_youtube_music_anonatsue.search_multiple(artist_song_list)
    logging.info(f"[❤️ YouTube Music(Anonatsue)] 크롤링 곡 개수: {len(results)}개")

    html_list = [result['html'] for result in results]
    info_list = YouTubeMusicSongCrawler.extract_song_info_list(html_list, artist_song_list)
    for info in info_list:
        print(f"[YouTubeMusic] 아티스트: {info['artist_name']}, 곡명: {info['song_name']}, 조회수: {info['view_count']}, 추출일: {info['extracted_date']}")
    filepaths = save_each_to_csv_ytmusic({info['song_name']: info for info in info_list}, company_name, 'youtube_music')
    print("저장된 파일 경로:")
    for song, path in filepaths.items():
        print(f"{song}: {path}")


'''===================== 지니 테스트(jaerium) ====================='''
def test_genie_jaerium():
    search_song_genie = GenieSearchSong()
    artist_name = "제이리움"
    company_name = "rhoonart"
    song_names = [
        "Beneath the Frozen Sky",
        "The Wisp of Winter",
        "Sparkles of the Night",
        "Soft Breezes in Winter",
        "The New Year’s Moment",
        "Cheers to the Future",
        "Softness in the Snow",
        "The Frost of Dreams"
        ]
    artist_song_list = [(artist_name, song) for song in song_names]
    results = search_song_genie.search_multiple(artist_song_list)
    logging.info(f"[🩵 Genie(Jaerium)] 크롤링 곡 개수: {len(results)}개")

    html_list = [result['html'] for result in results]
    info_list = GenieSongCrawler.crawl(html_list, artist_song_list)
    for info in info_list:
        print(f"[Genie] 아티스트: {info['artist_name']}, 곡명: {info['song_name']}, 전체 청취자수: {info['total_person_count']}, 전체 재생수: {info['total_play_count']}, 추출일: {info['extracted_date']}")
    filepaths = save_each_to_csv_genie({info['song_name']: info for info in info_list}, company_name, 'genie')
    print("저장된 파일 경로:")
    for song, path in filepaths.items():
        print(f"{song}: {path}")


'''===================== 지니 테스트(anonatsue) ====================='''
def test_genie_anonatsue():
    search_song_genie = GenieSearchSong()
    artist_name = "anonatsue"
    company_name = "rhoonart"
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
        "Wind’s Caress",
        "Secret Garden Lullaby",
        "Azure Morning",
        "Lush Green Fields",
        "Meadow Whispers"
    ]
    artist_song_list = [(artist_name, song) for song in song_names]
    results = search_song_genie.search_multiple(artist_song_list)
    logging.info(f"[🩵 Genie(Anonatsue)] 크롤링 곡 개수: {len(results)}개")

    html_list = [result['html'] for result in results]
    info_list = GenieSongCrawler.crawl(html_list, artist_song_list)
    for info in info_list:
        print(f"[Genie] 아티스트: {info['artist_name']}, 곡명: {info['song_name']}, 전체 청취자수: {info['total_person_count']}, 전체 재생수: {info['total_play_count']}, 추출일: {info['extracted_date']}")
    filepaths = save_each_to_csv_genie({info['song_name']: info for info in info_list}, company_name, 'genie')
    print("저장된 파일 경로:")
    for song, path in filepaths.items():
        print(f"{song}: {path}")


'''===================== 유튜브 테스트 ====================='''
def test_youtube():
    company_name = "rhoonart"
    song_urls = [
        "https://www.youtube.com/watch?v=Sv2mIvMwrSY",
        "https://www.youtube.com/watch?v=R1CZTJ8hW0s",
        "https://www.youtube.com/watch?v=T4gsXNcF4Z0",
        "https://www.youtube.com/watch?v=-VQx4dePV5I",
        "https://www.youtube.com/watch?v=ecTQx5JNZBA",
        "https://www.youtube.com/watch?v=NiTwT05VgPA",
        "https://www.youtube.com/watch?v=nZpOGr1C8es",
        "https://www.youtube.com/watch?v=xpSJnLMCRxc",
        "https://www.youtube.com/watch?v=6hhhleiuaJA",
        "https://www.youtube.com/watch?v=jKY7pm7xlLk",
        "https://www.youtube.com/watch?v=C36Y5fmPnrQ",
        "https://www.youtube.com/watch?v=cpfFpC5xrrY",
        "https://www.youtube.com/watch?v=TlkHKmjha3U",
        "https://www.youtube.com/watch?v=M1MFK5rWUpU",
        "https://www.youtube.com/watch?v=LDJAuOW-_-4",
        "https://www.youtube.com/watch?v=z7WJw6SY0m0",
        "https://www.youtube.com/watch?v=2r0Wh1uEiuE",
        "https://www.youtube.com/watch?v=R6VH1qB-Hlg",
        "https://www.youtube.com/watch?v=HSUgcYisbmw",
        "https://www.youtube.com/watch?v=fi-QYKZP1d0",
        "https://www.youtube.com/watch?v=uIcpEprBKUA",
        "https://www.youtube.com/watch?v=r8clc_Vwahs",
        "https://www.youtube.com/watch?v=jn__gJ-7-vE",
        "https://www.youtube.com/watch?v=61yiWvXwB74",
        "https://www.youtube.com/watch?v=Dz8dI9G-kMk"
    ]
    results = YouTubeSongCrawler(song_urls)
    logging.info(f"[🖤 YouTube] 크롤링 곡 개수: {len(results)}개")
    for song_id, info in results.items():
        print(f"[YouTube] 곡명: {info['song_name']}, 조회수: {info['view_count']}, URL: {info['youtube_url']}, 업로드일: {info['upload_date']}, 추출일: {info['extracted_date']}")
    filepaths = save_each_to_csv_youtube(results, company_name, 'youtube')
    print("저장된 파일 경로:")
    for song, path in filepaths.items():
        print(f"{song}: {path}")



if __name__ == "__main__":
    print("\n===== YouTubeMusic(Jaerium) 테스트 =====")
    test_jaerium_youtube_music()
    print("\n===== YouTubeMusic(Anonatsue) 테스트 =====")
    test_anonatsue_youtube_music()

    print("\n===== Genie(Jaerium) 테스트 =====")
    test_genie_jaerium()
    print("\n===== Genie(Anonatsue) 테스트 =====")
    test_genie_anonatsue()

    print("\n===== YouTube 테스트 =====")
    test_youtube()