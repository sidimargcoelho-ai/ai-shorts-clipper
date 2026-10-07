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

URL = "https://www.youtube.com/watch?v=vbZquVH5bcs"
DENO_PATH = r"C:\Users\sidim\AppData\Local\Microsoft\WinGet\Packages\DenoLand.Deno_Microsoft.Winget.Source_8wekyb3d8bbwe\deno.exe"

def download_section(url: str, start_sec: float, end_sec: float, out_path: Path) -> Path:
    # Limpar arquivos .part residuais
    for p in out_path.parent.glob(f"{out_path.stem}*.part"):
        try:
            p.unlink()
        except Exception:
            pass

    # Verificar se já existe como .mp4 ou .mkv
    mkv_path = out_path.with_name(out_path.name + ".mkv")
    if mkv_path.exists() and mkv_path.stat().st_size > 500000:
        try:
            mkv_path.rename(out_path)
        except Exception:
            pass

    if out_path.exists() and out_path.stat().st_size > 500000:
        print(f"  [Cache] Seção já baixada: {out_path.name}")
        return out_path

    out_path.parent.mkdir(parents=True, exist_ok=True)
    sec_arg = f"*{int(start_sec)}-{int(end_sec) + 1}"
    print(f"  [Download] Baixando seção {sec_arg} ({end_sec - start_sec:.1f}s)...")

    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--js-runtimes", f"deno:{DENO_PATH}",
        "--remote-components", "ejs:github",
        "--cookies-from-browser", "firefox",
        "--download-sections", sec_arg,
        "-f", "137+140/bestvideo[vcodec^=avc1]+bestaudio/best",
        "--merge-output-format", "mp4",
        "--force-overwrites",
        "-o", str(out_path),
        url
    ]

    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    
    # Se o yt-dlp gerou com extensão .mkv ou .mp4.mkv, renomeia para out_path
    if not out_path.exists():
        candidates = list(out_path.parent.glob(f"{out_path.stem}*"))
        for cand in candidates:
            if cand.suffix.lower() in [".mkv", ".mp4", ".webm"] and cand.stat().st_size > 500000:
                try:
                    cand.rename(out_path)
                    break
                except Exception:
                    pass

    if not out_path.exists():
        err_msg = res.stderr.decode("utf-8", errors="ignore")
        raise RuntimeError(f"Erro ao baixar seção: {err_msg[-300:]}")

    return out_path


def run_batch():
    print("=" * 60)
    print("🎬 PROCESSANDO 10 SHORTS DE AUGUSTO CURY COM GPU NVENC")
    print("=" * 60)

    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    with open("inputs/vbZquVH5bcs.transcript.json", "r", encoding="utf-8") as f:
        transcript = json.load(f)

    with open("inputs/cury_curated_cuts.json", "r", encoding="utf-8") as f:
        clips = json.load(f)

    sections_dir = Path("inputs/sections_cury")
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

        out_short = output_dir / f"Short_Cury_{clip['title']}.mp4"
        if out_short.exists() and out_short.stat().st_size > 1000000:
            print(f"  ✨ [Pronto] Short já renderizado com sucesso: {out_short.name}")
            finished_shorts.append({
                "title": clip["title"],
                "theme": clip["description"],
                "file": str(out_short.resolve()),
                "duration": clip["duration"]
            })
            continue

        # 1. Download apenas da fatia do vídeo (com Deno + cookies)
        section_file = sections_dir / f"{clip['title']}_raw.mp4"
        download_section(URL, clip["start"], clip["end"], section_file)

        # 2. Rastreamento de rosto 9:16
        print("  [Tracker] Analisando enquadramento com MediaPipe...")
        crop_info = tracker.analyze_clip(section_file, 0.0, clip["duration"], mode="face_tracking")

        # 3. Geração de Legendas Animadas no formato .ass
        sub_file = output_dir / f"Cury_{clip['title']}.ass"
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
    print(f"🎉 TODOS OS {len(finished_shorts)} SHORTS DE AUGUSTO CURY ESTÃO PRONTOS PARA POSTAR NO TIKTOK!")
    for s in finished_shorts:
        print(f"  ✅ {s['title']} ({s['duration']}s): {s['file']}")
    print("=" * 60)

if __name__ == "__main__":
    run_batch()
