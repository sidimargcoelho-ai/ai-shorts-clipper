import os
from pathlib import Path
from typing import Dict, Any, List

def format_ass_time(seconds: float) -> str:
    """Converte segundos para o formato de tempo do ASS: H:MM:SS.cs"""
    seconds = max(0.0, seconds)
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int(round((seconds - int(seconds)) * 100))
    if centis >= 100:
        centis = 99
    return f"{hrs}:{mins:02d}:{secs:02d}.{centis:02d}"

class SubtitleGenerator:
    """
    Gera legendas dinâmicas animadas em formato .ass com destaque palavra por palavra (estilo TikTok/Hormozi).
    """
    def __init__(self, config: Dict[str, Any]):
        sub_cfg = config.get("subtitles", {})
        self.font_name = sub_cfg.get("font_name", "Arial Black")
        self.font_size = sub_cfg.get("font_size", 26)
        self.bold = sub_cfg.get("bold", 1)
        self.italic = sub_cfg.get("italic", 0)
        self.primary_color = sub_cfg.get("primary_color", "&H00FFFFFF")       # Branco
        self.highlight_color = sub_cfg.get("highlight_color", "&H0000FFFF")   # Amarelo
        self.outline_color = sub_cfg.get("outline_color", "&H00000000")       # Preto
        self.shadow_color = sub_cfg.get("shadow_color", "&H80000000")
        self.outline_width = sub_cfg.get("outline_width", 3.5)
        self.shadow = sub_cfg.get("shadow", 2.0)
        self.words_per_subtitle = sub_cfg.get("words_per_subtitle", 3)
        self.margin_v = sub_cfg.get("margin_v", 240)

    def generate_ass(self, transcript_data: Dict[str, Any], clip_start: float, clip_end: float, output_path: Path) -> Path:
        """
        Gera o arquivo de legenda .ass para o trecho do vídeo selecionado.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 1. Filtrar todas as palavras que pertencem a esse trecho
        clip_words = []
        for segment in transcript_data.get("segments", []):
            for w in segment.get("words", []):
                w_start = w["start"]
                w_end = w["end"]
                if w_end >= clip_start and w_start <= clip_end:
                    # Ajustar tempo relativo ao início do corte
                    rel_start = max(0.0, w_start - clip_start)
                    rel_end = max(0.0, w_end - clip_start)
                    clean_word = w["word"].strip().upper()
                    if clean_word:
                        clip_words.append({
                            "word": clean_word,
                            "start": rel_start,
                            "end": rel_end
                        })

        # 2. Agrupar em pequenos blocos de 2 a 4 palavras
        blocks = []
        for i in range(0, len(clip_words), self.words_per_subtitle):
            block = clip_words[i:i + self.words_per_subtitle]
            if block:
                blocks.append(block)

        # 3. Construir os eventos de diálogo do .ass
        dialogues = []
        for block in blocks:
            # Cada palavra do bloco ganha seu momento de destaque ativo
            for active_idx, target_word in enumerate(block):
                line_start = target_word["start"]
                line_end = target_word["end"]
                if line_end <= line_start:
                    line_end = line_start + 0.25

                # Monta o texto destacando a palavra falada no momento
                formatted_words = []
                for idx, w in enumerate(block):
                    if idx == active_idx:
                        # Palavra ativa com cor de destaque e leve pulso
                        formatted_words.append(f"{{\\c{self.highlight_color}\\fscx108\\fscy108}}{w['word']}{{\\c{self.primary_color}\\fscx100\\fscy100}}")
                    else:
                        formatted_words.append(w["word"])

                text_line = " ".join(formatted_words)
                start_str = format_ass_time(line_start)
                end_str = format_ass_time(line_end)

                dialogues.append(
                    f"Dialogue: 0,{start_str},{end_str},TikTokStyle,,0,0,0,,{text_line}"
                )

        # 4. Cabeçalho padrão do ASS para vídeo vertical 1080x1920
        ass_content = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TikTokStyle,{self.font_name},{self.font_size * 2},{self.primary_color},&H000000FF,{self.outline_color},{self.shadow_color},{self.bold},{self.italic},0,0,100,100,0,0,1,{self.outline_width * 2},{self.shadow * 2},2,40,40,{self.margin_v * 2},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(dialogues) + "\n"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(ass_content)

        print(f"[Subtitle] Legendas dinâmicas geradas: {output_path.name} ({len(dialogues)} eventos)")
        return output_path
