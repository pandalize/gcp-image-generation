#!/usr/bin/env python3
"""
V100 GPU フォトリアリスティック人間生成スクリプト (Juggernaut XL v10)
ネット上で人気の超リアル人間プロンプトを使用
"""

import requests
import json
import time
import os
from datetime import datetime

class V100PhotorealisticHuman:
    def __init__(self):
        self.server_ip = "localhost"
        self.port = 8188
        self.base_url = f"http://{self.server_ip}:{self.port}"
        
    def get_famous_photorealistic_prompt(self):
        """ネット上で有名なフォトリアリスティック人間プロンプト"""
        return {
            'name': 'Photorealistic_Human_Portrait_Master',
            'description': 'インターネット上で評価の高い超リアル人間生成プロンプト',
            'positive': 'RAW photo, (highly detailed skin), (8k uhd:1.1), dslr, soft lighting, high quality, film grain, Fujifilm XT3, photorealistic, hyperrealistic, ultra detailed face, beautiful detailed eyes, detailed skin texture, natural skin imperfections, subsurface scattering, realistic, portrait photography, professional photography, 85mm lens, depth of field, bokeh, natural lighting, studio lighting, perfect face, symmetrical face, gorgeous, stunning beautiful woman, 25 years old, wavy brown hair, hazel eyes, subtle makeup, natural beauty, elegant pose, confident expression, white shirt, minimalist background, commercial photography style, magazine cover quality, award winning photography, masterpiece, best quality',
            'negative': 'anime, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed face, blurry, bad art, bad anatomy, 3d render, double, clones, twins, brothers, same person, repeated person, long neck, make up, ugly, animated, hat, poorly drawn, out of frame, thin, weird, disfigured, weird colors, cartoon, animated, render, missing limbs, child, childish, young, loli',
            'cfg': 9.5,
            'steps': 100,
            'width': 1024,
            'height': 1024,
            'sampler': 'dpmpp_2m',
            'scheduler': 'karras'
        }

    def create_photorealistic_workflow(self, config):
        """超リアル人間生成ワークフロー作成"""
        seed = int(time.time() * 1000000) % (2**32)
        
        workflow = {
            "1": {
                "inputs": {
                    "ckpt_name": "juggernaut_v10.safetensors"
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "2": {
                "inputs": {
                    "text": config['positive'],
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "3": {
                "inputs": {
                    "text": config['negative'],
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "4": {
                "inputs": {
                    "width": config['width'],
                    "height": config['height'],
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "5": {
                "inputs": {
                    "seed": seed,
                    "steps": config['steps'],
                    "cfg": config['cfg'],
                    "sampler_name": config['sampler'],
                    "scheduler": config['scheduler'],
                    "denoise": 1.0,
                    "model": ["1", 0],
                    "positive": ["2", 0],
                    "negative": ["3", 0],
                    "latent_image": ["4", 0]
                },
                "class_type": "KSampler"
            },
            "6": {
                "inputs": {
                    "samples": ["5", 0],
                    "vae": ["1", 2]
                },
                "class_type": "VAEDecode"
            },
            "7": {
                "inputs": {
                    "filename_prefix": f"V100_PHOTOREALISTIC_HUMAN",
                    "images": ["6", 0]
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
                return response.json()
            else:
                print(f"Error queuing prompt: {response.status_code}")
                return None
        except Exception as e:
            print(f"Connection error: {e}")
            return None

    def get_queue_info(self):
        """キュー情報取得"""
        try:
            response = requests.get(f"{self.base_url}/queue", timeout=10)
            return response.json()
        except Exception as e:
            print(f"Error getting queue info: {e}")
            return None

    def wait_for_completion(self, prompt_id, name):
        """生成完了まで待機"""
        print(f"🎨 Generating photorealistic human: {name}...")
        start_time = time.time()
        max_wait = 300  # 5分最大待機時間
        waited = 0
        
        while waited < max_wait:
            queue_info = self.get_queue_info()
            if queue_info:
                queue_running = queue_info.get('queue_running', [])
                queue_pending = queue_info.get('queue_pending', [])
                
                in_queue = False
                in_pending = False
                
                for item in queue_running:
                    if len(item) > 1 and isinstance(item[1], dict) and item[1].get('prompt_id') == prompt_id:
                        in_queue = True
                        break
                
                for item in queue_pending:
                    if len(item) > 1 and isinstance(item[1], dict) and item[1].get('prompt_id') == prompt_id:
                        in_pending = True
                        break
                
                if not in_queue and not in_pending:
                    elapsed = time.time() - start_time
                    print(f"✅ {name} completed! ({elapsed:.1f}s)")
                    return True
            
            time.sleep(5)
            waited += 5
            
            if waited % 30 == 0:
                elapsed = time.time() - start_time
                print(f"⏳ {name} generating... ({elapsed:.0f}s elapsed)")
        
        print(f"⏰ Timeout waiting for {name}")
        return False

    def generate_photorealistic_human(self):
        """フォトリアリスティック人間生成"""
        config = self.get_famous_photorealistic_prompt()
        
        print(f"🚀 V100 Photorealistic Human Generation 開始 ({datetime.now()})")
        print(f"Model: Juggernaut XL v10")
        print(f"GPU: Tesla V100-SXM2-16GB")
        print(f"Prompt: Famous Internet Photorealistic Human")
        print(f"Settings: {config['steps']} steps, CFG {config['cfg']}")
        print("=" * 80)
        
        workflow = self.create_photorealistic_workflow(config)
        result = self.queue_prompt(workflow)
        
        if result and 'prompt_id' in result:
            prompt_id = result['prompt_id']
            print(f"📋 Queued with ID: {prompt_id}")
            
            if self.wait_for_completion(prompt_id, config['name']):
                print(f"🎉 Photorealistic human successfully generated!")
                print(f"📁 Output: V100_PHOTOREALISTIC_HUMAN_*.png")
                return True
            else:
                print(f"❌ Generation failed")
                return False
        else:
            print(f"❌ Failed to queue prompt")
            return False

def main():
    print("V100 Photorealistic Human Generation")
    
    generator = V100PhotorealisticHuman()
    
    # Test connection
    try:
        response = requests.get(f"{generator.base_url}/system_stats", timeout=10)
        if response.status_code == 200:
            print("✅ V100 ComfyUI connection successful")
        else:
            print("❌ V100 ComfyUI connection failed")
            return
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return
    
    # Generate photorealistic human
    success = generator.generate_photorealistic_human()
    
    if success:
        print(f"\n🏁 Photorealistic Human Generation完了: {datetime.now()}")
        print("📸 Check ComfyUI output folder for the generated image!")
    else:
        print(f"\n❌ Generation failed: {datetime.now()}")

if __name__ == "__main__":
    main()