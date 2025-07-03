import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from crawling_view.youtube.youtube_main import run_youtube_crawling

if __name__ == "__main__":
    # 아티스트별 URL 리스트
    artist_urls_dict = {
        "Jaerium": [
            "https://www.youtube.com/watch?v=Sv2mIvMwrSY",
            "https://www.youtube.com/watch?v=R1CZTJ8hW0s",
            "https://www.youtube.com/watch?v=T4gsXNcF4Z0",
            "https://www.youtube.com/watch?v=-VQx4dePV5I",
            "https://www.youtube.com/watch?v=ecTQx5JNZBA",
        ],
        "anonatsue": [
            "https://www.youtube.com/watch?v=NiTwT05VgPA",
            "https://www.youtube.com/watch?v=nZpOGr1C8es",
            "https://www.youtube.com/watch?v=xpSJnLMCRxc",
            "https://www.youtube.com/watch?v=6hhhleiuaJA",
            "https://www.youtube.com/watch?v=jKY7pm7xlLk",
        ]
    }

    # [('url', 'artist_name')] 형태로 변환
    url_artist_list = [
        (url, artist)
        for artist, urls in artist_urls_dict.items()
        for url in urls
    ]

    # YouTube 크롤링 실행
    print(f"🖤 YouTube 크롤링 시작 - 총 {len(url_artist_list)}개 URL")
    results = run_youtube_crawling(url_artist_list, save_csv=True, save_db=True)
    
    print(f"\n🖤 YouTube 크롤링 완료 - 성공: {len(results)}개")
    for song_id, result in results.items():
        print(f"[YouTube] 곡명: {result['song_name']}, 아티스트: {result['artist_name']}, "
              f"조회수: {result['view_count']}, 업로드일: {result['upload_date']}, "
              f"URL: {result['youtube_url']}") 