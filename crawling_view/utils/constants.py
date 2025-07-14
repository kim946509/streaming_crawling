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
        'button[aria-label="검색"]',
        'button[aria-label="Search"]',  # 영어 aria-label
        'button[aria-label*="검색"]',  # 검색이 포함된 aria-label
        'button[aria-label*="Search"]',  # Search가 포함된 aria-label
        'yt-icon-button.search-button',  # 검색 버튼 클래스
        # 'button#button.style-scope.yt-icon-button[aria-label="검색 시작"]',  # 전체 클래스 포함
        # 'button#button.style-scope.yt-icon-button[aria-label="Search"]',  # 영어 버전
        # 'yt-icon-button[title="검색 시작"]',  # 타이틀로 검색
        # 'yt-icon-button[title="Search"]',  # 영어 타이틀
        # 'button.style-scope.yt-icon-button',  # 일반적인 yt-icon-button
        # 'yt-icon-button[aria-label]',  # aria-label이 있는 모든 yt-icon-button
        # 'button[aria-label]',  # aria-label이 있는 모든 button
        # 'yt-icon-button',  # 모든 yt-icon-button (마지막 fallback)
        # 'button#button'  # 모든 button#button (최후의 fallback)
    ]
    SEARCH_INPUT = [
        'input[aria-autocomplete="list"]',       # aria-autocomplete list인 input
        'input#input',
        'input[aria-label="검색"]',
        'input[aria-label="Search"]',  # 영어 aria-label
        'input[aria-label*="검색"]',  # 검색이 포함된 aria-label
        'input[aria-label*="Search"]',  # Search가 포함된 aria-label
        # 'span#placeholder[aria-hidden="true"]',  # 새로운 검색 placeholder
        # 'span.style-scope.ytmusic-search-box',   # 검색 박스 스타일 클래스
        # 'ytmusic-search-box input',              # YouTube Music 검색 박스 내부 input
        # 'ytmusic-search-box span',               # YouTube Music 검색 박스 내부 span
        # 'input#input[autocomplete="off"]',       # autocomplete off인 input
        # 'input[aria-controls="suggestion-list"]', # suggestion-list 컨트롤하는 input
        # 'input[role="combobox"]',                # combobox 역할의 input
        # 'input.style-scope.ytmusic-search-box',  # ytmusic-search-box 스타일 클래스 input
        # 'input[type="search"]',                  # search 타입 input
        # 'input[placeholder*="검색"]',            # 검색이 포함된 placeholder
        # 'input[placeholder*="Search"]',          # Search가 포함된 placeholder
        # 'input[placeholder]',                    # placeholder가 있는 모든 input
        'input'                                  # 모든 input (최후의 fallback)
    ]
    SONG_TAB = [
        '//a[contains(@class, "yt-simple-endpoint") and .//yt-formatted-string[text()="노래"]]',   # 한글
        # 더 일반적인 셀렉터 추가
        '//a[contains(@class, "ytmusic-chip-cloud-chip-renderer") and @role="tab"]',  # role 속성 활용
        '//a[contains(@title, "노래") or contains(@title, "Songs")]',  # title 속성 활용
        '//a[contains(@class, "yt-simple-endpoint") and .//yt-formatted-string]',  # 어떤 텍스트든 상관없이
        '//a[contains(@class, "yt-simple-endpoint") and contains(@class, "style-scope") and contains(@class, "ytmusic-chip-cloud-chip-renderer")]',  # 세 클래스 모두 포함된 a 태그(노래탭)
        '//*[@id="header"]//a[1]',  # 헤더 내 첫 번째 a 태그(언어/텍스트 무관, 최우선)
        '//a[contains(@class, "yt-simple-endpoint") and .//yt-formatted-string[text()="Songs"]]',  # 영어
        '//a[contains(@class, "yt-simple-endpoint") and .//yt-formatted-string[text()="Song"]]',   # 영어 단수
        '//iron-selector[@id="chips"]//ytmusic-chip-cloud-chip-renderer//yt-formatted-string[text()="Songs"]/ancestor::a',  # 영어
        '//iron-selector[@id="chips"]//ytmusic-chip-cloud-chip-renderer//yt-formatted-string[text()="노래"]/ancestor::a',  # 한글
        '//iron-selector[@id="chips"]//ytmusic-chip-cloud-chip-renderer//a',  # 모든 탭 
        '//iron-selector[@id="chips"]//ytmusic-chip-cloud-chip-renderer//yt-formatted-string[contains(text(), "노래")]/ancestor::a',  # 한글 포함
        '//iron-selector[@id="chips"]//ytmusic-chip-cloud-chip-renderer//yt-formatted-string[contains(text(), "Songs")]/ancestor::a',  # 영어 포함
        '//iron-selector[@id="chips"]//ytmusic-chip-cloud-chip-renderer//a[contains(@aria-label, "노래")]',  # aria-label으로 한글
        '//iron-selector[@id="chips"]//ytmusic-chip-cloud-chip-renderer//a[contains(@aria-label, "Songs")]',  # aria-label으로 영어
        '//yt-formatted-string[@class="text style-scope ytmusic-chip-cloud-chip-renderer" and text()="노래"]/ancestor::a',  # 실제 HTML 구조 한글
        '//yt-formatted-string[@class="text style-scope ytmusic-chip-cloud-chip-renderer" and text()="Songs"]/ancestor::a',  # 실제 HTML 구조 영어
        '//yt-formatted-string[@class="text style-scope ytmusic-chip-cloud-chip-renderer" and contains(text(), "노래")]/ancestor::a',  # 실제 HTML 구조 한글 포함
        '//yt-formatted-string[@class="text style-scope ytmusic-chip-cloud-chip-renderer" and contains(text(), "Songs")]/ancestor::a',  # 실제 HTML 구조 영어 포함
    ]
    
    # 곡 정보 추출 관련
    SONG_ITEMS = [
        # 0. "노래" 섹션 컨테이너 내 곡만 추출 (최우선)
        'div#contents.style-scope.ytmusic-shelf-renderer > ytmusic-responsive-list-item-renderer',
        # 1. 가장 기본적인 구조 매칭
        'ytmusic-responsive-list-item-renderer[class*="style-scope"]',  # class에 style-scope가 포함된 모든 요소
        
        # 2. 필수 속성 조합으로 매칭
        'ytmusic-responsive-list-item-renderer[class*="style-scope"][has-thumbnail-overlay]',
        
        # 3. 내부 구조를 통한 매칭
        'ytmusic-responsive-list-item-renderer:has(.title-column)',  # title-column을 포함하는 요소
        'ytmusic-responsive-list-item-renderer:has(.secondary-flex-columns)',  # secondary-flex-columns을 포함하는 요소
        
        # 4. 복합 조건 매칭
        'ytmusic-responsive-list-item-renderer[class*="style-scope"]:has(.title-column):has(.secondary-flex-columns)',
        
        # 5. 특정 자식 요소를 통한 매칭
        'ytmusic-responsive-list-item-renderer:has(yt-formatted-string.title)',
        'ytmusic-responsive-list-item-renderer:has(ytmusic-thumbnail-renderer)',
        
        # 6. 동적 속성을 통한 매칭
        'ytmusic-responsive-list-item-renderer[stack-flex-columns]',
        'ytmusic-responsive-list-item-renderer[height-style="MUSIC_RESPONSIVE_LIST_ITEM_HEIGHT_TALL"]',
        
        # 7. 기존 셀렉터들 (fallback)
        'ytmusic-responsive-list-item-renderer.style-scope.ytmusic-shelf-renderer',
        'ytmusic-shelf-renderer ytmusic-responsive-list-item-renderer',
        'ytmusic-responsive-list-item-renderer',
        
        # 8. 부모 컨텍스트를 통한 매칭
        'ytmusic-shelf-renderer > ytmusic-responsive-list-item-renderer',
        'div.content-wrapper ytmusic-responsive-list-item-renderer',
        
        # 9. 재생 버튼 존재 여부를 통한 매칭
        'ytmusic-responsive-list-item-renderer:has(ytmusic-play-button-renderer)',
        
        # 10. 메뉴 버튼 존재 여부를 통한 매칭
        'ytmusic-responsive-list-item-renderer:has(ytmusic-menu-renderer)'
    ]
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

# 플랫폼 관련 상수
class Platforms:
    """지원하는 크롤링 플랫폼"""
    GENIE = 'genie'
    YOUTUBE_MUSIC = 'youtube_music'
    YOUTUBE = 'youtube'
    MELON = 'melon'
    
    # 전체 플랫폼 리스트
    ALL_PLATFORMS = [GENIE, YOUTUBE_MUSIC, YOUTUBE, MELON]
    
    # 플랫폼별 이름 매핑
    PLATFORM_NAMES = {
        GENIE: 'Genie',
        YOUTUBE_MUSIC: 'YouTube Music',
        YOUTUBE: 'YouTube',
        MELON: 'Melon'
    }

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
        # '--headless',  # 헤드리스 모드 (GUI 없이 실행)
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