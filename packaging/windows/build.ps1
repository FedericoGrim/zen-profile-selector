# Builds the Windows installer: PyInstaller bundles the app, Inno Setup wraps it.
# Usage: powershell -File packaging\windows\build.ps1 -Version 0.3.1
param([Parameter(Mandatory = $true)][string]$Version)
$ErrorActionPreference = "Stop"
$root = (Resolve-Path "$PSScriptRoot\..\..").Path
Set-Location $root

python -m pip install --quiet . "pyinstaller>=6.11,<7"
if ($LASTEXITCODE) { exit $LASTEXITCODE }

python -m PyInstaller --noconfirm --clean --windowed `
    --name zen-profile-selector `
    --icon "$root\src\zen_profile_selector\assets\icon.ico" `
    --collect-data zen_profile_selector `
    --collect-data customtkinter `
    --copy-metadata zen-profile-selector `
    --distpath build\pyinstaller\dist --workpath build\pyinstaller\work --specpath build\pyinstaller `
    packaging\windows\launcher.py
if ($LASTEXITCODE) { exit $LASTEXITCODE }

$iscc = Join-Path ${env:ProgramFiles(x86)} "Inno Setup 6\ISCC.exe"
if (-not (Test-Path $iscc)) { $iscc = Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 6\ISCC.exe" }
& $iscc /Qp "/DAppVersion=$Version" packaging\windows\installer.iss
exit $LASTEXITCODE
