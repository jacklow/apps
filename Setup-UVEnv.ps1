<#
.SYNOPSIS
  uv 環境を自動構築 → パッケージ導入 → 実行する PowerShell スクリプト
.NOTES
  - PowerShell の実行ポリシーによっては、一時的に緩和する必要があります:
      Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
#>

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "✖️ エラー: uv コマンドが見つかりません。まずは 'pip install uv' を行ってください。" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path -Path ".\venv" -PathType Container)) {
    Write-Host "① プロジェクトルートに venv がないため、作成します..." -ForegroundColor Cyan
    uv venv
} else {
    Write-Host "① 既存のプロジェクトルート venv を検出しました." -ForegroundColor Green
}

Write-Host "② ルートの venv をアクティベート..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1

$appsDir = "apps"
if (-not (Test-Path -Path ".\$appsDir" -PathType Container)) {
    Write-Host "✖️ エラー: ディレクトリ '$appsDir' が見つかりません." -ForegroundColor Red
    & .\venv\Scripts\Deactivate.ps1
    exit 1
}
Set-Location -Path $appsDir

if (-not (Test-Path -Path ".\pyproject.toml" -PathType Leaf)) {
    Write-Host "③ uv プロジェクトを初期化します (uv init .)..." -ForegroundColor Cyan
    uv init .
} else {
    Write-Host "③ pyproject.toml が既に存在。初期化済みと判断します." -ForegroundColor Green
}

if (-not (Test-Path -Path ".\venv" -PathType Container)) {
    Write-Host "④ apps 配下に venv がないため、作成します..." -ForegroundColor Cyan
    uv venv
} else {
    Write-Host "④ 既存の apps 配下 venv を検出しました." -ForegroundColor Green
}

Write-Host "⑤ apps 配下の venv をアクティベート..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1

$reqFile = "..\requirements.txt"
if (Test-Path -Path $reqFile -PathType Leaf) {
    Write-Host "⑥ requirements.txt を pip install..." -ForegroundColor Cyan
    pip install -r $reqFile
    Write-Host "⑦ uv に requirements.txt を登録 (uv add --requirements)..." -ForegroundColor Cyan
    uv add --requirements $reqFile
} else {
    Write-Host "⚠️ requirements.txt が見つかりません (パス: $reqFile)。" -ForegroundColor Yellow
}

$mainPy = "main.py"
if (Test-Path -Path $mainPy -PathType Leaf) {
    Write-Host "⑧ main.py を uv run で実行..." -ForegroundColor Cyan
    uv run $mainPy
} else {
    Write-Host "⚠️ main.py が apps 配下に見つかりません。実行をスキップします." -ForegroundColor Yellow
}

Write-Host "⑨ 処理完了。仮想環境を終了します..." -ForegroundColor Green
& .\venv\Scripts\Deactivate.ps1
Set-Location -Path ".."
if (Test-Path -Path ".\venv\Scripts\Deactivate.ps1" -PathType Leaf) {
    & .\venv\Scripts\Deactivate.ps1
}
