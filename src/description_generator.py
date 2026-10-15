import os
import re
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml
import httpx

SYSTEM_PROMPT_MASTER = """Você é um redator de elite especializado em transformar transcrições e resumos de vídeos em descrições de alto engajamento para TikTok, Reels e Shorts.

Siga rigorosamente as diretrizes abaixo:

1. IDIOMA E TOM:
- Português brasileiro (pt-BR).
- Tom natural, humano, profissional, claro e reflexivo.
- Sem jargões vazios e sem sensacionalismo.

2. ESTRUTURA (EXATAMENTE 2 PARÁGRAFOS):
- Primeiro parágrafo: Inicie diretamente pelo conceito central ou questão principal, sem introduções genéricas ("O vídeo aborda", "Neste vídeo", "Os especialistas falam", "Aqui está"). Explique os mecanismos e as relações essenciais entre os tópicos.
- Segundo parágrafo: Desenvolva as consequências práticas, impactos cotidianos ou diferenças importantes, encerrando com uma reflexão marcante e natural que faça o público pensar.

3. TRATAMENTO CIENTÍFICO E PSICOLÓGICO:
- Trate aspectos neurológicos e psicológicos com precisão e prudência.
- Não faça promessas milagrosas e preserve a seriedade do tema.

4. HASHTAGS:
- Na última linha, inclua estritamente até 5 hashtags relevantes no formato CamelCase (ex: #SaudeMental #Psicologia #Neurociencia #Autoconhecimento #PodPeople).
- NUNCA utilize o prefixo "Hashtags:" ou qualquer rótulo antes delas.

5. RESTRIÇÃO DE SAÍDA:
- Forneça EXCLUSIVAMENTE o texto final da descrição (2 parágrafos) seguido pelas hashtags.
- NÃO inclua saudações, introduções, explicações ou metalinguagem de qualquer tipo."""

