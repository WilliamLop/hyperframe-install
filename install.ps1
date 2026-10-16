param(
    [string]$Workspace = (Get-Location).Path,
    [string]$Project = ""
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  HyperFrames Short Producer - Instalador de Entorno y Skills" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

if ($Project -ne "") {
    python "$ScriptDir\scripts\setup_env.py" --workspace "$Workspace" --project "$Project"
} else {
    python "$ScriptDir\scripts\setup_env.py" --workspace "$Workspace"
}
