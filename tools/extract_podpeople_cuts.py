import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

with open("inputs/i-aKQL09x1A.transcript.json", "r", encoding="utf-8") as f:
    data = json.load(f)

segments = data["segments"]

def find_clip(t_start, t_end, title, description):
    sub = [s for s in segments if s["end"] >= t_start and s["start"] <= t_end]
    if not sub:
        return None
    full_text = " ".join(s["text"].replace("\n", " ").strip() for s in sub)
    return {
        "title": title,
        "description": description,
        "start": sub[0]["start"],
        "end": sub[-1]["end"],
        "duration": round(sub[-1]["end"] - sub[0]["start"], 2),
        "text": full_text
    }

candidates = [
    # 1. Genética dos Transtornos Mentais
    (150.0, 210.0, "01_Genetica_Dos_Transtornos_Mentais", "A predisposição genética e como os gatilhos ambientais ativam a doença"),

    # 2. Borderline e a Instabilidade Emocional
    (330.0, 390.0, "02_Borderline_E_Instabilidade", "A dor profunda do Borderline e a diferença para outros transtornos"),

    # 3. Depressão Não é Frescura: A Analogia da Pneumonia
    (510.0, 570.0, "03_Depressao_Nao_E_Falta_De_Forca_De_Vontade", "Você não diz pra quem tem pneumonia 'anima aí'; depressão é doença física do cérebro"),

    # 4. A Insônia da Depressão: Acordar às 3h da Manhã
    (870.0, 930.0, "04_A_Insonia_Terminal_Da_Depressao", "Por que quem tem depressão deita mas acorda de madrugada com angústia no peito"),

    # 5. Química Cerebral: O Cérebro Precisa de Remédio
    (690.0, 750.0, "05_A_Quimica_Cerebral_E_O_Remedio", "Quando o cérebro esgota neurotransmissores, nenhuma força de vontade resolve sozinha"),

    # 6. Famílias Disfuncionais e Traumas
    (1230.0, 1290.0, "06_Familias_Disfuncionais_E_Traumas", "Ambientes que invalidam emoções e criam adultos inseguros e ansiosos"),

    # 7. Descubra Seus Gatilhos Mentais
    (1590.0, 1650.0, "07_Descubra_Seus_Gatilhos_Mentais", "Autoconhecimento é saber exatamente quais situações te deixam vulnerável"),

    # 8. Primeiro Limpe a Depressão
    (1770.0, 1830.0, "08_Primeiro_Limpar_A_Depressao", "Não adianta tentar ser produtivo quando a mente está afundada em depressão"),

    # 9. Sucesso Sustentável vs Colapso
    (1980.0, 2040.0, "09_Sucesso_Sustentavel_Vs_Colapso", "De que adianta vencer lá fora se o seu cérebro está em ruínas por dentro?"),

    # 10. A Lógica do Funcionamento Cerebral
    (2160.0, 2220.0, "10_A_Logica_Do_Funcionamento_Cerebral", "Respeite os limites biológicos do seu cérebro antes que ele te pare à força"),

    # 11. Sinais de Que a Criança Está Sofrendo
    (2490.0, 2550.0, "11_Sinais_De_Que_A_Crianca_Esta_Sofrendo", "Mudança súbita de comportamento, bullying e silêncio são pedidos de socorro"),

    # 12. Ambientes Agressivos Adoecem a Mente
    (2670.0, 2730.0, "12_Ambientes_Agressivos_Adoecem", "Crescer em ambientes de briga constante altera a estrutura neurológica"),

    # 13. O Poder de Escrever o Que Sente
    (2850.0, 2910.0, "13_O_Poder_De_Externalizar_Emocoes", "Escrever e botar pra fora o sofrimento alivia a sobrecarga da amígdala cerebral"),

    # 14. Por Que Nossos Pais Eram Mais Regulados?
    (3030.0, 3090.0, "14_Por_Que_Antes_Eramos_Mais_Regulados", "Sem o vício das telas, as pessoas conversavam e regulavam suas emoções com presença"),

    # 15. Conhecimento Certo Traz a Cura
    (3180.0, 3240.0, "15_Conhecimento_Certo_Traz_A_Cura", "Informação correta liberta da culpa e mostra o caminho para recuperar a saúde mental")
]

selected_cuts = []
print("=== 15 CORTES SELECIONADOS: DRA. ANA BEATRIZ (PODPEOPLE EP. 049) ===")
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

with open("inputs/podpeople_curated_cuts.json", "w", encoding="utf-8") as f:
    json.dump(selected_cuts, f, indent=2, ensure_ascii=False)
