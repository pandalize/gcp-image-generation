#!/usr/bin/env python3
"""
テスト生成画像をダウンロード
"""
import subprocess
from pathlib import Path
import requests

def download_test_image():
    instance_name = "instance-20250807-125905"
    zone = "us-central1-c"
    server_ip = "34.70.230.62"
    port = 8188
    
    local_output = Path.home() / "Desktop" / "gcp" / "outputs" / "v100_generated"
    local_output.mkdir(parents=True, exist_ok=True)
    
    print("📥 V100テスト画像ダウンロード")
    print("=" * 40)
    print(f"📁 出力先: {local_output}")
    
    # テスト画像ファイル名
    test_filename = "V100_TEST__00001_.png"
    
    # 方法1: ComfyUI API経由でダウンロード
    print(f"\n🌐 API経由ダウンロード: {test_filename}")
    try:
        response = requests.get(
            f"http://{server_ip}:{port}/view",
            params={
                "filename": test_filename,
                "type": "output",
                "subfolder": ""
            },
            timeout=30
        )
        
        if response.status_code == 200:
            local_path = local_output / test_filename
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            file_size = local_path.stat().st_size
            print(f"✅ API成功: {test_filename} ({file_size:,} bytes)")
            return True
            
        else:
            print(f"❌ API失敗: {response.status_code}")
    except Exception as e:
        print(f"❌ APIエラー: {e}")
    
    # 方法2: SCP経由でダウンロード
    print(f"\n📡 SCP経由ダウンロード: {test_filename}")
    try:
        local_path = local_output / test_filename
        
        result = subprocess.run([
            "gcloud", "compute", "scp",
            f"{instance_name}:~/ComfyUI/output/{test_filename}",
            str(local_path),
            f"--zone={zone}",
            "--quiet"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and local_path.exists():
            file_size = local_path.stat().st_size
            print(f"✅ SCP成功: {test_filename} ({file_size:,} bytes)")
            return True
        else:
            print(f"❌ SCP失敗: {result.stderr}")
    except Exception as e:
        print(f"❌ SCPエラー: {e}")
    
    return False

if __name__ == "__main__":
    success = download_test_image()
    if success:
        print("\n🎉 ダウンロード完了!")
    else:
        print("\n❌ ダウンロード失敗")