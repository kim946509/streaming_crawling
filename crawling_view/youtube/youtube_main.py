"""
YouTube 크롤링 메인 실행 파일
"""
import logging
from ..common.driver import setup_driver
from ..common.csv_writer import save_youtube_csv
from ..common.db_writer import save_youtube_to_db
from .youtube_logic import YouTubeCrawler

logger = logging.getLogger(__name__)

def run_youtube_crawling(url_artist_list, save_csv=True, save_db=True):
    """
    YouTube 크롤링 실행
    
    Args:
        url_artist_list (list): 크롤링할 URL과 아티스트 리스트 [('url1', 'artist1'), ('url2', 'artist2'), ...]
        save_csv (bool): CSV 저장 여부
        save_db (bool): DB 저장 여부
    
    Returns:
        dict: 크롤링된 데이터 딕셔너리
    """
    logger.info(f"🖤 YouTube 크롤링 시작 - 총 {len(url_artist_list)}개 URL")
    
    try:
        # Chrome 드라이버 설정 및 실행
        with setup_driver() as driver:
            crawler = YouTubeCrawler(driver)
            
            # 크롤링 실행
            results = crawler.crawl_multiple(url_artist_list)
            
            logger.info(f"🖤 YouTube 크롤링 완료 - 성공: {len(results)}개")
            
            # CSV 저장
            if save_csv and results:
                csv_paths = save_youtube_csv(results)
                if csv_paths:
                    logger.info(f"📄 CSV 저장 완료: {len(csv_paths)}개 파일")
            
            # DB 저장
            if save_db and results:
                saved_count = save_youtube_to_db(results)
                logger.info(f"💾 DB 저장 완료: {saved_count}개 레코드")
            
            return results
            
    except Exception as e:
        logger.error(f"❌ YouTube 크롤링 실행 중 오류 발생: {e}", exc_info=True)
        return {}

if __name__ == "__main__":
    # 테스트용 실행
    test_urls = [
        ("https://www.youtube.com/watch?v=Sv2mIvMwrSY", "Jaerium"),
        ("https://www.youtube.com/watch?v=R1CZTJ8hW0s", "Jaerium"),
    ]
    
    results = run_youtube_crawling(test_urls)
    print(f"크롤링 결과: {len(results)}개")
    for song_id, result in results.items():
        print(f"[YouTube] 곡명: {result['song_name']}, 아티스트: {result['artist_name']}, "
              f"조회수: {result['view_count']}, 업로드일: {result['upload_date']}") 