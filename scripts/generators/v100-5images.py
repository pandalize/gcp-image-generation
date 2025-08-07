#!/usr/bin/env python3
"""
V100で5枚画像生成
"""
import requests
import json
import time
from pathlib import Path

class V100FiveImages:
    def __init__(self):
        self.server_ip = "34.70.230.62"
        self.port = 8188
        self.base_url = f"http://{self.server_ip}:{self.port}"
        self.local_output = Path.home() / "Desktop" / "gcp" / "outputs" / "v100_generated"
        
    def create_workflow(self, prompt_text, index):
        """ワークフロー作成"""
        workflow = {
            "3": {
                "inputs": {
                    "seed": int(time.time() * 1000000) % 1000000 + index,
                    "steps": 12,
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
                    "width": 512,
                    "height": 512,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "6": {
                "inputs": {
                    "text": prompt_text,
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
                    "filename_prefix": f"V100_Quick_{index:02d}_",
                    "images": ["8", 0]
                },
                "class_type": "SaveImage"
            }
        }
        return workflow
    
    def queue_prompt(self, workflow):
        """プロンプト送信"""
        try:
            response = requests.post(
                f"{self.base_url}/prompt", 
                json={"prompt": workflow}, 
                timeout=30
            )
            if response.status_code == 200:
                return response.json().get("prompt_id")
            return None
        except Exception as e:
            print(f"❌ エラー: {e}")
            return None
    
    def wait_completion(self):
        """完了待機"""
        print("⏳ 生成完了待機...")
        for i in range(120):  # 最大2分
            try:
                response = requests.get(f"{self.base_url}/queue", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    running = len(data.get("queue_running", []))
                    pending = len(data.get("queue_pending", []))
                    
                    if running == 0 and pending == 0:
                        print("✅ 全て完了!")
                        return True
                    
                    if i % 10 == 0:  # 10回に1回表示
                        print(f"📊 実行中:{running} 待機:{pending}")
                time.sleep(1)
            except:
                time.sleep(1)
        return False
    
    def download_images(self):
        """画像ダウンロード"""
        self.local_output.mkdir(parents=True, exist_ok=True)
        print("\n📥 画像ダウンロード...")
        
        try:
            response = requests.get(f"{self.base_url}/history", timeout=30)
            if response.status_code != 200:
                return 0
                
            history = response.json()
            filenames = []
            
            for prompt_id, data in history.items():
                outputs = data.get('outputs', {})
                for node_id, node_output in outputs.items():
                    images = node_output.get('images', [])
                    for img in images:
                        filename = img.get('filename')
                        if filename and 'V100_Quick_' in filename:
                            filenames.append(filename)
            
            filenames = sorted(list(set(filenames)))[-5:]  # 最新5個
            downloaded = 0
            
            for filename in filenames:
                try:
                    response = requests.get(
                        f"{self.base_url}/view",
                        params={"filename": filename, "type": "output", "subfolder": ""},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        local_path = self.local_output / filename
                        with open(local_path, 'wb') as f:
                            f.write(response.content)
                        
                        size = local_path.stat().st_size
                        print(f"✅ {filename} ({size//1024}KB)")
                        downloaded += 1
                        
                except Exception as e:
                    print(f"❌ {filename} - {e}")
            
            return downloaded
            
        except Exception as e:
            print(f"❌ ダウンロードエラー: {e}")
            return 0
    
    def generate_5_images(self):
        """5枚生成実行"""
        print("🎨 V100で5枚画像生成")
        print("=" * 30)
        
        prompts = [
            "beautiful anime girl, masterpiece, detailed",
            "cute cat, fluffy, adorable, high quality",
            "fantasy landscape, magical, colorful, detailed",
            "robot mecha, futuristic, cool design",
            "flower garden, spring, bright colors, peaceful"
        ]
        
        # 全てキューに追加
        queued = 0
        for i, prompt in enumerate(prompts, 1):
            print(f"🎯 [{i}/5] {prompt[:30]}...")
            workflow = self.create_workflow(prompt, i)
            prompt_id = self.queue_prompt(workflow)
            
            if prompt_id:
                print(f"✅ ID: {prompt_id}")
                queued += 1
            else:
                print("❌ 失敗")
        
        if queued > 0:
            print(f"\n📊 {queued}/5 キューに追加完了")
            
            # 完了待機
            if self.wait_completion():
                # ダウンロード
                downloaded = self.download_images()
                print(f"\n🎉 完了: {downloaded}枚ダウンロード")
            else:
                print("\n⏰ タイムアウト")
        else:
            print("\n❌ キュー追加失敗")

def main():
    generator = V100FiveImages()
    generator.generate_5_images()

if __name__ == "__main__":
    main()