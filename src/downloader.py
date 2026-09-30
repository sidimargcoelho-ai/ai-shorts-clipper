import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, Tuple
import yt_dlp

class Downloader:
    """
    Gerenciador de download e extração de áudio para vídeos locais ou URLs do YouTube.
    """
    def __init__(self, output_dir: str = "inputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def download_url(self, url: str) -> Tuple[Path, Path, Dict[str, Any]]:
        """
        Baixa o vídeo de melhor qualidade (até 1080p) e extrai o áudio otimizado para o Whisper.
        Retorna: (caminho_video, caminho_audio, metadados)
        """
        print(f"[Downloader] Analisando URL: {url}")
        
        ydl_opts_info = {'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
            info = ydl.extract_info(url, download=False)
            video_id = info.get('id', 'video')
            title = info.get('title', 'video')
            sanitized_title = "".join(c for c in title if c.isalnum() or c in (' ', '_', '-')).strip()
            sanitized_title = sanitized_title[:40].replace(" ", "_")
        
        video_filename = f"{video_id}_{sanitized_title}.mp4"
        video_path = self.output_dir / video_filename
        audio_path = self.output_dir / f"{video_id}_{sanitized_title}.wav"

        # Se o vídeo já foi baixado previamente, reutiliza
        if not video_path.exists():
            print(f"[Downloader] Baixando vídeo: {title}...")
            ydl_opts = {
                'format': 'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': str(video_path),
                'merge_output_format': 'mp4',
                'quiet': False,
                'no_warnings': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        else:
            print(f"[Downloader] Vídeo já encontrado no cache: {video_path}")

        # Extrai áudio WAV 16kHz mono (formato nativo ideal para Whisper)
        if not audio_path.exists():
            print(f"[Downloader] Extraindo faixa de áudio otimizada...")
            self._extract_audio(video_path, audio_path)

        metadata = {
            'id': video_id,
            'title': title,
            'duration': info.get('duration', 0),
            'channel': info.get('uploader', ''),
            'description': info.get('description', '')
        }

        return video_path, audio_path, metadata

    def prepare_local_file(self, file_path: str) -> Tuple[Path, Path, Dict[str, Any]]:
        """
        Prepara um arquivo local, extraindo o áudio se necessário.
        """
        src_path = Path(file_path).resolve()
        if not src_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        audio_path = self.output_dir / f"{src_path.stem}.wav"
        if not audio_path.exists():
            print(f"[Downloader] Extraindo áudio do arquivo local: {src_path.name}...")
            self._extract_audio(src_path, audio_path)

        # Obter duração do vídeo via ffprobe
        duration = self._get_video_duration(src_path)

        metadata = {
            'id': src_path.stem,
            'title': src_path.stem,
            'duration': duration,
            'channel': 'Local',
            'description': ''
        }

        return src_path, audio_path, metadata

    def _extract_audio(self, video_path: Path, audio_path: Path):
        """Extrai áudio mono 16kHz com FFmpeg para alta velocidade de inferência no Whisper"""
        cmd = [
            'ffmpeg', '-y',
            '-i', str(video_path),
            '-vn',
            '-acodec', 'pcm_s16le',
            '-ar', '16000',
            '-ac', '1',
            str(audio_path)
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        if res.returncode != 0:
            raise RuntimeError(f"Erro ao extrair áudio com FFmpeg: {res.stderr.decode('utf-8', errors='ignore')}")

    def _get_video_duration(self, video_path: Path) -> float:
        """Obtém a duração do vídeo em segundos"""
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            str(video_path)
        ]
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
            return float(res.stdout.strip())
        except Exception:
            return 0.0
