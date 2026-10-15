import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

with open("inputs/1PahvipPa2A.transcript.json", "r", encoding="utf-8") as f:
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
    # 1. O Preconceito com Remédios para a Mente
    (590.0, 650.0, "01_Preconceito_Com_Remedio_Para_A_Mente", "Por que as pessoas têm vergonha de tratar a mente mas falam de remédio para o estômago?"),

    # 2. Nem Todo TDAH é Igual
    (880.0, 940.0, "02_Nem_Todo_TDAH_E_Igual", "O erro de colocar todo mundo com TDAH dentro do mesmo aquário"),

    # 3. O Caos do TDAH no Relacionamento
    (1480.0, 1542.0, "03_O_Caos_Do_TDAH_No_Relacionamento", "Como a desorganização espacial e mental do TDAH afeta a convivência do casal"),

    # 4. Falha na Comunicação do Casal
    (2100.0, 2160.0, "04_Falha_De_Comunicacao_Do_TDAH", "O TDAH pensa rápido mas muitas vezes não conclui a comunicação com o parceiro"),

    # 5. O Diagnóstico Não Justifica Tudo
    (3880.0, 3942.0, "05_O_Diagnostico_Nao_Justifica_Tudo", "Ter TDAH não é desculpa para não evoluir e não cuidar de quem você ama"),

    # 6. O Celular Está Roubando Sua Presença
    (4490.0, 4552.0, "06_O_Celular_Esta_Roubando_Sua_Presenca", "Você sai com a pessoa mas fica vidrado na tela: a falta de presença real"),

    # 7. Quando a Mente do TDAH 'Viaja' no Filme
    (5700.0, 5760.0, "07_Quando_A_Mente_Do_TDAH_Viaja", "No meio de uma conversa ou de um filme você vai para outro planeta sem querer"),

    # 8. Seres Humanos em Eterna Construção
    (6300.0, 6360.0, "08_Relacionamento_E_Evolucao_Constante", "Relacionamento exige cumplicidade, paciência e entender que ninguém nasce pronto"),

    # 9. Hiperfoco no Começo e Desatenção Depois
    (6600.0, 6660.0, "09_Hiperfoco_No_Inicio_Do_Namoro", "Por que o TDAH é super intenso no início e depois parece que se desliga?"),

    # 10. Falar Demais e Interromper o Parceiro
    (6890.0, 6950.0, "10_Falar_Demais_E_Interromper", "A impulsividade verbal do TDAH que atropela as conversas do dia a dia")
]

selected_cuts = []
print("=== CANDIDATOS CURADOS PARA SHORTS DE ALEX ROCHA (TDAH) ===")
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

with open("inputs/alex_curated_cuts.json", "w", encoding="utf-8") as f:
    json.dump(selected_cuts, f, indent=2, ensure_ascii=False)
