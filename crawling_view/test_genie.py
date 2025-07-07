import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from genie.genie_main import run_genie_crawling

if __name__ == "__main__":
    # 아티스트별 곡 리스트 딕셔너리
    artist_songs_dict = {
        "제이리움": [
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

    # {'song_title': '곡명', 'artist_name': '가수명'} 형태로 변환
    song_list = [
        {'song_title': song, 'artist_name': artist}
        for artist, songs in artist_songs_dict.items()
        for song in songs
    ]

    # Genie 크롤링 실행
    print(f"🎵 Genie 크롤링 시작 - 총 {len(song_list)}곡")
    results = run_genie_crawling(song_list, save_csv=True, save_db=True)
    
    print(f"\n🎵 Genie 크롤링 완료 - 성공: {len(results)}곡")
    for result in results:
        view_count = result.get('view_count', {})
        if isinstance(view_count, dict):
            print(f"[Genie] 곡명: {result['song_title']}, 아티스트: {result['artist_name']}, "
                  f"전체 청취자수: {view_count.get('total_person_count', 0)}, "
                  f"총 재생수: {view_count.get('view_count', 0)}, "
                  f"크롤링 날짜: {result['crawl_date']}")
        else:
            print(f"[Genie] 곡명: {result['song_title']}, 아티스트: {result['artist_name']}, "
                  f"조회수: {view_count}, 크롤링 날짜: {result['crawl_date']}") 