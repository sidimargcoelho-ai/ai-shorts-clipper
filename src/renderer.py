import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

class VideoRenderer:
    """
    Renderizador FFmpeg com aceleração por GPU (NVIDIA NVENC) e queima de legendas estilizadas.
    """
    def __init__(self, config: Dict[str, Any]):
        renderer_cfg = config.get("renderer", {})
        self.codec = renderer_cfg.get("codec", "h264_nvenc")
        self.fallback_codec = renderer_cfg.get("fallback_codec", "libx264")
        self.preset = renderer_cfg.get("preset", "p4")
        self.video_bitrate = renderer_cfg.get("video_bitrate", "6000k")
        self.audio_bitrate = renderer_cfg.get("audio_bitrate", "192k")

    def render_clip(
        self,
        video_path: Path,
        start_time: float,
        end_time: float,
        crop_filter: str,
        subtitle_path: Optional[Path],
        output_path: Path
    ) -> Path:
        """
        Executa o corte, enquadramento 9:16 e sobreposição de legenda com FFmpeg.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        duration = end_time - start_time
        print(f"[Renderer] Renderizando corte: {duration:.1f}s ({start_time:.1f}s -> {end_time:.1f}s)...")
        t0 = time.time()

        # Monta a cadeia de filtros de vídeo
        filter_parts = [crop_filter]

        if subtitle_path and subtitle_path.exists():
            # No Windows, o FFmpeg requer barras normais '/' e dois pontos escapados '\:'
            clean_sub_path = subtitle_path.resolve().as_posix().replace(":", "\\:")
            filter_parts.append(f"subtitles='{clean_sub_path}'")

        vf_string = ",".join(filter_parts)

        # Tentativa com aceleração por GPU (NVENC)
        success = self._run_ffmpeg(
            video_path, start_time, duration, vf_string, output_path, self.codec, self.preset
        )

        # Fallback para CPU se NVENC falhar
        if not success:
            print(f"[Renderer] Tentando fallback para CPU ({self.fallback_codec})...")
            success = self._run_ffmpeg(
                video_path, start_time, duration, vf_string, output_path, self.fallback_codec, "fast"
            )

        if not success or not output_path.exists() or output_path.stat().st_size == 0:
            raise RuntimeError(f"Falha na renderização do corte: {output_path}")

        elapsed = time.time() - t0
        fps_speed = duration / max(elapsed, 0.001)
        print(f"[Renderer] Renderização finalizada com sucesso em {elapsed:.1f}s ({fps_speed:.1f}x em tempo real)!")
        print(f"[Renderer] Arquivo pronto: {output_path.resolve()}")

        return output_path

    def _run_ffmpeg(
        self,
        video_path: Path,
        start_time: float,
        duration: float,
        vf_string: str,
        output_path: Path,
        vcodec: str,
        preset: str
    ) -> bool:
        cmd = [
            'ffmpeg', '-y',
            '-ss', f"{start_time:.3f}",
            '-i', str(video_path),
            '-t', f"{duration:.3f}",
            '-vf', vf_string,
            '-c:v', vcodec,
            '-preset', preset,
            '-b:v', self.video_bitrate,
            '-c:a', 'aac',
            '-b:a', self.audio_bitrate,
            '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart',
            str(output_path)
        ]

        try:
            res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            if res.returncode != 0:
                print(f"[Renderer] Erro no FFmpeg: {res.stderr.decode('utf-8', errors='ignore')[-500:]}")
                return False
            return True
        except Exception as e:
            print(f"[Renderer] Exceção ao executar FFmpeg: {e}")
            return False
