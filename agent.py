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
    # prompt = ...
    # TODO: ここを記述してください
    prompt = "" # 穴埋め用のダミーです。ここを書き換えてください。

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
    # TODO: ここにファイル書き込みロジックを実装してください
    pass

if __name__ == "__main__":
    # 初期化と実行
    llm = init_llm()
    run_agent(llm)
