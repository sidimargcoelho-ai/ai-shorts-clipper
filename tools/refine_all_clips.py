import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

with open("inputs/o5T4QnQe5Os.transcript.json", "r", encoding="utf-8") as f:
    transcript = json.load(f)

segments = transcript["segments"]

def get_clean_slice(t_start, t_end, title, description):
    sub_segs = [s for s in segments if s["end"] >= t_start and s["start"] <= t_end]
    if not sub_segs:
        return None
    full_text = " ".join(s["text"] for s in sub_segs)
    return {
        "title": title,
        "description": description,
        "start": sub_segs[0]["start"],
        "end": sub_segs[-1]["end"],
        "duration": round(sub_segs[-1]["end"] - sub_segs[0]["start"], 2),
        "text": full_text
    }

# 8 Cortes Estratégicos de Alta Retenção no Podcast
curated_clips = [
    get_clean_slice(0.3, 56.8, "01_A_Regra_dos_90_Segundos_da_Raiva", "Como a amígdala cerebral dispara a raiva e como neutralizá-la em 90s"),
    get_clean_slice(1479.8, 1538.8, "02_Estresse_Cronico_Fogo_na_Panela", "Por que o estresse prolongado em fogo médio destrói os órgãos do corpo"),
    get_clean_slice(2700.0, 2760.2, "03_Dopamina_Barata_vs_Motivacao", "Como o consumo de dopamina barata no celular destrói sua força de vontade"),
    get_clean_slice(2997.7, 3059.7, "04_O_Script_do_Psicopata", "Como identificar o padrão repetitivo e sedutor de psicopatas nas relações"),
    get_clean_slice(4798.7, 4860.4, "05_Psicopatia_Nao_Tem_Cura", "Por que psicopatia é uma condição estrutural e não tem tratamento psiquiátrico"),
    get_clean_slice(5398.3, 5460.3, "06_Sinais_de_Psicopatia_na_Infancia", "A história real e assustadora da criança psicopata e o gato no congelador"),
    get_clean_slice(5699.5, 5762.1, "07_Perfis_Sem_Empatia_na_Atualidade", "Análise de casos recentes de pessoas sem empatia e frieza emocional"),
    get_clean_slice(6899.4, 6960.3, "08_A_Arte_de_Ser_Sua_Melhor_Companhia", "Ninguém morre junto: a importância vital de gostar de si mesmo")
]

curated_clips = [c for c in curated_clips if c is not None]

print("=== LISTA DE CORTES CURADOS PARA GERAÇÃO ===")
for i, c in enumerate(curated_clips, 1):
    m_s = int(c["start"] // 60)
    s_s = int(c["start"] % 60)
    m_e = int(c["end"] // 60)
    s_e = int(c["end"] % 60)
    print(f"\n{i}. [{m_s:02d}:{s_s:02d} -> {m_e:02d}:{s_e:02d}] {c['title']} ({c['duration']}s)")
    print(f"   Tema: {c['description']}")
    print(f"   Texto: \"{c['text'][:120]}...\"")

with open("inputs/curated_cuts.json", "w", encoding="utf-8") as f:
    json.dump(curated_clips, f, indent=2, ensure_ascii=False)
