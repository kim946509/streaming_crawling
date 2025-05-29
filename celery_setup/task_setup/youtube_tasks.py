from celery import shared_task
from crawling_view.youtube_crawler_views import YouTubeSongCrawler, save_each_to_csv
import logging

logger = logging.getLogger(__name__)

@shared_task
def youtube_crawl_rhoonart():
    urls = [
        # 루나르트 곡들의 유튜브 주소
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
    results = YouTubeSongCrawler(urls)
    save_each_to_csv(results, "rhoonart")

