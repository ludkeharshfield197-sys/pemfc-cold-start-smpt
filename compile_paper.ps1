$ErrorActionPreference = 'Stop'
$paperDir = Join-Path $PSScriptRoot 'manuscript'
$buildDir = Join-Path $PSScriptRoot 'build'
New-Item -ItemType Directory -Path $buildDir -Force | Out-Null
Push-Location -LiteralPath $paperDir
try {
    1..2 | ForEach-Object {
        & pdflatex --disable-installer -interaction=nonstopmode -halt-on-error -no-shell-escape "-output-directory=$buildDir" 'main.tex'
        if ($LASTEXITCODE -ne 0) { throw 'LaTeX compilation failed' }
    }
    Copy-Item -LiteralPath (Join-Path $buildDir 'main.pdf') -Destination (Join-Path $paperDir 'main.pdf') -Force
} finally { Pop-Location }
