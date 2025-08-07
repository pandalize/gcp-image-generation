#!/usr/bin/env python3
"""
V100で2025年最新モデル性能比較テスト
"""
import requests
import json
import time
from pathlib import Path

class V100Model2025Test:
    def __init__(self):
        self.server_ip = "34.70.230.62"
        self.port = 8188
        self.base_url = f"http://{self.server_ip}:{self.port}"
        self.local_output = Path.home() / "Desktop" / "gcp" / "outputs" / "v100_2025_models"
        
    def create_workflow(self, model_name, index):
        """2025年最新モデル用ワークフロー"""
        workflow = {
            "3": {
                "inputs": {
                    "seed": 123456 + index,
                    "steps": 4 if "lightning" in model_name.lower() else 20,  # Lightning用4ステップ
                    "cfg": 6.0 if "lightning" in model_name.lower() else 7.5,
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
                    "ckpt_name": model_name
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
                    "text": "professional portrait photography, beautiful woman, natural lighting, detailed skin texture, high quality, photorealistic, DSLR, 8K resolution",
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "7": {
                "inputs": {
                    "text": "cartoon, anime, 3d render, illustration, painting, drawing, low quality, blurry, distorted, deformed, ugly, bad anatomy, extra limbs",
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
                    "filename_prefix": f"2025_Model_{index:02d}_",
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
                result = response.json()
                return result.get("prompt_id")
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"❌ エラー: {e}")
            return None
    
    def wait_for_completion(self):
        """生成完了待機"""
        while True:
            try:
                response = requests.get(f"{self.base_url}/queue", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    running = len(data.get("queue_running", []))
                    pending = len(data.get("queue_pending", []))
                    
                    if running == 0 and pending == 0:
                        return True
                    
                    print(f"📊 実行中:{running} 待機:{pending}")
                time.sleep(5)
            except:
                time.sleep(2)
    
    def download_images(self):
        """生成画像ダウンロード"""
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
                        if filename and '2025_Model_' in filename:
                            filenames.append(filename)
            
            # 新規ダウンロードのみ
            new_downloads = []
            for filename in filenames:
                local_path = self.local_output / filename
                if not local_path.exists():
                    new_downloads.append(filename)
            
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
    
    def test_2025_models(self):
        """2025年最新モデル性能テスト"""
        print("🔥 V100で2025年最新モデル性能テスト")
        print("=" * 50)
        
        # テスト対象モデル（2025年最新）
        models = [
            "juggernaut_xl_v10.safetensors",
            "devilish_photo_realism_sdxl.safetensors", 
            "realistic_vision_v6_b1.safetensors",
            "realism_engine_sdxl.safetensors",
            "sdxl_lightning_4step.safetensors"
        ]
        
        results = []
        
        for i, model in enumerate(models, 1):
            print(f"\n🎯 [{i}/{len(models)}] テスト: {model}")
            
            start_time = time.time()
            
            workflow = self.create_workflow(model, i)
            prompt_id = self.queue_prompt(workflow)
            
            if prompt_id:
                print(f"✅ キューID: {prompt_id}")
                
                # 完了待機
                self.wait_for_completion()
                
                end_time = time.time()
                duration = end_time - start_time
                
                print(f"⏱️ 生成時間: {duration:.1f}秒")
                
                results.append({
                    "model": model,
                    "duration": duration,
                    "steps": 4 if "lightning" in model.lower() else 20
                })
            else:
                print("❌ キュー失敗")
        
        # 結果表示
        print(f"\n📊 2025年最新モデル性能比較結果")
        print("=" * 60)
        
        for result in results:
            model = result['model']
            duration = result['duration']
            steps = result['steps']
            
            print(f"🎯 {model}:")
            print(f"   ⏱️  時間: {duration:.1f}秒")
            print(f"   ⚙️  ステップ: {steps}")
            print(f"   🚀 効率: {steps/duration:.1f} steps/sec")
            print()
        
        # ダウンロード
        downloaded = self.download_images()
        print(f"📥 ダウンロード完了: {downloaded}枚")
        print(f"📁 保存先: {self.local_output}")
        
        # 最速モデル特定
        if results:
            fastest = min(results, key=lambda x: x['duration'])
            print(f"\n⭐ 最速モデル: {fastest['model']} ({fastest['duration']:.1f}秒)")
            
            most_efficient = max(results, key=lambda x: x['steps']/x['duration'])
            print(f"🏆 最高効率: {most_efficient['model']} ({most_efficient['steps']/most_efficient['duration']:.1f} steps/sec)")

def main():
    tester = V100Model2025Test()
    tester.test_2025_models()

if __name__ == "__main__":
    main()