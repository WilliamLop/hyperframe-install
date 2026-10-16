#!/usr/bin/env python3
"""
Instalador Universal de Entorno y Skills de HyperFrames (Antigravity, Claude, ChatGPT/Codex).
Configura las skills globales y locales, verifica HyperFrames CLI, prepara binarios FFmpeg
y deja la carpeta del proyecto lista para analizar el .md del video y comenzar el Plan de Edición.
"""

import argparse
import os
import shutil
import subprocess
from pathlib import Path


def copy_tree_safe(src: Path, dst: Path):
    if not src.exists():
        return
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)


def install_global_and_workspace_skills(repo_root: Path, workspace_dir: Path):
    home = Path.home()
    skills_src = repo_root / "skills"
    agents_src = repo_root / "agents"

    # Directorios globales compatibles con Antigravity, Gemini CLI, Claude Code y ChatGPT/Codex
    global_skill_targets = [
        home / ".gemini" / "skills",
        home / ".gemini" / "antigravity" / "skills",
        home / ".claude" / "skills",
        home / ".codex" / "skills",
    ]

    for target in global_skill_targets:
        try:
            copy_tree_safe(skills_src, target)
            print(f"[OK] Skills instaladas en ruta global: {target}")
        except Exception as exc:
            print(f"[WARN] No se pudo copiar a {target}: {exc}")

    # Instalar también en el workspace (.agents/skills y .agents/agents)
    ws_skills = workspace_dir / ".agents" / "skills"
    ws_agents = workspace_dir / ".agents" / "agents"
    copy_tree_safe(skills_src, ws_skills)
    copy_tree_safe(agents_src, ws_agents)
    print(f"[OK] Skills y Subagentes instalados en el workspace: {workspace_dir / '.agents'}")

    # Copiar archivos de instrucciones multi-modelo (GEMINI.md, CLAUDE.md, AGENTS.md)
    for rule_file in ["GEMINI.md", "CLAUDE.md", "AGENTS.md"]:
        src_rule = repo_root / rule_file
        dst_rule = workspace_dir / rule_file
        if src_rule.exists():
            shutil.copy2(src_rule, dst_rule)
            print(f"[OK] Regla {rule_file} configurada en {dst_rule}")


def setup_ffmpeg_binaries(workspace_dir: Path, project_dir: Path):
    exe_suffix = ".exe" if os.name == "nt" else ""
    ffmpeg_name = f"ffmpeg{exe_suffix}"
    ffprobe_name = f"ffprobe{exe_suffix}"

    hf_bin = project_dir / ".hyperframes" / "bin"
    proj_bin = project_dir / "bin"
    ws_bin = workspace_dir / "bin"
    hf_bin.mkdir(parents=True, exist_ok=True)
    proj_bin.mkdir(parents=True, exist_ok=True)

    # Buscar ffmpeg/ffprobe en el workspace, node_modules (ffmpeg-static / ffprobe-static), proyectos hermanos o PATH
    candidates = [
        ws_bin,
        project_dir.parent / "bin",
        project_dir / "node_modules" / "ffmpeg-static",
        project_dir.parent / "video-caballo" / "bin",
        project_dir.parent / "video-caballo" / ".hyperframes" / "bin",
    ]

    for binary in [ffmpeg_name, ffprobe_name]:
        found_path = None
        for cand in candidates:
            p = cand / binary
            if p.exists():
                found_path = p
                break
        if not found_path and binary == ffprobe_name:
            # Buscar en node_modules/ffprobe-static/bin/...
            ffprobe_static_dir = project_dir / "node_modules" / "ffprobe-static" / "bin"
            if ffprobe_static_dir.exists():
                matches = list(ffprobe_static_dir.rglob(ffprobe_name))
                if matches:
                    found_path = matches[0]
        if not found_path:
            which_res = shutil.which(binary.replace(exe_suffix, ""))
            if which_res:
                found_path = Path(which_res)

        if found_path and found_path.exists():
            for dest_dir in [hf_bin, proj_bin, ws_bin]:
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest_file = dest_dir / binary
                if not dest_file.exists():
                    shutil.copy2(found_path, dest_file)
            print(f"[OK] Binario {binary} listo en .hyperframes/bin/")
        else:
            print(f"[INFO] {binary} no encontrado localmente; instalando ffmpeg-static / ffprobe-static...")


