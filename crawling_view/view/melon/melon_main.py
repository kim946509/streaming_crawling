"""
Melon 크롤링 메인 실행 파일 (API 기반)
"""
import logging
import time
from .melon_logic import MelonCrawler
from crawling_view.data.csv_writer import save_melon_csv
from crawling_view.data.db_writer import save_melon_to_db
import random

logger = logging.getLogger(__name__)

def run_melon_crawling(song_list, save_csv=True, save_db=True):
    """
    Melon 크롤링 실행 (API 기반)
    
    Args:
        song_list (list): 크롤링할 곡 리스트 [{'melon_song_id': 'id', 'song_id': 'id'}, ...]
        save_csv (bool): CSV 저장 여부
        save_db (bool): DB 저장 여부
    
    Returns:
        list: 크롤링된 데이터 리스트
    """
    logger.info(f"🍈 Melon 크롤링 시작 - 총 {len(song_list)}곡")
    
    crawled_data = []
    crawler = MelonCrawler()
    
    try:
        # 각 곡에 대해 크롤링 실행
        for song_info in song_list:
            melon_song_id = song_info.get('melon_song_id', '')
            song_id = song_info.get('song_id')
            
            if not melon_song_id:
                logger.warning(f"⚠️ melon_song_id가 없습니다: {song_info}")
                continue
            
            logger.debug(f"🔍 API 호출 중: melon_song_id={melon_song_id} (song_id={song_id})")
            
            # 크롤링 실행
            result = crawler.crawl_song(melon_song_id, song_id)
            
            if result:
                crawled_data.append(result)
                logger.debug(f"✅ 크롤링 완료: {result['song_title']} - {result['artist_name']} (조회수: {result['views']}, 청취자: {result['listeners']})")
            else:
                logger.warning(f"❌ 크롤링 실패: melon_song_id={melon_song_id}")
            
            # API 호출 간격 조절 (서버 부하 방지)
            time.sleep(random.uniform(0.5, 1.5))
        
        logger.info(f"🍈 Melon 크롤링 완료 - 성공: {len(crawled_data)}곡")
        
        # CSV 저장
        if save_csv and crawled_data:
            csv_path = save_melon_csv(crawled_data)
            if csv_path:
                logger.info(f"📄 CSV 저장 완료: {csv_path}")
        
        # DB 저장
        if save_db and crawled_data:
            saved_count = save_melon_to_db(crawled_data)
            logger.info(f"💾 DB 저장 완료: {saved_count}개 레코드")
        
        return crawled_data
        
    except Exception as e:
        logger.error(f"❌ Melon 크롤링 실행 중 오류 발생: {e}", exc_info=True)
        return []

if __name__ == "__main__":
    # 테스트용 실행
    import random
    
    test_songs = [
        {'melon_song_id': '39156202', 'song_id': 'test_1'},  # FAMOUS - ALLDAY PROJECT
        {'melon_song_id': '39156203', 'song_id': 'test_2'},  # 다른 곡
    ]
    
    results = run_melon_crawling(test_songs)
    print(f"크롤링 결과: {len(results)}곡") 