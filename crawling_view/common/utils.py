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
    """
    텍스트 정규화 함수
    - 유니코드 정규화
    - 아포스트로피 통일
    - 공백 정규화 및 소문자 변환
    
    Args:
        text (str): 정규화할 텍스트
        
    Returns:
        str: 정규화된 텍스트
    """
    if not text:
        return ''
    
    # 유니코드 정규화 (아포스트로피, 따옴표 등을 통일)
    text = unicodedata.normalize('NFKC', text)
    
    # 모든 아포스트로피를 ' 로 통일
    text = text.replace('\u2018', "'").replace('\u2019', "'").replace('\u0060', "'").replace('\u00B4', "'")
    
    # 공백 정규화 및 소문자 변환
    return ' '.join(text.lower().split())

def clean_filename(filename):
    """
    파일명에 사용할 수 없는 문자를 제거하고 정리
    
    Args:
        filename (str): 정리할 파일명
        
    Returns:
        str: 정리된 파일명
    """
    if not filename:
        return 'unknown'
    
    # 파일명에 사용할 수 없는 문자 제거
    filename = re.sub(r'[\\/:*?"<>|]', '', filename)
    
    # 공백을 언더바로 변환
    filename = filename.replace(' ', '_')
    
    # 빈 문자열이면 기본값 반환
    if not filename:
        return 'unknown'
    
    return filename

def make_soup(html):
    """
    HTML 문자열을 BeautifulSoup 객체로 변환
    
    Args:
        html (str): HTML 문자열
        
    Returns:
        BeautifulSoup: BeautifulSoup 객체 또는 None
    """
    try:
        if not html:
            return None
        return BeautifulSoup(html, 'html.parser')
    except Exception as e:
        logger.error(f"❌ HTML 파싱 실패: {e}")
        return None

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
    """
    현재 시간을 '%Y-%m-%d %H:%M:%S' 형식으로 반환
    
    Returns:
        str: 현재 시간 문자열
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def convert_view_count(view_count_text):
    """
    조회수 텍스트를 숫자로 변환
    
    Args:
        view_count_text (str): 조회수 텍스트 (예: "1.5만 회", "2.3천 회", "1,234회")
        
    Returns:
        int: 변환된 숫자 또는 None
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
        logger.error(f"❌ 조회수 변환 실패: {view_count_text}")
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