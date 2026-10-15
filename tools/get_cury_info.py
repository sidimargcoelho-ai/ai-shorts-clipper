import yt_dlp
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

URL = "https://www.youtube.com/watch?v=vbZquVH5bcs"

ydl_opts = {'quiet': True, 'no_warnings': True}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(URL, download=False)

print("Title:", info.get("title"))
duration = info.get("duration", 0)
print(f"Duration: {duration}s ({duration/60:.1f} min)")

chapters = info.get("chapters") or []
print(f"Chapters found: {len(chapters)}")
for c in chapters:
    print(f"  [{c['start_time']:.0f}s - {c['end_time']:.0f}s] {c['title']}")

subtitles = info.get("subtitles") or {}
auto_subs = info.get("automatic_captions") or {}
print("Subtitles:", list(subtitles.keys()))
print("Auto captions:", [k for k in auto_subs.keys() if "pt" in k])
