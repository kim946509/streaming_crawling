"""
크롤링에서 사용하는 공통 유틸리티 함수들
"""
import re
import unicodedata
from datetime import datetime
from bs4 import BeautifulSoup
from .constants import CommonSettings, INVALID_FILENAME_CHARS
import logging

logger = logging.getLogger(__name__)

def normalize_text(text):
    """특수문자와 공백을 정규화"""
    if not text:
        return ''
    
    # 유니코드 정규화
    text = unicodedata.normalize('NFKC', text)
    
    # 다양한 아포스트로피를 표준 아포스트로피로 통일
    text = text.replace('\u2018', "'").replace('\u2019', "'").replace('\u0060', "'").replace('\u00B4', "'")
    
    # 공백 정규화 및 소문자 변환
    return ' '.join(text.lower().split())

def normalize_song_name(text):
    """Genie 전용 곡명 정규화"""
    return re.sub(r'[\W_]+', '', text).lower() if text else ''

def clean_filename(filename):
    """파일명에 사용할 수 없는 문자 제거"""
    if not filename:
        return 'unknown'
    
    # 특수문자 제거 및 공백을 언더바로 변환
    clean_name = re.sub(INVALID_FILENAME_CHARS, '', filename)
    clean_name = clean_name.replace(' ', '_')
    
    return clean_name if clean_name else 'unknown'

def make_soup(html):
    """HTML을 BeautifulSoup 객체로 변환"""
    if not html:
        return None
    return BeautifulSoup(html, 'html.parser')

def parse_date(date_text):
    """날짜 텍스트를 표준 형식으로 변환"""
    if not date_text:
        return None
    
    # "YYYY. MM. DD." 또는 "YYYY.MM.DD" 형식을 "YYYY.MM.DD" 형식으로 변환
    date_match = re.search(r'(\d{4})[.\-\/\s]*(\d{1,2})[.\-\/\s]*(\d{1,2})', date_text)
    if date_match:
        year, month, day = date_match.groups()
        return f"{year}.{int(month):02d}.{int(day):02d}"
    
    return date_text.strip()

def get_current_timestamp():
    """현재 시간을 표준 형식으로 반환"""
    return datetime.now().strftime(CommonSettings.DATE_FORMAT)

def convert_view_count(view_count_text):
    """
    조회수 텍스트를 숫자로 변환
    예: "1.5만 회" -> 15000, "2.3천 회" -> 2300, "1,234회" -> 1234, "9회" -> 9
    """
    if not view_count_text:
        return None
        
    # 쉼표, "조회수", "회" 제거
    view_count_text = view_count_text.replace(',', '').replace('조회수', '').replace('회', '').strip()
    
    try:
        # "만" 단위 처리
        if '만' in view_count_text:
            number = float(view_count_text.replace('만', ''))
            return int(number * 10000)
        # "천" 단위 처리
        elif '천' in view_count_text:
            number = float(view_count_text.replace('천', ''))
            return int(number * 1000)
        # 일반 숫자 처리
        else:
            return int(view_count_text)
    except (ValueError, TypeError):
        logger.error(f"조회수 변환 실패: {view_count_text}")
        return None

def find_with_selectors(soup, selectors, get_text=True):
    """
    여러 selector를 순차적으로 시도하여 첫 번째로 찾은 element(또는 text)를 반환
    """
    if not soup:
        return None
        
    for selector in selectors:
        if isinstance(selector, dict):
            if selector.get('type') == 'css':
                el = soup.select_one(selector['value'])
            elif selector.get('type') == 'tag_class':
                el = soup.find(selector['tag'], class_=selector['class'])
            elif selector.get('type') == 'tag_id':
                el = soup.find(selector['tag'], id=selector['id'])
            else:
                continue
        else:
            # 문자열인 경우 CSS 셀렉터로 처리
            el = soup.select_one(selector)
            
        if el:
            return el.text.strip() if get_text else el
    return None 