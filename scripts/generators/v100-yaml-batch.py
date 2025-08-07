#!/usr/bin/env python3
"""
V100でYAMLプロンプト30枚一括生成・ダウンロード
"""
import requests
import json
import time
import yaml
import subprocess
from pathlib import Path
import os

class V100YAMLBatch:
    def __init__(self):
        self.server_ip = "34.70.230.62"
        self.port = 8188
        self.base_url = f"http://{self.server_ip}:{self.port}"
        self.prompts_file = Path(__file__).parent.parent.parent / "prompts.yaml"
        self.local_output = Path.home() / "Desktop" / "gcp" / "outputs" / "v100_generated"
        self.instance_name = "instance-20250807-125905"
        self.zone = "us-central1-c"
        
    def load_prompts(self):
        """YAMLプロンプト読み込み"""
        try:
            with open(self.prompts_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data.get('prompts', [])
        except Exception as e:
            print(f"❌ プロンプト読み込みエラー: {e}")
            return []
    
    def create_workflow(self, prompt_config, index):
        """ワークフロー作成"""
        positive = prompt_config.get('positive', '')
        negative = prompt_config.get('negative', 'low quality, blurry, worst quality')
        steps = min(prompt_config.get('steps', 15), 15)  # 高速化
        cfg = prompt_config.get('cfg', 6.0)
        
        workflow = {
            "3": {
                "inputs": {
                    "seed": int(time.time() * 1000000) % 1000000 + index,
                    "steps": steps,
                    "cfg": cfg,
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
                    "width": 512,  # 高速化のため小さく
                    "height": 512,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "6": {
                "inputs": {
                    "text": positive,
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "7": {
                "inputs": {
                    "text": negative,
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
                    "filename_prefix": f"YAML_Gen_{index:03d}_",
                    "images": ["8", 0]
                },
                "class_type": "SaveImage"
            }
        }
        return workflow
    
    def queue_prompt(self, workflow):
        """プロンプトをキューに追加"""
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
            print(f"❌ キューエラー: {e}")
            return None
    
    def wait_for_completion(self):
        """すべての生成完了を待機"""
        print("⏳ 生成完了待機...")
        while True:
            try:
                response = requests.get(f"{self.base_url}/queue", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    running = len(data.get("queue_running", []))
                    pending = len(data.get("queue_pending", []))
                    
                    if running == 0 and pending == 0:
                        print("✅ すべての生成完了!")
                        return True
                    
                    print(f"📊 実行中: {running}, 待機中: {pending}")
                time.sleep(5)
            except:
                time.sleep(2)
    
    def download_generated_images(self):
        """生成画像をAPI経由でダウンロード"""
        self.local_output.mkdir(parents=True, exist_ok=True)
        print(f"\n📥 画像ダウンロード開始")
        print(f"📁 出力先: {self.local_output}")
        
        # 履歴から画像ファイル名を取得
        try:
            response = requests.get(f"{self.base_url}/history", timeout=30)
            if response.status_code != 200:
                print("❌ 履歴取得失敗")
                return 0
                
            history = response.json()
            filenames = []
            
            for prompt_id, data in history.items():
                outputs = data.get('outputs', {})
                for node_id, node_output in outputs.items():
                    images = node_output.get('images', [])
                    for img in images:
                        filename = img.get('filename')
                        if filename and 'YAML_Gen_' in filename:
                            filenames.append(filename)
            
            # 重複削除・ソート
            filenames = sorted(list(set(filenames)))
            print(f"🖼️ 発見: {len(filenames)}個の画像")
            
            # ダウンロード
            downloaded = 0
            for filename in filenames:
                try:
                    response = requests.get(
                        f"{self.base_url}/view",
                        params={
                            "filename": filename,
                            "type": "output",
                            "subfolder": ""
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        local_path = self.local_output / filename
                        with open(local_path, 'wb') as f:
                            f.write(response.content)
                        
                        size = local_path.stat().st_size
                        print(f"✅ {filename} ({size:,} bytes)")
                        downloaded += 1
                    else:
                        print(f"❌ {filename} - HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ {filename} - エラー: {e}")
            
            return downloaded
            
        except Exception as e:
            print(f"❌ ダウンロード処理エラー: {e}")
            return 0
    
    def generate_and_download_all(self):
        """30枚一括生成・ダウンロード"""
        print("🎨 V100 YAML一括生成・ダウンロード")
        print("=" * 50)
        
        # プロンプト読み込み
        prompts = self.load_prompts()
        if not prompts:
            print("❌ プロンプトが見つかりません")
            return
        
        print(f"📋 プロンプト数: {len(prompts)}")
        
        # すべてのプロンプトをキューに追加
        successful_queues = 0
        for i, prompt_config in enumerate(prompts, 1):
            positive = prompt_config.get('positive', '')[:50]
            print(f"\n🎯 [{i}/{len(prompts)}] キューに追加: {positive}...")
            
            workflow = self.create_workflow(prompt_config, i)
            prompt_id = self.queue_prompt(workflow)
            
            if prompt_id:
                print(f"✅ ID: {prompt_id}")
                successful_queues += 1
            else:
                print("❌ キュー失敗")
        
        print(f"\n📊 キュー完了: {successful_queues}/{len(prompts)}")
        
        if successful_queues > 0:
            # 完了待機
            self.wait_for_completion()
            
            # ダウンロード
            downloaded = self.download_generated_images()
            print(f"\n🎉 完了: {downloaded}個の画像をダウンロード")
        else:
            print("❌ キューに追加された画像がありません")

def main():
    generator = V100YAMLBatch()
    generator.generate_and_download_all()

if __name__ == "__main__":
    main()