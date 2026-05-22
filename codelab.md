summary: Gemma 4 E2B と Google AI Edge で構築するローカル・プライベートエージェント
id: gemini-nano-local-agent
categories: AI, Gemma, Python
environments: Web
status: Published
feedback link: https://github.com/shiomiayari/LLMBUildwithAI0531/issues
author: Ayari Shiomi

# CodeLab：Gemma 4 E2B と Google AI Edge で構築するローカル・プライベートエージェント

## 1. 概要 & なぜオンデバイスAIなのか？
Duration: 15

本ハンズオンでは、Googleが2026年4月にリリースした最新のオンデバイス向けオープンモデルファミリーである「**Gemma 4 E2B（Effective 2B）**」および「**Google AI Edge（MediaPipe LLM Inference API）**」を使用し、外部にデータを一切送信しない完全ローカル完結型の「**プライベートログ解析エージェント**」を構築します。

### 💡 なぜ今、オンデバイスAIなのか？
クラウドLLM（Gemini 2.0 Flash/Pro等）は極めて強力ですが、実務で導入する際には以下の「3つの壁」に直面します。

1. **データプライバシーの壁**: 社外秘のシステムログや個人情報をクラウドに送信できない。
2. **コストの壁**: 大量のログ分析を24時間クラウドAPIで回すと、莫大なリクエスト費用がかかる。
3. **レイテンシ・ネットワークの壁**: ネットワーク遅延が発生する、またはオフライン環境（工場や機密エリア）では動作しない。

オンデバイスAIは、これらの問題を**「手元のPCの計算資源だけで動かす」**ことで根本から解決します。

---

### 🛠️ ローカルエージェントのデータフロー図

本ハンズオンで構築するエージェントのアーキテクチャです。入力から出力まで、データは1バイトもローカルPCの外に出ません。

```plaintext
[入力: system_log.txt] (ローカルの障害ログ)
          │
          ▼ (Pythonでファイル読み込み)
[コンテキスト・エンジニアリング] (プロンプト＋Few-shotの整形)
          │
          ▼ (MediaPipe LLM Inference API経由でロード)
┌──────────────────────────────────────────────┐
│  💻 ローカルPC内の計算資源 (CPU/GPU)          │
│  🤖 Gemma 4 E2B (完全にオフラインで推論実行)   │
└──────────────────────────────────────────────┘
          │
          ▼ (構造化JSONデータの出力)
[自動アクション実行] (JSONパース ➡️ ファイル保存)
          │
          ▼
[出力: incident_report.json] (ローカルに保存)
```

---

### 🎯 このハンズオンで学べること
- **オンデバイスAIの基本**: MediaPipeを用いた最新モデル（Gemma 4）のロードと実行方法。
- **コンテキストエンジニアリングの真髄**: 巨大モデルと異なり、「少し賢さに制限のある」軽量モデルを、Few-shotプロンプトによって劇的に賢く動かすテクニック。
- **エージェント化の基礎**: LLMの出力をプログラムで受け取り、次のアクション（ファイル保存）に自動で繋げるパイプライン設計。
- **リソース管理の実践**: 数GBあるモデルファイルや一時ファイルを、プログラムから綺麗に消去するクリーンアップ設計。

---

## 2. 事前準備と環境構築
Duration: 25

まずは開発用のフォルダを作成し、Pythonの仮想環境と必要なパッケージをインストールします。

> aside negative
> **重要（推奨環境）**:
> 本ハンズオンは **Python 3.10 〜 3.11** の環境を推奨します。Python 3.12以降では、一部のMediaPipeバイナリビルドとの互換性エラーが発生する場合があります。

---

### ステップ 2-1: プロジェクトの作成と仮想環境の構築
ターミナルを開き、以下のコマンドを順に実行して環境を作成します。

```bash
# プロジェクトフォルダを作成して移動
mkdir gemini-nano-agent
cd gemini-nano-agent

# 仮想環境（.venv）の作成
# Windowsの場合
python -m venv .venv
.venv\Scripts\activate

# macOS / Linuxの場合
python3 -m venv .venv
source .venv/bin/activate
```

---

### ステップ 2-2: 必要なライブラリのインストール
Google AI Edgeを動かすための `mediapipe` と、関連ツールをインストールします。

```bash
# pip自体を最新化
pip install --upgrade pip

# MediaPipeのインストール (Google AI EdgeのPythonハーネスを含みます)
pip install mediapipe
```

---

