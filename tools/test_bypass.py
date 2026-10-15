import yt_dlp
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

url = "https://www.youtube.com/watch?v=vbZquVH5bcs"

test_configs = [
    ("android", {'extractor_args': {'youtube': {'player_client': ['android']}}}),
    ("ios", {'extractor_args': {'youtube': {'player_client': ['ios']}}}),
    ("tv", {'extractor_args': {'youtube': {'player_client': ['tv']}}}),
    ("mweb", {'extractor_args': {'youtube': {'player_client': ['mweb']}}}),
    ("firefox_cookies", {'cookiesfrombrowser': ('firefox',)}),
    ("edge_cookies", {'cookiesfrombrowser': ('edge',)}),
]

for name, opts in test_configs:
    opts['quiet'] = True
    opts['no_warnings'] = True
    print(f"Testing {name}...")
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            print(f"  SUCCESS with {name}!")
            print(f"  Title: {info.get('title')}")
            print(f"  Duration: {info.get('duration')}s")
            chapters = info.get('chapters') or []
            print(f"  Chapters: {len(chapters)}")
            for c in chapters[:5]:
                print(f"    - {c['title']} ({c['start_time']}s)")
            break
    except Exception as e:
        print(f"  Failed {name}: {str(e)[:80]}")
