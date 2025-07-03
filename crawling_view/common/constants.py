"""
크롤링에서 사용하는 상수 정의
"""

# Genie 관련 셀렉터
class GenieSelectors:
    # 검색 관련
    SEARCH_INPUT = [
        'input#sc-fd',
        'input#input',
        'input[aria-label="검색"]'
    ]
    SONG_INFO_BUTTON = 'a.btn-basic.btn-info[onclick^="fnViewSongInfo"]'
    
    # 곡 정보 추출 관련
    SONG_TITLE = 'h2.name'
    ARTIST_INFO = 'ul.info-data li:nth-of-type(1) span.value'
    TOTAL_STATS = 'div.total'
    TOTAL_STATS_PARAGRAPHS = 'p'

# YouTube Music 관련 셀렉터
class YouTubeMusicSelectors:
    # 검색 관련
    SEARCH_BUTTON = [
        'button#button[aria-label="검색 시작"]', 
        'button[aria-label="검색"]'
    ]
    SEARCH_INPUT = [
        'input#input',
        'input[aria-label="검색"]'
    ]
    SONG_TAB = '//iron-selector[@id="chips"]//ytmusic-chip-cloud-chip-renderer//yt-formatted-string[text()="노래"]/ancestor::a'
    
    # 곡 정보 추출 관련
    SONG_ITEMS = 'ytmusic-shelf-renderer ytmusic-responsive-list-item-renderer'
    SONG_TITLE = 'yt-formatted-string.title a'
    ARTIST_COLUMN = '.secondary-flex-columns'
    ARTIST_LINK = 'a'
    VIEW_COUNT_FLEX = 'yt-formatted-string.flex-column'

# YouTube 관련 셀렉터
class YouTubeSelectors:
    TITLE_SELECTORS = [
        'h1.style-scope.ytd-watch-metadata',
        'h1.style-scope.ytd-watch-metadata > yt-formatted-string',
        'yt-formatted-string.style-scope.ytd-watch-metadata',
        'h1.title',
        'h1.ytd-watch-metadata',
        'h1#title'
    ]
    
    VIEW_COUNT_SELECTORS = [
        'span.view-count',
        'span#view-count',
        'div#count span.view-count',
        'div#info span.view-count',
        'span.ytd-video-view-count-renderer',
        'yt-view-count-renderer span.view-count'
    ]
    
    UPLOAD_DATE_SELECTORS = [
        'div#info-strings yt-formatted-string',
        'div#date yt-formatted-string',
        'span.date',
        'div#info-strings',
        'yt-formatted-string#info-strings'
    ]

# 공통 설정
class CommonSettings:
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    CSV_ENCODING = 'utf-8-sig'
    DEFAULT_WAIT_TIME = 10
    RANDOM_DELAY_MIN = 0.7
    RANDOM_DELAY_MAX = 1.5
    
# 파일명 정리용 정규식
INVALID_FILENAME_CHARS = r'[\\/:*?"<>|]'

# Genie 전용 설정
class GenieSettings:
    MAX_SEARCH_ATTEMPTS = 5
    MAX_PARSE_ATTEMPTS = 6
    BASE_URL = "https://www.genie.co.kr/" 