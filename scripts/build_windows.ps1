$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$env:PYINSTALLER_CONFIG_DIR = Join-Path $root ".pyinstaller"
$env:TEMP = Join-Path $root ".tmp"
$env:TMP = $env:TEMP
New-Item -ItemType Directory -Force -Path $env:PYINSTALLER_CONFIG_DIR, $env:TEMP | Out-Null

$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "请先运行 python -m venv .venv 并安装 requirements.txt"
}

& $python -m PyInstaller `
    --noconfirm `
    --clean `
    --onedir `
    --windowed `
    --collect-all ttkbootstrap `
    --name JobTracker `
    app.py

if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$dist = Join-Path $root "dist\JobTracker"
$resolvedRoot = (Resolve-Path -LiteralPath $root).Path
$resolvedDist = (Resolve-Path -LiteralPath $dist).Path
if (-not $resolvedDist.StartsWith($resolvedRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "拒绝清理工作区之外的发布目录：$resolvedDist"
}

$runtimeArtifacts = @(
    (Join-Path $dist "config.json"),
    (Join-Path $dist "求职投递管理工具.xlsx"),
    (Join-Path $dist "backups")
)
foreach ($artifact in $runtimeArtifacts) {
    if (Test-Path -LiteralPath $artifact) {
        Remove-Item -LiteralPath $artifact -Recurse -Force
    }
}

Copy-Item -LiteralPath (Join-Path $root "README.md") -Destination $dist -Force
Copy-Item -LiteralPath (Join-Path $root "LICENSE") -Destination $dist -Force
Copy-Item -LiteralPath (Join-Path $root "examples") -Destination $dist -Recurse -Force

$releaseZip = Join-Path $root "dist\JobTool-Windows-x64.zip"
if (Test-Path -LiteralPath $releaseZip) {
    Remove-Item -LiteralPath $releaseZip -Force
}
Compress-Archive -Path (Join-Path $dist "*") -DestinationPath $releaseZip -CompressionLevel Optimal

Write-Host "Build complete: $dist"
Write-Host "Release package: $releaseZip"
