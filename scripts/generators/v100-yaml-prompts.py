#!/usr/bin/env python3
"""
V100でprompts.yamlを使った画像生成・ダウンロード
"""
import requests
import json
import time
import yaml
from pathlib import Path

class V100YAMLPrompts:
    def __init__(self):
        self.server_ip = "34.70.230.62"
        self.port = 8188
        self.base_url = f"http://{self.server_ip}:{self.port}"
        self.prompts_file = Path.home() / "Desktop" / "gcp" / "prompts.yaml"
        self.local_output = Path.home() / "Desktop" / "gcp" / "outputs" / "v100_yaml_prompts"
        
    def load_prompts(self):
        """YAMLファイルからプロンプトを読み込み"""
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
        steps = prompt_config.get('steps', 25)
        cfg = prompt_config.get('cfg', 7.0)
        
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
                    "width": 768,
                    "height": 1024,
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
                    "filename_prefix": f"YAML_Prompt_{index:03d}_",
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
                        if filename and 'YAML_Prompt_' in filename:
                            filenames.append(filename)
            
            # 新規ダウンロードのみ
            new_downloads = []
            for filename in filenames:
                local_path = self.local_output / filename
                if not local_path.exists():
                    new_downloads.append(filename)
            
            if not new_downloads:
                return 0
            
            print(f"📥 新規ダウンロード: {len(new_downloads)}個")
            
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
    
    def generate_from_yaml(self):
        """prompts.yamlから画像生成・ダウンロード"""
        print("🎨 V100でprompts.yaml画像生成")
        print("=" * 50)
        print(f"📁 プロンプトファイル: {self.prompts_file}")
        print(f"📁 出力先: {self.local_output}")
        
        # プロンプト読み込み
        prompts = self.load_prompts()
        if not prompts:
            print("❌ プロンプトが見つかりません")
            return
        
        print(f"📋 読み込まれたプロンプト数: {len(prompts)}個")
        
        # 各プロンプトを生成
        queued = 0
        for i, prompt_config in enumerate(prompts, 1):
            positive = prompt_config.get('positive', '')[:60]
            print(f"\n🎯 [{i}/{len(prompts)}] {positive}...")
            
            workflow = self.create_workflow(prompt_config, i)
            prompt_id = self.queue_prompt(workflow)
            
            if prompt_id:
                print(f"✅ キューID: {prompt_id}")
                queued += 1
            else:
                print("❌ キュー失敗")
        
        if queued > 0:
            print(f"\n📊 キュー完了: {queued}/{len(prompts)}個")
            
            # 完了待機
            print("⏳ 生成完了待機...")
            max_wait = 600  # 10分最大待機
            waited = 0
            
            while waited < max_wait:
                running, pending = self.check_queue_status()
                if running == 0 and pending == 0:
                    print("✅ 全て完了!")
                    break
                
                if running + pending > 0:
                    print(f"📊 実行中:{running} 待機:{pending}")
                
                time.sleep(10)
                waited += 10
            
            # ダウンロード
            downloaded = self.download_completed_images()
            print(f"\n🎉 ダウンロード完了: {downloaded}枚")
            print(f"📁 保存先: {self.local_output}")
            
            # ローカルファイル確認
            local_files = sorted(self.local_output.glob("YAML_Prompt_*.png"))
            if local_files:
                print(f"\n📊 ローカル保存済み:")
                for file in local_files:
                    size = file.stat().st_size
                    print(f"  🖼️ {file.name} ({size//1024}KB)")
        else:
            print("❌ キューに追加された画像がありません")

def main():
    generator = V100YAMLPrompts()
    generator.generate_from_yaml()

if __name__ == "__main__":
    main()