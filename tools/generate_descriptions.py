import os
import sys
import json
from pathlib import Path

# Adicionar raiz ao PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.description_generator import DescriptionGenerator

def generate_podpeople_descriptions():
    cuts_file = Path("inputs/podpeople_curated_cuts.json")
    if not cuts_file.exists():
        print(f"Arquivo {cuts_file} não encontrado.")
        return

    with open(cuts_file, "r", encoding="utf-8") as f:
        clips = json.load(f)

    desc_gen = DescriptionGenerator()
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("📝 GERANDO DESCRIÇÕES PARA TIKTOK (15 SHORTS DA DRA. ANA BEATRIZ)")
    print("=" * 60)

    # Descrições especializadas e detalhadas para os 15 cortes da Dra. Ana Beatriz
    # seguindo rigorosamente:
    # - 2 parágrafos
    # - Início direto sem clichês ("O vídeo aborda", etc.)
    # - Conexão de causas, sintomas e impactos no cotidiano
    # - Linguagem clara, científica e empática
    # - Até 5 hashtags no formato CamelCase sem a palavra "Hashtags:"
    curated_descriptions = {
        "01_Genetica_Dos_Transtornos_Mentais": (
            "A vulnerabilidade para o desenvolvimento de transtornos mentais, como o borderline e a depressão, carrega uma base biológica significativa. Embora os estudos científicos ainda variem entre 35% e 50% de herdabilidade genética, a herança biológica não atua de forma isolada: ela funciona como uma predisposição que aguarda condições do ambiente para se manifestar.\n\n"
            "É no início da infância que a estrutura afetiva se consolida através da validação emocional e da segurança oferecida pelos cuidadores. Quando um organismo geneticamente vulnerável é exposto a ambientes instáveis ou negligentes, o risco de sofrimento psíquico na vida adulta se multiplica, tornando o acolhimento precoce um fator indispensável de proteção.\n\n"
            "#SaudeMental #DraAnaBeatriz #Borderline #Genetica #Neurociencia"
        ),
        "02_Borderline_E_Instabilidade": (
            "O Transtorno de Personalidade Borderline é caracterizado por uma dor psíquica intensa e uma profunda dificuldade na regulação emocional. Longe de ser apenas uma instabilidade superficial de humor, a condição envolve a interação de fatores genéticos com vivências traumáticas que marcaram a formação afetiva do indivíduo.\n\n"
            "Compreender a complexidade do borderline é fundamental para afastar o estigma e o julgamento que costumam cercar as pessoas diagnosticadas. Sem a devida orientação clínica e terapêutica especializada, a pessoa permanece presa a ciclos de angústia e rupturas relacionais que poderiam ser manejados com tratamento adequado.\n\n"
            "#Borderline #DraAnaBeatriz #SaudeMental #Psicologia #RegulacaoEmocional"
        ),
        "03_Depressao_Nao_E_Falta_De_Forca_De_Vontade": (
            "A depressão profunda é uma alteração biológica e metabólica do sistema nervoso central, e não uma fraqueza de caráter ou falta de força de vontade. Da mesma forma que não se pede para alguém com pneumonia respirar fundo na praia para se curar, não se deve exigir ânimo espontâneo de um cérebro com depleção neuroquímica severa.\n\n"
            "Cobrar positividade ou esforço de quem está em crise depressiva apenas amplifica a culpa e atrasa a busca por socorro profissional. O tratamento clínico adequado — unindo psicofármacos e psicoterapia — é indispensável para restabelecer os circuitos cerebrais e devolver à pessoa a capacidade funcional de viver.\n\n"
            "#Depressao #DraAnaBeatriz #SaudeMental #Neurociencia #Psicologia"
        ),
        "04_A_Insonia_Terminal_Da_Depressao": (
            "O estresse crônico não tratado desregula todo o metabolismo corporal e sobrecarrega o sistema cardiovascular, frequentemente evoluindo para quadros depressivos graves. Um dos sinais biológicos mais característicos dessa transição é a chamada insônia terminal, quando o indivíduo adormece, mas desperta subitamente entre 3 e 4 horas da manhã sem conseguir retomar o repouso.\n\n"
            "Esse despertar precoce geralmente vem acompanhado de angústia matinal intensa, anedonia e perda total de interesse por atividades que antes traziam satisfação. Reconhecer essas alterações metabólicas e do sono é vital para intervir clinicamente antes que o colapso físico e emocional se aprofunde.\n\n"
            "#Insonia #Depressao #Estresse #DraAnaBeatriz #SaudeMental"
        ),
        "05_A_Quimica_Cerebral_E_O_Remedio": (
            "A abordagem terapêutica da depressão profunda exige diferenciar episódios unipolares de transtornos recorrentes ou manifestações de bipolaridade. Quando os neurotransmissores atingem níveis críticos de esgotamento químico, técnicas comportamentais isoladas não conseguem reverter o quadro sem o suporte médico necessário.\n\n"
            "Assim como uma infecção pulmonar requer intervenção farmacológica direcionada, o cérebro em colapso químico precisa de medicação para recalibrar sua fisiologia básica. Restabelecer o equilíbrio biológico é a condição fundamental para que a psicoterapia e as mudanças de estilo de vida tenham real eficácia.\n\n"
            "#Neuroquimica #Depressao #Psiquiatria #DraAnaBeatriz #SaudeMental"
        ),
        "06_Familias_Disfuncionais_E_Traumas": (
            "A neuropsicologia do trauma infantil demonstra que crescer em ambientes com cuidadores emocionalmente disfuncionais compromete o desenvolvimento saudável do cérebro. A faixa etária entre 4 e 6 anos é uma janela crucial na qual a criança aprende a identificar, nomear e acolher aquilo que sente a partir da validação que recebe dos pais.\n\n"
            "Ambientes familiares marcados pela invalidação constante ou pela hostilidade forçam o cérebro da criança a permanecer em estado de alerta permanente. Como consequência, esses indivíduos frequentemente se tornam adultos hipervigilantes, com baixa tolerância à frustração e vulneráveis a quadros crônicos de ansiedade e depressão.\n\n"
            "#TraumaInfantil #DesenvolvimentoInfantil #DraAnaBeatriz #Psicologia #SaudeMental"
        ),
        "07_Descubra_Seus_Gatilhos_Mentais": (
            "A estabilização clínica com medicação psiquiátrica tem a função de apagar o incêndio dos sintomas agudos, mas a sustentação do bem-estar depende do processo psicoterapêutico. É por meio do autoconhecimento direcionado que a pessoa mapeia seus gatilhos mentais — aquelas circunstâncias e dinâmicas relacionais que deflagram crises de ansiedade, pânico ou depressão.\n\n"
            "Saber exatamente quais estímulos acionam a vulnerabilidade do próprio organismo transforma o medo da recaída em capacidade de autogerenciamento. Compreender a própria mente permite antecipar respostas emocionais e estabelecer limites antes que o estresse atinja o ponto de ruptura.\n\n"
            "#GatilhosEmocionais #Autoconhecimento #Terapia #DraAnaBeatriz #InteligenciaEmocional"
        ),
        "08_Primeiro_Limpar_A_Depressao": (
            "O processo de reflexão e autoconhecimento profundo exige uma base mínima de energia psíquica e estabilidade emocional para ser produtivo. Quando a mente está dominada por ruminações pessimistas, névoa cognitiva e fadiga extrema decorrentes da depressão, forçar reflexões complexas pode apenas amplificar o desgaste e a sensação de incapacidade.\n\n"
            "A prioridade inicial do tratamento deve ser sempre limpar o quadro depressivo agudo e devolver a homeostase ao cérebro. Uma vez recuperada a lucidez e a clareza mental, o indivíduo passa a ter as condições cognitivas necessárias para ressignificar a própria história e planejar o futuro.\n\n"
            "#Depressao #ClarezaMental #SaudeMental #DraAnaBeatriz #Recuperacao"
        ),
        "09_Sucesso_Sustentavel_Vs_Colapso": (
            "Transformações humanas autênticas e consolidadas não acontecem por meio de choques emocionais em eventos de poucos dias ou fórmulas mágicas instantâneas. Qualquer ideia de sucesso que exija o sacrifício crônico do equilíbrio cerebral e emocional resulta em colapso biológico a médio e longo prazo.\n\n"
            "A verdadeira sustentabilidade do desempenho profissional parte do respeito aos limites da própria mente e de um compromisso contínuo de aprendizagem. A motivação passageira pode até servir como ponto de partida, mas a consistência real depende da construção diária de hábitos saudáveis.\n\n"
            "#SucessoSustentavel #Burnout #DraAnaBeatriz #Produtividade #SaudeMental"
        ),
        "10_A_Logica_Do_Funcionamento_Cerebral": (
            "O cérebro humano opera sob regras biológicas claras e limites fisiológicos bem definidos que não podem ser contornados pela força do pensamento positivo. A evolução pessoal é um processo diário de aprendizagem, adaptação e autorregulação, e não um salto repentino decorrente de soluções milagrosas.\n\n"
            "Buscar atalhos mágicos para resolver questões complexas da mente gera frustração crônica e esgotamento. Ao compreender a lógica biológica do cérebro, aprendemos a respeitar o tempo das mudanças e a valorizar as pequenas melhorias diárias que consolidam a estabilidade psíquica.\n\n"
            "#Neurociencia #DesenvolvimentoPessoal #DraAnaBeatriz #Habitos #SaudeMental"
        ),
        "11_Sinais_De_Que_A_Crianca_Esta_Sofrendo": (
            "Crianças raramente conseguem comunicar o sofrimento psicológico em palavras elaboradas; o estresse infantil manifesta-se prioritariamente por meio de mudanças bruscas de comportamento. Queda inesperada no rendimento escolar, isolamento repentino, crises de agressividade ou silêncio excessivo costumam ser os sinais visíveis de um pedido silencioso de ajuda.\n\n"
            "Fatores como bullying, assédio psicológico, pressões familiares e conflitos na rotina doméstica impactam diretamente a segurança emocional dos pequenos. Estar atento às alterações de humor e manter uma escuta aberta é a melhor forma de proteger a integridade emocional das crianças em formação.\n\n"
            "#SaudeInfantil #PaisEEfilhos #Bullying #DraAnaBeatriz #ComportamentoInfantil"
        ),
        "12_Ambientes_Agressivos_Adoecem": (
            "O aumento visível da agressividade e da intolerância nas relações cotidianas reflete um cenário generalizado de desregulação emocional. Quando os indivíduos perdem a capacidade de reconhecer aquilo que sentem e de gerenciar suas reações, o convívio social se torna tenso e conflituoso.\n\n"
            "A educação socioemocional precisa ser tratada como um compromisso conjunto entre famílias, escolas e toda a sociedade. Ambientes que promovem o diálogo e ensinam a lidar com a frustração ajudam a conter a escalada da violência e preservam a saúde mental coletiva.\n\n"
            "#RegulacaoEmocional #EducacaoEmocional #DraAnaBeatriz #Sociedade #SaudeMental"
        ),
        "13_O_Poder_De_Externalizar_Emocoes": (
            "A prática de escrever sobre as próprias experiências e colocar em palavras os sentimentos cotidianos fortalece a chamada memória autobiográfica. Externalizar conflitos e vitórias permite que a mente organize a própria narrativa de vida, aliviando a sobrecarga emocional acumulada nas estruturas límbicas do cérebro.\n\n"
            "O hábito de registrar pensamentos cria um espaço seguro de privacidade e elaboração interna que hoje foi quase totalmente substituído pela superexposição digital. Resgatar momentos de intimidade consigo mesmo é uma ferramenta simples e poderosa para cultivar clareza e autorregulação mental.\n\n"
            "#EscritaTerapeutica #Autoconhecimento #DraAnaBeatriz #SaudeEmocional #Reflexao"
        ),
        "14_Por_Que_Antes_Eramos_Mais_Regulados": (
            "O excesso de estímulos digitais e a conexão contínua reduziram drasticamente os momentos de conversa presencial e partilha genuína de sentimentos. Em décadas anteriores, sem a distração incessante das telas, o contato interpessoal diário funcionava como um regulador natural das emoções humanas.\n\n"
            "Não é possível gerenciar ou acolher sentimentos que sequer somos capazes de identificar ou nomear com calma. Recuperar a presença nas interações e aprender a desacelerar a rotina são passos indispensáveis para reencontrar o equilíbrio emocional em meio ao barulho do mundo contemporâneo.\n\n"
            "#DesconexaoDigital #Presente #DraAnaBeatriz #EquilibrioEmocional #SaudeMental"
        ),
        "15_Conhecimento_Certo_Traz_A_Cura": (
            "O acesso a informações embasadas sobre saúde mental e neurociência liberta as pessoas da culpa e desmistifica os preconceitos que atrasam a busca por auxílio. Quando o público compreende que o adoecimento psíquico possui causas biológicas e ambientais claras, o caminho para a recuperação se torna mais acessível.\n\n"
            "Tirar dúvidas abertamente e debater sintomas sem tabus estimula a prevenção e incentiva o acolhimento dentro das famílias e círculos sociais. O conhecimento verdadeiro não apenas esclarece a mente, mas salva vidas ao indicar a direção correta do tratamento.\n\n"
            "#ConhecimentoLiberta #DraAnaBeatriz #SaudeMental #Psiquiatria #Acolhimento"
        )
    }

    generated_count = 0
    for clip in clips:
        title = clip["title"]
        mp4_name = f"Short_PodPeople_{title}.mp4"
        txt_name = f"Short_PodPeople_{title}.txt"
        txt_path = output_dir / txt_name

        # Se temos uma versão curada de alta precisão
        if title in curated_descriptions:
            content = curated_descriptions[title]
        else:
            content = desc_gen.generate(
                clip_text=clip.get("text", ""),
                clip_title=title,
                context_desc=clip.get("description", "")
            )

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")

        print(f"  ✅ [TXT Gerado] {txt_name}")
        generated_count += 1

    print("=" * 60)
    print(f"🎉 TODAS AS {generated_count} DESCRIÇÕES FORAM GERADAS COM SUCESSO!")
    print("=" * 60)

if __name__ == "__main__":
    generate_podpeople_descriptions()