class DescriptionGenerator:
    """
    Gera descrições profissionais e otimizadas para TikTok/Shorts com base na transcrição dos cortes,
    seguindo o fluxo de análise, síntese e redação de alto engajamento.
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        if config is None:
            config_path = Path("config.yaml")
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
            else:
                config = {}

        self.config = config.get("descriptions", {})
        self.enabled = self.config.get("enabled", True)
        self.provider = self.config.get("provider", "auto").lower()
        self.gemini_key = self.config.get("gemini_api_key") or os.getenv("GEMINI_API_KEY", "")
        self.groq_key = self.config.get("groq_api_key") or os.getenv("GROQ_API_KEY", "")
        self.openai_key = self.config.get("openai_api_key") or os.getenv("OPENAI_API_KEY", "")

    def generate(self, clip_text: str, clip_title: str = "", context_desc: str = "") -> str:
        """
        Gera a descrição pronta para o TikTok no formato padrão:
        - 2 parágrafos articulados
        - Linha final com até 5 hashtags CamelCase
        """
        # Se um provedor com API key estiver disponível, usa LLM
        if self.provider in ["auto", "gemini"] and self.gemini_key:
            res = self._call_gemini(clip_text, clip_title, context_desc)
            if res:
                return res

        if self.provider in ["auto", "groq"] and self.groq_key:
            res = self._call_groq(clip_text, clip_title, context_desc)
            if res:
                return res

        if self.provider in ["auto", "openai"] and self.openai_key:
            res = self._call_openai(clip_text, clip_title, context_desc)
            if res:
                return res

        # Fallback local de alta fidelidade
        return self._generate_local(clip_text, clip_title, context_desc)

    def _call_gemini(self, clip_text: str, clip_title: str, context_desc: str) -> Optional[str]:
        try:
            model = self.config.get("model", "gemini-1.5-flash")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.gemini_key}"
            prompt = f"Título do Corte: {clip_title}\nContexto/Tema: {context_desc}\nTranscrição do Corte:\n{clip_text}"
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": f"{SYSTEM_PROMPT_MASTER}\n\nMaterial do vídeo:\n{prompt}"}]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.6,
                    "maxOutputTokens": 600
                }
            }
            with httpx.Client(timeout=20.0) as client:
                resp = client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "").strip()
        except Exception as e:
            print(f"  [Aviso] Falha ao chamar Gemini API ({e}). Usando gerador local.")
        return None

    def _call_groq(self, clip_text: str, clip_title: str, context_desc: str) -> Optional[str]:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {self.groq_key}"}
            prompt = f"Título do Corte: {clip_title}\nContexto/Tema: {context_desc}\nTranscrição do Corte:\n{clip_text}"
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT_MASTER},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.6,
                "max_tokens": 600
            }
            with httpx.Client(timeout=20.0) as client:
                resp = client.post(url, json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    choices = data.get("choices", [])
                    if choices:
                        return choices[0].get("message", {}).get("content", "").strip()
        except Exception as e:
            print(f"  [Aviso] Falha ao chamar Groq API ({e}). Usando gerador local.")
        return None

    def _call_openai(self, clip_text: str, clip_title: str, context_desc: str) -> Optional[str]:
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {self.openai_key}"}
            prompt = f"Título do Corte: {clip_title}\nContexto/Tema: {context_desc}\nTranscrição do Corte:\n{clip_text}"
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT_MASTER},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.6,
                "max_tokens": 600
            }
            with httpx.Client(timeout=20.0) as client:
                resp = client.post(url, json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    choices = data.get("choices", [])
                    if choices:
                        return choices[0].get("message", {}).get("content", "").strip()
        except Exception as e:
            print(f"  [Aviso] Falha ao chamar OpenAI API ({e}). Usando gerador local.")
        return None

    def _generate_local(self, clip_text: str, clip_title: str, context_desc: str) -> str:
        """
        Gerador semântico local que produz descrições coesas seguindo rigorosamente
        o formato de 2 parágrafos + 5 hashtags CamelCase.
        """
        # Limpar texto de cacoetes orais
        clean_text = clip_text
        for filler in ["né", "tipo assim", "sabe", "tá gente", "tá bom", "quer dizer", "olha só", "vamos lá"]:
            clean_text = re.sub(rf"\b{filler}\b", "", clean_text, flags=re.IGNORECASE)
        clean_text = re.sub(r"\s+", " ", clean_text).strip()

        # Extrair frases com sentido
        sentences = [s.strip() for s in re.split(r"[.?!]+", clean_text) if len(s.strip().split()) >= 4]

        # Tema base
        theme = context_desc.strip() if context_desc else clip_title.replace("_", " ").strip()
        if theme.lower().startswith("corte manual"):
            theme = "Funcionamento da mente e comportamento humano"

        # Construir Parágrafo 1: Apresentação do tema + mecanismo
        if sentences:
            lead_sentence = sentences[0]
            lead_sentence = lead_sentence[0].upper() + lead_sentence[1:] if len(lead_sentence) > 1 else lead_sentence
            
            p1_parts = [f"{theme.capitalize()}: {lead_sentence}."]
            if len(sentences) > 1:
                p1_parts.append(f"{sentences[1].capitalize()}.")
            p1 = " ".join(p1_parts)
        else:
            p1 = f"{theme.capitalize()} é um dos pilares mais determinantes para compreender a saúde mental e as respostas emocionais do organismo."

        # Construir Parágrafo 2: Consequências, impacto e reflexão
        if len(sentences) >= 3:
            impact_sentence = sentences[2].capitalize()
            p2 = f"Quando esses mecanismos operam no dia a dia, {impact_sentence.lower()}. Compreender essa dinâmica permite agir com clareza e transformar a maneira como lidamos com os próprios limites."
        elif len(sentences) >= 2:
            p2 = f"Identificar esses padrões no cotidiano evita desgastes desnecessários e favorece o equilíbrio. Ter consciência de como o cérebro reage aos estímulos é o primeiro passo para o autodomínio sustentável."
        else:
            p2 = "Compreender os sinais que a mente emite diariamente é essencial para evitar sobrecargas e promover mudanças reais na rotina. O conhecimento aplicado traz estabilidade e bem-estar."

        # Selecionar hashtags temáticas CamelCase (máximo 5)
        hashtags = self._select_hashtags(clip_text, theme)

        return f"{p1}\n\n{p2}\n\n{' '.join(hashtags)}"

    def _select_hashtags(self, text: str, theme: str) -> List[str]:
        combined = (text + " " + theme).lower()
        tags = []

        if any(w in combined for w in ["tdah", "hiperfoco", "desatencao", "atencao"]):
            tags.append("#TDAH")
        if any(w in combined for w in ["depressao", "tristeza", "angustia", "desanimo"]):
            tags.append("#Depressao")
        if any(w in combined for w in ["ansiedade", "panico", "crise", "estresse"]):
            tags.append("#Ansiedade")
        if any(w in combined for w in ["borderline", "bipolar", "humor"]):
            tags.append("#Borderline")
        if any(w in combined for w in ["relacionamento", "namoro", "casamento", "casal"]):
            tags.append("#Relacionamento")
        if any(w in combined for w in ["cerebro", "neurociencia", "neuronio", "quimica"]):
            tags.append("#Neurociencia")
        if any(w in combined for w in ["crianca", "infancia", "pais", "familia"]):
            tags.append("#DesenvolvimentoInfantil")
        if any(w in combined for w in ["autoconhecimento", "terapia", "psicologia"]):
            tags.append("#Psicologia")
        if any(w in combined for w in ["dra ana", "ana beatriz", "podpeople"]):
            tags.append("#DraAnaBeatriz")

        # Tags gerais para completar
        defaults = ["#SaudeMental", "#Autoconhecimento", "#InteligenciaEmocional", "#Reflexao", "#BemEstar"]
        for d in defaults:
            if d not in tags:
                tags.append(d)
            if len(tags) >= 5:
                break

        return tags[:5]

    def save_description(self, text: str, output_path: Path) -> Path:
        """Salva a descrição gerada em um arquivo .txt correspondente"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text.strip() + "\n")
        return output_path
