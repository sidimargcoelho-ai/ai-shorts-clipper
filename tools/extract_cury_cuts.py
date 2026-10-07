import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

with open("inputs/vbZquVH5bcs.transcript.json", "r", encoding="utf-8") as f:
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
    # 1. Autossabotagem e a Mente
    (300.0, 360.0, "01_Ninguem_Pode_Te_Ferir_Mais_Que_Sua_Mente", "Você pode ter inimigos fora, mas ninguém te fere mais do que seus próprios pensamentos"),
    
    # 2. A Única Empresa Que Não Pode Falir
    (1200.0, 1260.0, "02_A_Unica_Empresa_Que_Nao_Pode_Falir", "De que adianta gerenciar empresas e patrimônios se o seu EU não governa sua própria mente?"),
    
    # 3. O Que Fazer Com a Sua Dor
    (1500.0, 1560.0, "03_O_Que_Fazer_Com_A_Sua_Dor", "Não importa o que fizeram com você, o que importa é o que você faz a partir desta dor"),
    
    # 4. Líderes Entram em Colapso Antes das Empresas
    (1800.0, 1860.0, "04_Lideres_Em_Colapso_Emocional", "Antes das empresas quebrarem, os líderes colapsam por falta de gestão da emoção"),
    
    # 5. Minha Saúde Emocional é Intocável
    (2100.0, 2160.0, "05_Minha_Saude_Emocional_E_Intocavel", "Você pode me criticar ou excluir: eu não compro o que não me pertence"),
    
    # 6. Como Falar com Filhos Sem Dar Sermão
    (2700.0, 2760.0, "06_Como_Conversar_Com_Seu_Filho", "Em vez de mais um sermão que bloqueia o cérebro, provoque um choque de sabedoria"),
    
    # 7. Pais Mal-Humorados e a Perda da Leveza
    (3000.0, 3060.0, "07_Por_Que_Os_Pais_Perdem_O_Bom_Humor", "Por que com o tempo os pais deixam de ser alegres e passam a ser cobradores?"),
    
    # 8. Mente Capitalista e Coração Social
    (5100.0, 5160.0, "08_Mente_Capitalista_Coracao_Social", "Nós precisamos aprender a produzir com inteligência e sentir com o coração"),
    
    # 9. Aprenda a Ver o Invisível
    (6000.0, 6060.0, "09_Aprenda_A_Ver_O_Invisivel", "Cada tijolo tem histórias, tem lágrimas e sonhos: aprenda a enxergar além das aparências"),
    
    # 10. Janelas da Memória e Cárcere Mental
    (6600.0, 6660.0, "10_Janelas_Killer_E_Carcere_Mental", "Como um único trauma pode sequestrar a memória e gerar uma prisão psicológica")
]

selected_cuts = []
print("=== CANDIDATOS CURADOS PARA SHORTS DE AUGUSTO CURY ===")
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

with open("inputs/cury_curated_cuts.json", "w", encoding="utf-8") as f:
    json.dump(selected_cuts, f, indent=2, ensure_ascii=False)
