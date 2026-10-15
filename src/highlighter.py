import re
from typing import List, Dict, Any

HOOK_KEYWORDS = [
    "o maior erro", "o segredo", "ninguém te conta", "você sabia", "aconteceu que",
    "o problema é", "por que", "nunca faça", "a verdade sobre", "como eu fiz",
    "pare de", "atenção", "olha isso", "chocante", "surpreendente", "dica",
    "segredo", "milhões", "dinheiro", "sucesso", "fracasso", "resultado",
    "você precisa", "não cometa", "o que acontece", "descobri", "incrível"
]

class HighlightDetector:
    """
    Identifica os melhores trechos para cortes (Shorts/TikTok/Reels) a partir da transcrição.
    """
    def __init__(self, min_duration: int = 30, max_duration: int = 65, target_duration: int = 45):
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.target_duration = target_duration

    def detect_highlights(self, transcript_data: Dict[str, Any], max_clips: int = 15) -> List[Dict[str, Any]]:
        """
        Analisa os segmentos e gera os melhores candidatos a cortes (garantindo pelo menos max_clips quando o vídeo permitir).
        """
        segments = transcript_data.get("segments", [])
        if not segments:
            return []

        candidates = []
        n_segments = len(segments)

        for i in range(n_segments):
            start_seg = segments[i]
            start_time = start_seg["start"]
            current_text = [start_seg["text"]]

            for j in range(i + 1, n_segments):
                end_seg = segments[j]
                current_text.append(end_seg["text"])
                duration = end_seg["end"] - start_time

                if self.min_duration <= duration <= self.max_duration:
                    full_clip_text = " ".join(current_text)
                    score = self._calculate_viral_score(start_seg["text"], full_clip_text, duration)

                    candidates.append({
                        "start": start_time,
                        "end": end_seg["end"],
                        "duration": round(duration, 2),
                        "text": full_clip_text,
                        "hook": start_seg["text"],
                        "score": round(score, 2),
                        "title": self._generate_title(start_seg["text"], full_clip_text)
                    })
                elif duration > self.max_duration:
                    break

        # Ordenar por score decrescente
        candidates.sort(key=lambda x: x["score"], reverse=True)

        # Filtrar sobreposições excessivas (garantir variedade)
        selected_clips: List[Dict[str, Any]] = []
        for cand in candidates:
            overlaps = False
            for sel in selected_clips:
                overlap_start = max(cand["start"], sel["start"])
                overlap_end = min(cand["end"], sel["end"])
                if overlap_end > overlap_start:
                    overlap_duration = overlap_end - overlap_start
                    if overlap_duration > 8.0:  # Limite de sobreposição
                        overlaps = True
                        break
            if not overlaps:
                selected_clips.append(cand)
                if len(selected_clips) >= max_clips:
                    break

        # Se não atingiu max_clips, busca cobrir a linha do tempo (timeline distribution)
        if len(selected_clips) < max_clips and candidates:
            for cand in candidates:
                if any(cand["start"] == sel["start"] and cand["end"] == sel["end"] for sel in selected_clips):
                    continue
                # Permite sobreposição menor se ainda faltar clips
                overlaps = False
                for sel in selected_clips:
                    overlap_start = max(cand["start"], sel["start"])
                    overlap_end = min(cand["end"], sel["end"])
                    if overlap_end > overlap_start:
                        overlap_duration = overlap_end - overlap_start
                        if overlap_duration > 15.0:
                            overlaps = True
                            break
                if not overlaps:
                    selected_clips.append(cand)
                    if len(selected_clips) >= max_clips:
                        break

        # Ordenar cronologicamente para facilitar navegação
        selected_clips.sort(key=lambda x: x["start"])
        return selected_clips

    def _calculate_viral_score(self, hook_text: str, full_text: str, duration: float) -> float:
        """Calcula uma pontuação estimada de engajamento do corte"""
        score = 50.0

        # Penalidade/Bônus por duração ideal (perto de 40-50s é excelente para o algoritmo)
        duration_diff = abs(duration - self.target_duration)
        score += max(0, 15.0 - duration_diff * 0.7)

        # Presença de ganchos no início do trecho (primeiras palavras)
        hook_lower = hook_text.lower()
        full_lower = full_text.lower()

        for kw in HOOK_KEYWORDS:
            if kw in hook_lower:
                score += 15.0
            elif kw in full_lower:
                score += 5.0

        # Terminação com pontuação forte (frase completa)
        if full_text.endswith((".", "!", "?")):
            score += 10.0

        # Perguntas geram alta curiosidade inicial
        if "?" in hook_text:
            score += 12.0

        # Densidade de palavras por segundo (ritmo dinâmico)
        word_count = len(full_text.split())
        words_per_sec = word_count / max(duration, 1)
        if 2.0 <= words_per_sec <= 3.5:  # Ritmo ideal de fala para vídeos curtos
            score += 10.0

        return score

    def _generate_title(self, hook_text: str, full_text: str) -> str:
        """Gera um título chamativo para o corte"""
        words = hook_text.split()
        if len(words) > 8:
            return " ".join(words[:8]) + "..."
        return hook_text
