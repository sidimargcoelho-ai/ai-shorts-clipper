import yt_dlp
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

url = "https://www.youtube.com/watch?v=vbZquVH5bcs"

profiles = [
    ("firefox:zgjnoryb.default-release", {'cookiesfrombrowser': ('firefox:zgjnoryb.default-release',)}),
    ("firefox:cx9bopz2.default", {'cookiesfrombrowser': ('firefox:cx9bopz2.default',)}),
    ("web_creator", {'extractor_args': {'youtube': {'player_client': ['web_creator']}}}),
    ("web_safari", {'extractor_args': {'youtube': {'player_client': ['web_safari']}}}),
    ("tv_embedded", {'extractor_args': {'youtube': {'player_client': ['tv_embedded']}}}),
]

for name, opts in profiles:
    opts['quiet'] = True
    opts['no_warnings'] = True
    print(f"Testing {name}...")
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            print(f"SUCCESS with {name}! Title: {info.get('title')}")
            print(f"Duration: {info.get('duration')}s")
            break
    except Exception as e:
        print(f"Failed {name}: {str(e)[:100]}")
