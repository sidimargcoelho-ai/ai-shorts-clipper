import os
import sys
import argparse
import yaml
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


from src.downloader import Downloader
from src.transcriber import Transcriber
from src.highlighter import HighlightDetector
from src.tracker import FaceTracker
from src.subtitle import SubtitleGenerator
from src.renderer import VideoRenderer
from src.description_generator import DescriptionGenerator

def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def run_pipeline(
    url: str = None,
    input_file: str = None,
    num_clips: int = 15,
    start_time: float = None,
    end_time: float = None,
    crop_mode: str = None,
    whisper_model: str = None,
    no_subtitles: bool = False,
    list_only: bool = False
):
    print("=" * 60)
    print("🎬 PIPELINE AUTOMATIZADO DE SHORTS & CORTES VIRAL")
    print("=" * 60)

    config = load_config()

    if crop_mode:
        config["cropping"]["mode"] = crop_mode
    if whisper_model:
        config["whisper"]["model_size"] = whisper_model

    # 1. Download ou Carregamento do Vídeo
    downloader = Downloader(output_dir="inputs")
    if url:
        video_path, audio_path, metadata = downloader.download_url(url)
    elif input_file:
        video_path, audio_path, metadata = downloader.prepare_local_file(input_file)
    else:
        raise ValueError("É necessário informar uma URL (--url) ou um arquivo local (--input).")

    print(f"\n[Info] Título: {metadata['title']}")
    print(f"[Info] Duração Total: {metadata['duration']:.1f} segundos")

    # 2. Transcrição com faster-whisper (GPU CUDA)
    transcriber = Transcriber(
        model_size=config["whisper"]["model_size"],
        device=config["whisper"]["device"],
        compute_type=config["whisper"]["compute_type"]
    )
    transcript_data = transcriber.transcribe(
        audio_path,
        language=config["whisper"].get("language", "pt")
    )

    # 3. Definição dos Trechos (Automático ou Manual)
    if start_time is not None and end_time is not None:
        clips = [{
            "start": start_time,
            "end": end_time,
            "duration": end_time - start_time,
            "title": f"Corte Manual {start_time:.0f}s-{end_time:.0f}s",
            "text": "Trecho manual definido pelo usuário",
            "score": 100.0
        }]
    else:
        highlighter = HighlightDetector(
            min_duration=config["clipping"]["min_duration"],
            max_duration=config["clipping"]["max_duration"],
            target_duration=config["clipping"]["target_duration"]
        )
        clips = highlighter.detect_highlights(transcript_data, max_clips=num_clips)

    print(f"\n[Destaques] {len(clips)} momentos selecionados:")
    for idx, c in enumerate(clips, 1):
        print(f"  {idx}. [{c['start']:.1f}s -> {c['end']:.1f}s] ({c['duration']:.1f}s) | Score: {c.get('score', 0)}/100")
        print(f"     Título: \"{c['title']}\"")

    if list_only:
        print("\n[Modo Lista] Listagem concluída. Nenhuma renderização executada.")
        return

    # 4. Processamento, Rastreamento e Renderização
    tracker = FaceTracker(
        model_path="models/face_detector.tflite",
        smoothing=config["cropping"]["smoothing"]
    )
    subtitle_gen = SubtitleGenerator(config)
    renderer = VideoRenderer(config)
    desc_gen = DescriptionGenerator(config)

    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_files = []

    for idx, clip in enumerate(clips, 1):
        print("\n" + "-" * 50)
        print(f"⚙️ Processando Corte #{idx} ({clip['start']:.1f}s - {clip['end']:.1f}s): {clip['title']}")
        print("-" * 50)

        # A. Enquadramento 9:16 com Face Tracking
        crop_info = tracker.analyze_clip(
            video_path,
            start_time=clip["start"],
            end_time=clip["end"],
            mode=config["cropping"]["mode"]
        )

        # B. Geração de Legendas Dinâmicas
        sub_path = None
        if not no_subtitles:
            sub_filename = f"clip_{idx}_{int(clip['start'])}_{int(clip['end'])}.ass"
            sub_path = output_dir / sub_filename
            subtitle_gen.generate_ass(
                transcript_data,
                clip_start=clip["start"],
                clip_end=clip["end"],
                output_path=sub_path
            )

        # C. Renderização do Corte Final
        clean_title = "".join(c for c in clip['title'] if c.isalnum() or c in (' ', '_', '-')).strip().replace(" ", "_")[:25]
        out_filename = f"Short_{idx}_{int(clip['start'])}_{int(clip['end'])}_{clean_title}.mp4"
        out_path = output_dir / out_filename

        final_clip = renderer.render_clip(
            video_path=video_path,
            start_time=clip["start"],
            end_time=clip["end"],
            crop_filter=crop_info["ffmpeg_crop_filter"],
            subtitle_path=sub_path,
            output_path=out_path
        )
        generated_files.append(final_clip)

        # D. Geração da Descrição Pronta para TikTok (.txt com o mesmo nome do .mp4)
        if desc_gen.enabled:
            print("  📝 Gerando descrição para TikTok...")
            desc_text = desc_gen.generate(
                clip_text=clip.get("text", ""),
                clip_title=clip.get("title", ""),
                context_desc=clip.get("description", "")
            )
            txt_path = out_path.with_suffix(".txt")
            desc_gen.save_description(desc_text, txt_path)
            print(f"  ✅ Descrição salva com sucesso: {txt_path.name}")

    print("\n" + "=" * 60)
    print(f"🎉 SUCESSO! {len(generated_files)} Shorts e Descrições gerados:")
    for f in generated_files:
        print(f"  👉 Vídeo: {f.name} | Descrição: {f.with_suffix('.txt').name}")
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description="Pipeline de Cortes Automáticos para Shorts/TikTok")
    parser.add_argument("--url", type=str, help="URL do vídeo (YouTube, Twitch, etc.)")
    parser.add_argument("--input", type=str, help="Caminho para arquivo de vídeo local")
    parser.add_argument("--clips", type=int, default=15, help="Quantidade de cortes a gerar (padrão: 15)")
    parser.add_argument("--start", type=float, default=None, help="Início manual do corte em segundos")
    parser.add_argument("--end", type=float, default=None, help="Fim manual do corte em segundos")
    parser.add_argument("--mode", type=str, choices=["face_tracking", "split_screen", "center"], default=None, help="Modo de enquadramento 9:16")
    parser.add_argument("--model", type=str, default=None, help="Modelo do Whisper (tiny, base, small, medium)")
    parser.add_argument("--no-subtitles", action="store_true", help="Desativa a queima de legendas")
    parser.add_argument("--no-descriptions", action="store_true", help="Desativa a geração de arquivos .txt com descrição")
    parser.add_argument("--list-only", action="store_true", help="Apenas transcreve e lista os momentos virais")

    args = parser.parse_args()

    if not args.url and not args.input:
        parser.print_help()
        sys.exit(1)

    run_pipeline(
        url=args.url,
        input_file=args.input,
        num_clips=args.clips,
        start_time=args.start,
        end_time=args.end,
        crop_mode=args.mode,
        whisper_model=args.model,
        no_subtitles=args.no_subtitles,
        list_only=args.list_only
    )

if __name__ == "__main__":
    main()
