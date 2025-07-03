# YouTube Music 로그인 정보
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

youtube_music_id = os.getenv('YOUTUBE_MUSIC_ID', 'kim946509@gmail.com')
youtube_music_password = os.getenv('YOUTUBE_MUSIC_PASSWORD', 'rlarlaeodus12') 