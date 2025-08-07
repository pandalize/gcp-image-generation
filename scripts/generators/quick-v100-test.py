#!/usr/bin/env python3
"""
V100修復後テスト生成 - 単一画像でテスト
"""
import requests
import json
import time

def test_v100_generation():
    server_ip = "34.70.230.62"
    port = 8188
    base_url = f"http://{server_ip}:{port}"
    
    print("🔍 V100修復後テスト生成")
    print("=" * 40)
    
    # サーバー確認
    try:
        response = requests.get(f"{base_url}/system_stats", timeout=10)
        if response.status_code == 200:
            print("✅ サーバー接続OK")
            data = response.json()
            print(f"🎯 GPU: {data['devices'][0]['name']}")
        else:
            print("❌ サーバー接続失敗")
            return
    except Exception as e:
        print(f"❌ 接続エラー: {e}")
        return
    
    # テスト用ワークフロー（シンプル）
    workflow = {
        "3": {
            "inputs": {
                "seed": 12345,
                "steps": 10,  # 少ないステップでテスト
                "cfg": 6.0,
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
                "ckpt_name": "sd_xl_base_1.0.safetensors"
            },
            "class_type": "CheckpointLoaderSimple"
        },
        "5": {
            "inputs": {
                "width": 512,  # 小さいサイズでテスト
                "height": 512,
                "batch_size": 1
            },
            "class_type": "EmptyLatentImage"
        },
        "6": {
            "inputs": {
                "text": "beautiful anime girl, masterpiece",
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "7": {
            "inputs": {
                "text": "low quality, blurry, worst quality",
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
                "filename_prefix": "V100_TEST_",
                "images": ["8", 0]
            },
            "class_type": "SaveImage"
        }
    }
    
    # プロンプト送信
    print("📤 テスト生成開始...")
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
            print("⏳ 生成待機中...")
            for i in range(60):  # 最大60秒待機
                try:
                    queue_response = requests.get(f"{base_url}/queue", timeout=10)
                    if queue_response.status_code == 200:
                        queue_data = queue_response.json()
                        running = len(queue_data.get("queue_running", []))
                        pending = len(queue_data.get("queue_pending", []))
                        
                        if running == 0 and pending == 0:
                            print("🎉 生成完了!")
                            break
                        else:
                            print(f"📊 実行中:{running} 待機:{pending}")
                    
                    time.sleep(3)
                except:
                    print(".", end="", flush=True)
                    time.sleep(1)
            
            # 履歴確認
            print("\n📋 生成結果確認...")
            history_response = requests.get(f"{base_url}/history", timeout=10)
            if history_response.status_code == 200:
                history = history_response.json()
                if prompt_id in history:
                    entry = history[prompt_id]
                    outputs = entry.get("outputs", {})
                    if outputs:
                        print("✅ 生成成功 - outputs検出")
                        for node_id, node_output in outputs.items():
                            images = node_output.get("images", [])
                            for img in images:
                                filename = img.get("filename", "unknown")
                                print(f"🖼️ 画像: {filename}")
                    else:
                        print("⚠️ outputs が空です")
                        print(f"Status: {entry.get('status', {})}")
                else:
                    print("❌ 履歴に見つかりません")
        else:
            print(f"❌ 送信失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    test_v100_generation()