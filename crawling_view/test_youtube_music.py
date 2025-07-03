import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from youtube_music.youtube_music_main import run_youtube_music_crawling
from user_id_and_password import youtube_music_id, youtube_music_password

if __name__ == "__main__":
    # 아티스트별 곡 리스트 딕셔너리
    artist_songs_dict = {
        "Jaerium": [
            "Cheers to the Future",
            "Softness in the Snow",
            "The Frost of Dreams",
            "Beneath the Frozen Sky",
            "The Wisp of Winter",
            "Sparkles of the Night",
            "Soft Breezes in Winter",
            "The New Year's Moment",
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

    # YouTube Music 크롤링 실행
    print(f"🎵 YouTube Music 크롤링 시작 - 총 {len(song_list)}곡")
    results = run_youtube_music_crawling(
        song_list, 
        youtube_music_id, 
        youtube_music_password, 
        save_csv=True, 
        save_db=True
    )
    
    print(f"\n🎵 YouTube Music 크롤링 완료 - 성공: {len(results)}곡")
    for result in results:
        print(f"[YouTube Music] 곡명: {result['song_title']}, 아티스트: {result['artist_name']}, "
              f"조회수: {result['view_count']}, 크롤링 날짜: {result['crawl_date']}") 