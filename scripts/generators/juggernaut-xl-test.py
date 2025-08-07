#!/usr/bin/env python3
"""
Juggernaut XL v10テスト - 2025年最高峰モデル
"""
import requests
import json
import time
from pathlib import Path

def test_juggernaut_xl():
    server_ip = "34.70.230.62"
    port = 8188
    base_url = f"http://{server_ip}:{port}"
    
    print("🏆 Juggernaut XL v10 テスト (2025年最高峰)")
    print("=" * 50)
    
    # サーバー確認
    try:
        response = requests.get(f"{base_url}/system_stats", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ サーバー接続OK")
            print(f"🎯 GPU: {data['devices'][0]['name']}")
        else:
            print("❌ サーバー応答なし")
            return False
    except:
        print("❌ 接続失敗")
        return False
    
    # Juggernaut XL v10 ワークフロー
    workflow = {
        "3": {
            "inputs": {
                "seed": 999999,
                "steps": 25,  # 高品質のため多めのステップ
                "cfg": 8.0,   # Juggernaut推奨CFG
                "sampler_name": "euler",
                "scheduler": "normal", 
                "denoise": 1.0,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            },
            "class_type": "KSampler"
        },
        "4": {
            "inputs": {
                "ckpt_name": "juggernaut_xl_v10.safetensors"
            },
            "class_type": "CheckpointLoaderSimple"
        },
        "5": {
            "inputs": {
                "width": 1024,
                "height": 1024,
                "batch_size": 1
            },
            "class_type": "EmptyLatentImage"
        },
        "6": {
            "inputs": {
                "text": "stunning professional photography, beautiful woman with long flowing hair, piercing blue eyes, natural makeup, golden hour lighting, depth of field, cinematic composition, award winning portrait, hyperrealistic, 8K ultra detailed",
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "7": {
            "inputs": {
                "text": "cartoon, anime, 3d render, illustration, painting, drawing, low quality, blurry, distorted, deformed, ugly, bad anatomy, extra limbs, bad proportions, oversaturated",
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "8": {
            "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2]
            },
            "class_type": "VAEDecode"
        },
        "9": {
            "inputs": {
                "filename_prefix": "Juggernaut_XL_v10_",
                "images": ["8", 0]
            },
            "class_type": "SaveImage"
        }
    }
    
    print("📤 Juggernaut XL v10 生成開始...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{base_url}/prompt", 
            json={"prompt": workflow}, 
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            prompt_id = result.get("prompt_id")
            print(f"✅ キューID: {prompt_id}")
            
            # 完了待機
            print("⏳ 生成中...")
            while True:
                try:
                    queue_response = requests.get(f"{base_url}/queue", timeout=10)
                    if queue_response.status_code == 200:
                        queue_data = queue_response.json()
                        running = len(queue_data.get("queue_running", []))
                        pending = len(queue_data.get("queue_pending", []))
                        
                        if running == 0 and pending == 0:
                            end_time = time.time()
                            duration = end_time - start_time
                            print(f"🎉 生成完了! 時間: {duration:.1f}秒")
                            
                            # ダウンロード
                            local_output = Path.home() / "Desktop" / "gcp" / "outputs" / "juggernaut_xl_test"
                            local_output.mkdir(parents=True, exist_ok=True)
                            
                            # 最新の画像をダウンロード
                            filename = "Juggernaut_XL_v10__00001_.png"
                            try:
                                img_response = requests.get(
                                    f"{base_url}/view",
                                    params={"filename": filename, "type": "output", "subfolder": ""},
                                    timeout=30
                                )
                                
                                if img_response.status_code == 200:
                                    local_path = local_output / filename
                                    with open(local_path, 'wb') as f:
                                        f.write(img_response.content)
                                    
                                    size = local_path.stat().st_size
                                    print(f"📥 ダウンロード成功: {filename} ({size//1024}KB)")
                                    print(f"📁 保存先: {local_path}")
                                    return True
                                else:
                                    print(f"❌ 画像ダウンロード失敗: HTTP {img_response.status_code}")
                            except Exception as e:
                                print(f"❌ ダウンロードエラー: {e}")
                            
                            return True
                        else:
                            print(f"📊 実行中:{running} 待機:{pending}")
                    
                    time.sleep(5)
                except:
                    time.sleep(2)
        else:
            print(f"❌ 送信失敗: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

if __name__ == "__main__":
    success = test_juggernaut_xl()
    if success:
        print("\n🏆 Juggernaut XL v10テスト完了!")
        print("2025年最高峰モデルでリアルフォト生成成功!")
    else:
        print("\n❌ テスト失敗")