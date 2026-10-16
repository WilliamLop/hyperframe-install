# 🎬 HyperFrame Install — Universal AI Skill & Video Environment Setup

Repositorio oficial de instalación rápida del entorno **HyperFrames (`@heygen/hyperframes`)**, **11 Skills especializadas** y **3 Subagentes de Producción** para edición automatizada de videos verticales de alta retención (`9:16`, `1080x1920`, `30fps`, `H.264 + AAC`).

100% compatible con:
- **Google Antigravity (AGY / Gemini)** (`GEMINI.md`, `.agents/skills/`, `.agents/agents/`)
- **Claude Code / Claude** (`CLAUDE.md`, `.claude/skills/`, `npx skills add`)
- **ChatGPT / OpenAI Codex / Cursor** (`AGENTS.md`, `~/.codex/skills/`)

---

## 📦 Qué incluye este repositorio

1. **11 Skills de HyperFrames (`skills/`):**
   - `hyperframes-short-producer` *(Skill Maestra de instalación, planificación y producción end-to-end)*
   - `hyperframes` *(Router principal de composición)*
   - `hyperframes-core`, `hyperframes-animation`, `hyperframes-audio`, `hyperframes-cli`, `hyperframes-creative`, `hyperframes-keyframes`, `hyperframes-registry`, `hyperframes-studio`, `media-use`
2. **3 Subagentes Especializados (`agents/`):**
   - `audio-mixing-subagent`: Síntesis acústica de efectos de sonido (`.wav` a `44100 Hz` en Python) + *Auto-Ducking* (`-12 dB` con voz / `0 dB` en silencios dramáticos) + DSP de voz.
   - `motion-graphics-subagent`: Movimientos de cámara con GSAP (*Ken Burns*, *Push-In*, *Camera Shake*) + VFX deterministas en Canvas 2D.
   - `subtitles-retencion-subagent`: Subtítulos dinámicos estilo Hormozi (2–5 palabras, blanco `#FFFFFF` + palabras clave `#FFD700` con *pop-in* y contraste WCAG AAA).
3. **Plantillas Base Probadas (`templates/`):**
   - `build_composition.py`, `generate_sfx.py`, `hyperframes.json`, `package.json`.
4. **Instalador Automático Multiplataforma (`scripts/setup_env.py`, `install.ps1`, `install.sh`)**:
   - Instala las skills globalmente y en tu workspace, configura `@heygen/hyperframes`, enlaza `ffmpeg`/`ffprobe` y audita la carpeta de tu nuevo video.

---

## 🚀 Cómo instalar y usar (3 formas)

### Opción A: Pedírselo directamente a tu Agente de IA (Antigravity / Claude / ChatGPT)
Pega este único prompt al iniciar un proyecto nuevo:

```text
Usa el repositorio https://github.com/WilliamLop/hyperframe-install.git para instalar las skills y configurar el entorno en la carpeta del proyecto (ejecuta `python scripts/setup_env.py --workspace . --project <nombre-carpeta-video>`). Luego lee el archivo .md dentro de la carpeta del video, analiza todas las imágenes y audios disponibles, y crea el Plan de Edición (editing_plan.md) antes de lanzar los 3 subagentes.
```

### Opción B: Instalación mediante CLI de Skills (`npx skills`)
```bash
npx skills add WilliamLop/hyperframe-install
```

### Opción C: Ejecución directa por terminal (Windows / Mac / Linux)
```powershell
# Clonar una vez
git clone https://github.com/WilliamLop/hyperframe-install.git

# Preparar cualquier carpeta de video nueva (ej. video-carro)
python hyperframe-install/scripts/setup_env.py --workspace "c:\Users\WILLIAM CL\Downloads\edicion-gemini" --project "video-carro"
```

---

## 📁 Estructura que deja lista en tu proyecto de video

Cuando ejecutas `setup_env.py` sobre una carpeta (por ejemplo `video-carro`), deja todo configurado para que solo pongas tus recursos (`.md` con la idea/guion, imágenes `escena-*.jpg` y audios `.mp3/.wav`):

```text
edicion-gemini/
├── GEMINI.md / CLAUDE.md / AGENTS.md   # Reglas automáticas para Antigravity, Claude y ChatGPT
├── .agents/
│   ├── skills/                         # Las 11 skills de HyperFrames
│   └── agents/                         # Los 3 subagentes especializados
└── video-carro/
    ├── package.json                    # @heygen/hyperframes listo
    ├── hyperframes.json                # Configuración 1080x1920 @ 30fps
    ├── .hyperframes/bin/               # ffmpeg y ffprobe listos para renderizar
    ├── subagents/                      # Carpeta para audio_layer, visual_layer, subtitles_layer
    ├── templates_ref/                  # Plantillas doradas (generate_sfx.py y build_composition.py)
    └── [Tus imágenes, audios y archivo .md del video]
```
