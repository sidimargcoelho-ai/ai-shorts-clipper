import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from faster_whisper import WhisperModel

class Transcriber:
    """
    Transcritor de áudio usando faster-whisper com timestamps palavra por palavra.
    """
    def __init__(self, model_size: str = "small", device: str = "cuda", compute_type: str = "float16"):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = None

    def _load_model(self):
        if self.model is None:
            print(f"[Transcriber] Carregando modelo Whisper '{self.model_size}' no dispositivo '{self.device}'...")
            try:
                self.model = WhisperModel(
                    self.model_size,
                    device=self.device,
                    compute_type=self.compute_type
                )
            except Exception as e:
                print(f"[Transcriber] Falha ao carregar no modo GPU/CUDA ({e}). Recorrendo para CPU...")
                self.device = "cpu"
                self.compute_type = "int8"
                self.model = WhisperModel(
                    self.model_size,
                    device="cpu",
                    compute_type="int8"
                )

    def transcribe(self, audio_path: Path, language: Optional[str] = "pt", force_recompute: bool = False) -> Dict[str, Any]:
        """
        Transcreve o áudio gerando timestamps por palavra e armazena em cache JSON.
        """
        json_cache = audio_path.with_suffix(".transcript.json")
        if json_cache.exists() and not force_recompute:
            print(f"[Transcriber] Utilizando transcrição em cache: {json_cache.name}")
            with open(json_cache, "r", encoding="utf-8") as f:
                return json.load(f)

        self._load_model()

        print(f"[Transcriber] Iniciando transcrição com timestamps detalhados...")
        segments_generator, info = self.model.transcribe(
            str(audio_path),
            language=language if language else None,
            word_timestamps=True,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500)
        )

        detected_lang = info.language
        print(f"[Transcriber] Idioma detectado: {detected_lang} (probabilidade: {info.language_probability:.2f})")

        segments_data = []
        full_text = []

        for seg in segments_generator:
            words = []
            if seg.words:
                for w in seg.words:
                    words.append({
                        "word": w.word.strip(),
                        "start": round(w.start, 3),
                        "end": round(w.end, 3),
                        "probability": round(w.probability, 3)
                    })

            segments_data.append({
                "id": seg.id,
                "start": round(seg.start, 3),
                "end": round(seg.end, 3),
                "text": seg.text.strip(),
                "words": words
            })
            full_text.append(seg.text.strip())

        result = {
            "language": detected_lang,
            "duration": round(info.duration, 2),
            "text": " ".join(full_text),
            "segments": segments_data
        }

        with open(json_cache, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"[Transcriber] Transcrição concluída! Salva em: {json_cache.name}")
        return result
