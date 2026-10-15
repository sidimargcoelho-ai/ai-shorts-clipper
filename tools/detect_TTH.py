import sys
sys.path.insert(0, "D:\\Shorts")
import json
from pathlib import Path
from src.highlighter import HighlightDetector

with open("inputs/TTH_eWH8IK0.transcript.json", "r", encoding="utf-8") as f:
    transcript = json.load(f)

det = HighlightDetector(min_duration=30, max_duration=65, target_duration=45)
clips = det.detect_highlights(transcript, max_clips=5)

with open("inputs/curated_TTH.json", "w", encoding="utf-8") as f:
    json.dump([{"title": f"Corte{i+1}", "start": c["start"], "end": c["end"],
                "duration": c["duration"], "score": c["score"],
                "description": c["title"], "text": c["text"][:200]} for i, c in enumerate(clips)], f, indent=2, ensure_ascii=False)

for i, c in enumerate(clips, 1):
    print(f"{i}. [{c['start']:.1f}s -> {c['end']:.1f}s] ({c['duration']:.1f}s) Score:{c['score']}")
    print(f"   {c['title']}")