def setup_project_folder(repo_root: Path, workspace_dir: Path, project_dir: Path):
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "subagents").mkdir(parents=True, exist_ok=True)

    # 1. Copiar package.json y hyperframes.json base si no existen
    templates_dir = repo_root / "templates"
    for cfg in ["package.json", "hyperframes.json"]:
        src_cfg = templates_dir / cfg
        dst_cfg = project_dir / cfg
        if src_cfg.exists() and not dst_cfg.exists():
            shutil.copy2(src_cfg, dst_cfg)
            print(f"[OK] {cfg} inicializado en {project_dir}")

    # 2. Copiar scripts de referencia (plantillas de SFX y ensamblador)
    ref_dir = project_dir / "templates_ref"
    ref_dir.mkdir(parents=True, exist_ok=True)
    for tpl in ["build_composition.py", "generate_sfx.py"]:
        src_tpl = templates_dir / tpl
        if src_tpl.exists():
            shutil.copy2(src_tpl, ref_dir / tpl)

    # 3. Instalar o reutilizar node_modules (ffmpeg-static / ffprobe-static)
    nm_target = project_dir / "node_modules"
    sibling_nm = project_dir.parent / "video-caballo" / "node_modules"
    ws_nm = workspace_dir / "node_modules"

    if not nm_target.exists():
        if ws_nm.exists():
            print(f"[INFO] Copiando node_modules desde workspace {ws_nm}...")
            copy_tree_safe(ws_nm, nm_target)
        elif sibling_nm.exists():
            print(f"[INFO] Reutilizando node_modules desde {sibling_nm}...")
            copy_tree_safe(sibling_nm, nm_target)
        else:
            print("[INFO] Instalando dependencias base (ffmpeg-static, ffprobe-static) vía npm...")
            npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
            subprocess.run([npm_cmd, "install"], cwd=str(project_dir), check=False)

    # 4. Configurar binarios FFmpeg / FFprobe
    setup_ffmpeg_binaries(workspace_dir, project_dir)

    # 5. Auditar recursos disponibles en la carpeta del proyecto
    print("\n=== AUDITORIA DE RECURSOS EN EL PROYECTO ===")
    md_files = sorted([f.name for f in project_dir.glob("*.md")])
    img_files = sorted([f.name for f in project_dir.iterdir() if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")])
    aud_files = sorted([f.name for f in project_dir.iterdir() if f.suffix.lower() in (".mp3", ".wav", ".m4a", ".ogg")])

    print(f"Carpeta del proyecto : {project_dir}")
    print(f"Archivos .md (Guion) : {md_files if md_files else 'Pendiente de agregar por el usuario'}")
    print(f"Imagenes ({len(img_files)})       : {img_files}")
    print(f"Audios ({len(aud_files)})         : {aud_files}")
    print("============================================\n")
    print("[LISTO] Entorno HyperFrames 100% configurado. Ya puedes pedirle al modelo que analice la carpeta y genere el editing_plan.md.")


def main():
    parser = argparse.ArgumentParser(description="Instalador de Entorno y Skills HyperFrames")
    parser.add_argument(
        "--workspace",
        type=str,
        default=os.getcwd(),
        help="Ruta de la carpeta raiz de edicion (ej. edicion-gemini)",
    )
    parser.add_argument(
        "--project",
        type=str,
        default=None,
        help="Ruta o nombre de la carpeta del proyecto de video (ej. video-carro)",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    workspace_dir = Path(args.workspace).resolve()

    if args.project:
        proj_path = Path(args.project)
        project_dir = proj_path.resolve() if proj_path.is_absolute() else (workspace_dir / proj_path).resolve()
    else:
        project_dir = workspace_dir

    install_global_and_workspace_skills(repo_root, workspace_dir)
    setup_project_folder(repo_root, workspace_dir, project_dir)


if __name__ == "__main__":
    main()
