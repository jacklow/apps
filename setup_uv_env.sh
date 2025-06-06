#!/usr/bin/env bash
set -e

if ! command -v uv &> /dev/null; then
  echo "✖️ エラー: uv コマンドが見つかりません。'pip install uv' などでインストールしてください。"
  exit 1
fi

if [ ! -d "venv" ]; then
  echo "① ルートに venv がないため作成します..."
  uv venv
else
  echo "① 既存のルート venv を検出しました。"
fi

echo "② ルートの venv をアクティベート..."
source venv/bin/activate

APPS_DIR="apps"
if [ ! -d "${APPS_DIR}" ]; then
  echo "✖️ エラー: ディレクトリ '${APPS_DIR}' が見つかりません。"
  deactivate
  exit 1
fi
cd "${APPS_DIR}"

if [ ! -f "pyproject.toml" ]; then
  echo "③ uv プロジェクトを初期化します (uv init .)..."
  uv init .
else
  echo "③ pyproject.toml が既に存在。初期化済みと判断します。"
fi

if [ ! -d "venv" ]; then
  echo "④ apps 配下に venv がないため作成します..."
  uv venv
else
  echo "④ 既存の apps 配下 venv を検出しました。"
fi

echo "⑤ apps 配下の venv をアクティベート..."
source venv/bin/activate

REQ_FILE="../requirements.txt"
if [ -f "${REQ_FILE}" ]; then
  echo "⑥ requirements.txt を pip install..."
  pip install -r "${REQ_FILE}"
  echo "⑦ uv に requirements.txt を登録 (uv add --requirements)..."
  uv add --requirements "${REQ_FILE}"
else
  echo "⚠️ requirements.txt が見つかりません (パス: ${REQ_FILE})。"
fi

MAIN_PY="main.py"
if [ -f "${MAIN_PY}" ]; then
  echo "⑧ main.py を uv run で実行..."
  uv run "${MAIN_PY}"
else
  echo "⚠️ main.py が apps 配下に見つかりません。実行をスキップします。"
fi

echo "⑨ 処理完了。仮想環境を終了します..."
deactivate
