"""
곡 정보 매칭 로직
"""
import logging
from .utils import normalize_text

logger = logging.getLogger(__name__)

# 키워드 유사도 매칭 임계값 (기본 30%)
KEYWORD_SIMILARITY_THRESHOLD = 0.3

def compare_song_info(song_title, artist_name, target_song_title, target_artist_name):
    """
    곡 정보 비교 메인 함수
    
    Args:
        song_title (str): 추출된 곡명
        artist_name (str): 추출된 아티스트명
        target_song_title (str): 검색한 곡명
        target_artist_name (str): 검색한 아티스트명
        
    Returns:
        dict: 비교 결과를 담은 딕셔너리
            {
                'title_match': bool,
                'artist_match': bool,
                'both_match': bool,
                'match_type': str,  # 'exact_partial', 'keyword_similarity', 'none'
                'normalized_song': str,
                'normalized_target_song': str,
                'normalized_artist': str,
                'normalized_target_artist': str
            }
    """
    # 공백 제거 정규화
    def normalize_no_space(text):
        """공백을 제거한 정규화"""
        normalized = normalize_text(text)
        return normalized.replace(' ', '') if normalized else ''
    
    # 공백 포함 정규화 (키워드 추출용)
    normalized_song_with_space = normalize_text(song_title)
    normalized_target_song_with_space = normalize_text(target_song_title)
    normalized_artist_with_space = normalize_text(artist_name)
    normalized_target_artist_with_space = normalize_text(target_artist_name)
    
    # 공백 제거 정규화 (문자열 매칭용)
    normalized_song = normalize_no_space(song_title)
    normalized_target_song = normalize_no_space(target_song_title)
    normalized_artist = normalize_no_space(artist_name)
    normalized_target_artist = normalize_no_space(target_artist_name)
    
    # 1단계: 정확 매칭 + 부분 매칭
    title_match_1, artist_match_1 = exact_and_partial_match(
        normalized_song, normalized_target_song,
        normalized_artist, normalized_target_artist
    )
    
    # 최종 매칭 결과 초기화
    title_match = title_match_1
    artist_match = artist_match_1
    match_type = 'exact_partial'
    
    # 2단계: 키워드 유사도 매칭 (실패한 부분만)
    if not title_match_1 or not artist_match_1:
        logger.debug("정확/부분 매칭에서 일부 실패, 키워드 유사도 매칭 시도")
        title_match_2, artist_match_2 = keyword_similarity_match(
            normalized_song_with_space, normalized_target_song_with_space,
            normalized_artist_with_space, normalized_target_artist_with_space
        )
        
        # 1단계에서 실패한 부분을 2단계 결과로 보완
        if not title_match_1 and title_match_2:
            title_match = True
            match_type = 'mixed'
        if not artist_match_1 and artist_match_2:
            artist_match = True
            match_type = 'mixed'
        
        # 둘 다 2단계에서 성공한 경우
        if title_match_2 and artist_match_2:
            match_type = 'keyword_similarity'
    
    both_match = title_match and artist_match
    
    logger.debug(f"곡명 매칭: '{song_title}' → '{normalized_song}' vs '{target_song_title}' → '{normalized_target_song}' = {title_match}")
    logger.debug(f"아티스트 매칭: '{artist_name}' → '{normalized_artist}' vs '{target_artist_name}' → '{normalized_target_artist}' = {artist_match}")
    logger.debug(f"전체 매칭: {both_match} (타입: {match_type})")
    
    return {
        'title_match': title_match,
        'artist_match': artist_match,
        'both_match': both_match,
        'match_type': match_type,
        'normalized_song': normalized_song,
        'normalized_target_song': normalized_target_song,
        'normalized_artist': normalized_artist,
        'normalized_target_artist': normalized_target_artist
    }

def exact_and_partial_match(normalized_song, normalized_target_song, normalized_artist, normalized_target_artist):
    """
    정확 매칭 + 부분 매칭
    
    Args:
        normalized_song (str): 정규화된 곡명
        normalized_target_song (str): 정규화된 검색 곡명
        normalized_artist (str): 정규화된 아티스트명
        normalized_target_artist (str): 정규화된 검색 아티스트명
        
    Returns:
        tuple: (title_match, artist_match)
    """
    # 곡명 매칭: 정확히 일치하거나 한쪽이 다른 쪽에 포함
    title_match = (
        normalized_song == normalized_target_song or  # 정확 매칭
        (len(normalized_song) >= 3 and normalized_song in normalized_target_song) or  # 부분 매칭
        (len(normalized_target_song) >= 3 and normalized_target_song in normalized_song)
    )
    
    # 아티스트명 매칭: 더 유연한 매칭
    artist_match = _match_artist_names(normalized_artist, normalized_target_artist)
    
    logger.debug(f"정확/부분 매칭: 곡명={title_match}, 아티스트={artist_match}")
    logger.debug(f"  곡명: '{normalized_song}' vs '{normalized_target_song}'")
    logger.debug(f"  아티스트: '{normalized_artist}' vs '{normalized_target_artist}'")
    return title_match, artist_match

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

def keyword_similarity_match(normalized_song, normalized_target_song, normalized_artist, normalized_target_artist):
    """
    키워드 유사도 매칭
    
    Args:
        normalized_song (str): 정규화된 곡명 (공백 포함)
        normalized_target_song (str): 정규화된 검색 곡명 (공백 포함)
        normalized_artist (str): 정규화된 아티스트명 (공백 포함)
        normalized_target_artist (str): 정규화된 검색 아티스트명 (공백 포함)
        
    Returns:
        tuple: (title_match, artist_match)
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
    song_keywords = get_keywords(normalized_song)
    target_song_keywords = get_keywords(normalized_target_song)
    artist_keywords = get_keywords(normalized_artist)
    target_artist_keywords = get_keywords(normalized_target_artist)
    
    # 유사도 계산
    title_similarity = calculate_similarity(song_keywords, target_song_keywords)
    artist_similarity = calculate_similarity(artist_keywords, target_artist_keywords)
    
    # 임계값 이상이면 매칭 성공
    title_match = title_similarity >= KEYWORD_SIMILARITY_THRESHOLD
    artist_match = artist_similarity >= KEYWORD_SIMILARITY_THRESHOLD
    
    logger.debug(f"키워드 유사도 매칭:")
    logger.debug(f"  곡명: '{normalized_song}' vs '{normalized_target_song}'")
    logger.debug(f"  키워드: {song_keywords} vs {target_song_keywords}")
    logger.debug(f"  유사도: {title_similarity:.2f} → {title_match}")
    logger.debug(f"  아티스트: '{normalized_artist}' vs '{normalized_target_artist}'")
    logger.debug(f"  키워드: {artist_keywords} vs {target_artist_keywords}")
    logger.debug(f"  유사도: {artist_similarity:.2f} → {artist_match}")
    
    return title_match, artist_match 