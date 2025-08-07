#!/usr/bin/env python3
"""
V100インスタンスの生成画像を直接GCP経由でダウンロード
SSH経由でファイル一覧を取得してローカルに転送
"""
import subprocess
import os
from pathlib import Path
import json

class V100FileRetriever:
    def __init__(self):
        self.instance_name = "instance-20250807-125905"
        self.zone = "us-central1-a"
        self.project = "steady-flag-433105-j6"
        self.local_output = Path.home() / "Desktop" / "gcp" / "outputs" / "v100_generated"
        
    def ensure_output_dir(self):
        """出力ディレクトリを作成"""
        self.local_output.mkdir(parents=True, exist_ok=True)
        print(f"📁 ローカル出力: {self.local_output}")
    
    def find_images_on_v100(self):
        """V100インスタンス上の画像ファイルを検索"""
        print("🔍 V100インスタンス上の画像ファイルを検索中...")
        
        # 複数の場所を検索
        search_commands = [
            "find ~/ComfyUI -name '*.png' -o -name '*.jpg' 2>/dev/null",
            "find ~/ComfyUI/output -name '*' -type f 2>/dev/null",
            "find ~/ComfyUI/temp -name '*' -type f 2>/dev/null",
            "find /tmp -name '*.png' -o -name '*.jpg' 2>/dev/null | head -50",
            "ls -la ~/ComfyUI/output/ 2>/dev/null",
            "ls -la ~/ComfyUI/ | grep -E '\\.png|\\.jpg' 2>/dev/null"
        ]
        
        found_files = []
        
        for command in search_commands:
            try:
                result = subprocess.run([
                    "gcloud", "compute", "ssh", 
                    f"{self.instance_name}",
                    f"--zone={self.zone}",
                    f"--project={self.project}",
                    "--command", command
                ], capture_output=True, text=True, timeout=60)
                
                if result.stdout.strip():
                    print(f"✅ 発見: {command}")
                    files = result.stdout.strip().split('\n')
                    for file in files:
                        if file.strip() and ('png' in file.lower() or 'jpg' in file.lower()):
                            found_files.append(file.strip())
                            
            except subprocess.TimeoutExpired:
                print(f"⏰ タイムアウト: {command}")
            except Exception as e:
                print(f"⚠️ エラー: {command} - {e}")
        
        # 重複を除去
        unique_files = list(set(found_files))
        
        print(f"📊 発見された画像ファイル: {len(unique_files)}個")
        for file in unique_files[:10]:  # 最初の10個を表示
            print(f"  📄 {file}")
        
        return unique_files
    
    def download_file(self, remote_path):
        """個別ファイルをダウンロード"""
        try:
            filename = os.path.basename(remote_path)
            local_path = self.local_output / filename
            
            print(f"📥 ダウンロード中: {filename}")
            
            result = subprocess.run([
                "gcloud", "compute", "scp",
                f"{self.instance_name}:{remote_path}",
                str(local_path),
                f"--zone={self.zone}",
                f"--project={self.project}"
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print(f"✅ 成功: {filename}")
                return True
            else:
                print(f"❌ 失敗: {filename} - {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ タイムアウト: {filename}")
            return False
        except Exception as e:
            print(f"⚠️ エラー: {filename} - {e}")
            return False
    
    def retrieve_all_images(self):
        """全画像を取得"""
        print("🚀 V100画像ファイル取得開始")
        print("=" * 50)
        print(f"🎯 インスタンス: {self.instance_name}")
        print(f"🌏 ゾーン: {self.zone}")
        
        # 出力ディレクトリ準備
        self.ensure_output_dir()
        
        # ファイル検索
        found_files = self.find_images_on_v100()
        
        if not found_files:
            print("❌ 画像ファイルが見つかりませんでした")
            
            # 代替案: ComfyUIのプロセス確認
            print("\n🔄 ComfyUIプロセス確認...")
            try:
                result = subprocess.run([
                    "gcloud", "compute", "ssh", 
                    f"{self.instance_name}",
                    f"--zone={self.zone}",
                    f"--project={self.project}",
                    "--command", "ps aux | grep comfyui && ls -la ~/ComfyUI/output/"
                ], capture_output=True, text=True, timeout=30)
                
                print("📋 プロセス情報:")
                print(result.stdout)
                
            except Exception as e:
                print(f"⚠️ プロセス確認エラー: {e}")
            
            return
        
        # ファイルダウンロード
        downloaded = 0
        for remote_path in found_files:
            if self.download_file(remote_path):
                downloaded += 1
        
        print(f"\n🎉 完了: {downloaded}個のファイルをダウンロード")
        if downloaded > 0:
            print(f"📁 保存先: {self.local_output}")

def main():
    retriever = V100FileRetriever()
    retriever.retrieve_all_images()

if __name__ == "__main__":
    main()