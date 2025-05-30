from crawling_view.youtube_music_crawler_views import SearchSong, YouTubeMusicSongCrawler, save_each_to_csv
from user_id_and_password import youtube_music_id, youtube_music_password

def test_jaerium():
    search_song = SearchSong(youtube_music_id, youtube_music_password)
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
    results = search_song.search_multiple(artist_song_list)
    html_list = [result['html'] for result in results]
    info_list = YouTubeMusicSongCrawler.extract_song_info_list(html_list, artist_song_list)
    for info in info_list:
        print(f"아티스트: {info['artist_name']}, 곡명: {info['song_name']}, 조회수: {info['view_count']}, 추출일: {info['extracted_date']}")
    filepaths = save_each_to_csv({info['song_name']: info for info in info_list}, company_name, 'youtube_music')
    print("저장된 파일 경로:")
    for song, path in filepaths.items():
        print(f"{song}: {path}")

def test_anonatsue():
    search_song = SearchSong(youtube_music_id, youtube_music_password)
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
    results = search_song.search_multiple(artist_song_list)

    html_list = [result['html'] for result in results]
    info_list = YouTubeMusicSongCrawler.extract_song_info_list(html_list, artist_song_list)

    for info in info_list:
        print(f"아티스트: {info['artist_name']}, 곡명: {info['song_name']}, 조회수: {info['view_count']}, 추출일: {info['extracted_date']}")

    # CSV 저장 테스트
    filepaths = save_each_to_csv({info['song_name']: info for info in info_list}, company_name, 'youtube_music')
    print("저장된 파일 경로:")
    for song, path in filepaths.items():
        print(f"{song}: {path}")

if __name__ == "__main__":
    print("===== Jaerium 테스트 =====")
    test_jaerium()
    print("\n===== Anonatsue 테스트 =====")
    test_anonatsue()