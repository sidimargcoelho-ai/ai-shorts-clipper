import os
import sys
import json
import time
import subprocess
from pathlib import Path
import yaml

# Adicionar raiz ao PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.tracker import FaceTracker
from src.subtitle import SubtitleGenerator
from src.renderer import VideoRenderer


YOUTUBE_URL = "https://www.youtube.com/watch?v=o5T4QnQe5Os"

def download_section(url: str, start_sec: float, end_sec: float, out_path: Path) -> Path:
    part_file = out_path.with_name(out_path.name + ".part")
    if part_file.exists():
        try:
            part_file.unlink()
        except Exception:
            pass

    if out_path.exists() and out_path.stat().st_size > 100000:
        print(f"  [Cache] Seção já baixada: {out_path.name}")
        return out_path

    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Formatar intervalo para yt-dlp
    sec_arg = f"*{int(start_sec)}-{int(end_sec) + 1}"
    print(f"  [Download] Baixando seção {sec_arg} ({end_sec - start_sec:.1f}s)...")

    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--download-sections", sec_arg,
        "-f", "137+140/bestvideo[vcodec^=avc1]+bestaudio/best",
        "--force-overwrites",
        "-o", str(out_path),
        url
    ]

    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if res.returncode != 0 or not out_path.exists():
        raise RuntimeError(f"Erro ao baixar seção: {res.stderr.decode('utf-8', errors='ignore')[-300:]}")

    return out_path

def run_batch():
    print("=" * 60)
    print("🚀 PROCESSANDO CORTES ESTRATÉGICOS DO PODCAST COM GPU NVENC")
    print("=" * 60)

    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    with open("inputs/o5T4QnQe5Os.transcript.json", "r", encoding="utf-8") as f:
        transcript = json.load(f)

    with open("inputs/curated_cuts.json", "r", encoding="utf-8") as f:
        clips = json.load(f)

    sections_dir = Path("inputs/sections")
    output_dir = Path("output")
    sections_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    tracker = FaceTracker(model_path="models/face_detector.tflite")
    sub_gen = SubtitleGenerator(config)
    renderer = VideoRenderer(config)

    total = len(clips)
    finished_shorts = []

    for idx, clip in enumerate(clips, 1):
        print(f"\n[{idx}/{total}] 🎬 {clip['title']} ({clip['duration']}s)")
        print(f"     Tema: {clip['description']}")

        out_short = output_dir / f"Short_{clip['title']}.mp4"
        if out_short.exists() and out_short.stat().st_size > 100000:
            print(f"  ✨ [Pronto] Short já renderizado com sucesso: {out_short.name}")
            finished_shorts.append({
                "title": clip["title"],
                "theme": clip["description"],
                "file": str(out_short.resolve()),
                "duration": clip["duration"]
            })
            continue

        # 1. Download apenas da fatia do vídeo
        section_file = sections_dir / f"{clip['title']}_raw.mp4"
        download_section(YOUTUBE_URL, clip["start"], clip["end"], section_file)

        # 2. Rastreamento de rosto 9:16
        print("  [Tracker] Analisando enquadramento com MediaPipe...")
        crop_info = tracker.analyze_clip(section_file, 0.0, clip["duration"], mode="face_tracking")

        # 3. Geração de Legendas Animadas no formato .ass
        sub_file = output_dir / f"{clip['title']}.ass"
        print("  [Subtitle] Gerando legendas dinâmicas TikTok/Hormozi...")
        sub_gen.generate_ass(transcript, clip["start"], clip["end"], sub_file)

        # 4. Renderização com GPU NVENC
        print(f"  [Renderer] Renderizando vídeo 9:16 com GTX 1650...")
        renderer.render_clip(
            video_path=section_file,
            start_time=0.0,
            end_time=clip["duration"],
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
    print(f"🎉 TODOS OS {len(finished_shorts)} SHORTS FORAM RENDERIZADOS COM SUCESSO!")
    for s in finished_shorts:
        print(f"  ✅ {s['title']} ({s['duration']}s): {s['file']}")
    print("=" * 60)

if __name__ == "__main__":
    run_batch()
