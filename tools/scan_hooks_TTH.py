import sys
sys.path.insert(0, "D:\\Shorts")
import json
from src.highlighter import HOOK_KEYWORDS

with open("inputs/TTH_eWH8IK0.transcript.json", "r", encoding="utf-8") as f:
    transcript = json.load(f)

segs = transcript.get("segments", [])
print(f"Total segmentos: {len(segs)}, duracao: {transcript.get('duration')}")

# Mostrar trechos com keywords fortes
for i, s in enumerate(segs):
    txt = s["text"].lower()
    hits = [k for k in HOOK_KEYWORDS if k in txt]
    if hits and len(s["text"]) > 40:
        print(f"[{s['start']:.0f}s] ({', '.join(hits)}) {s['text'][:100]}")
