summary: Gemini Nano と Google AI Edge で構築するローカル・プライベートエージェント
id: gemini-nano-local-agent
categories: AI, Gemini, Python
environments: Web
status: Published
feedback link: https://github.com/shiomiayari/LLMBUildwithAI0531/issues
author: Ayari Shiomi

# CodeLab：Gemini Nano と Google AI Edge で構築するローカル・プライベートエージェント

## 1. 概要
Duration: 20

本ハンズオンでは、GoogleのオンデバイスAI向け軽量LLMである「Gemini Nano（MediaPipe LLM Inference API）」を使用し、外部にデータを一切送信しない完全ローカル完結型の「プライベートログ解析エージェント」を構築します。

巨大なクラウドLLMに頼るのではなく、限られたリソースの軽量モデルをいかに「コンテキストエンジニアリング」と「Few-shot」で制御し、実用的なタスクを自律的に実行（エージェント化）させるかを学びます。また、ワークショップの最後には、ストレージを圧迫しないようプログラムによるクリーンアップまで行います。

### 学習目標
- オンデバイスAI（Gemini Nano）と Google AI Edge / MediaPipe の基礎の理解
- 軽量LLMを最大限活かすためのコンテキストエンジニアリング・Few-shot プロンプティングの習得
- Pythonを用いたローカルエージェントの作成と自動ファイルレポート生成
- 不要になったモデルファイルや環境のクリーンアップ処理の自動化

---

## 2. 事前準備と環境構築
Duration: 30

まずは開発環境を整えます。Python 3.10 〜 3.11 の環境を推奨します。

### ステップ 2-1: プロジェクトの作成と仮想環境の構築
ターミナルを開き、任意の場所に作業ディレクトリを作成して移動します。

```bash
mkdir gemini-nano-agent
cd gemini-nano-agent
```

Pythonの仮想環境（venv）を作成し、アクティベートします。

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### ステップ 2-2: 必要なライブラリのインストール
Google AI Edgeを動かすための `mediapipe` と、本タスクに必要なパッケージをインストールします。

```bash
pip install --upgrade pip
pip install mediapipe
```

### ステップ 2-3: ディレクトリ構造の作成
以下のコマンド（またはエディタ）で、必要なフォルダとファイルを作成しておきます。

```bash
mkdir models inputs outputs
touch agent.py cleanup.py
```

最終的な構成は以下のようになります：

```plaintext
gemini-nano-agent/
├── .venv/
├── models/
│   └── (ここにモデルファイルを配置)
├── inputs/
│   └── system_log.txt
├── outputs/
├── agent.py
└── cleanup.py
```

### ステップ 2-4: モデルファイルの配置
事前にダウンロード（または運営から配布）された、MediaPipe用のGemini Nanoモデルファイル（例：`gemini_nano.bin` や `gemma-2b-it-cpu-int4.bin` などのGoogle AI Edge用互換モデル）を、`models/` ディレクトリの直下に配置してください。

---

## 3. 【演習】エージェントの実装（穴埋めワーク）
Duration: 50

`agent.py` を開き、以下のコードベースを記述（またはコピー）してください。中級者の方向けに、コンテキストの注入部分やプロンプトの設計部分が `【TODO】` になっています。制限時間内で実装を完成させましょう。

```python
import os
import time
from mediapipe.tasks.python.genai import llm_inference

# ==========================================
# 設定・パスの定義
# ==========================================
MODEL_PATH = "./models/gemini_nano.bin"  # 配置したモデル名に合わせて変更してください
LOG_FILE_PATH = "./inputs/system_log.txt"
OUTPUT_DIR = "./outputs"

def init_llm():
    """MediaPipeのLLM Inference APIを初期化する"""
    print("🤖 Gemini Nano モデルをロード中... (これには数十秒かかる場合があります)")
    start_time = time.time()
    
    # MediaPipeのLLM設定
    options = llm_inference.LlmInferenceOptions(
        model_asset_path=MODEL_PATH,
        max_tokens=1024,
        temperature=0.2, # 決定論的な出力を得るために低めに設定
        top_k=40
    )
    llm = llm_inference.LlmInference.create_from_options(options)
    
    print(f"✅ ロード完了! (所要時間: {time.time() - start_time:.2f}秒)")
    return llm

def prepare_inputs():
    """ハンズオン用のダミーログファイルを生成する"""
    os.makedirs("./inputs", exist_ok=True)
    if not os.path.exists(LOG_FILE_PATH):
        dummy_log = (
            "2026-05-31 14:23:10 [ERROR] [auth-service] User ID 89432 failed password verification 5 times. IP: 192.168.1.105\n"
            "2026-05-31 14:23:15 [WARN] [auth-service] High connection pool usage detected (88%).\n"
            "2026-05-31 14:24:01 [ERROR] [auth-service] Database connection timeout during login retry for ID 89432.\n"
            "2026-05-31 14:24:02 [FATAL] [gateway] auth-service is unresponsive. Circuit breaker triggered.\n"
        )
        with open(LOG_FILE_PATH, "w", encoding="utf-8") as f:
            f.write(dummy_log)
        print("📝 テスト用のシステムログ(inputs/system_log.txt)を作成しました。")

# ==========================================
# 【演習メイン】エージェントロジックの実装
# ==========================================
def run_agent(llm):
    # テストログの準備
    prepare_inputs()
    
    # 1. ローカルファイルの読み込み（コンテキストエンジニアリングの準備）
    with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
        raw_log_data = f.read()

    # -------------------------------------------------------------
    # 【TODO 1】コンテキストとプロンプトの設計（Few-shotの組み込み）
    # -------------------------------------------------------------
    # 軽量モデル（Nano）に正確なインシデントレポートを出力させるため、
    # 思考プロセス（Chain of Thought）の手本を含むFew-shotプロンプトを構築してください。
    # -------------------------------------------------------------
    prompt = f"""You are an expert site reliability engineering (SRE) agent.
Analyze the following system logs and generate a structured incident report.

# Output Format Specification
Your response MUST be in raw JSON format using this schema:
{{
  "severity": "FATAL" or "ERROR" or "WARN",
  "root_cause": "Brief description of why the failure happened",
  "impact": "What is the current business/system impact",
  "next_action": "Immediate step for engineers to take"
}}

# Example (Few-shot)
Log: 2026-05-01 10:00:00 [ERROR] [disk] Disk space 99%. 2026-05-01 10:01:00 [FATAL] [db] Cannot write to disk, shutting down.
Response: {{"severity": "FATAL", "root_cause": "Disk space exhaustion leading to database shutdown", "impact": "Database is offline, completely stopping all application services", "next_action": "Allocate more storage to the DB volume and restart the service"}}

# Target Log to Analyze
Log: {raw_log_data}
Response:"""

    print("\n🔍 エージェントがローカルログの解析を開始します...")
    start_time = time.time()
    
    # 推論の実行（完全ローカル）
    response = llm.generate_response(prompt)
    
    print(f"⚡ 解析完了! (推論時間: {time.time() - start_time:.2f}秒)")
    print("\n--- [Gemini Nano からのローカル出力] ---")
    print(response)
    print("---------------------------------------")

    # -------------------------------------------------------------
    # 【TODO 2】アクションの実行とファイル保存
    # -------------------------------------------------------------
    # エージェントの出力を "./outputs/incident_report.json" として
    # 自動保存するロジックを実装してください。
    # -------------------------------------------------------------
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    report_path = os.path.join(OUTPUT_DIR, "incident_report.json")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(response)
    print(f"💾 レポートをローカルに保存しました: {report_path}")

if __name__ == "__main__":
    # 初期化と実行
    llm = init_llm()
    run_agent(llm)
```

