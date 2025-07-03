"""
크롤링에서 사용하는 상수 정의
"""

# Genie 관련 셀렉터
class GenieSelectors:
    # 검색 관련
    SEARCH_INPUT = "input[type='search']"
    SEARCH_BUTTON = "button[type='submit']"
    SONG_ITEMS = "tr.list__item"
    SONG_TITLE = "a.link__text"
    ARTIST_NAME = "a.link__text"
    ARTIST_LINK = "td.info a.link__text"
    PLAY_COUNT = "span.count__text"
    PERSON_COUNT = "span.count__text"
    VIEW_COUNT_CONTAINER = "td.count"
    
    # 검색 결과 테이블 관련
    SEARCH_RESULTS_TABLE = "table.list-wrap"
    RESULT_ROWS = "tr.list__item"
    TITLE_COLUMN = "td.info"
    ARTIST_COLUMN = "td.info"
    COUNT_COLUMN = "td.count"

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
    
    # Chrome 드라이버 옵션
    CHROME_OPTIONS = [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-blink-features=AutomationControlled',
        '--window-size=1920,1080',
        '--start-maximized',
        '--disable-extensions',
        '--disable-popup-blocking',
        '--disable-notifications',
        '--lang=ko_KR',
        '--log-level=3',
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    
    CHROME_EXPERIMENTAL_OPTIONS = {
        "excludeSwitches": ["enable-automation"],
        "useAutomationExtension": False
    }

# 파일명 정리용 정규식
INVALID_FILENAME_CHARS = r'[\\/:*?"<>|]'

# Genie 전용 설정
class GenieSettings:
    MAX_SEARCH_ATTEMPTS = 5
    MAX_PARSE_ATTEMPTS = 6
    BASE_URL = "https://www.genie.co.kr/" 

class FilePaths:
    """파일 경로 상수"""
    CSV_BASE_DIR = "csv_folder"
    LOG_DIR = "logs"
    
    # CSV 파일 컬럼
    GENIE_COLUMNS = ['song_title', 'artist_name', 'total_person_count', 'total_play_count', 'crawl_date']
    YOUTUBE_MUSIC_COLUMNS = ['song_title', 'artist_name', 'view_count', 'crawl_date']
    YOUTUBE_COLUMNS = ['song_id', 'song_title', 'artist_name', 'view_count', 'youtube_url', 'upload_date', 'crawl_date'] 