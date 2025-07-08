"""
크롤링에서 사용하는 상수 정의
"""

# Genie 관련 셀렉터
class GenieSelectors:
    # 검색 관련
    SEARCH_INPUT = [
        "input[type='search']",
        "input.searchField",
        "#keyword"
    ]
    SEARCH_BUTTON = "button[type='submit']"
    
    # 곡 정보 관련 (실제 동작하는 셀렉터)
    SONG_INFO_BUTTON = 'a.btn-basic.btn-info[onclick^="fnViewSongInfo"]'
    SONG_TITLE = 'h2.name'  # 곡 정보 페이지의 곡명
    
    # 아티스트명 추출 selector 리스트
    ARTIST_SELECTORS = [
        'a[onclick^="fnGoMore(\'artistInfo\'"]',  # 아티스트 정보 링크
        'div.info-zone p.artist a',  # 곡 정보 페이지의 아티스트 링크
        'div.info-zone p.artist',    # 곡 정보 페이지의 아티스트 텍스트
        'p.artist a',                # 일반적인 아티스트 링크
        'p.artist',                  # 일반적인 아티스트 텍스트
        'a.link__text'               # 기존 검색 결과 페이지의 아티스트 링크
    ]
    
    # 곡 정보 페이지 통계 관련
    TOTAL_STATS = '.daily-chart .total'  # 통계 정보 컨테이너
    TOTAL_STATS_PARAGRAPHS = 'div p'  # 통계 수치 (div 안의 p 태그)
    
    # 기존 검색 결과 관련 셀렉터들
    SONG_ITEMS = "tr.list__item"
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
        'yt-formatted-string#info span:first-child',  # 최신 구조: info id의 첫 번째 span
        'yt-formatted-string#info > span:first-child',  # info id의 직계 자식 첫 번째 span
        'yt-formatted-string#info > span', 
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
    RANDOM_DELAY_MIN = 1.2
    RANDOM_DELAY_MAX = 2
    
    # Chrome 드라이버 옵션
    CHROME_OPTIONS = [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-blink-features=AutomationControlled',
        '--window-size=1920,1080',
        '--disable-extensions',
        '--disable-popup-blocking',
        '--disable-notifications',
        '--lang=ko_KR',
        '--log-level=3',
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        '--incognito',  # 시크릿 모드로 실행 (캐시 무시)
        '--disable-application-cache',  # 애플리케이션 캐시 비활성화
        '--disable-cache',  # 캐시 비활성화
        '--disable-offline-load-stale-cache',  # 오프라인 캐시 비활성화
        '--disk-cache-size=0',  # 디스크 캐시 크기를 0으로 설정
        '--media-cache-size=0',  # 미디어 캐시 크기를 0으로 설정
        '--aggressive-cache-discard',  # 적극적인 캐시 삭제
        '--memory-pressure-off',  # 메모리 압박 해제
        '--max_old_space_size=4096',  # 메모리 제한 증가
        '--headless',  # 헤드리스 모드 (GUI 없이 실행)
        '--disable-web-security',  # 웹 보안 비활성화 (헤드리스에서 필요할 수 있음)
        '--allow-running-insecure-content',  # 안전하지 않은 콘텐츠 허용
        '--disable-features=VizDisplayCompositor'  # 디스플레이 컴포지터 비활성화
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
    GENIE_COLUMNS = ['song_id','artist_name','song_title','total_person_count', 'views', 'crawl_date']
    YOUTUBE_MUSIC_COLUMNS = ['song_id','artist_name','song_title','views', 'crawl_date']
    YOUTUBE_COLUMNS = ['song_id','artist_name','song_title','views', 'youtube_url', 'upload_date', 'crawl_date'] 