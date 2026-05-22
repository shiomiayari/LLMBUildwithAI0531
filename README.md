# Gemma 4 E2B & Google AI Edge (MediaPipe) — Local SRE Agent Workshop

[![Google AI Edge](https://img.shields.io/badge/Google_AI_Edge-MediaPipe-blue.svg?logo=google)](https://ai.google.dev/edge)
[![Gemma 4](https://img.shields.io/badge/Gemma_4-E2B_Model-green.svg?logo=googlegemini)](https://www.kaggle.com/models/google/gemma-4)
[![GitHub Pages](https://img.shields.io/badge/Codelab-Live-orange.svg?logo=github)](https://shiomiayari.github.io/LLMBUildwithAI0531/)

本リポジトリは、GDG（Google Developer Group）ハンズオンイベント等のための開発用テンプレートリポジトリです。
Googleの最新オンデバイスオープンLLMである **「Gemma 4 E2B」** と **「Google AI Edge (MediaPipe LLM Inference API)」** を用いて、外部にデータを一切送信しない完全ローカル完結型の「プライベートログ解析エージェント」を構築します。

---

## 📖 インタラクティブ教材（Codelab）

ステップバイステップの教材は、GitHub Pagesで公開されている以下のCodelabをご確認ください。
👉 **[Gemma 4 & Google AI Edge で構築するローカル・プライベートエージェント (Codelab)](https://shiomiayari.github.io/LLMBUildwithAI0531/)**

---

## 🚀 クイックスタート

ハンズオン当日は、このリポジトリをベースにして以下の手順で開発を進めます。

### 1. 環境構築
Python 3.10 〜 3.11 の環境で以下を実行します。

```bash
# リポジトリのクローン
git clone https://github.com/shiomiayari/LLMBUildwithAI0531.git
cd LLMBUildwithAI0531

# 仮想環境の作成と起動
# Windowsの場合
python -m venv .venv
.venv\Scripts\activate

# macOS / Linuxの場合
python3 -m venv .venv
source .venv/bin/activate

# 必要なライブラリのインストール
pip install --upgrade pip
pip install mediapipe
```

### 2. ディレクトリ構成
ハンズオンを進めるにあたり、以下の構成になります。
```plaintext
LLMBUildwithAI0531/
├── .venv/                   # Python仮想環境
├── models/
│   └── gemma-4-e2b-it.task  # 【重要】ダウンロードしたモデルファイルを配置します
├── inputs/
│   └── system_log.txt       # 解析対象のログ（スクリプト実行時に自動生成）
├── outputs/                 # 解析レポートの出力先
├── agent.py                 # 【穴埋め演習用】メインプログラム
├── agent_solution.py        # 【解答例】完成版プログラム
└── cleanup.py               # 【お片付け用】クリーンアップスクリプト
```

### 3. モデルファイルの入手と配置
1. **[Kaggle Models](https://www.kaggle.com/models)** にアクセスし、アカウントにログイン（または新規登録）します。
2. 「Gemma 4」を検索し、MediaPipe / LiteRT に対応した `.task` 形式（例: `gemma-4-e2b-it`）の規約に同意しダウンロードします。
3. ダウンロードしたファイルを `models/` ディレクトリ配下に置き、ファイル名を **`gemma-4-e2b-it.task`** に変更します。

---

## 💻 演習（ハンズオンの内容）

1. **`agent.py`** を開き、コメントに記述された `【TODO 1】` と `【TODO 2】` を実装して、エージェントを完成させてください。
2. **実行**: 
   ```bash
   python agent.py
   ```
3. **解答例の確認**: `agent_solution.py` で模範解答のコードを確認できます。
4. **お片付け**: 終了後、PCのストレージ容量を圧迫しないよう、以下のクリーンアップを実行してください。
   ```bash
   python cleanup.py
   ```

---

## 🔗 関連リンク

- [Google AI Edge 公式ドキュメント](https://ai.google.dev/edge)
- [MediaPipe LLM Inference API ガイド](https://ai.google.dev/edge/mediapipe/solutions/genai/llm_inference)
- [Kaggle Models](https://www.kaggle.com/models)
- [Gemma 4 リリースノート (Google Official)](https://blog.google/)
