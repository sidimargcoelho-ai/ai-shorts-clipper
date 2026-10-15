import sys
sys.path.insert(0, "D:\\Shorts")
import os, json, subprocess
from pathlib import Path
import yaml

YOUTUBE_URL = "https://www.youtube.com/watch?v=TTH_eWH8IK0"

with open("config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)
with open("inputs/TTH_eWH8IK0.transcript.json", "r", encoding="utf-8") as f:
    transcript = json.load(f)
with open("inputs/curated_TTH.json", "r", encoding="utf-8") as f:
    clips = json.load(f)

from src.tracker import FaceTracker
from src.subtitle import SubtitleGenerator
from src.renderer import VideoRenderer

sections_dir = Path("inputs/sections")
output_dir = Path("output")
sections_dir.mkdir(parents=True, exist_ok=True)
output_dir.mkdir(parents=True, exist_ok=True)

def download_section(url, start_sec, end_sec, out_path):
    if out_path.exists() and out_path.stat().st_size > 100000:
        print(f"  [Cache] {out_path.name}")
        return out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sec_arg = f"*{int(start_sec)}-{int(end_sec)+1}"
    print(f"  [Download] secao {sec_arg}...")
    cmd = [sys.executable, "-m", "yt_dlp", "--download-sections", sec_arg,
           "-f", "bestvideo[vcodec^=avc1]+bestaudio/best",
           "--force-keyframes-at-cuts", "-o", str(out_path), url]
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if res.returncode != 0 or not out_path.exists():
        raise RuntimeError(res.stderr.decode("utf-8", errors="ignore")[-300:])
    return out_path

tracker = FaceTracker(model_path="models/face_detector.tflite")
sub_gen = SubtitleGenerator(config)
renderer = VideoRenderer(config)

for idx, clip in enumerate(clips, 1):
    print(f"\n[{idx}/{len(clips)}] {clip['title']} ({clip['duration']}s)")
    out_short = output_dir / f"Short_TTH_{clip['title']}.mp4"
    if out_short.exists() and out_short.stat().st_size > 100000:
        print(f"  Pronto: {out_short.name}")
        continue
    section_file = sections_dir / f"TTH_{clip['title']}_raw.mp4"
    download_section(YOUTUBE_URL, clip["start"], clip["end"], section_file)
    crop_info = tracker.analyze_clip(section_file, 0.0, clip["duration"], mode="face_tracking")
    sub_file = output_dir / f"TTH_{clip['title']}.ass"
    sub_gen.generate_ass(transcript, clip["start"], clip["end"], sub_file)
    renderer.render_clip(section_file, 0.0, clip["duration"], crop_info["ffmpeg_crop_filter"], sub_file, out_short)
    print(f"  OK: {out_short.resolve()}")

print("\nFIM BATCH TTH")
