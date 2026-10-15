import sys
sys.path.insert(0, "D:\\Shorts")
import json
from src.highlighter import HighlightDetector

with open("inputs/TTH_eWH8IK0.transcript.json", "r", encoding="utf-8") as f:
    transcript = json.load(f)

# Focar em trechos com temas fortes: filtrar segmentos relevantes
segs = transcript.get("segments", [])

def window_text(t_start, t_end):
    parts = [s["text"] for s in segs if s["end"] >= t_start and s["start"] <= t_end]
    return " ".join(parts)

# Candidatos manuais com gancho forte (segundos)
candidatos = [
    (1704, 1749, "Lavagem_Dinheiro_MercadoFormal", "Como o dinheiro do crime se infiltra no mercado formal"),
    (2038, 2083, "Carro_2Milhoes_Status", "Carro de 2 milhoes: status ou ostentacao?"),
    (2766, 2811, "Operacao_Aeroporto_500Milhoes", "Operacao com 500 milhoes apreendidos"),
    (4210, 4255, "Operacao_Madrugada_Apreensao", "Operacao de madrugada: centenas de milhoes"),
    (6132, 6177, "Japao_Dinheiro_Lacrado", "Historia do Japao: dinheiro lacrado no banco"),
]

det = HighlightDetector(min_duration=30, max_duration=65, target_duration=45)

out = []
for t_start, t_end, title, desc in candidatos:
    txt = window_text(t_start, t_end)
    score = det._calculate_viral_score(txt[:200], txt, t_end - t_start)
    out.append({"title": title, "start": float(t_start), "end": float(t_end),
                "duration": round(t_end - t_start, 2), "score": round(score, 2),
                "description": desc, "text": txt[:300]})
    print(f"[{t_start}s -> {t_end}s] Score:{score:.1f} {title}")

with open("inputs/curated_TTH.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("OK curated_TTH.json")
