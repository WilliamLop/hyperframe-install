# Estándar Maestro de Producción de Videos Verticales (HyperFrames 9:16)

Este directorio (`edicion-gemini`) contiene proyectos de edición de video vertical de alta retención (`1080x1920`, `30fps`, `H.264 + AAC`) renderizados con **HyperFrames (`@heygen/hyperframes`)** y **GSAP 3.12.5**.

El proyecto [**`video-caballo`**](./video-caballo/) es la **Referencia Dorada (Golden Reference)** de arquitectura, calidad visual, mezcla de sonido y retención. Cualquier modelo (incluyendo modelos rápidos como **Flash**) DEBE seguir estrictamente esta guía y reutilizar la arquitectura probada de `video-caballo`.

---

## 1. Flujo de Trabajo Obligatorio en 4 Fases

1. **Fase 1 — Auditoría y Plan de Edición (`editing_plan.md`):**
   - Inspecciona todos los archivos de la carpeta del proyecto (imágenes `.jpg/.png`, locución `.mp3/.wav`, música `.wav/.mp3`).
   - Verifica la duración exacta de los audios con `ffprobe` (disponible en `../bin/ffprobe.exe` o `../video-caballo/bin/ffprobe.exe`) y transcribe o alinea los timestamps exactos de la voz en off.
   - Si alguna imagen clave tiene baja resolución, mejórala o prioriza el uso de las imágenes 2K con re-encuadres dinámicos (planos generales + *close-ups* macro).
   - Crea `editing_plan.md` documentando el guion técnico segundo a segundo (`0.0s` al final), cambios de plano cada `1.8s - 2.4s`, curvas de *auto-ducking* y diseño de efectos de sonido (SFX).

2. **Fase 2 — Ejecución con 3 Subagentes Especializados (o Capas Modulares en `subagents/`):**
   Divide el ensamblaje en 3 módulos JSON dentro de `subagents/`:
   - **Subagente 1 (`audio-mixing-subagent` -> `subagents/audio_layer.json` + `generate_sfx.py`):**
     - Sintetiza en Python (`wave`, `struct`, `math`, `random` con semilla fija, `44100 Hz`, 16-bit) los efectos de sonido (SFX) específicos de cada escena para no depender de descargas externas.
     - Configura la voz en off a `0 dB` (`data-volume="1.0"`) con cadena DSP (`highpass 85Hz`, `peaking 3200Hz +2dB`, `compressor`).
     - Configura la música con `data-fx-carve` hacia `"voiceover"` y curva de automatización (`data-automation`) para **Auto-Ducking**: baja a `-12 dB` (`v: 0.25`) cuando habla el narrador y sube en los silencios dramáticos (`v: 0.88 - 0.95`).
   - **Subagente 2 (`motion-graphics-subagent` -> `subagents/visual_layer.json`):**
     - Ninguna imagen estática: aplica *Ken Burns*, *Push-In*, *Pull-Back*, *Pan* lateral/vertical, *Camera Shake* determinista en el clímax y transiciones (*Cross-Dissolve* solapando `0.35s - 0.45s` o *Flash/Glow* en giros dramáticos).
     - Añade **Canvas 2D de VFX deterministas** sincronizados exclusivamente al tiempo `t` de la timeline principal (`mainTl.time()`), tales como lluvia, partículas doradas, destellos de lente (*lens flare*), chispas, humo, luces de neón/estadio o confeti, más fundido a negro en el último segundo.
   - **Subagente 3 (`subtitles-retencion-subagent` -> `subagents/subtitles_layer.json`):**
     - Subtítulos dinámicos estilo Hormozi / Cinematográfico en bloques cortos de **2 a 5 palabras** centrados en el tercio medio-inferior (`top: 1260px`, `height: 260px`, `left: 60px`, `right: 60px`).
     - Tipografía `900` uppercase blanca (`#FFFFFF`) con borde negro (`-webkit-text-stroke: 2.5px #000`), sombra profunda y contenedor translúcido oscuro (`rgba(8, 10, 18, 0.72)`) para aprobar el 100% de las pruebas de contraste WCAG AAA.
     - Palabras clave envueltas en `<span class="kw">` en color **Dorado (`#FFD700`)** o color de acento temático, con animación *pop-in* (`back.out(2.2)`).

