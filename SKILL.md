---
name: hyperframes-short-producer
description: >-
  Installs and configures the complete HyperFrames video editing environment, skills,
  and 3-subagent pipeline (Audio Mixing + SFX, GSAP Motion Graphics + VFX, Dynamic Subtitles),
  then analyzes a project folder and its .md video brief to plan, assemble, validate, and render
  high-retention vertical videos (9:16, 1080x1920, 30fps). Compatible with Antigravity, Claude, and ChatGPT/Codex.
---

# HyperFrames Short Producer (Instalación + Producción End-to-End)

Usa esta skill cuando el usuario quiera:
1. **Instalar y dejar listo el entorno de HyperFrames** con todas las sub-skills (`hyperframes-core`, `hyperframes-audio`, `hyperframes-animation`, `hyperframes-cli`, etc.) y los 3 subagentes especializados.
2. **Iniciar un nuevo proyecto de video** a partir de una carpeta con recursos (`.md` del guion/idea, imágenes `escena-*.jpg/.png`, locución `.mp3` y música `.wav`).

---

## Paso 1: Instalación Automática y Preparación del Entorno

Antes de analizar o editar un proyecto nuevo, ejecuta el script de inicialización incluido en este repositorio para instalar todas las skills de HyperFrames, configurar `@heygen/hyperframes`, preparar `ffmpeg`/`ffprobe` y auditar los archivos de la carpeta del video:

```bash
python scripts/setup_env.py --workspace "<ruta-raiz-edicion>" --project "<nombre-carpeta-video>"
```

*(Si aún no tienes clonado el repositorio en el entorno actual, clónalo primero con: `git clone https://github.com/WilliamLop/hyperframe-install.git` y ejecuta `python hyperframe-install/scripts/setup_env.py --workspace . --project "<carpeta-video>"`).*

### Qué deja listo `setup_env.py`:
- Instala las **10 skills de HyperFrames** en las rutas globales y locales de **Antigravity** (`~/.gemini/skills/`, `.agents/skills/`), **Claude** (`~/.claude/skills/`) y **ChatGPT/Codex** (`~/.codex/skills/`).
- Instala los **3 Subagentes Especializados** en `.agents/agents/`:
  1. `audio-mixing-subagent`
  2. `motion-graphics-subagent`
  3. `subtitles-retencion-subagent`
- Crea `package.json`, `hyperframes.json`, instala o reutiliza `node_modules/@heygen/hyperframes`, configura `.hyperframes/bin/ffmpeg` y copia las plantillas base en `templates_ref/`.

---

## Paso 2: Análisis de la Carpeta y del `.md` del Video -> `editing_plan.md`

Una vez listo el entorno en la carpeta del proyecto:
1. Lee el archivo `.md` proporcionado por el usuario con la historia, guion o instrucciones del video.
2. Audita la duración exacta de la locución y la música con `ffprobe` y verifica las dimensiones de todas las imágenes.
3. Genera `editing_plan.md` en la carpeta del proyecto con:
   - **Desglose de planos cada `1.8s - 2.4s`** (ninguna imagen estática).
   - **Mapa de tiempos de la locución** y ventanas de silencio dramático.
   - **Curva de Auto-Ducking** (`-12 dB` / `v: 0.25` cuando hay voz; `0 dB` / `v: 0.90+` en silencios dramáticos).
   - **Diseño de SFX sintetizados en WAV** y **Efectos Visuales (Canvas 2D)** por escena.

---

## Paso 3: Producción Modular en 3 Capas (`subagents/`)

Ejecuta en paralelo los 3 subagentes (en Antigravity/Claude) o construye secuencialmente los 3 módulos JSON tomando como base `templates_ref/`:

1. **Capa 1 — Audio Mixing & SFX (`subagents/audio_layer.json` + `generate_sfx.py`):**
   - Sintetiza en Python (`44100 Hz`, 16-bit PCM) los archivos `.wav` de efectos de sonido orgánicos de cada escena.
   - Configura `voiceover` (`0 dB`, EQ + compresor) y `music-bed` (`data-fx-carve` + `data-automation` para Auto-Ducking).
2. **Capa 2 — Motion Graphics & VFX (`subagents/visual_layer.json`):**
   - Movimientos de cámara con GSAP (`scale`, `x`, `y`, `rotation`) aplicados sobre `.shot-inner` (nunca sobre `.clip`).
   - Cortes rápidos en el clímax con *Camera Shake* determinista y transiciones *Cross-Dissolve* o *Flash/Glow*.
   - Canvas 2D determinista sincronizado a `mainTl.time()`.
3. **Capa 3 — Subtítulos Dinámicos (`subagents/subtitles_layer.json`):**
   - Bloques de **2 a 5 palabras** centrados con Flexbox en `top: 1260px`.
   - Texto blanco `#FFFFFF` con borde negro + palabras clave `<span class="kw">` en **Dorado (`#FFD700`)** con `display: inline-block` y animación *pop-in* (`back.out(2.2)`).

---

## Paso 4: Ensamblaje, Linter y Renderizado Final

1. Adapta y ejecuta `python build_composition.py` para generar `index.html` y `hyperframes.json`.
2. Valida la composición con:
   ```bash
   npx hyperframes check
   ```
   Asegúrate de obtener **0 errores** y **100% contrast checks passed** (recuerda: nunca usar `transform` en CSS sobre elementos animados con GSAP y nunca usar `<br>` en subtítulos).
3. Renderiza el video final en MP4 (`1080x1920`, `30fps`, H.264 + AAC):
   ```bash
   npx hyperframes render --output video_final.mp4
   ```
