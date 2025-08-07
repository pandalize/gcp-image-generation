#!/usr/bin/env python3
"""
V100でリアルな女の子100枚生成・ダウンロード
"""
import requests
import json
import time
import random
from pathlib import Path

class V100RealisticGirls:
    def __init__(self):
        self.server_ip = "34.70.230.62"
        self.port = 8188
        self.base_url = f"http://{self.server_ip}:{self.port}"
        self.local_output = Path.home() / "Desktop" / "gcp" / "outputs" / "v100_realistic_girls"
        
    def create_realistic_prompts(self):
        """リアルな女性のプロンプト生成"""
        base_styles = [
            "photorealistic portrait of beautiful woman",
            "realistic photo of attractive young woman", 
            "professional headshot of beautiful girl",
            "high quality portrait photography of woman",
            "realistic beautiful female model photo"
        ]
        
        features = [
            "long hair", "short hair", "curly hair", "straight hair",
            "blue eyes", "brown eyes", "green eyes", "hazel eyes",
            "soft smile", "gentle expression", "confident look", "serene face",
            "natural makeup", "elegant style", "casual wear", "professional attire"
        ]
        
        lighting = [
            "natural lighting", "soft studio lighting", "golden hour light",
            "professional photography lighting", "window light", "warm lighting"
        ]
        
        quality_terms = [
            "8K resolution", "ultra detailed", "high quality", "masterpiece",
            "professional photography", "DSLR photo", "sharp focus", "realistic skin texture"
        ]
        
        prompts = []
        for i in range(100):
            prompt_parts = [
                random.choice(base_styles),
                random.choice(features),
                random.choice(features),
                random.choice(lighting),
                random.choice(quality_terms),
                random.choice(quality_terms)
            ]
            
            positive = ", ".join(prompt_parts)
            negative = "cartoon, anime, 3d render, illustration, painting, drawing, low quality, blurry, distorted, deformed, ugly, bad anatomy, extra limbs, bad proportions"
            
            prompts.append({
                "positive": positive,
                "negative": negative,
                "steps": random.choice([15, 18, 20]),
                "cfg": random.uniform(6.0, 8.0)
            })
        
        return prompts
    
    def create_workflow(self, prompt_config, index):
        """ワークフロー作成"""
        workflow = {
            "3": {
                "inputs": {
                    "seed": random.randint(1000, 999999),
                    "steps": prompt_config["steps"],
                    "cfg": prompt_config["cfg"],
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
                    "width": 768,  # より高解像度
                    "height": 1024,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "6": {
                "inputs": {
                    "text": prompt_config["positive"],
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "7": {
                "inputs": {
                    "text": prompt_config["negative"],
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
                    "filename_prefix": f"Realistic_Girl_{index:03d}_",
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
    
    def check_queue_status(self):
        """キュー状況確認"""
        try:
            response = requests.get(f"{self.base_url}/queue", timeout=10)
            if response.status_code == 200:
                data = response.json()
                running = len(data.get("queue_running", []))
                pending = len(data.get("queue_pending", []))
                return running, pending
            return 0, 0
        except:
            return 0, 0
    
    def download_completed_images(self):
        """完成した画像をダウンロード"""
        self.local_output.mkdir(parents=True, exist_ok=True)
        
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
                        if filename and 'Realistic_Girl_' in filename:
                            filenames.append(filename)
            
            # 新規ダウンロードのみ
            new_downloads = []
            for filename in filenames:
                local_path = self.local_output / filename
                if not local_path.exists():
                    new_downloads.append(filename)
            
            if not new_downloads:
                return 0
            
            print(f"\n📥 新規ダウンロード: {len(new_downloads)}個")
            
            downloaded = 0
            for filename in new_downloads:
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
    
    def generate_100_realistic_girls(self):
        """100枚のリアルな女性画像生成・ダウンロード"""
        print("🎨 V100でリアルな女の子100枚生成")
        print("=" * 50)
        
        # プロンプト生成
        print("📋 リアルな女性プロンプト100個生成中...")
        prompts = self.create_realistic_prompts()
        
        # バッチ処理（20枚ずつ）
        batch_size = 20
        total_downloaded = 0
        
        for batch_num in range(0, 100, batch_size):
            batch_end = min(batch_num + batch_size, 100)
            batch_prompts = prompts[batch_num:batch_end]
            
            print(f"\n🎯 バッチ {batch_num//batch_size + 1}/5: {batch_num+1}-{batch_end}枚目")
            
            # バッチをキューに追加
            queued = 0
            for i, prompt_config in enumerate(batch_prompts, batch_num + 1):
                workflow = self.create_workflow(prompt_config, i)
                prompt_id = self.queue_prompt(workflow)
                
                if prompt_id:
                    queued += 1
                    if i % 5 == 0:
                        print(f"📤 [{i}/100] キュー追加中...")
            
            print(f"✅ バッチキュー完了: {queued}/{len(batch_prompts)}")
            
            # バッチ完了待機
            print("⏳ バッチ生成完了待機...")
            while True:
                running, pending = self.check_queue_status()
                if running == 0 and pending == 0:
                    print("✅ バッチ完了!")
                    break
                
                if running + pending > 0:
                    print(f"📊 実行中:{running} 待機:{pending}")
                time.sleep(10)
            
            # バッチダウンロード
            downloaded = self.download_completed_images()
            total_downloaded += downloaded
            print(f"📥 バッチダウンロード: {downloaded}枚")
            
            # 次バッチ前に少し待機
            if batch_end < 100:
                print("⏸️ 次バッチまで5秒待機...")
                time.sleep(5)
        
        # 最終結果
        print(f"\n🎉 100枚生成完了!")
        print(f"📊 総ダウンロード数: {total_downloaded}枚")
        print(f"📁 保存先: {self.local_output}")
        
        # ローカルファイル確認
        local_files = sorted(self.local_output.glob("Realistic_Girl_*.png"))
        print(f"📋 ローカル保存済み: {len(local_files)}枚")

def main():
    generator = V100RealisticGirls()
    generator.generate_100_realistic_girls()

if __name__ == "__main__":
    main()