---
name: shorts-optimizer
description: >
  Otimiza solicitacoes no AI Shorts Clipper (d:\Shorts):
  normaliza input, reaproveita cache, evita re-download e
  re-transcricao, escolhe modelo Whisper, crop e fluxo mais barato.
---

# Shorts Optimizer Skill

> Orquestracao e economia para o pipeline em `d:\Shorts`.
> Objetivo: **nunca pagar 2x pelo mesmo trabalho**.

## 1. Como o projeto funciona

```
URL/local -> Downloader -> inputs/*.mp4 + *.wav 16kHz mono
  -> Transcriber (faster-whisper cuda/small) -> *.transcript.json
  -> HighlightDetector (30-65s, alvo 45s, score viral)
  -> FaceTracker (MediaPipe crop 9:16) + SubtitleGenerator (.ass)
  -> VideoRenderer (ffmpeg h264_nvenc -> output/1080x1920.mp4)
```

Entradas: `main.py` (CLI), `app.py` (Gradio :7860),
`tools/batch_generate_shorts.py` (curated_cuts.json por secao),
`config.yaml`, `tests/test_pipeline.py`.

## 2. Quando ativar

Ative quando o usuario pedir: corta, clipa, shorts, reels,
tiktok, melhores momentos, transcreve, legenda, viral, hook,
renderiza, 9:16, face tracking, ou citar main.py/app.py/tools.

## 3. Protocolo obrigatorio

### PASSO 0 - Normalizar
Extraia: fonte=(url|local) + escopo=(auto N|manual start-end|list-only|batch)
+ estilo=(legenda on/off, crop mode, whisper model).
Se faltar url|input, pergunte. Nunca adivinhe URL.

### PASSO 1 - Checar cache ANTES de executar
1. `inputs/*.mp4` existe? reutilizar, nao baixar.
2. `inputs/*.wav` existe? Downloader pula extracao.
3. `inputs/*.transcript.json` existe? Transcriber usa cache se
   force_recompute=False. NUNCA force sem motivo.
4. `output/Short_*` ou `inputs/sections/*_raw.mp4` >100KB? pular.
5. Video >20min? prefira `--download-sections "*ini-fim"`.

### PASSO 2 - Roteamento mais barato
- "quais trechos?": `main.py --url/--input --list-only`
- "corta N virais": primeiro `--list-only`, depois render N
- "trecho X-Y": `main.py --input ... --start X --end Y`
- "lista pronta curated_cuts.json": `tools/batch_generate_shorts.py`
- "quero clicar": `app.py` (Analisar 1x, Renderizar selecionados)
- "testar GPU": `tests/test_pipeline.py`

### PASSO 3 - Parametros (custo x qualidade)
- Whisper: tiny=triagem, small=padrao pt-BR, medium=so se errar.
  Sempre cuda/float16/pt. Fallback cpu/int8 ja existe.
- Crop: face_tracking default; sem `models/face_detector.tflite`
  ou sem rosto cai p/ center. Aula/slide use center.
- Clipping: min 30 / max 65 / alvo 45s. Overlap >10s descartada.
- Legenda: 3 palavras, MarginV 240, amarelo &H0000FFFF.
  `--no-subtitles` so se pedir sem legenda.
- Render: h264_nvenc p4 6000k/192k 1080x1920, fallback libx264.

### PASSO 4 - Execucao (venv Windows)
```powershell
.\.venv\Scripts\python.exe main.py --url "https://..." --clips 3 --list-only
.\.venv\Scripts\python.exe main.py --url "https://..." --clips 3
.\.venv\Scripts\python.exe main.py --input "inputs/meu.mp4" --start 120 --end 165
.\.venv\Scripts\python.exe main.py --input "inputs/meu.mp4" --clips 3 --no-subtitles --mode center --model tiny
.\.venv\Scripts\python.exe app.py
.\.venv\Scripts\python.exe tools/batch_generate_shorts.py
.\.venv\Scripts\python.exe tests/test_pipeline.py
```

## 4. Anti-patterns (PROIBIDO)
1. Baixar cheio se `inputs/<id>_*.mp4` existe.
2. Transcrever com force_recompute=True sem motivo.
3. Recarregar WhisperModel por clipe (1x por sessao).
4. Renderizar todos sem filtrar sobreposicao/selecao.
5. Renderizar sem list-only previo em video >30min.
6. Ignorar output/ existente e re-renderizar igual.
7. Usar medium/large-v3 de primeira na GTX 1650.
8. Path com `\` no filtro subtitles (use as_posix + escape).

## 5. Resposta padrao
```
[Optimizer] Fonte:<url|local> | Cache:<hit/miss> | Fluxo:<list|auto|manual|batch|web>
Comando: <comando exato>
```
Apos executar: clips(start->end,score) + outputs + tempo + proximo passo.

## 6. Exemplos
- "corta 3 desse link" -> checar inputs/<id>* -> list-only -> mostrar -> render.
- "60-110s do mp4" -> --start 60 --end 110 (pula detector).
- "tenho curated_cuts.json" -> batch_generate_shorts.py, nao main.py.


