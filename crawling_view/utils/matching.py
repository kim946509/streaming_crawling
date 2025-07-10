"""
문자열 매칭 관련 유틸리티
"""
import logging
from difflib import SequenceMatcher
from .utils import normalize_text

logger = logging.getLogger(__name__)

# 키워드 유사도 매칭 임계값 (기본 30%)
KEYWORD_SIMILARITY_THRESHOLD = 0.3

def compare_song_info(found_title, found_artist, target_info):
    """
    검색된 곡 정보와 목표 곡 정보를 비교
    
    Args:
        found_title (str): 검색된 곡 제목
        found_artist (str): 검색된 아티스트명
        target_info (dict): 목표 곡 정보 (title_ko, title_en, artist_ko, artist_en)
        
    Returns:
        dict: 매칭 결과
    """
    # 공백 제거 정규화
    def normalize_no_space(text):
        """공백을 제거한 정규화"""
        normalized = normalize_text(text)
        return normalized.replace(' ', '') if normalized else ''
    
    # 정규화
    found_title = normalize_text(found_title)
    found_artist = normalize_text(found_artist)
    found_title_no_space = normalize_no_space(found_title)
    found_artist_no_space = normalize_no_space(found_artist)
    
    target_title_ko = normalize_text(target_info['title_ko'])
    target_title_en = normalize_text(target_info['title_en'])
    target_artist_ko = normalize_text(target_info['artist_ko'])
    target_artist_en = normalize_text(target_info['artist_en'])
    
    target_title_ko_no_space = normalize_no_space(target_title_ko)
    target_title_en_no_space = normalize_no_space(target_title_en)
    target_artist_ko_no_space = normalize_no_space(target_artist_ko)
    target_artist_en_no_space = normalize_no_space(target_artist_en)
    
    # 1단계: 정확 매칭 + 부분 매칭
    title_match_exact, artist_match_exact = exact_and_partial_match(
        found_title_no_space,
        [target_title_ko_no_space, target_title_en_no_space],
        found_artist_no_space,
        [target_artist_ko_no_space, target_artist_en_no_space]
    )
    
    # 2단계: 키워드 유사도 매칭 (실패한 부분만)
    title_match_keyword = False
    artist_match_keyword = False
    if not title_match_exact or not artist_match_exact:
        title_match_keyword, artist_match_keyword = keyword_similarity_match(
            found_title,
            [target_title_ko, target_title_en],
            found_artist,
            [target_artist_ko, target_artist_en]
        )
    
    # 3단계: 유사도 매칭
    title_ko_ratio = SequenceMatcher(None, found_title, target_title_ko).ratio()
    title_en_ratio = SequenceMatcher(None, found_title, target_title_en).ratio()
    artist_ko_ratio = SequenceMatcher(None, found_artist, target_artist_ko).ratio()
    artist_en_ratio = SequenceMatcher(None, found_artist, target_artist_en).ratio()
    
    title_match_ratio = title_ko_ratio > 0.8 or title_en_ratio > 0.8
    artist_match_ratio = artist_ko_ratio > 0.8 or artist_en_ratio > 0.8
    
    # 최종 매칭 결과
    title_match = title_match_exact or title_match_keyword or title_match_ratio
    artist_match = artist_match_exact or artist_match_keyword or artist_match_ratio
    
    # 매칭 타입 결정
    if title_match_exact and artist_match_exact:
        match_type = 'exact_partial'
    elif title_match_keyword and artist_match_keyword:
        match_type = 'keyword_similarity'
    elif title_match_ratio and artist_match_ratio:
        match_type = 'ratio'
    elif title_match and artist_match:
        match_type = 'mixed'
    else:
        match_type = 'none'
    
    # 매칭 상세 정보
    match_details = {
        'title_match': title_match,
        'artist_match': artist_match,
        'both_match': title_match and artist_match,
        'match_type': match_type,
        'details': {
            'exact': {
                'title': title_match_exact,
                'artist': artist_match_exact
            },
            'keyword': {
                'title': title_match_keyword,
                'artist': artist_match_keyword
            },
            'ratio': {
                'title_ko': title_ko_ratio,
                'title_en': title_en_ratio,
                'artist_ko': artist_ko_ratio,
                'artist_en': artist_en_ratio
            }
        }
    }
    
    logger.debug(f"매칭 상세 정보: {match_details}")
    return match_details

