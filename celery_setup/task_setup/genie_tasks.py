from celery import shared_task
from crawling_view.genie.genie_main import run_genie_crawling
import logging

logger = logging.getLogger(__name__)

# ------------------------------ rhoonart ------------------------------
class rhoonart_songs:
    jaerium = [
        "Beneath the Frozen Sky",
        "The Wisp of Winter",
        "Sparkles of the Night",
        "Soft Breezes in Winter",
        "The New Year's Moment",
        "Cheers to the Future",
        "Softness in the Snow",
        "The Frost of Dreams"
    ]
    anonatsue = [
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

    @staticmethod
    def crawl_artist(artist_name, song_names):
        # 새로운 구조에 맞게 데이터 변환
        song_list = [
            {'song_title': song, 'artist_name': artist_name}
            for song in song_names
        ]
        
        # 새로운 크롤링 함수 호출
        results = run_genie_crawling(song_list, save_csv=True, save_db=True)
        
        logger.info(f"✅ Genie 크롤링 완료: {len(results)}개 곡")
        return results

# ------------------------------ Jaerium ------------------------------
@shared_task
def genie_crawl_jaerium_test():
    return rhoonart_songs.crawl_artist("제이리움", rhoonart_songs.jaerium)

# ------------------------------ anonatsue ------------------------------
@shared_task
def genie_crawl_anonatsue_test():
    return rhoonart_songs.crawl_artist("anonatsue", rhoonart_songs.anonatsue)