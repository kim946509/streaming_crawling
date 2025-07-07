"""
Chrome WebDriver 설정 및 관리
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from contextlib import contextmanager
import logging
from .constants import CommonSettings

logger = logging.getLogger(__name__)

@contextmanager
def setup_driver(headless=True, incognito=True):
    """
    Chrome WebDriver 설정 및 생성
    
    Args:
        headless (bool): 헤드리스 모드 여부 (기본값: True - 서버 환경용)
        incognito (bool): 시크릿 모드 여부
    """
    options = Options()
    
    # constants.py에서 정의된 모든 Chrome 옵션 적용
    for option in CommonSettings.CHROME_OPTIONS:
        options.add_argument(option)
    
    # 헤드리스 모드가 False인 경우 headless 옵션 제거
    if not headless:
        # headless 옵션을 제거
        options.arguments = [arg for arg in options.arguments if arg != '--headless']
    
    # 시크릿 모드가 False인 경우 incognito 옵션 제거
    if not incognito:
        # incognito 옵션을 제거
        options.arguments = [arg for arg in options.arguments if arg != '--incognito']
    
    # 자동화 탐지 방지
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # 자동화 탐지 방지 스크립트
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    mode = "헤드리스" if headless else "GUI"
    logger.info(f"🟢 Chrome 브라우저 실행 완료 ({mode} 모드)")

    try:
        yield driver
    except Exception as e:
        logger.error(f"❌ Chrome 브라우저 실행 실패: {e}", exc_info=True)
        raise
    finally:
        driver.quit()
        logger.info("�� Chrome 브라우저 종료") 