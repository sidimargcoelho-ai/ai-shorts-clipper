import sys
sys.path.insert(0, "D:\\Shorts")
import subprocess
from pathlib import Path

URL = "https://www.youtube.com/watch?v=TTH_eWH8IK0"
out = Path("inputs/TTH_full.mp4")
print(f"Baixando video completo 720p -> {out}", flush=True)
cmd = [sys.executable, "-m", "yt_dlp",
       "-f", "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]/best",
       "--merge-output-format", "mp4",
       "-o", str(out), URL]
res = subprocess.run(cmd)
print(f"Exit: {res.returncode}", flush=True)