### ステップ 2-3: ディレクトリ構造の作成
以下のフォルダと空のスクリプトファイルを作成します。

```bash
mkdir models inputs outputs
touch agent.py cleanup.py
```

最終的なディレクトリ構成は以下のようになります：

```plaintext
gemini-nano-agent/
├── .venv/                   # Python仮想環境
├── models/
│   └── gemma-4-e2b-it.task  # 【重要】ここにモデルファイルを配置します
├── inputs/
│   └── system_log.txt       # 解析対象のログファイル（自動生成されます）
├── outputs/                 # 解析レポートが出力されるフォルダ
├── agent.py                 # エージェントのメインプログラム
└── cleanup.py               # クリーンアッププログラム
```

---

### ステップ 2-4: モデルファイルの配置
事前にKaggle ModelsからダウンロードしたMediaPipe用「Gemma 4 E2B」モデルファイル（`gemma-4-e2b-it-cpu-int4.task` など）を、`models/` フォルダの直下に配置し、ファイル名を `gemma-4-e2b-it.task` に変更してください。

> aside positive
> **モデルの入手方法**:
> Gemma 4は公式の **[Kaggle Models](https://www.kaggle.com/models)** からダウンロードできます。「Gemma 4」を検索し、利用規約に同意した上で、MediaPipe/LiteRT向けの `.task` 形式（または `.tflite` / `.bin`）のファイルをダウンロードしてください。

---

## 3. 【演習】エージェントの実装（穴埋めワーク）
Duration: 50

`agent.py` を開き、以下のテンプレートコードを貼り付けてください。

このコードには、**【TODO 1】**（コンテキストエンジニアリングとFew-shotプロンプトの設計）と、**【TODO 2】**（エージェントが出力したレポートのファイル保存）の2つの未完成部分があります。

### agent.py のコードテンプレート

```python
import os
import time
from mediapipe.tasks.python.genai import llm_inference

# ==========================================
# 設定・パスの定義
# ==========================================
MODEL_PATH = "./models/gemma-4-e2b-it.task"
LOG_FILE_PATH = "./inputs/system_log.txt"
OUTPUT_DIR = "./outputs"

def init_llm():
    """MediaPipeのLLM Inference APIを初期化する"""
    print("🤖 Gemma 4 モデルをロード中... (これには数十秒かかる場合があります)")
    start_time = time.time()
    
    # MediaPipeのLLM設定
    options = llm_inference.LlmInferenceOptions(
        model_asset_path=MODEL_PATH,
        max_tokens=1024,
        temperature=0.2, # 決定論的なJSON出力を得るために低めに設定
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
    
    # 1. ローカルファイルの読み込み
    with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
        raw_log_data = f.read()

    # -------------------------------------------------------------
    # 【TODO 1】コンテキストとプロンプトの設計（Few-shotの組み込み）
    # -------------------------------------------------------------
    # 軽量モデル（Gemma 4）に正確なインシデントレポートを出力させるため、
    # 思考プロセス（Chain of Thought）の手本を含むFew-shotプロンプトを構築してください。
    # -------------------------------------------------------------
    prompt = f"""ここにプロンプトを記述してください"""

    print("\n🔍 エージェントがローカルログの解析を開始します...")
    start_time = time.time()
    
    # 推論の実行（完全ローカル）
    response = llm.generate_response(prompt)
    
    print(f"⚡ 解析完了! (推論時間: {time.time() - start_time:.2f}秒)")
    print("\n--- [Gemma 4 からのローカル出力] ---")
    print(response)
    print("---------------------------------------")

    # -------------------------------------------------------------
    # 【TODO 2】アクションの実行とファイル保存
    # -------------------------------------------------------------
    # エージェントの出力を "./outputs/incident_report.json" として
    # 自動保存するロジックを実装してください。
    # -------------------------------------------------------------
    # ここにファイル書き込みロジックを実装してください

if __name__ == "__main__":
    # 初期化と実行
    llm = init_llm()
    run_agent(llm)
```

---

### 💡 実装のヒント

#### **【TODO 1】プロンプトの設計**
Gemma 4 E2Bのような軽量モデルは、複雑な指示を一度に受けるとフォーマットを崩しがちです。以下の要素を意識してプロンプト（`prompt` 変数）を書き換えてみましょう。
- **役割の定義 (Role)**: 「あなたは優秀なSRE（Site Reliability Engineer）エージェントです」
- **出力形式の厳密な指定**: JSONのキー名（`severity`, `root_cause`, `impact`, `next_action`）を明示的に指定します。
- **Few-shot (例示)**: 「このようなログが入力されたら、このようにJSONを出力する」という具体的な入出力例（1〜2パターン）をプロンプト内に含める。

#### **【TODO 2】ファイル保存の実装**
`response` にはモデルから返ってきた文字列（JSON形式を期待）が格納されています。`outputs/` フォルダの中に `incident_report.json` という名前で保存するコード（`open()` 関数などを使用）を記述します。

---

### 🏁 期待される実行結果

実装が完成し、`python agent.py` を実行すると、以下のように完全にパース可能なJSONレポートが出力され、ファイルとしてローカルに保存されます。

```json
{
  "severity": "FATAL",
  "root_cause": "auth-service became unresponsive due to connection pool exhaustion and database timeouts, triggering the gateway circuit breaker",
  "impact": "All incoming login requests are blocked, causing full authentication outage for users",
  "next_action": "Check database server load, scale connection pool size of auth-service, and reset the gateway circuit breaker"
}
```

---

## 4. クリーンアップの実装（PC의 環境美化）
Duration: 15

検証や開発が終わった後、環境をきれいに片付けることは本番運用の設計（SRE）においても非常に重要なプラクティスです。特に今回のモデルファイルは**1GB以上**あり、放置するとPCのストレージを圧迫します。

`cleanup.py` を開き、以下のプログラムを記述してください。

```python
import os
import shutil

def cleanup_workspace():
    print("🧹 GDGハンズオン環境のクリーンアップを開始します...")
    
    # 1. 重いモデルファイルの削除
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
    print("💡 最後に、このターミナルで `deactivate` を実行し、")
    print("   作業フォルダ自体（gemini-nano-agent）を削除すれば完全に元通りになります。")

if __name__ == "__main__":
    # 誤操作による削除を防ぐための安全プロンプト
    confirm = input("ハンズオンの成果物およびモデルファイルを完全に削除しますか？ (y/N): ")
    if confirm.lower() == 'y':
        cleanup_workspace()
    else:
        print("❌ クリーンアップはキャンセルされました。")
```

### クリーンアップの実行
完了したら、以下のコマンドでクリーンアップを実行します。

```bash
python cleanup.py
```

---

## 5. 【中級者向け】ディスカッション & 深掘り考察
Duration: 15

無事にエージェントが動作した方は、本日のテーマであるオンデバイスAIエージェントの設計思想について深く考えてみましょう。

### 🧠 考察 1：軽量モデルにおける「コンテキストエンジニアリング」の重要性
Gemini 2.0 Proのような数千億〜数兆パラメータを持つ巨大モデルであれば、適当なプロンプトでも綺麗にJSONを吐き出します。
しかし、2B（20億パラメータ）クラスの Gemma 4 E2B は、**「プロンプトの設計（コンテキストエンジニアリング）」**によって出力品質が天と地ほど変わります。

* プロンプトから **Few-shot（例示）** を抜いて実行してみましょう。出力はどう変化しますか？
* JSONフォーマットが崩れたり、英語での指示に対して日本語で答えるのを忘れてハルシネーション（嘘の出力）を起こしたりしませんでしたか？
* **結論**: オンデバイスAIを実務で使う上で、エンジニアの「インプット（文脈）を最適化する技術」はクラウド以上に不可欠なスキルになります。

---

### 🌐 考察 2：オンデバイスAIにおける「LLMOps」の課題
今回は自分のPC上で手動でモデルを配置し、スクリプトで削除しました。しかし、これを実際のプロダクト（Webブラウザやスマートフォンアプリ）として一般ユーザーに届ける場合、以下のような特有の課題が生じます。

1. **モデルの配信方法**: ユーザーに毎回1GB以上のモデルをダウンロードさせるわけにはいかない。
   * ➡️ *解決策の例*: Chrome Built-in AI（ChromeブラウザがOS経由で一度だけモデルをバックグラウンドダウンロードする仕組み）の活用。
2. **ハイブリッド運用（Cloud + Edge）**: 
   * ➡️ 全ての推論をクラウドに投げると破産するため、「個人情報のマスキングや簡単な一次分類はデバイス上のGemma 4で行い、より複雑な論理思考が必要な箇所だけ Vertex AI（Gemini 2.0 Pro）に転送する」といったシステム設計（ハイブリッドLLMアーキテクチャ）が今後の主流になります。
