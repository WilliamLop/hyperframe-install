import html as html_lib
import json
import os
import shutil

os.makedirs('.hyperframes/bin', exist_ok=True)
if os.path.exists('bin/ffmpeg.exe'):
    shutil.copyfile('bin/ffmpeg.exe', '.hyperframes/bin/ffmpeg.exe')
if os.path.exists('bin/ffprobe.exe'):
    shutil.copyfile('bin/ffprobe.exe', '.hyperframes/bin/ffprobe.exe')

with open('subagents/visual_layer.json', 'r', encoding='utf-8') as f:
    visual = json.load(f)
with open('subagents/subtitles_layer.json', 'r', encoding='utf-8') as f:
    subs = json.load(f)

def attr_json(obj):
    return html_lib.escape(json.dumps(obj, separators=(',', ':')), quote=True)

vo_chain = {
    "version": 1,
    "nodes": [
        {"type": "highpass", "id": "vo_hp", "label": "Remove Rumble", "params": {"frequency": 85, "q": 0.707, "poles": "2"}},
        {"type": "peaking", "id": "vo_pres", "label": "Add Clarity", "params": {"frequency": 3200, "gain": 2.0, "q": 1.1}},
        {"type": "compressor", "id": "vo_comp", "label": "Even Out Voice", "params": {"threshold": -16, "ratio": 3.0, "attack": 5, "release": 120}}
    ]
}

music_carve = {
    "enabled": True,
    "sources": ["voiceover"],
    "strength": 0.8
}

music_chain = {
    "version": 1,
    "nodes": [
        {"type": "peaking", "id": "m_dip1", "fromCarve": True, "params": {"frequency": 400, "gain": -4.0, "q": 1.5}},
        {"type": "peaking", "id": "m_dip2", "fromCarve": True, "params": {"frequency": 1600, "gain": -6.0, "q": 1.5}},
        {"type": "peaking", "id": "m_dip3", "fromCarve": True, "params": {"frequency": 2800, "gain": -4.5, "q": 1.4}}
    ]
}

music_auto = {
    "version": 1,
    "lanes": [
        {
            "target": "volume",
            "points": [
                {"t": 0.0, "v": 0.25},
                {"t": 3.05, "v": 0.25},
                {"t": 3.18, "v": 0.95},
                {"t": 3.82, "v": 0.95},
                {"t": 3.95, "v": 0.25},
                {"t": 6.45, "v": 0.25},
                {"t": 6.60, "v": 1.0},
                {"t": 7.70, "v": 1.0},
                {"t": 7.85, "v": 0.25},
                {"t": 14.05, "v": 0.25},
                {"t": 14.18, "v": 0.95},
                {"t": 14.62, "v": 0.95},
                {"t": 14.75, "v": 0.25},
                {"t": 18.90, "v": 0.25},
                {"t": 19.05, "v": 1.0},
                {"t": 21.10, "v": 1.0},
                {"t": 21.25, "v": 0.25},
                {"t": 23.30, "v": 0.25},
                {"t": 23.45, "v": 1.0},
                {"t": 24.25, "v": 1.0},
                {"t": 24.40, "v": 0.25},
                {"t": 26.35, "v": 0.25},
                {"t": 26.50, "v": 1.0},
                {"t": 26.98, "v": 1.0},
                {"t": 27.12, "v": 0.25},
                {"t": 30.30, "v": 0.25},
                {"t": 30.42, "v": 1.0},
                {"t": 30.82, "v": 1.0},
                {"t": 30.95, "v": 0.25},
                {"t": 32.65, "v": 0.25},
                {"t": 32.78, "v": 1.0},
                {"t": 33.22, "v": 1.0},
                {"t": 33.35, "v": 0.25},
                {"t": 35.20, "v": 0.25},
                {"t": 35.32, "v": 0.85},
                {"t": 35.78, "v": 0.85},
                {"t": 35.90, "v": 0.25},
                {"t": 39.05, "v": 0.25},
                {"t": 39.25, "v": 0.90},
                {"t": 40.00, "v": 0.0}
            ]
        }
    ]
}

rain_auto = {
    "version": 1,
    "lanes": [
        {
            "target": "volume",
            "points": [
                {"t": 0.0, "v": 0.0},
                {"t": 0.3, "v": 0.34},
                {"t": 4.7, "v": 0.34},
                {"t": 5.5, "v": 0.0}
            ]
        }
    ]
}

