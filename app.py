import os
import gradio as gr
from pathlib import Path
import yaml

from src.downloader import Downloader
from src.transcriber import Transcriber
from src.highlighter import HighlightDetector
from src.tracker import FaceTracker
from src.subtitle import SubtitleGenerator
from src.renderer import VideoRenderer

def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

config = load_config()

# Cache de sessão
session_state = {
    "video_path": None,
    "audio_path": None,
    "metadata": None,
    "transcript_data": None,
    "clips": []
}

def analyze_video(url, local_file, whisper_model, num_clips, progress=gr.Progress()):
    if not url and not local_file:
        raise gr.Error("Por favor informe uma URL do YouTube ou envie um arquivo de vídeo.")

    progress(0.1, desc="Obtendo vídeo e áudio...")
    downloader = Downloader(output_dir="inputs")
    if url:
        video_path, audio_path, meta = downloader.download_url(url)
    else:
        video_path, audio_path, meta = downloader.prepare_local_file(local_file)

    session_state["video_path"] = video_path
    session_state["audio_path"] = audio_path
    session_state["metadata"] = meta

    progress(0.3, desc=f"Transcrevendo com Whisper ({whisper_model})...")
    transcriber = Transcriber(
        model_size=whisper_model,
        device=config["whisper"]["device"],
        compute_type=config["whisper"]["compute_type"]
    )
    transcript = transcriber.transcribe(audio_path, language=config["whisper"].get("language", "pt"))
    session_state["transcript_data"] = transcript

    progress(0.7, desc="Identificando momentos virais com IA...")
    highlighter = HighlightDetector(
        min_duration=config["clipping"]["min_duration"],
        max_duration=config["clipping"]["max_duration"],
        target_duration=config["clipping"]["target_duration"]
    )
    clips = highlighter.detect_highlights(transcript, max_clips=int(num_clips))
    session_state["clips"] = clips

    # Formatar tabela/texto de momentos
    clips_summary = f"### 🎯 {len(clips)} Melhores Momentos Encontrados:\n\n"
    for i, c in enumerate(clips, 1):
        clips_summary += f"**Corte #{i}: {c['title']}**\n"
        clips_summary += f"- ⏱️ Tempo: `{c['start']:.1f}s` até `{c['end']:.1f}s` ({c['duration']:.1f} segundos)\n"
        clips_summary += f"- 🚀 Score de Viralidade: **{c['score']}/100**\n"
        clips_summary += f"- 💬 *\"{c['text'][:140]}...\"*\n\n"

    progress(1.0, desc="Análise completa!")
    return (
        f"✅ Vídeo: **{meta['title']}** ({meta['duration']:.1f}s)",
        clips_summary,
        gr.update(choices=[f"Corte #{i}: {c['title']} ({c['start']:.0f}s-{c['end']:.0f}s)" for i, c in enumerate(clips, 1)], value=[f"Corte #{i}: {c['title']} ({c['start']:.0f}s-{c['end']:.0f}s)" for i, c in enumerate(clips, 1)])
    )

def render_selected_clips(selected_clip_indices, crop_mode, add_subtitles, progress=gr.Progress()):
    if not session_state.get("video_path") or not session_state.get("clips"):
        raise gr.Error("Analise um vídeo primeiro antes de renderizar.")

    all_clips = session_state["clips"]
    video_path = session_state["video_path"]
    transcript = session_state["transcript_data"]

    # Identificar quais clipes foram selecionados
    indices_to_render = []
    for sel in selected_clip_indices:
        idx = int(sel.split(":")[0].replace("Corte #", "")) - 1
        indices_to_render.append(idx)

    if not indices_to_render:
        raise gr.Error("Nenhum corte selecionado para renderização.")

    tracker = FaceTracker(model_path="models/face_detector.tflite")
    subtitle_gen = SubtitleGenerator(config)
    renderer = VideoRenderer(config)
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    rendered_videos = []
    total = len(indices_to_render)

    for step, idx in enumerate(indices_to_render, 1):
        clip = all_clips[idx]
        progress((step - 0.5) / total, desc=f"Renderizando Corte #{idx + 1}...")

        # Face tracking
        crop_info = tracker.analyze_clip(video_path, clip["start"], clip["end"], mode=crop_mode)

        # Legendas
        sub_path = None
        if add_subtitles:
            sub_path = output_dir / f"clip_{idx + 1}_{int(clip['start'])}_{int(clip['end'])}.ass"
            subtitle_gen.generate_ass(transcript, clip["start"], clip["end"], sub_path)

        # Render
        clean_title = "".join(c for c in clip['title'] if c.isalnum() or c in (' ', '_', '-')).strip().replace(" ", "_")[:20]
        out_filename = f"Short_{idx + 1}_{int(clip['start'])}_{int(clip['end'])}_{clean_title}.mp4"
        out_path = output_dir / out_filename

        final_clip = renderer.render_clip(
            video_path=video_path,
            start_time=clip["start"],
            end_time=clip["end"],
            crop_filter=crop_info["ffmpeg_crop_filter"],
            subtitle_path=sub_path,
            output_path=out_path
        )
        rendered_videos.append(str(final_clip.resolve()))

    progress(1.0, desc="Renderização concluída!")
    first_video = rendered_videos[0] if rendered_videos else None
    return first_video, rendered_videos

# Construção da Interface Gradio
with gr.Blocks(title="AI Shorts Maker", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🎬 AI Shorts & TikTok Auto-Clipper
    ### Transforme vídeos longos e podcasts em cortes verticais 9:16 com Legendas Dinâmicas e Rastreamento de Rosto
    """)

    with gr.Row():
        with gr.Column(scale=1):
            url_input = gr.Textbox(label="🔗 URL do Vídeo (YouTube)", placeholder="https://www.youtube.com/watch?v=...")
            file_input = gr.Video(label="📁 Ou envie um arquivo de vídeo local")
            
            with gr.Row():
                whisper_model = gr.Dropdown(choices=["tiny", "base", "small", "medium"], value="small", label="Modelo Whisper (IA de Áudio)")
                num_clips = gr.Slider(minimum=1, maximum=10, value=3, step=1, label="Qtd. de Cortes")

            analyze_btn = gr.Button("🔍 1. Analisar Vídeo e Momentos Virais", variant="primary")

            gr.Markdown("---")
            crop_mode = gr.Radio(choices=["face_tracking", "center"], value="face_tracking", label="Modo de Enquadramento 9:16")
            add_subtitles = gr.Checkbox(value=True, label="Gerar Legendas Animadas (Estilo TikTok/Hormozi)")
            clip_selector = gr.CheckboxGroup(label="Selecione os Cortes para Renderizar", choices=[])
            render_btn = gr.Button("⚡ 2. Renderizar Shorts com GPU (NVENC)", variant="secondary")

        with gr.Column(scale=1):
            status_text = gr.Markdown("Status: Aguardando vídeo...")
            clips_output = gr.Markdown("Os melhores momentos analisados aparecerão aqui.")
            player_preview = gr.Video(label="Pré-visualização do Short Gerado (9:16)", interactive=False)
            files_output = gr.File(label="Arquivos Prontos para Download")

    analyze_btn.click(
        fn=analyze_video,
        inputs=[url_input, file_input, whisper_model, num_clips],
        outputs=[status_text, clips_output, clip_selector]
    )

    render_btn.click(
        fn=render_selected_clips,
        inputs=[clip_selector, crop_mode, add_subtitles],
        outputs=[player_preview, files_output]
    )

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860, inbrowser=True)
