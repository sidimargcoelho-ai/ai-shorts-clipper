# 🎬 AI Shorts & TikTok Auto-Clipper

Sistema automatizado em Python para transformar vídeos longos (podcasts, entrevistas, aulas, lives do YouTube ou arquivos locais) em **Shorts / TikTok / Reels verticais (9:16)** com **legendas dinâmicas animadas**, **rastreamento inteligente de rosto** e **aceleração por GPU NVIDIA (NVENC)**.

---

## ⚡ Como Usar

### Opção 1: Interface Web no Navegador (Recomendado)
Dê um duplo clique no arquivo **`run_web.bat`** ou execute:
```powershell
.\.venv\Scripts\python.exe app.py
```
Acesse no seu navegador: **`http://localhost:7860`**
1. Cole a URL do YouTube ou selecione um arquivo de vídeo.
2. Clique em **"1. Analisar Vídeo e Momentos Virais"**.
3. Escolha os cortes desejados e clique em **"2. Renderizar Shorts com GPU"**.
4. Pré-visualize o vídeo vertical diretamente no navegador e baixe os arquivos prontos!

---

### Opção 2: Linha de Comando (CLI Rápido)

#### 1. Cortar automaticamente os 3 melhores momentos de um vídeo do YouTube:
```powershell
.\.venv\Scripts\python.exe main.py --url "https://www.youtube.com/watch?v=SEU_VIDEO" --clips 3
```

#### 2. Cortar a partir de um arquivo local (.mp4):
```powershell
.\.venv\Scripts\python.exe main.py --input "inputs/meu_podcast.mp4" --clips 3
```

#### 3. Cortar um trecho específico manualmente com legendas automáticas:
```powershell
.\.venv\Scripts\python.exe main.py --input "inputs/meu_video.mp4" --start 60 --end 110
```

#### 4. Apenas analisar e listar os momentos virais sem renderizar:
```powershell
.\.venv\Scripts\python.exe main.py --url "https://..." --list-only
```

---

## ⚙️ Personalização (`config.yaml`)

Você pode personalizar as cores, fontes e estilo das legendas em `config.yaml`:
* **`subtitles.font_name`**: Fonte utilizada (ex: `Arial Black`, `Montserrat`, `Impact`).
* **`subtitles.highlight_color`**: Cor da palavra falada no momento (`&H0000FFFF` para Amarelo, `&H0000FF00` para Verde).
* **`subtitles.words_per_subtitle`**: Quantidade de palavras exibidas por vez (padrão: 3 para máxima retenção).
* **`cropping.mode`**: `face_tracking` (rastreia o rosto do locutor) ou `center` (corte central).
* **`renderer.codec`**: `h264_nvenc` para usar a placa NVIDIA GTX 1650.

---

## 📁 Estrutura de Pastas

* `inputs/`: Vídeos baixados ou adicionados manualmente.
* `output/`: Shorts finais renderizados em **1080x1920 (9:16)** prontos para publicação.
* `models/`: Modelos leves de IA para detecção facial.
* `src/`: Módulos de download, transcrição, detecção viral, corte e renderização.
