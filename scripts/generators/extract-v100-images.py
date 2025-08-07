#!/usr/bin/env python3
"""
V100 ComfyUI API経由で画像抽出・ダウンロード
"""
import subprocess
import json
import os
from pathlib import Path
import requests

class V100ImageExtractor:
    def __init__(self):
        self.instance_name = "instance-20250807-125905"
        self.zone = "us-central1-c"
        self.project = "gen-lang-client-0106774703"
        self.server_ip = "34.70.230.62"
        self.port = 8188
        self.base_url = f"http://{self.server_ip}:{self.port}"
        self.local_output = Path.home() / "Desktop" / "gcp" / "outputs" / "v100_generated"
        
    def get_history_via_ssh(self):
        """SSH経由でComfyUI履歴を取得"""
        try:
            result = subprocess.run([
                "gcloud", "compute", "ssh", 
                f"{self.instance_name}",
                f"--zone={self.zone}",
                f"--project={self.project}",
                "--command", "curl -s http://localhost:8188/history"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and result.stdout.strip():
                return json.loads(result.stdout.strip())
            return {}
        except Exception as e:
            print(f"❌ SSH履歴取得エラー: {e}")
            return {}
    
    def extract_image_filenames(self, history):
        """履歴から画像ファイル名を抽出"""
        filenames = []
        for prompt_id, data in history.items():
            outputs = data.get('outputs', {})
            for node_id, node_output in outputs.items():
                images = node_output.get('images', [])
                for image_data in images:
                    filename = image_data.get('filename')
                    if filename:
                        filenames.append(filename)
        return list(set(filenames))  # 重複削除
    
    def download_image_via_ssh(self, filename):
        """SSH経由で個別画像をダウンロード"""
        try:
            # まずComfyUI outputディレクトリを確認
            local_path = self.local_output / filename
            
            # ComfyUIのoutputディレクトリから直接ダウンロード
            result = subprocess.run([
                "gcloud", "compute", "scp",
                f"{self.instance_name}:~/ComfyUI/output/{filename}",
                str(local_path),
                f"--zone={self.zone}",
                f"--project={self.project}"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                return True
            else:
                # temp フォルダも試してみる
                result2 = subprocess.run([
                    "gcloud", "compute", "scp",
                    f"{self.instance_name}:~/ComfyUI/temp/{filename}",
                    str(local_path),
                    f"--zone={self.zone}",
                    f"--project={self.project}"
                ], capture_output=True, text=True, timeout=60)
                
                return result2.returncode == 0
                
        except Exception as e:
            print(f"❌ ダウンロードエラー {filename}: {e}")
            return False
    
    def download_via_api_through_ssh(self, filename):
        """SSH経由でComfyUI API から画像を取得"""
        try:
            # SSH経由でComfyUI APIから画像データを取得
            api_command = f"curl -s 'http://localhost:8188/view?filename={filename}&type=output' --output /tmp/{filename}"
            
            result = subprocess.run([
                "gcloud", "compute", "ssh", 
                f"{self.instance_name}",
                f"--zone={self.zone}",
                f"--project={self.project}",
                "--command", api_command
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                # ダウンロードした画像を転送
                local_path = self.local_output / filename
                
                scp_result = subprocess.run([
                    "gcloud", "compute", "scp",
                    f"{self.instance_name}:/tmp/{filename}",
                    str(local_path),
                    f"--zone={self.zone}",
                    f"--project={self.project}"
                ], capture_output=True, text=True, timeout=60)
                
                # 一時ファイルをクリーンアップ
                subprocess.run([
                    "gcloud", "compute", "ssh", 
                    f"{self.instance_name}",
                    f"--zone={self.zone}",
                    f"--project={self.project}",
                    "--command", f"rm -f /tmp/{filename}"
                ], capture_output=True, text=True, timeout=30)
                
                return scp_result.returncode == 0
            return False
        except Exception as e:
            print(f"❌ API経由ダウンロードエラー {filename}: {e}")
            return False
    
    def extract_all_images(self):
        """全画像を抽出・ダウンロード"""
        print("🎨 V100生成画像抽出・ダウンロード")
        print("=" * 50)
        print(f"🎯 インスタンス: {self.instance_name}")
        print(f"🌐 API: {self.base_url}")
        
        # 出力ディレクトリ作成
        self.local_output.mkdir(parents=True, exist_ok=True)
        print(f"📁 出力先: {self.local_output}")
        
        # ComfyUI履歴取得
        print("\n📋 ComfyUI生成履歴を取得中...")
        history = self.get_history_via_ssh()
        
        if not history:
            print("❌ 履歴が見つかりません")
            return
        
        print(f"✅ {len(history)}件の生成履歴を発見")
        
        # 画像ファイル名を抽出
        filenames = self.extract_image_filenames(history)
        
        if not filenames:
            print("❌ 画像ファイルが見つかりません")
            return
        
        print(f"🖼️ {len(filenames)}個の画像ファイルを発見")
        for filename in filenames[:10]:  # 最初の10個を表示
            print(f"  📄 {filename}")
        
        # ダウンロード実行
        print(f"\n📥 ダウンロード開始...")
        downloaded = 0
        
        for filename in filenames:
            print(f"📥 {filename}...")
            
            # まずSCP直接転送を試す
            if self.download_image_via_ssh(filename):
                downloaded += 1
                print(f"✅ SCP成功")
                continue
            
            # API経由を試す    
            if self.download_via_api_through_ssh(filename):
                downloaded += 1
                print(f"✅ API成功")
            else:
                print(f"❌ 失敗")
        
        print(f"\n🎉 完了: {downloaded}個の画像をダウンロード")
        if downloaded > 0:
            print(f"📁 保存先: {self.local_output}")
        
        # ダウンロードしたファイルを確認
        local_files = list(self.local_output.glob("*"))
        if local_files:
            print(f"\n📊 ローカルファイル:")
            for file in local_files:
                size = file.stat().st_size
                print(f"  🖼️ {file.name} ({size:,} bytes)")

def main():
    extractor = V100ImageExtractor()
    extractor.extract_all_images()

if __name__ == "__main__":
    main()