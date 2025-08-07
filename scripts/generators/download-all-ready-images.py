#!/usr/bin/env python3
"""
V100で生成完了した画像を全てローカルダウンロード
"""
import requests
import json
import time
from pathlib import Path

def download_all_ready_images():
    server_ip = "34.70.230.62"
    port = 8188
    base_url = f"http://{server_ip}:{port}"
    local_output = Path.home() / "Desktop" / "gcp" / "outputs" / "v100_generated"
    local_output.mkdir(parents=True, exist_ok=True)
    
    print("📥 V100生成済み画像を全てダウンロード")
    print("=" * 50)
    print(f"📁 出力先: {local_output}")
    
    try:
        # 履歴から完成した画像を取得
        response = requests.get(f"{base_url}/history", timeout=30)
        if response.status_code != 200:
            print("❌ 履歴取得失敗")
            return
            
        history = response.json()
        filenames = []
        
        # 完成した画像のファイル名を収集
        for prompt_id, data in history.items():
            # 完了したもののみ（エラーでないもの）
            status = data.get('status', {})
            if status.get('completed', False) or status.get('status_str') == 'success':
                outputs = data.get('outputs', {})
                for node_id, node_output in outputs.items():
                    images = node_output.get('images', [])
                    for img in images:
                        filename = img.get('filename')
                        if filename:
                            filenames.append(filename)
        
        # 重複削除・ソート
        unique_filenames = sorted(list(set(filenames)))
        print(f"🖼️ 発見: {len(unique_filenames)}個の完成画像")
        
        if not unique_filenames:
            print("⚠️ 完成した画像が見つかりません")
            return
        
        # 既にダウンロード済みをスキップ
        new_downloads = []
        for filename in unique_filenames:
            local_path = local_output / filename
            if not local_path.exists():
                new_downloads.append(filename)
            else:
                print(f"⏭️ スキップ: {filename} (既存)")
        
        print(f"📦 新規ダウンロード対象: {len(new_downloads)}個")
        
        # ダウンロード実行
        downloaded = 0
        for i, filename in enumerate(new_downloads, 1):
            print(f"\n📥 [{i}/{len(new_downloads)}] {filename}")
            
            try:
                response = requests.get(
                    f"{base_url}/view",
                    params={
                        "filename": filename,
                        "type": "output",
                        "subfolder": ""
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    local_path = local_output / filename
                    with open(local_path, 'wb') as f:
                        f.write(response.content)
                    
                    size = local_path.stat().st_size
                    print(f"✅ 完了 ({size//1024}KB)")
                    downloaded += 1
                else:
                    print(f"❌ HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"❌ エラー: {e}")
        
        # 結果表示
        print(f"\n🎉 ダウンロード完了: {downloaded}個")
        print(f"📁 保存先: {local_output}")
        
        # ローカルファイル一覧表示
        local_files = sorted(local_output.glob("*"))
        if local_files:
            print(f"\n📊 ローカル画像一覧 ({len(local_files)}個):")
            for file in local_files:
                size = file.stat().st_size
                print(f"  🖼️ {file.name} ({size//1024}KB)")
        
        return downloaded
        
    except Exception as e:
        print(f"❌ 処理エラー: {e}")
        return 0

if __name__ == "__main__":
    download_all_ready_images()