3. **Fase 3 — Ensamblaje (`build_composition.py`) y Validación (`npx hyperframes check`):**
   - Ensambla `subagents/visual_layer.json`, `subagents/subtitles_layer.json` y las pistas de audio en `index.html` + `hyperframes.json`.
   - Ejecuta siempre `npx hyperframes check` y corrige cualquier advertencia hasta obtener **0 errores y 100% contrast checks passed**.

4. **Fase 4 — Renderizado Final (`npx hyperframes render`):**
   - Renderiza a `1080x1920`, `30fps`, `H.264 + AAC` y verifica el archivo `.mp4` resultante con `ffprobe`.

---

## 2. Reglas Técnicas Críticas de HyperFrames (Evitar Errores de Linter y Render)

1. **PROHIBIDO mezclar `transform` en CSS con animaciones GSAP (`gsap_css_transform_conflict`):**
   - Nunca pongas `transform: translate(...)` ni `transform: scale(...)` en las reglas CSS de elementos que vayan a ser animados con GSAP (`x`, `y`, `scale`, `rotation`).
   - Para centrar subtítulos o tarjetas, usa Flexbox en el contenedor padre (`display: flex; justify-content: center; align-items: center;`) y anima el hijo (`.sub-box`).
2. **`display: inline-block` obligatorio en `<span class="kw">` (`gsap_inline_transform`):**
   - Los elementos inline (`<span>`) no aceptan transformaciones 2D/3D si no tienen `display: inline-block;`.
3. **PROHIBIDO animar `visibility` o `autoAlpha` directamente en elementos `.clip`:**
   - El motor de HyperFrames controla la visibilidad de los elementos con clase `.clip` según `data-start` y `data-duration`. Anima siempre la opacidad o escala en un contenedor hijo (`.shot-inner`, `.sub-box`).
4. **PROHIBIDO usar `<br>` dentro de bloques de texto de subtítulos:**
   - Para dividir un subtítulo en 2 líneas sin errores del linter y sin desbordamientos horizontales (`text_overflow`), usa dos `<div class="sub-line">` dentro de `.sub-box` con `white-space: nowrap`.
5. **Determinismo Absoluto (Sin `requestAnimationFrame` libre ni `Math.random()` en runtime):**
   - Todo Canvas 2D o animación JS debe calcular su estado únicamente en función de `const t = mainTl.time();` registrado en `window.__hf.timeline`.
6. **Reutilización Instantánea de Binarios (`ffmpeg.exe` / `ffprobe.exe`) y Paquetes:**
   - Antes de ejecutar `npx hyperframes check` o `npx hyperframes render` en un proyecto nuevo, copia `bin/ffmpeg.exe` y `bin/ffprobe.exe` desde `../bin/` (o `../video-caballo/bin/`) hacia `.hyperframes/bin/ffmpeg.exe` y `.hyperframes/bin/ffprobe.exe` del nuevo proyecto.
   - Puedes copiar `package.json` y enlazar o copiar `node_modules` desde `../video-caballo/node_modules` para no perder tiempo descargando paquetes.

---

## 3. Archivos de Referencia para Consultar Antes de Empezar un Nuevo Video

Antes de escribir código en un proyecto nuevo (por ejemplo `video-carro`), revisa estos archivos en `video-caballo`:
- `video-caballo/build_composition.py` (estructura exacta de `index.html`, cadenas DSP de audio y registro de `window.__hf`).
- `video-caballo/generate_sfx.py` (síntesis acústica de SFX en WAV a `44100 Hz`).
- `video-caballo/subagents/visual_layer.json` (estructura de los planos `.clip` + `.shot-inner` y Canvas 2D determinista).
- `video-caballo/subagents/subtitles_layer.json` (CSS y GSAP de subtítulos sin conflictos de transform ni desbordamientos).
