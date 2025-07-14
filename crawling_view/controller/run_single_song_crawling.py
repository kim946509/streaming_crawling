"""
단일 곡 크롤링 실행 스크립트 (운영용)
"""
import sys
import os
import django
import logging
import argparse
from datetime import datetime

# Django 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from crawling_view.models import SongInfo
from crawling_view.utils.constants import Platforms
from crawling_view.controller.single_crawling_manager import run_single_song_crawling

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/single_crawling_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='단일 곡 크롤링 실행')
    parser.add_argument('--song_id', required=True, help='크롤링할 곡의 SongInfo id')
    parser.add_argument('--platform', choices=Platforms.ALL_PLATFORMS, help='특정 플랫폼만 크롤링(생략시 전체)')
    parser.add_argument('--save_csv', action='store_true', default=True, help='CSV 저장 여부 (기본값: 저장)')
    parser.add_argument('--save_db', action='store_true', default=True, help='DB 저장 여부 (기본값: 저장)')
    args = parser.parse_args()

    logger.info(f"🚀 단일 곡 크롤링 시작: song_id={args.song_id}, platform={args.platform or 'all'}, save_csv={args.save_csv}, save_db={args.save_db}")

    # 곡 정보 조회
    try:
        song = SongInfo.objects.get(id=args.song_id)
    except SongInfo.DoesNotExist:
        logger.error(f"❌ SongInfo id={args.song_id}를 찾을 수 없습니다.")
        sys.exit(1)

    # 곡 정보 dict 생성 (플랫폼별 정보 포함)
    song_dict = {
        'song_id': song.id,
        'song_title': song.title_ko,
        'artist_name': song.artist_ko,
        'title_en': song.title_en,
        'artist_en': song.artist_en,
        'youtube_url': song.youtube_url,
        'melon_song_id': song.melon_song_id,
    }

    # single_crawling_manager를 사용하여 크롤링 실행
    try:
        result = run_single_song_crawling(
            song_dict=song_dict,
            save_csv=args.save_csv,
            save_db=args.save_db,
            platform=args.platform
        )
        
        logger.info("✅ 단일 곡 크롤링 완료")
        logger.info(f"📊 크롤링 결과 요약: {result}")
        
    except Exception as e:
        logger.error(f"❌ 크롤링 중 오류 발생: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 