import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

with open("inputs/Vlfu3whCnzI.transcript.json", "r", encoding="utf-8") as f:
    data = json.load(f)

segments = data["segments"]

def find_clip(t_start, t_end, title, description):
    sub = [s for s in segments if s["end"] >= t_start and s["start"] <= t_end]
    if not sub:
        return None
    full_text = " ".join(s["text"] for s in sub)
    return {
        "title": title,
        "description": description,
        "start": sub[0]["start"],
        "end": sub[-1]["end"],
        "duration": round(sub[-1]["end"] - sub[0]["start"], 2),
        "text": full_text
    }

candidates = [
    # 1. Nem Toda Desatenção é TDAH
    (0.0, 58.0, "01_Nem_Toda_Desatencao_E_TDAH", "Todo mundo que tem desatenção tem TDAH? A diferença entre rebaixamento atencional e transtorno"),

    # 2. Por Que Tanta Gente Só Descobre Adulto?
    (290.0, 350.0, "02_Por_Que_Tantos_Descobrem_Na_Fase_Adulta", "O diagnóstico tardio e pessoas que passaram a vida inteira sofrendo sem saber o motivo"),

    # 3. O Desamparo Aprendido: Cansei de Tentar
    (580.0, 642.0, "03_O_Desamparo_Aprendido_Do_TDAH", "Tentei tanto e não consegui que agora eu simplesmente desisti de tentar"),

    # 4. Distração vs Hiperfoco
    (880.0, 940.0, "04_Como_Funciona_A_Distraibilidade", "O que realmente acontece no cérebro quando você se distrai com facilidade"),

    # 5. O Tédio da Mente Rápida na Escola
    (1180.0, 1242.0, "05_O_Tedio_Da_Mente_Rapida", "A criança que aprende rápido e tem que ficar sentada esperando meia hora o coleguinha"),

    # 6. Funções Executivas e a Vida Adulta
    (1480.0, 1542.0, "06_Dificuldades_De_Organizacao_Na_Vida_Adulta", "Como a falha nas funções executivas paralisa o trabalho e a rotina"),

    # 7. A Sobrecarga Mental das Mulheres
    (3290.0, 3352.0, "07_A_Sobrecarga_Mental_Feminina", "Cobranças sociais: ter que dar conta de ser mãe, esposa, profissional e perfeita"),

    # 8. Como Diferenciar TDAH de Mente Sobrecarregada
    (3580.0, 3642.0, "08_Como_Diferenciar_TDAH_De_Sobrecarga", "Sempre esteve presente desde a infância ou surgiu pelo excesso de tarefas na fase adulta?")
]

selected_cuts = []
print("=== CANDIDATOS CURADOS PARA TDAH OU MENTE SOBRECARREGADA ===")
for start, end, title, desc in candidates:
    clip = find_clip(start, end, title, desc)
    if clip:
        selected_cuts.append(clip)
        m_s = int(clip["start"] // 60)
        s_s = int(clip["start"] % 60)
        m_e = int(clip["end"] // 60)
        s_e = int(clip["end"] % 60)
        print(f"\n🎬 {clip['title']} ({clip['duration']}s) [{m_s:02d}:{s_s:02d} -> {m_e:02d}:{s_e:02d}]")
        print(f"   Tema: {clip['description']}")
        print(f"   Texto: \"{clip['text'][:140]}...\"")

with open("inputs/sobrecarregada_curated_cuts.json", "w", encoding="utf-8") as f:
    json.dump(selected_cuts, f, indent=2, ensure_ascii=False)
