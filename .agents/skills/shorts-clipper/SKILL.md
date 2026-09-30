---
name: shorts-clipper
description: >-
  Corta e transforma automaticamente vídeos longos (YouTube ou locais) em Shorts/TikTok/Reels verticais 9:16
  com legendas dinâmicas estilo Hormozi, rastreamento de rosto com IA e aceleração de GPU (NVENC).
---

# Shorts Clipper Skill

Esta skill automatiza a extração de melhores momentos (cortes virais) a partir de vídeos longos usando a pipeline Python local em `d:\Shorts`.

## Capacidades
1. **Download & Extração**: Baixa links do YouTube ou carrega arquivos de vídeo locais em `inputs/`.
2. **Transcrição Rápida com Timestamps**: Usa `faster-whisper` em GPU CUDA para gerar transcrição no nível de cada palavra.
3. **Detecção de Gancho & Retenção**: Identifica os momentos de 30 a 60 segundos com maior probabilidade de viralizar.
4. **Enquadramento 9:16 (Face Tracking)**: Usa MediaPipe para centralizar o locutor suavemente em formato vertical.
5. **Legendas Dinâmicas**: Gera legendas no formato `.ass` com efeito de destaque (palavra ativa em amarelo/verde).
6. **Renderização Acelerada (NVENC)**: Renderiza o MP4 vertical na pasta `output/` usando a GPU NVIDIA GTX 1650.

## Como Executar

### Via CLI:
```powershell
# Cortar 3 melhores momentos de um vídeo do YouTube:
.\.venv\Scripts\python.exe main.py --url "https://www.youtube.com/watch?v=..." --clips 3

# Cortar com início e fim manuais específicos (ex: de 120s a 165s):
.\.venv\Scripts\python.exe main.py --input "inputs/meu_video.mp4" --start 120 --end 165

# Apenas listar e analisar os momentos virais sem renderizar:
.\.venv\Scripts\python.exe main.py --url "https://..." --list-only
```

### Via Interface Web (Gradio):
```powershell
# Iniciar a interface no navegador:
.\.venv\Scripts\python.exe app.py
# Ou clicar no arquivo run_web.bat
```
