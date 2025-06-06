#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup_uv_env.py

Windows / Linux / macOS を問わず、以下の流れを自動化するスクリプトです:

  1. uv コマンドがインストール済みかチェック
  2. プロジェクトルートに venv がなければ作成 (uv venv)
  3. ルート venv を使って次のアクションを行う:
     └ apps フォルダに移動
         ├ uv プロジェクト初期化 (pyproject.toml がなければ uv init .)
         ├ apps 配下に venv がなければ作成 (uv venv)
         └ venv の Python を用いて
            • requirements.txt があれば pip install -r requirements.txt
            • uv add --requirements requirements.txt
            • uv run main.py (main.py があれば)

“アクティベート”せずとも、venv 内の Python を直接呼び出す方法を使っているため、
シェルの種類や OS を気にせずに動きます。
"""

import os
import sys
import subprocess
import platform
from shutil import which

# ------------------------------------------------------------
# ヘルパー関数
# ------------------------------------------------------------
def run_cmd(cmd_list, cwd=None, env=None):
    """subprocess.run でコマンドを実行し、エラー時は例外を投げる。"""
    result = subprocess.run(
        cmd_list,
        cwd=cwd,
        env=env,
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )
    print(result.stdout, end="")
    if result.returncode != 0:
        raise RuntimeError(
            f"コマンド '{cmd_list}' がエラーコード {result.returncode} で終了しました。"
        )


def is_windows():
    return platform.system().lower().startswith("win")


def venv_python_path(base_path):
    """venv フォルダ内の Python 実行ファイルのパスを返す。"""
    if is_windows():
        return os.path.join(base_path, "Scripts", "python.exe")
    candidate = os.path.join(base_path, "bin", "python3")
    if os.path.isfile(candidate):
        return candidate
    return os.path.join(base_path, "bin", "python")


# ------------------------------------------------------------
# メイン処理
# ------------------------------------------------------------
def main():
    project_root = os.getcwd()
    apps_dir = os.path.join(project_root, "apps")
    requirements_file = os.path.join(project_root, "requirements.txt")

    if which("uv") is None:
        print("✖️ エラー: 'uv' コマンドが見つかりません。先に 'pip install uv' などでインストールしてください。")
        sys.exit(1)
    print("✅ uv コマンドを検出しました。")

    root_venv = os.path.join(project_root, "venv")
    if not os.path.isdir(root_venv):
        print("① プロジェクトルートに venv がないため、'uv venv' で仮想環境を作成します...")
        run_cmd(["uv", "venv"], cwd=project_root)
    else:
        print("① プロジェクトルートに既存の venv を検出しました。")

    root_py = venv_python_path(root_venv)
    if not os.path.isfile(root_py):
        print(f"✖️ エラー: 仮想環境の Python が見つかりません。パス: {root_py}")
        sys.exit(1)
    print(f"② ルート venv の Python: {root_py}")

    if not os.path.isdir(apps_dir):
        print(f"✖️ エラー: プロジェクトルート直下に 'apps' フォルダが見つかりません。パス: {apps_dir}")
        sys.exit(1)
    print(f"③ apps フォルダを発見: {apps_dir}")

    pyproject_toml = os.path.join(apps_dir, "pyproject.toml")
    if not os.path.isfile(pyproject_toml):
        print("④ apps フォルダ内に 'pyproject.toml' が見つかりません。'uv init .' で初期化します...")
        run_cmd(["uv", "init", "."], cwd=apps_dir)
    else:
        print("④ apps フォルダ内に既存の 'pyproject.toml' があるため、初期化済みと判断します。")

    apps_venv = os.path.join(apps_dir, "venv")
    if not os.path.isdir(apps_venv):
        print("⑤ apps 配下に venv がないため、'uv venv' で仮想環境を作成します...")
        run_cmd(["uv", "venv"], cwd=apps_dir)
    else:
        print("⑤ apps 配下に既存の venv を検出しました。")

    apps_py = venv_python_path(apps_venv)
    if not os.path.isfile(apps_py):
        print(f"✖️ エラー: apps 配下の venv 内に Python が見つかりません。パス: {apps_py}")
        sys.exit(1)
    print(f"⑥ apps 配下の venv Python: {apps_py}")

    if os.path.isfile(requirements_file):
        print(
            f"⑦ ルートの requirements.txt を '{apps_py} -m pip install -r requirements.txt' でインストールします…"
        )
        run_cmd([apps_py, "-m", "pip", "install", "-r", requirements_file], cwd=apps_dir)

        print("⑧ 'uv add --requirements requirements.txt' を実行します…")
        env = os.environ.copy()
        if is_windows():
            venv_bin = os.path.join(apps_venv, "Scripts")
        else:
            venv_bin = os.path.join(apps_venv, "bin")
        env["PATH"] = venv_bin + os.pathsep + env.get("PATH", "")
        run_cmd(["uv", "add", "--requirements", requirements_file], cwd=apps_dir, env=env)
    else:
        print("⚠️ ルートに requirements.txt が見つかりません。必要であればプロジェクトルートに配置してください。")

    main_py = os.path.join(apps_dir, "main.py")
    if os.path.isfile(main_py):
        print("⑨ 'uv run main.py' を実行します…")
        env = os.environ.copy()
        if is_windows():
            venv_bin = os.path.join(apps_venv, "Scripts")
        else:
            venv_bin = os.path.join(apps_venv, "bin")
        env["PATH"] = venv_bin + os.pathsep + env.get("PATH", "")
        run_cmd(["uv", "run", "main.py"], cwd=apps_dir, env=env)
    else:
        print("⚠️ apps 配下に main.py が見つかりません。uv run はスキップします。")

    print("✅ 全処理が完了しました。")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✖️ エラー発生: {e}")
        sys.exit(1)
