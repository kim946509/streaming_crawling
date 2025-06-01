from celery import shared_task
from crawling_view.youtube_music_crawler_views import YouTubeMusicSearchSong, YouTubeMusicSongCrawler, save_each_to_csv
from user_id_and_password import youtube_music_id, youtube_music_password
import logging

logger = logging.getLogger(__name__)

# ------------------------------ Jaerium ------------------------------
@shared_task
def youtube_music_crawl_jaerium_test():
    search_song = YouTubeMusicSearchSong(youtube_music_id, youtube_music_password)
    company_name = "rhoonart"
    artist_name = "Jaerium"
    song_names = [
        "Cheers to the Future",
        "Softness in the Snow",
        "The Frost of Dreams",
        "Beneath the Frozen Sky", 
        "The Wisp of Winter", 
        "Sparkles of the Night", 
        "Soft Breezes in Winter", 
        "The New Year’s Moment", 
        "Cheers to the Future", 
        "Softness in the Snow", 
        "The Frost of Dreams", 
]

    artist_song_list = [(artist_name, song) for song in song_names]
    search_results = search_song.search_multiple(artist_song_list)

    html_list = [item['html'] for item in search_results]
    result_list = YouTubeMusicSongCrawler.extract_song_info_list(html_list, artist_song_list)
    logger.info(f"YouTubeMusicSongCrawler result: {result_list}")

    filepaths = save_each_to_csv({info['song_name']: info for info in result_list}, company_name, 'youtube_music')
    logger.info(f"저장된 파일 경로: {filepaths}")
    return result_list

# ------------------------------ anonatsue ------------------------------
@shared_task
def youtube_music_crawl_anonatsue_test():
    search_song = YouTubeMusicSearchSong(youtube_music_id, youtube_music_password)
    company_name = "rhoonart"
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
        "Wind’s Caress",
        "Secret Garden Lullaby",
        "Azure Morning",
        "Lush Green Fields",
        "Meadow Whispers",
    ]

    artist_song_list = [(artist_name, song) for song in song_names]
    search_results = search_song.search_multiple(artist_song_list)

    html_list = [item['html'] for item in search_results]
    result_list = YouTubeMusicSongCrawler.extract_song_info_list(html_list, artist_song_list)
    logger.info(f"YouTubeMusicSongCrawler result: {result_list}")

    filepaths = save_each_to_csv({info['song_name']: info for info in result_list}, company_name, 'youtube_music')
    logger.info(f"저장된 파일 경로: {filepaths}")
    return result_list