warm_auto = {
    "version": 1,
    "lanes": [
        {
            "target": "volume",
            "points": [
                {"t": 0.0, "v": 0.0},
                {"t": 0.8, "v": 0.30},
                {"t": 13.2, "v": 0.30},
                {"t": 14.0, "v": 0.0}
            ]
        }
    ]
}

whinny_auto = {
    "version": 1,
    "lanes": [
        {
            "target": "volume",
            "points": [
                {"t": 0.0, "v": 0.32},
                {"t": 1.65, "v": 0.55},
                {"t": 2.15, "v": 0.45},
                {"t": 2.5, "v": 0.0}
            ]
        }
    ]
}

trocha_auto = {
    "version": 1,
    "lanes": [
        {
            "target": "volume",
            "points": [
                {"t": 0.0, "v": 0.32},
                {"t": 1.5, "v": 0.52},
                {"t": 2.1, "v": 0.28},
                {"t": 5.4, "v": 0.50},
                {"t": 6.0, "v": 0.30},
                {"t": 7.75, "v": 0.58},
                {"t": 8.5, "v": 0.0}
            ]
        }
    ]
}

audio_html = f"""<!-- ==================== CAPA DE AUDIO & AUTO-DUCKING ==================== -->
<audio id="voiceover" src="audio-video-caballo.mp3" data-start="0" data-duration="39.39" data-track-index="1" data-volume="1.0" data-fx-chain="{attr_json(vo_chain)}"></audio>
<audio id="music-bed" src="musica-video-caballo.wav" data-start="0" data-duration="40" data-track-index="2" data-volume="1.0" data-fx-carve="{attr_json(music_carve)}" data-fx-chain="{attr_json(music_chain)}" data-automation="{attr_json(music_auto)}"></audio>
<audio id="sfx-rain" src="sfx-lluvia.wav" data-start="0" data-duration="5.5" data-track-index="3" data-volume="0.34" data-automation="{attr_json(rain_auto)}"></audio>
<audio id="sfx-warm" src="sfx-ambiente-calido.wav" data-start="5.0" data-duration="14.0" data-track-index="4" data-volume="0.30" data-automation="{attr_json(warm_auto)}"></audio>
<audio id="sfx-whinny" src="sfx-relincho-epico.wav" data-start="19.0" data-duration="2.5" data-track-index="5" data-volume="0.45" data-automation="{attr_json(whinny_auto)}"></audio>
<audio id="sfx-trocha" src="sfx-trocha-ovacion.wav" data-start="25.0" data-duration="8.5" data-track-index="6" data-volume="0.42" data-automation="{attr_json(trocha_auto)}"></audio>
"""

visual_js = visual['js'].replace(
    'function registerVisualLayer(tl) {',
    'function registerVisualLayer(tl) {\n  tl.set(["#lightning-flash", "#flash-gold-overlay", "#flash-stadium-overlay"], { opacity: 0 }, 0);'
)

html = f"""<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>Alisson y Relámpago - Short Viral</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{
        box-sizing: border-box;
      }}
      html, body {{
        margin: 0;
        padding: 0;
        width: 100%;
        height: 100%;
        background: #06080c;
        color: #ffffff;
        font-family: system-ui, -apple-system, 'Segoe UI', Roboto, Arial, sans-serif;
        overflow: hidden;
      }}
      #root {{
        position: relative;
        width: 100%;
        height: 100%;
        overflow: hidden;
        background: #06080c;
      }}
      {visual['css']}
      {subs['css']}
    </style>
  </head>
  <body>
    <div
      id="root"
      data-composition-id="alisson-relampago"
      data-start="0"
      data-width="1080"
      data-height="1920"
      data-duration="40"
      data-fps="30"
    >
      <!-- CAPA 1: IMÁGENES Y MOVIMIENTO DE CÁMARA + VFX -->
      {visual['html']}

      <!-- CAPA 2: SUBTÍTULOS DINÁMICOS DE ALTA RETENCIÓN -->
      {subs['html']}

      <!-- CAPA 3: AUDIO MIXING, VOZ GUÍA, MÚSICA CON AUTO-DUCKING Y SFX -->
      {audio_html}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {visual_js}
      {subs['js']}
      if (typeof registerVisualLayer === 'function') {{
        registerVisualLayer(tl);
      }}
      if (typeof registerSubtitles === 'function') {{
        registerSubtitles(tl);
      }}
      window.__timelines["alisson-relampago"] = tl;
    </script>
  </body>
</html>
"""

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Successfully rebuilt index.html with valid v1 audio schema")
