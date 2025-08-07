#!/usr/bin/env python3
"""
V100でリアルな女性1枚テスト生成
"""
import requests
import json
import time
from pathlib import Path

def test_realistic_generation():
    server_ip = "34.70.230.62"
    port = 8188
    base_url = f"http://{server_ip}:{port}"
    
    print("🔍 V100リアル女性テスト生成")
    print("=" * 40)
    
    # テスト用ワークフロー
    workflow = {
        "3": {
            "inputs": {
                "seed": 123456,
                "steps": 20,
                "cfg": 7.5,
                "sampler_name": "euler_a",
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
                "ckpt_name": "sd_xl_base_1.0.safetensors"
            },
            "class_type": "CheckpointLoaderSimple"
        },
        "5": {
            "inputs": {
                "width": 768,
                "height": 1024,
                "batch_size": 1
            },
            "class_type": "EmptyLatentImage"
        },
        "6": {
            "inputs": {
                "text": "photorealistic portrait of beautiful woman, long hair, blue eyes, natural makeup, soft lighting, high quality, 8K resolution, professional photography",
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "7": {
            "inputs": {
                "text": "cartoon, anime, 3d render, illustration, painting, drawing, low quality, blurry, distorted, deformed, ugly, bad anatomy",
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
                "filename_prefix": "Realistic_Test_",
                "images": ["8", 0]
            },
            "class_type": "SaveImage"
        }
    }
    
    print("📤 テスト生成送信...")
    try:
        response = requests.post(
            f"{base_url}/prompt", 
            json={"prompt": workflow}, 
            timeout=30
        )
        
        print(f"📋 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            prompt_id = result.get("prompt_id")
            print(f"✅ キューID: {prompt_id}")
            
            if prompt_id:
                # 完了待機
                print("⏳ 生成待機中...")
                for i in range(60):
                    try:
                        queue_response = requests.get(f"{base_url}/queue", timeout=10)
                        if queue_response.status_code == 200:
                            queue_data = queue_response.json()
                            running = len(queue_data.get("queue_running", []))
                            pending = len(queue_data.get("queue_pending", []))
                            
                            if running == 0 and pending == 0:
                                print("🎉 生成完了!")
                                return True
                            else:
                                if i % 5 == 0:
                                    print(f"📊 実行中:{running} 待機:{pending}")
                        
                        time.sleep(2)
                    except Exception as e:
                        print(f"⚠️ 待機エラー: {e}")
                        time.sleep(1)
                
                print("⏰ タイムアウト")
            else:
                print("❌ prompt_idが取得できません")
                print(f"Response: {result}")
        else:
            print(f"❌ 送信失敗: {response.text}")
            
    except Exception as e:
        print(f"❌ 接続エラー: {e}")
    
    return False

if __name__ == "__main__":
    success = test_realistic_generation()
    if success:
        print("✅ テスト成功")
    else:
        print("❌ テスト失敗")