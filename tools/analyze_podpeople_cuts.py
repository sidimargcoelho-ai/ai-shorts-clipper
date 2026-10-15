import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

with open("inputs/i-aKQL09x1A.transcript.json", "r", encoding="utf-8") as f:
    data = json.load(f)

segments = data["segments"]
print(f"Total de segmentos transcritos: {len(segments)}")

# Amostrar a cada 3 minutos para mapear o episódio inteiro
block_size = 180 # 3 minutos
block_texts = {}

for seg in segments:
    b_idx = int(seg["start"] // block_size)
    if b_idx not in block_texts:
        block_texts[b_idx] = []
    block_texts[b_idx].append(seg["text"])

print("\n--- MAPA TEMÁTICO DO EPISÓDIO (Blocos de 3 min) ---")
for b_idx in sorted(block_texts.keys()):
    t_min = (b_idx * block_size) / 60
    sample = " ".join(block_texts[b_idx])[:150]
    print(f"[{t_min:5.1f} min] {sample}...")
