from celery import shared_task
from crawling_view.youtube_music_crawler_views import SearchSong, YouTubeMusicSongCrawler, save_each_to_csv
from user_id_and_password import youtube_music_id, youtube_music_password

@shared_task
def youtube_music_crawl_jaerium():
    search_song = SearchSong(youtube_music_id, youtube_music_password)
    artist_name = "Jaerium"
    song_names = ["Cheers to the Future", "Softness in the Snow", "The Frost of Dreams"]

    artist_song_list = [(artist_name, song) for song in song_names]
    results = search_song.search_multiple(artist_song_list)
    save_each_to_csv(results, "rhoonart")