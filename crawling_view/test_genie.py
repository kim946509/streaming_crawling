import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from genie_crawler_views import GenieSearchSong, GenieSongCrawler, save_each_to_csv, save_to_db

if __name__ == "__main__":
    # 아티스트별 곡 리스트 딕셔너리
    artist_songs_dict = {
        "제이리움": [
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
            "The Frost of Dreams"
            ],
        "anonatsue": [
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
    }

    # (아티스트, 곡명) 튜플 리스트로 변환
    artist_song_list = [
        (artist, song)
        for artist, songs in artist_songs_dict.items()
        for song in songs
    ]

    # 1. 곡 정보 페이지 HTML 수집
    searcher = GenieSearchSong()
    html_list = []
    for artist, song in artist_song_list:
        print(f"[검색] {artist} - {song}")
        html = searcher.search(artist, song)
        html_list.append(html)
        print(f"HTML 수집 완료: {html is not None}")

    # 2. 곡 정보 크롤링
    print("\n[크롤링 결과]")
    results = GenieSongCrawler.crawl(html_list, artist_song_list)
    for result in results:
        print(f"[Genie] 곡명: {result['song_name']}, 아티스트: {result['artist_name']}, 전체 청취자수: {result['total_person_count']}, 총 재생수: {result['total_play_count']}, 추출일: {result['extracted_date']}")

    # 3. 리스트를 딕셔너리로 변환 (song_name을 key로)
    results_dict = {item['song_name']: item for item in results}

    # 4. CSV 저장
    save_each_to_csv(results_dict, "rhoonart", "genie")

    # 5. DB 저장
    save_to_db(results_dict) 