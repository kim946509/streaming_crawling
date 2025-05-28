from celery import shared_task
from streaming_site_list.youtube.views.crawler import YouTubeSongCrawler
import logging

logger = logging.getLogger(__name__)

@shared_task
def YouTubeSongCrawlingTask():
    """⬇️ 여기에 크롤링 하길 원하는 노래의 유튜브 주소를 추가하면 크롤링됩니다 👍🏻"""
    urls = [
        "https://www.youtube.com/watch?v=Sv2mIvMwrSY", "https://www.youtube.com/watch?v=R1CZTJ8hW0s", 
        "https://www.youtube.com/watch?v=T4gsXNcF4Z0", "https://www.youtube.com/watch?v=-VQx4dePV5I", 
        "https://www.youtube.com/watch?v=ecTQx5JNZBA", "https://www.youtube.com/watch?v=NiTwT05VgPA", 
        "https://www.youtube.com/watch?v=nZpOGr1C8es", "https://www.youtube.com/watch?v=M1MFK5rWUpU", 
        "https://www.youtube.com/watch?v=xpSJnLMCRxc", "https://www.youtube.com/watch?v=6hhhleiuaJA", 
        "https://www.youtube.com/watch?v=jKY7pm7xlLk", "https://www.youtube.com/watch?v=C36Y5fmPnrQ", 
        "https://www.youtube.com/watch?v=cpfFpC5xrrY", "https://www.youtube.com/watch?v=TlkHKmjha3U", 
        "https://www.youtube.com/watch?v=M1MFK5rWUpU", "https://www.youtube.com/watch?v=LDJAuOW-_-4", 
        "https://www.youtube.com/watch?v=z7WJw6SY0m0", "https://www.youtube.com/watch?v=ecTQx5JNZBA", 
        "https://www.youtube.com/watch?v=2r0Wh1uEiuE", "https://www.youtube.com/watch?v=R6VH1qB-Hlg", 
        "https://www.youtube.com/watch?v=HSUgcYisbmw", "https://www.youtube.com/watch?v=fi-QYKZP1d0", 
        "https://www.youtube.com/watch?v=uIcpEprBKUA", "https://www.youtube.com/watch?v=LDJAuOW-_-4", 
        "https://www.youtube.com/watch?v=r8clc_Vwahs", "https://www.youtube.com/watch?v=z7WJw6SY0m0", 
        "https://www.youtube.com/watch?v=jn__gJ-7-vE", "https://www.youtube.com/watch?v=61yiWvXwB74", 
        "https://www.youtube.com/watch?v=Dz8dI9G-kMk"
    ]
    try:
        logger.info("🚀 유튜브 크롤링 시작")
        YouTubeSongCrawler(urls)
        logger.info("✅ 유튜브 크롤링 완료")
    except Exception as e:
        logger.error(f"❌ 오류 발생: {e}", exc_info=True)
