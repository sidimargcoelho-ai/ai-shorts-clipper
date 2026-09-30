import os
import sys
import subprocess
from pathlib import Path

# Adicionar raiz ao PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


from src.subtitle import SubtitleGenerator
from src.tracker import FaceTracker
from src.renderer import VideoRenderer
import yaml

def run_tests():
    print("🧪 [TEST] Iniciando testes do pipeline...")
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # 1. Gerar vídeo sintetizado de 3 segundos (1280x720) com áudio de teste
    test_video = Path("tests/sample_input.mp4")
    if not test_video.exists():
        print("  - Gerando vídeo de teste com FFmpeg...")
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "testsrc=duration=3:size=1280x720:rate=30",
            "-f", "lavfi", "-i", "sine=frequency=1000:duration=3",
            "-c:v", "libx264", "-c:a", "aac",
            str(test_video)
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    assert test_video.exists(), "Vídeo de teste não foi criado"
    print("  ✅ 1. Vídeo de teste gerado com sucesso.")

    # 2. Testar Tracker
    print("  - Testando FaceTracker...")
    tracker = FaceTracker(model_path="models/face_detector.tflite")
    crop_info = tracker.analyze_clip(test_video, start_time=0.0, end_time=3.0, mode="face_tracking")
    assert "crop_w" in crop_info and "crop_h" in crop_info
    print(f"  ✅ 2. FaceTracker funcionou: {crop_info['ffmpeg_crop_filter']}")

    # 3. Testar SubtitleGenerator
    print("  - Testando SubtitleGenerator (.ass)...")
    sub_gen = SubtitleGenerator(config)
    mock_transcript = {
        "segments": [
            {
                "id": 0,
                "start": 0.0,
                "end": 3.0,
                "text": "ESSE É UM TESTE VIRAL",
                "words": [
                    {"word": "ESSE", "start": 0.2, "end": 0.7},
                    {"word": "É", "start": 0.8, "end": 1.1},
                    {"word": "UM", "start": 1.2, "end": 1.5},
                    {"word": "TESTE", "start": 1.6, "end": 2.2},
                    {"word": "VIRAL", "start": 2.3, "end": 2.9}
                ]
            }
        ]
    }
    test_sub = Path("tests/sample_sub.ass")
    sub_gen.generate_ass(mock_transcript, clip_start=0.0, clip_end=3.0, output_path=test_sub)
    assert test_sub.exists() and test_sub.stat().st_size > 0
    print("  ✅ 3. SubtitleGenerator gerou arquivo .ass perfeitamente.")

    # 4. Testar VideoRenderer com aceleração NVENC e queima de legendas
    print("  - Testando VideoRenderer (NVENC + Subtitles)...")
    renderer = VideoRenderer(config)
    test_output = Path("tests/sample_output_short.mp4")
    out_rendered = renderer.render_clip(
        video_path=test_video,
        start_time=0.0,
        end_time=3.0,
        crop_filter=crop_info["ffmpeg_crop_filter"],
        subtitle_path=test_sub,
        output_path=test_output
    )

    assert out_rendered.exists() and out_rendered.stat().st_size > 0
    print(f"  ✅ 4. Vídeo renderizado em 9:16 com sucesso: {test_output.stat().st_size} bytes!")

    # 5. Validar resolução do vídeo gerado (1080x1920)
    cmd_probe = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=s=x:p=0",
        str(test_output)
    ]
    probe_res = subprocess.run(cmd_probe, stdout=subprocess.PIPE, text=True)
    res_str = probe_res.stdout.strip()
    print(f"  ✅ 5. Resolução confirmada: {res_str} (9:16 Vertical)")
    assert "1080x1920" in res_str, f"Esperado 1080x1920, obteve: {res_str}"

    print("\n🎉 TODOS OS TESTES PASSARAM COM SUCESSO!")

if __name__ == "__main__":
    run_tests()
