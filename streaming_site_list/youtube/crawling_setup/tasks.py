from celery import shared_task
from streaming_site_list.youtube.views.crawler import SongViewCountCrawl
import logging

logger = logging.getLogger(__name__)

@shared_task
def SongViewCountTask(song_ids_str):
    SongViewCountCrawl.delay(song_ids_str)