def exact_and_partial_match(found_text, target_texts, found_artist, target_artists):
    """
    정확 매칭 + 부분 매칭
    
    Args:
        found_text (str): 찾은 텍스트
        target_texts (list): 목표 텍스트 리스트 [국문, 영문]
        found_artist (str): 찾은 아티스트
        target_artists (list): 목표 아티스트 리스트 [국문, 영문]
        
    Returns:
        tuple: (text_match, artist_match)
    """
    # 텍스트 매칭: 정확히 일치하거나 한쪽이 다른 쪽에 포함
    text_match = any(
        found_text == target or
        (len(found_text) >= 3 and found_text in target) or
        (len(target) >= 3 and target in found_text)
        for target in target_texts if target
    )
    
    # 아티스트 매칭: 더 유연한 매칭
    artist_match = any(
        _match_artist_names(found_artist, target)
        for target in target_artists if target
    )
    
    logger.debug(f"정확/부분 매칭: 텍스트={text_match}, 아티스트={artist_match}")
    return text_match, artist_match

def _match_artist_names(artist1, artist2):
    """
    아티스트명 매칭 (단순한 방식)
    
    Args:
        artist1 (str): 첫 번째 아티스트명
        artist2 (str): 두 번째 아티스트명
        
    Returns:
        bool: 매칭 성공 여부
    """
    # 1. 정확 매칭
    if artist1 == artist2:
        return True
    
    # 2. 부분 문자열 매칭
    if (len(artist1) >= 2 and artist1 in artist2) or (len(artist2) >= 2 and artist2 in artist1):
        return True
    
    return False

def keyword_similarity_match(found_text, target_texts, found_artist, target_artists):
    """
    키워드 유사도 매칭
    
    Args:
        found_text (str): 찾은 텍스트 (공백 포함)
        target_texts (list): 목표 텍스트 리스트 [국문, 영문] (공백 포함)
        found_artist (str): 찾은 아티스트 (공백 포함)
        target_artists (list): 목표 아티스트 리스트 [국문, 영문] (공백 포함)
        
    Returns:
        tuple: (text_match, artist_match)
    """
    def get_keywords(text):
        """텍스트에서 주요 키워드 추출 (2글자 이상의 단어들)"""
        if not text:
            return set()
        words = text.split()
        return {word for word in words if len(word) >= 2}
    
    def calculate_similarity(keywords1, keywords2):
        """키워드 유사도 계산 (자카드 유사도)"""
        if not keywords1 or not keywords2:
            return 0.0
        
        common_keywords = keywords1 & keywords2
        total_keywords = keywords1 | keywords2
        
        if not total_keywords:
            return 0.0
        
        return len(common_keywords) / len(total_keywords)
    
    # 키워드 추출
    found_text_keywords = get_keywords(found_text)
    found_artist_keywords = get_keywords(found_artist)
    
    # 각 언어별로 유사도 계산하여 가장 높은 값 사용
    text_similarities = [
        calculate_similarity(found_text_keywords, get_keywords(target))
        for target in target_texts if target
    ]
    artist_similarities = [
        calculate_similarity(found_artist_keywords, get_keywords(target))
        for target in target_artists if target
    ]
    
    text_similarity = max(text_similarities) if text_similarities else 0.0
    artist_similarity = max(artist_similarities) if artist_similarities else 0.0
    
    # 임계값 이상이면 매칭 성공
    text_match = text_similarity >= KEYWORD_SIMILARITY_THRESHOLD
    artist_match = artist_similarity >= KEYWORD_SIMILARITY_THRESHOLD
    
    logger.debug(f"키워드 유사도 매칭:")
    logger.debug(f"  텍스트 유사도: {text_similarity:.2f} → {text_match}")
    logger.debug(f"  아티스트 유사도: {artist_similarity:.2f} → {artist_match}")
    
    return text_match, artist_match 

def compare_song_info_multilang(found_title, found_artist, target_info):
    """
    국문/영문 조합을 모두 시도하여 하나라도 매칭되면 True 반환
    Args:
        found_title (str): 검색된 곡 제목
        found_artist (str): 검색된 아티스트명
        target_info (dict): {'title_ko', 'title_en', 'artist_ko', 'artist_en'}
    Returns:
        dict: 매칭 결과 (기존 compare_song_info 결과 + 어떤 조합에서 매칭됐는지)
    """
    results = []
    combos = [
        (target_info['title_ko'], target_info['artist_ko'], 'ko/ko'),
        (target_info['title_en'], target_info['artist_en'], 'en/en'),
        (target_info['title_ko'], target_info['artist_en'], 'ko/en'),
        (target_info['title_en'], target_info['artist_ko'], 'en/ko'),
    ]
    for tgt_title, tgt_artist, combo in combos:
        result = compare_song_info(found_title, found_artist, {
            'title_ko': tgt_title,
            'title_en': tgt_title,
            'artist_ko': tgt_artist,
            'artist_en': tgt_artist
        })
        result['combo'] = combo
        results.append(result)
        if result['both_match']:
            result['matched_combo'] = combo
            return result
    # 모두 실패 시 마지막 결과 반환
    results[-1]['matched_combo'] = None
    return results[-1] 