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
