#!/usr/bin/env python3
"""
V100生成画像ダウンロードツール
ComfyUI APIから画像を取得してローカルに保存
"""
import requests
import json
import os
from pathlib import Path
from datetime import datetime
import base64

class V100ImageDownloader:
    def __init__(self, server_ip="34.70.230.62", port=8188):
        self.server_ip = server_ip
        self.port = port
        self.base_url = f"http://{server_ip}:{port}"
        self.output_dir = Path.home() / "Desktop" / "gcp" / "outputs" / "v100_generated"
        
    def ensure_output_dir(self):
        """出力ディレクトリを作成"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 出力ディレクトリ: {self.output_dir}")
        
    def get_history(self, max_items=100):
        """生成履歴を取得"""
        try:
            response = requests.get(f"{self.base_url}/history", timeout=30)
            if response.status_code == 200:
                history = response.json()
                # 最新のmax_items件を取得
                sorted_history = sorted(history.items(), key=lambda x: x[0], reverse=True)
                return sorted_history[:max_items]
            return []
        except Exception as e:
            print(f"❌ 履歴取得エラー: {e}")
            return []
    
    def download_image(self, filename, subfolder, folder_type):
        """個別画像をダウンロード"""
        try:
            # ComfyUIの画像取得エンドポイント
            params = {
                "filename": filename,
                "subfolder": subfolder,
                "type": folder_type
            }
            
            response = requests.get(
                f"{self.base_url}/view",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                # 画像データを保存
                local_path = self.output_dir / filename
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                return True
            return False
        except Exception as e:
            print(f"❌ ダウンロードエラー: {e}")
            return False
    
    def download_all_images(self):
        """全ての生成画像をダウンロード"""
        print("🔍 V100生成画像ダウンロード開始")
        print("=" * 50)
        print(f"🎯 V100サーバー: {self.base_url}")
        
        # 出力ディレクトリ作成
        self.ensure_output_dir()
        
        # 履歴取得
        print("📋 生成履歴を取得中...")
        history = self.get_history()
        
        if not history:
            print("❌ 生成履歴が見つかりません")
            print("💡 V100で画像生成を実行してください")
            return
        
        print(f"✅ {len(history)}件の履歴を発見")
        
        # 各履歴から画像を抽出
        total_downloaded = 0
        for prompt_id, data in history:
            outputs = data.get('outputs', {})
            
            for node_id, node_output in outputs.items():
                images = node_output.get('images', [])
                
                for image_data in images:
                    filename = image_data.get('filename')
                    subfolder = image_data.get('subfolder', '')
                    folder_type = image_data.get('type', 'output')
                    
                    if filename:
                        print(f"📥 ダウンロード中: {filename}")
                        if self.download_image(filename, subfolder, folder_type):
                            total_downloaded += 1
                            print(f"✅ 保存完了: {self.output_dir / filename}")
                        else:
                            print(f"⚠️ スキップ: {filename}")
        
        if total_downloaded > 0:
            print(f"\n🎉 完了: {total_downloaded}枚の画像をダウンロード")
            print(f"📁 保存先: {self.output_dir}")
        else:
            print("⚠️ ダウンロード可能な画像が見つかりませんでした")
            
            # 別の方法を試す
            print("\n🔄 別の方法で画像を検索中...")
            self.try_direct_api_download()
    
    def try_direct_api_download(self):
        """API直接アクセスで画像取得を試行"""
        print("🔍 output フォルダから直接取得を試行...")
        
        # V100_Gen_で始まるファイルを探す
        for i in range(1, 31):  # 30枚を想定
            for ext in ['png', 'jpg']:
                filename = f"V100_Gen_{i:05d}_.{ext}"
                
                print(f"🔎 チェック中: {filename}")
                if self.download_image(filename, "", "output"):
                    print(f"✅ 取得成功: {filename}")
                    
        print("\n📊 ダウンロード試行完了")

def main():
    downloader = V100ImageDownloader()
    downloader.download_all_images()

if __name__ == "__main__":
    main()