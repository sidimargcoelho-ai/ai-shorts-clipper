import os
import sys
import json
import time
from pathlib import Path
import yaml

# Adicionar raiz ao PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.tracker import FaceTracker
from src.subtitle import SubtitleGenerator
from src.renderer import VideoRenderer

LOCAL_VIDEO = Path("inputs/podpeople_full.mp4")

def run_local_batch():
    print("=" * 60)
    print("🎬 RENDERIZANDO OS 15 SHORTS DA DRA. ANA BEATRIZ LOCALMENTE COM GPU NVENC")
    print("=" * 60)

    if not LOCAL_VIDEO.exists():
        raise FileNotFoundError(f"Vídeo base não encontrado: {LOCAL_VIDEO}")

    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    with open("inputs/i-aKQL09x1A.transcript.json", "r", encoding="utf-8") as f:
        transcript = json.load(f)

    with open("inputs/podpeople_curated_cuts.json", "r", encoding="utf-8") as f:
        clips = json.load(f)

    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    tracker = FaceTracker(model_path="models/face_detector.tflite")
    sub_gen = SubtitleGenerator(config)
    renderer = VideoRenderer(config)

    total = len(clips)
    finished_shorts = []

    for idx, clip in enumerate(clips, 1):
        print(f"\n[{idx}/{total}] 🎬 {clip['title']} ({clip['duration']}s)")
        print(f"     Tema: {clip['description']}")
        print(f"     Trecho: {clip['start']:.1f}s -> {clip['end']:.1f}s")

        out_short = output_dir / f"Short_PodPeople_{clip['title']}.mp4"
        if out_short.exists() and out_short.stat().st_size > 1000000:
            print(f"  ✨ [Pronto] Short já renderizado com sucesso: {out_short.name}")
            finished_shorts.append({
                "title": clip["title"],
                "theme": clip["description"],
                "file": str(out_short.resolve()),
                "duration": clip["duration"]
            })
            continue

        # 1. Rastreamento facial em 9:16
        print("  [Tracker] Analisando enquadramento com MediaPipe...")
        crop_info = tracker.analyze_clip(LOCAL_VIDEO, clip["start"], clip["end"], mode="face_tracking")

        # 2. Legendas animadas em .ass
        sub_file = output_dir / f"PodPeople_{clip['title']}.ass"
        print("  [Subtitle] Gerando legendas dinâmicas TikTok/Hormozi...")
        sub_gen.generate_ass(transcript, clip["start"], clip["end"], sub_file)

        # 3. Renderização acelerada por GPU
        print(f"  [Renderer] Renderizando corte em 9:16 com GTX 1650...")
        renderer.render_clip(
            video_path=LOCAL_VIDEO,
            start_time=clip["start"],
            end_time=clip["end"],
            crop_filter=crop_info["ffmpeg_crop_filter"],
            subtitle_path=sub_file,
            output_path=out_short
        )

        finished_shorts.append({
            "title": clip["title"],
            "theme": clip["description"],
            "file": str(out_short.resolve()),
            "duration": clip["duration"]
        })

    print("\n" + "=" * 60)
    print(f"🎉 TODOS OS {len(finished_shorts)} SHORTS ESTÃO PRONTOS PARA POSTAR NO TIKTOK!")
    for s in finished_shorts:
        print(f"  ✅ {s['title']} ({s['duration']}s): {s['file']}")
    print("=" * 60)

if __name__ == "__main__":
    run_local_batch()
