"""
CSV 파일 저장 관련 함수들
"""
import csv
import os
from datetime import datetime
from crawling_view.utils.constants import CommonSettings
from crawling_view.utils.utils import clean_filename
import logging
import pandas as pd
from pathlib import Path
from crawling_view.utils.constants import FilePaths

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

def _create_directory(company_name, service_name):
    """
    CSV 저장용 디렉토리 생성
    
    Args:
        company_name (str): 회사명
        service_name (str): 서비스명
        
    Returns:
        Path: 생성된 디렉토리 경로
    """
    dir_path = Path(FilePaths.CSV_BASE_DIR) / company_name / service_name
    dir_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"✅ {company_name} 하위에 {service_name} 폴더 생성 완료")
    return dir_path

def save_genie_csv(results, company_name="rhoonart"):
    """
    Genie 크롤링 결과를 CSV로 저장
    
    Args:
        results (list): 크롤링 결과 리스트
        company_name (str): 회사명
        
    Returns:
        list: 저장된 파일 경로 리스트
    """
    if not results:
        return []
    
    csv_dir = _create_directory(company_name, 'genie')
    saved_files = []
    
    for result in results:
        song_title = result.get('song_title', 'unknown')
        
        # 파일명 정리
        filename = f"{clean_filename(song_title)}.csv"
        filepath = csv_dir / filename
        
        # views 데이터 처리
        views_data = result.get('views', {})
        if isinstance(views_data, dict):
            total_person_count = views_data.get('total_person_count', 0)
            views = views_data.get('views', 0)
        else:
            total_person_count = 0
            views = views_data if views_data else 0
        
        # DataFrame 생성
        df = pd.DataFrame([{
            'song_id': f"genie_{result.get('artist_name', '')}_{song_title}".lower().replace(' ', '_'),
            'song_title': song_title,
            'artist_name': result.get('artist_name'),
            'total_person_count': total_person_count,
            'views': views,
            'crawl_date': result.get('crawl_date')
        }])
        
        # 기존 파일이 있으면 누적
        if filepath.exists():
            try:
                old_df = pd.read_csv(filepath)
                combined_df = pd.concat([old_df, df], ignore_index=True)
            except Exception as e:
                logger.error(f"❌ 기존 CSV 읽기 실패: {filepath} - {e}")
                combined_df = df
        else:
            combined_df = df
        
        # 날짜순 정렬 후 저장
        combined_df = combined_df.sort_values(by="crawl_date", ascending=False)
        combined_df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        saved_files.append(str(filepath))
        logger.info(f"✅ CSV 파일 저장 완료: {filepath}")
    
    return saved_files

def save_youtube_music_csv(results, company_name="rhoonart"):
    """
    YouTube Music 크롤링 결과를 CSV로 저장
    
    Args:
        results (list): 크롤링 결과 리스트
        company_name (str): 회사명
        
    Returns:
        list: 저장된 파일 경로 리스트
    """
    if not results:
        return []
    
    csv_dir = _create_directory(company_name, 'youtube_music')
    saved_files = []
    
    for result in results:
        song_title = result.get('song_title', 'unknown')
        
        # 파일명 정리
        filename = f"{clean_filename(song_title)}.csv"
        filepath = csv_dir / filename
        
        # DataFrame 생성
        df = pd.DataFrame([{
            'song_id': f"ytmusic_{result.get('artist_name', '')}_{song_title}".lower().replace(' ', '_'),
            'song_title': song_title,
            'artist_name': result.get('artist_name'),
            'views': result.get('views', 0),
            'crawl_date': result.get('crawl_date')
        }])
        
        # 기존 파일이 있으면 누적
        if filepath.exists():
            try:
                old_df = pd.read_csv(filepath)
                combined_df = pd.concat([old_df, df], ignore_index=True)
            except Exception as e:
                logger.error(f"❌ 기존 CSV 읽기 실패: {filepath} - {e}")
                combined_df = df
        else:
            combined_df = df
        
        # 날짜순 정렬 후 저장
        combined_df = combined_df.sort_values(by="crawl_date", ascending=False)
        combined_df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        saved_files.append(str(filepath))
        logger.info(f"✅ CSV 파일 저장 완료: {filepath}")
    
    return saved_files

def save_youtube_csv(results, company_name="rhoonart"):
    """
    YouTube 크롤링 결과를 CSV로 저장
    
    Args:
        results (dict): 크롤링 결과 딕셔너리
        company_name (str): 회사명
        
    Returns:
        list: 저장된 파일 경로 리스트
    """
    if not results:
        return []
    
    csv_dir = _create_directory(company_name, 'youtube')
    saved_files = []
    
    for url, result in results.items():
        song_title = result.get('song_title', 'unknown')
        
        # 파일명 정리
        filename = f"{clean_filename(song_title)}.csv"
        filepath = csv_dir / filename
        
        # DataFrame 생성
        df = pd.DataFrame([{
            'song_id': f"youtube_{result.get('artist_name', '')}_{song_title}".lower().replace(' ', '_'),
            'song_title': song_title,
            'artist_name': result.get('artist_name'),
            'views': result.get('views', 0),
            'crawl_date': result.get('crawl_date')
        }])
        
        # 기존 파일이 있으면 누적
        if filepath.exists():
            try:
                old_df = pd.read_csv(filepath)
                combined_df = pd.concat([old_df, df], ignore_index=True)
            except Exception as e:
                logger.error(f"❌ 기존 CSV 읽기 실패: {filepath} - {e}")
                combined_df = df
        else:
            combined_df = df
        
        # 날짜순 정렬 후 저장
        combined_df = combined_df.sort_values(by="crawl_date", ascending=False)
        combined_df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        saved_files.append(str(filepath))
        logger.info(f"✅ CSV 파일 저장 완료: {filepath}")
    
    return saved_files

def save_melon_csv(results, company_name="rhoonart"):
    """
    Melon 크롤링 결과를 CSV로 저장
    
    Args:
        results (list): 크롤링 결과 리스트
        company_name (str): 회사명
        
    Returns:
        list: 저장된 파일 경로 리스트
    """
    if not results:
        return []
    
    csv_dir = _create_directory(company_name, 'melon')
    saved_files = []
    
    for result in results:
        song_title = result.get('song_title', 'unknown')
        
        # 파일명 정리
        filename = f"{clean_filename(song_title)}.csv"
        filepath = csv_dir / filename
        
        # DataFrame 생성
        df = pd.DataFrame([{
            'song_id': f"melon_{result.get('artist_name', '')}_{song_title}".lower().replace(' ', '_'),
            'song_title': song_title,
            'artist_name': result.get('artist_name'),
            'views': result.get('views', 0),
            'listeners': result.get('listeners', 0),
            'melon_song_id': result.get('melon_song_id', ''),
            'crawl_date': result.get('crawl_date')
        }])
        
        # 기존 파일이 있으면 누적
        if filepath.exists():
            try:
                old_df = pd.read_csv(filepath)
                combined_df = pd.concat([old_df, df], ignore_index=True)
            except Exception as e:
                logger.error(f"❌ 기존 CSV 읽기 실패: {filepath} - {e}")
                combined_df = df
        else:
            combined_df = df
        
        # 날짜순 정렬 후 저장
        combined_df = combined_df.sort_values(by="crawl_date", ascending=False)
        combined_df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        saved_files.append(str(filepath))
        logger.info(f"✅ CSV 파일 저장 완료: {filepath}")
    
    return saved_files 