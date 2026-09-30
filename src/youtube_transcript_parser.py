import json
import re
from pathlib import Path
from typing import Dict, Any, List

def parse_json3_subs(json3_path: Path, output_json_path: Path) -> Dict[str, Any]:
    with open(json3_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    events = data.get("events", [])
    segments = []
    seg_id = 0
    full_text_list = []

    for event in events:
        segs = event.get("segs", [])
        if not segs:
            continue

        raw_event_text = "".join(s.get("utf8", "") for s in segs).strip()
        if not raw_event_text or raw_event_text == "\n":
            continue

        t_start_ms = event.get("tStartMs", 0)
        d_duration_ms = event.get("dDurationMs", 0)
        event_start_sec = t_start_ms / 1000.0
        event_end_sec = (t_start_ms + d_duration_ms) / 1000.0

        words = []
        seg_text_clean = []

        for idx, seg in enumerate(segs):
            word_str = seg.get("utf8", "").strip()
            word_str = word_str.replace(">>", "").strip()
            if not word_str:
                continue

            offset_ms = seg.get("tOffsetMs", 0)
            w_start = (t_start_ms + offset_ms) / 1000.0

            # Estimar fim da palavra com base no próximo segmento ou duração do evento
            if idx + 1 < len(segs) and "tOffsetMs" in segs[idx + 1]:
                next_offset = segs[idx + 1]["tOffsetMs"]
                w_end = (t_start_ms + next_offset) / 1000.0
            else:
                w_end = min(event_end_sec, w_start + 0.35)

            if w_end <= w_start:
                w_end = w_start + 0.25

            words.append({
                "word": word_str,
                "start": round(w_start, 3),
                "end": round(w_end, 3),
                "probability": 1.0
            })
            seg_text_clean.append(word_str)

        if words:
            clean_text = " ".join(seg_text_clean)
            segments.append({
                "id": seg_id,
                "start": words[0]["start"],
                "end": words[-1]["end"],
                "text": clean_text,
                "words": words
            })
            full_text_list.append(clean_text)
            seg_id += 1

    total_duration = segments[-1]["end"] if segments else 0.0

    result = {
        "language": "pt",
        "duration": round(total_duration, 2),
        "text": " ".join(full_text_list),
        "segments": segments
    }

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"[Parser] Transcrição convertida com sucesso: {len(segments)} segmentos ({total_duration/60:.1f} minutos).")
    return result

if __name__ == "__main__":
    parse_json3_subs(
        Path("inputs/podcast_subs.pt-orig.json3"),
        Path("inputs/o5T4QnQe5Os.transcript.json")
    )
