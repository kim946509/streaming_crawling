"""
Chrome WebDriver 설정 및 관리
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

@contextmanager
def setup_driver(headless=False, incognito=True):
    """
    Chrome WebDriver 설정 및 생성
    
    Args:
        headless (bool): 헤드리스 모드 여부
        incognito (bool): 시크릿 모드 여부
    """
    options = Options()
    
    if headless:
        options.add_argument('--headless')
    
    # 기본 옵션들
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-notifications')
    options.add_argument('--lang=ko_KR')
    options.add_argument('--log-level=3')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    if incognito:
        options.add_argument('--incognito')
    
    # 자동화 탐지 방지
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # 자동화 탐지 방지 스크립트
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    logger.info("🟢 Chrome 브라우저 실행 완료")

    try:
        yield driver
    except Exception as e:
        logger.error(f"❌ Chrome 브라우저 실행 실패: {e}", exc_info=True)
        raise
    finally:
        driver.quit()
        logger.info("�� Chrome 브라우저 종료") 