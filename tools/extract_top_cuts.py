import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

with open("inputs/o5T4QnQe5Os.transcript.json", "r", encoding="utf-8") as f:
    data = json.load(f)

segments = data["segments"]

def find_clip_by_time_range(t_start, t_end, title):
    clip_segs = [s for s in segments if s["end"] >= t_start and s["start"] <= t_end]
    if not clip_segs:
        return None
    full_text = " ".join([s["text"] for s in clip_segs])
    actual_start = clip_segs[0]["start"]
    actual_end = clip_segs[-1]["end"]
    return {
        "title": title,
        "start": round(actual_start, 2),
        "end": round(actual_end, 2),
        "duration": round(actual_end - actual_start, 2),
        "text": full_text
    }

# Alvos estratégicos baseados nos temas mais impactantes
targets = [
    # 1. A Regra dos 90 Segundos da Raiva
    (0.0, 55.0, "A Regra dos 90 Segundos da Raiva"),
    # 2. Como a Raiva e o Estresse destroem os Órgãos
    (30.0, 85.0, "O Que Acontece no Corpo Quando Sentimos Raiva"),
    # 3. Estresse Crônico é Fogo Baixo na Panela
    (1480.0, 1538.0, "Estresse Crônico: O Fogo Médio que Corrói Você"),
    # 4. Dopamina Barata destrói a Motivação
    (2700.0, 2760.0, "Dopamina Barata vs Motivação Real"),
    # 5. O Golpe do Psicopata: O Mesmo Script
    (3000.0, 3060.0, "Psicopatas Usam Sempre o Mesmo Roteiro"),
    # 6. Psicopatia Não Tem Cura Nem Tratamento
    (4800.0, 4860.0, "Psicopata Não Tem Tratamento: A Verdade Sem Filtro"),
    # 7. Sinais de Psicopatia na Infância (O Caso do Gato no Freezer)
    (5400.0, 5460.0, "Sinais Chocantes de Psicopatia Desde Criança"),
    # 8. Casos Reais: Como Identificar Pessoas Perigosas
    (5700.0, 5760.0, "Como Identificar Pessoas sem Empatia"),
    # 9. Depois dos 50 a Vida Muda / Seja Sua Melhor Companhia
    (6900.0, 6960.0, "A Arte de Ser Sua Melhor Companhia")
]

print("--- REFINANDO CORTES ESTRATÉGICOS ---")
found_clips = []
for start, end, title in targets:
    # Achar os segmentos em volta desse ponto
    clip = find_clip_by_time_range(start, end, title)
    if clip:
        found_clips.append(clip)
        print(f"\n🎬 {clip['title']}")
        print(f"⏱️ {clip['start']}s -> {clip['end']}s ({clip['duration']}s)")
        print(f"💬 \"{clip['text'][:160]}...\"")

with open("inputs/selected_clips.json", "w", encoding="utf-8") as f:
    json.dump(found_clips, f, indent=2, ensure_ascii=False)
