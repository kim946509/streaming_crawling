"""
CSV 파일 저장 관련 함수들
"""
import csv
import os
from datetime import datetime
from .constants import CommonSettings
from .utils import clean_filename
import logging

logger = logging.getLogger(__name__)

def save_to_csv(data, filename_prefix, headers=None):
    """
    크롤링 데이터를 CSV 파일로 저장
    
    Args:
        data (list): 저장할 데이터 리스트
        filename_prefix (str): 파일명 앞에 붙을 접두사
        headers (list): CSV 헤더 리스트
    
    Returns:
        str: 저장된 파일 경로
    """
    if not data:
        logger.warning("저장할 데이터가 없습니다.")
        return None
    
    # 파일명 생성
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{filename_prefix}_{timestamp}.csv"
    
    # csv_folder 디렉터리 확인 및 생성
    csv_folder = 'csv_folder'
    if not os.path.exists(csv_folder):
        os.makedirs(csv_folder)
    
    file_path = os.path.join(csv_folder, filename)
    
    try:
        with open(file_path, 'w', newline='', encoding=CommonSettings.CSV_ENCODING) as csvfile:
            if headers:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                writer.writerows(data)
            else:
                # 데이터가 dict인 경우 자동으로 헤더 생성
                if data and isinstance(data[0], dict):
                    headers = list(data[0].keys())
                    writer = csv.DictWriter(csvfile, fieldnames=headers)
                    writer.writeheader()
                    writer.writerows(data)
                else:
                    # 단순 리스트인 경우
                    writer = csv.writer(csvfile)
                    writer.writerows(data)
        
        logger.info(f"✅ CSV 파일 저장 완료: {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"❌ CSV 파일 저장 실패: {e}", exc_info=True)
        return None

def save_genie_csv(data):
    """Genie 크롤링 데이터를 CSV로 저장"""
    # 데이터 변환 (view_count를 분리)
    csv_data = []
    for item in data:
        view_count = item.get('view_count', {})
        if isinstance(view_count, dict):
            csv_row = {
                'song_title': item['song_title'],
                'artist_name': item['artist_name'],
                'total_person_count': view_count.get('total_person_count', 0),
                'total_play_count': view_count.get('total_play_count', 0),
                'crawl_date': item['crawl_date']
            }
        else:
            csv_row = {
                'song_title': item['song_title'],
                'artist_name': item['artist_name'],
                'total_person_count': 0,
                'total_play_count': 0,
                'crawl_date': item['crawl_date']
            }
        csv_data.append(csv_row)
    
    headers = ['song_title', 'artist_name', 'total_person_count', 'total_play_count', 'crawl_date']
    return save_to_csv(csv_data, 'genie_crawling', headers)

def save_youtube_music_csv(data):
    """YouTube Music 크롤링 데이터를 CSV로 저장"""
    headers = ['song_title', 'artist_name', 'view_count', 'crawl_date']
    return save_to_csv(data, 'youtube_music_crawling', headers)

def save_youtube_csv(data):
    """YouTube 크롤링 데이터를 CSV로 저장"""
    headers = ['song_title', 'artist_name', 'view_count', 'upload_date', 'crawl_date']
    return save_to_csv(data, 'youtube_crawling', headers) 