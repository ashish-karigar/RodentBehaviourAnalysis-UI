Write-Host "Building RodentBehaviourAnalysis UI for Windows..."

Set-Location "$PSScriptRoot\.."

conda activate RBA-UI

pip install -r requirements.txt
pip install pyinstaller

if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}

if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
}

Get-ChildItem -Filter "*.spec" | Remove-Item -Force -ErrorAction SilentlyContinue

pyinstaller --noconfirm --clean build-scripts/rba_ui_win.spec

Write-Host ""
Write-Host "Build complete."
Write-Host "Exe created at:"
Write-Host "dist\RodentBehaviourAnalysisUI\RodentBehaviourAnalysisUI.exe"