### 実装後の実行
TODOを埋めたら、スクリプトを実行してエージェントを動かしてみましょう。ネットワークが遮断されたオフライン状態でも、爆速で解析が行われレポートが出力されることを確認してください。

```bash
python agent.py
```

---

## 4. クリーンアップの実装（PCの環境美化）
Duration: 15

開発者として、検証が終わった後のリソース管理（クリーンアップ）まで自動化することは重要なプラクティスです。特に数GBあるモデルファイルはストレージを圧迫するため、プログラムを書いて綺麗に片付けます。

`cleanup.py` を開き、以下のコードを記述して実行してください。

```python
import os
import shutil

def cleanup_workspace():
    print("🧹 GDGハンズオン環境のクリーンアップを開始します...")
    
    # 1. 重いモデルファイルの削除
    # (注意: 他のプロジェクトで再利用したい場合は、手動で退避させてください)
    model_dir = "./models"
    if os.path.exists(model_dir):
        print(f"⚠️ {model_dir} 内の大きなモデルファイルを削除しています...")
        shutil.rmtree(model_dir)
        print("✅ モデルディレクトリを完全に削除しました。")
        
    # 2. 一時的な入力・出力データの削除
    for target_dir in ["./inputs", "./outputs"]:
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
            print(f"✅ 一時フォルダを削除しました: {target_dir}")
            
    print("\n✨ すべてのローカルデータクリーンアップが完了しました！")
    print("💡 最後に、このターミナルウィンドウを閉じるか `deactivate` を実行し、")
    print("   `rm -rf gemini-nano-agent` を実行すれば、仮想環境も含めて完全に元通りになります。")

if __name__ == "__main__":
    # 誤爆防止の確認
    confirm = input("ハンズオンの成果物およびモデルファイルを完全に削除しますか？ (y/N): ")
    if confirm.lower() == 'y':
        cleanup_workspace()
    else:
        print("❌ クリーンアップはキャンセルされました。")
```

### 実行コマンド
```bash
python cleanup.py
```

---

## 5. 【中級者向けディスカッション・考察ポイント】
Duration: 20

無事に動いた方は、セッションのテーマである「コンテキストエンジニアリング」「ハーネス」「LLMOps」に絡めて以下の点を考えてみましょう。

### コンテキストエンジニアリング（プロンプト設計）の依存度
Gemini 2.0 Proなどの巨大モデルであれば、フォーマット指定が雑でもJSONを綺麗に吐き出します。しかし、Gemini Nanoのような軽量モデルでは、少しプロンプトの記述を変える（Few-shotを抜く、など）だけで、簡単にJSON構造が壊れたりハルシネーションを起こしたりします。「モデルのサイズに合わせてインプット（コンテキスト）の質を極限まで高める」ことの重要性を実感できたでしょうか。

### オンデバイス運用のLLMOps
今回は手動でモデルを配置し、手動で消去しました。しかし実際のプロダクト（スマホアプリやブラウザアプリ）に組み込む場合、「ユーザーに数GBのモデルをどうやってダウンロードさせるか」「モデルのアップデート（バージョン管理）をどう配信するか」「不要になった瞬間のキャッシュクリアをどうOSレベルでハンドリングするか」が、Edge領域におけるLLMOpsの非常に面白い戦いどころになります。
