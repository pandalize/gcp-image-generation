#!/usr/bin/env python3
"""
V100 GPU 超高品質5枚生成スクリプト (Juggernaut XL v10 Ultimate Quality)
最高設定での究極品質画像生成
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

class V100UltraQualityGenerator:
    def __init__(self):
        self.server_ip = "localhost"  # V100 ComfyUI
        self.port = 8188
        self.base_url = f"http://{self.server_ip}:{self.port}"
        self.output_dir = "/home/fujinoyuki/v100_ultra_quality"
        self.create_output_dir()
        
    def create_output_dir(self):
        """Create output directory if it doesn't exist."""
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"V100 Ultra Quality Output directory: {self.output_dir}")
    
    def get_ultra_quality_prompts(self):
        """5つの最高品質プロンプト設定"""
        return [
            {
                'name': 'Ultra_Portrait_Masterpiece_01',
                'description': '究極ポートレート傑作 #1',
                'positive': 'masterpiece, best quality, ultra high resolution, 8K, photorealistic, professional photography, studio lighting, perfect face, flawless skin, detailed eyes, natural beauty, elegant pose, soft shadows, cinematic composition, award winning photography, magazine cover quality, hyperrealistic, ultra detailed, perfect anatomy, beautiful woman, sophisticated lighting setup, depth of field, bokeh background, premium quality',
                'negative': 'worst quality, low quality, normal quality, lowres, blurry, pixelated, jpeg artifacts, grainy, noise, distorted, deformed, ugly, bad anatomy, bad proportions, extra limbs, cloned face, malformed limbs, gross proportions, missing arms, missing legs, extra arms, extra legs, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed face, ugly face, bad face, fat, old, mature, child, loli, amateur, unprofessional, low production value',
                'cfg': 9.0,
                'steps': 80,
                'width': 1024,
                'height': 1024,
                'sampler': 'dpmpp_2m',
                'scheduler': 'karras'
            },
            {
                'name': 'Ultra_Fashion_Editorial_02',
                'description': 'ファッション雑誌編集部品質 #2',
                'positive': 'high fashion editorial, vogue style, professional model, perfect makeup, flawless skin texture, studio lighting, fashion photography masterpiece, commercial quality, magazine cover, elegant pose, sophisticated styling, luxury aesthetic, premium fashion shoot, artistic composition, dramatic lighting, beauty retouching quality, ultra sharp details, crystal clear image, perfect symmetry, editorial excellence, haute couture quality',
                'negative': 'casual wear, amateur photography, poor lighting, bad makeup, skin imperfections, low fashion, cheap clothing, unprofessional styling, bad composition, harsh lighting, overexposed, underexposed, motion blur, focus blur, compression artifacts, low resolution, pixelated, distorted proportions, unnatural pose, amateurish, DIY fashion, poor quality fabric',
                'cfg': 9.5,
                'steps': 85,
                'width': 1024,
                'height': 1024,
                'sampler': 'dpmpp_2m',
                'scheduler': 'karras'
            },
            {
                'name': 'Ultra_Cinematic_Portrait_03',
                'description': '映画品質シネマティックポートレート #3',
                'positive': 'cinematic portrait, movie quality, Hollywood production value, film grain, cinematic lighting, dramatic shadows, depth of field, bokeh, anamorphic lens, color grading, film photography, cinema quality, professional cinematography, movie star quality, epic portrait, cinematic composition, film studio lighting, premium production, theatrical quality, blockbuster movie style, ultra cinematic, perfect film aesthetics',
                'negative': 'home video quality, amateur filmmaking, poor cinematography, flat lighting, no depth, digital video look, cheap production, low budget, poor color grading, overlit, underlit, harsh shadows, no atmosphere, unprofessional, television quality, soap opera look, low production value, poor film grain, digital artifacts, compression',
                'cfg': 8.5,
                'steps': 75,
                'width': 1024,
                'height': 1024,
                'sampler': 'euler_ancestral',
                'scheduler': 'karras'
            },
            {
                'name': 'Ultra_Luxury_Portrait_04',
                'description': '高級ラグジュアリーポートレート #4',
                'positive': 'luxury portrait, premium quality, high-end photography, expensive production, elite fashion, luxury brand quality, sophisticated elegance, refined beauty, upscale aesthetic, premium lighting, luxury studio setup, high-class photography, exclusive quality, VIP treatment, luxury magazine, premium brand campaign, elite model, high society, luxury lifestyle, expensive taste, premium materials, gold standard quality',
                'negative': 'budget photography, cheap production, low-end quality, mass market, discount brand, poor materials, cheap lighting, budget studio, amateur setup, low-class, common quality, basic production, standard photography, ordinary lighting, cheap aesthetic, low-cost, economy quality, bargain production, discount quality, mass production look',
                'cfg': 10.0,
                'steps': 90,
                'width': 1024,
                'height': 1024,
                'sampler': 'dpmpp_2m',
                'scheduler': 'karras'
            },
            {
                'name': 'Ultra_Artistic_Masterwork_05',
                'description': 'アーティスティック最高傑作 #5',
                'positive': 'artistic masterpiece, fine art photography, gallery quality, museum piece, artistic excellence, creative vision, innovative composition, artistic lighting, fine art portrait, contemporary art, artistic interpretation, creative masterwork, art gallery exhibition, fine art print, artistic perfection, creative genius, avant-garde photography, artistic innovation, fine art aesthetic, museum quality, artistic brilliance, creative artistry, fine art mastery',
                'negative': 'commercial photography, stock photo, generic composition, unoriginal, copy-cat, uninspired, basic photography, conventional, ordinary, predictable, cliche, formulaic, mass produced, template-based, unimaginative, boring, standard, typical, common, usual, normal, average, mediocre, mundane, conventional wisdom, by-the-numbers, paint-by-numbers, cookie-cutter',
                'cfg': 11.0,
                'steps': 100,
                'width': 1024,
                'height': 1024,
                'sampler': 'dpmpp_sde',
                'scheduler': 'karras'
            }
        ]

    def create_ultra_workflow_json(self, config):
        """Create ultra-high quality ComfyUI workflow JSON for Juggernaut XL v10"""
        # 高精度シード生成
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
                    "filename_prefix": f"V100_ULTRA_{config['name']}",
                    "images": ["6", 0]
                },
                "class_type": "SaveImage"
            }
        }
        return workflow

    def queue_prompt(self, workflow):
        """Queue a prompt for generation"""
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
        """Get current queue information"""
        try:
            response = requests.get(f"{self.base_url}/queue", timeout=10)
            return response.json()
        except Exception as e:
            print(f"Error getting queue info: {e}")
            return None

    def wait_for_completion(self, prompt_id, config_name):
        """Wait for a specific prompt to complete"""
        print(f"🎨 Generating ultra-quality {config_name}...")
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
                
                # Check running queue
                for item in queue_running:
                    if len(item) > 1 and isinstance(item[1], dict) and item[1].get('prompt_id') == prompt_id:
                        in_queue = True
                        break
                
                # Check pending queue  
                for item in queue_pending:
                    if len(item) > 1 and isinstance(item[1], dict) and item[1].get('prompt_id') == prompt_id:
                        in_pending = True
                        break
                
                if not in_queue and not in_pending:
                    elapsed = time.time() - start_time
                    print(f"✅ {config_name} completed! ({elapsed:.1f}s)")
                    return True
            
            time.sleep(5)
            waited += 5
            
            # 進捗表示
            if waited % 30 == 0:
                elapsed = time.time() - start_time
                print(f"⏳ {config_name} generating... ({elapsed:.0f}s elapsed)")
        
        print(f"⏰ Timeout waiting for {config_name}")
        return False

    def generate_ultra_quality_images(self):
        """Generate 5 ultra-high quality images"""
        configs = self.get_ultra_quality_prompts()
        
        print(f"🚀 V100 Ultra Quality 5枚生成開始 ({datetime.now()})")
        print(f"Model: Juggernaut XL v10")
        print(f"GPU: Tesla V100-SXM2-16GB")
        print(f"Quality: Ultra High (75-100 steps, CFG 8.5-11.0)")
        print("=" * 80)
        
        total_start = time.time()
        successful_generations = 0
        results = []
        
        for i, config in enumerate(configs, 1):
            print(f"\n{'='*60}")
            print(f"🎯 Ultra Quality Image {i}/5: {config['name']}")
            print(f"📝 Description: {config['description']}")
            print(f"⚙️  Settings: {config['steps']} steps, CFG {config['cfg']}, {config['sampler']}")
            print(f"{'='*60}")
            
            workflow = self.create_ultra_workflow_json(config)
            result = self.queue_prompt(workflow)
            
            if result and 'prompt_id' in result:
                prompt_id = result['prompt_id']
                print(f"📋 Queued with ID: {prompt_id}")
                
                if self.wait_for_completion(prompt_id, config['name']):
                    successful_generations += 1
                    results.append({
                        'name': config['name'],
                        'description': config['description'],
                        'steps': config['steps'],
                        'cfg': config['cfg'],
                        'status': 'success'
                    })
                    print(f"🎉 {config['name']} successfully generated!")
                else:
                    results.append({
                        'name': config['name'],
                        'description': config['description'], 
                        'steps': config['steps'],
                        'cfg': config['cfg'],
                        'status': 'failed'
                    })
                    print(f"❌ {config['name']} generation failed")
            else:
                print(f"❌ Failed to queue {config['name']}")
                results.append({
                    'name': config['name'],
                    'description': config['description'],
                    'steps': config['steps'], 
                    'cfg': config['cfg'],
                    'status': 'queue_failed'
                })
        
        total_time = time.time() - total_start
        
        # 結果サマリー
        print(f"\n{'='*60}")
        print("🎉 V100 Ultra Quality Generation Complete!")
        print(f"{'='*60}")
        print(f"✅ Successful generations: {successful_generations}/5")
        print(f"⏱️  Total time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
        if successful_generations > 0:
            print(f"📊 Average per image: {total_time/successful_generations:.1f} seconds")
        print(f"📁 Output directory: /home/fujinoyuki/ComfyUI/output/")
        print(f"🏷️  File prefix: V100_ULTRA_*")
        print(f"⏰ Completed at: {datetime.now()}")
        
        print("\n📋 Generation Results:")
        print("-" * 60)
        for result in results:
            status_icon = "✅" if result['status'] == 'success' else "❌"
            print(f"{status_icon} {result['name']}: {result['steps']}steps, CFG{result['cfg']} - {result['status']}")
        
        return results

def main():
    print("V100 Ultra Quality 5枚生成開始")
    
    generator = V100UltraQualityGenerator()
    
    # Test connection
    try:
        response = requests.get(f"{generator.base_url}/system_stats", timeout=10)
        if response.status_code == 200:
            print("✅ V100 ComfyUI connection successful")
            gpu_info = response.json().get('devices', [{}])[0].get('name', 'Unknown')
            print(f"GPU Info: {gpu_info}")
        else:
            print("❌ V100 ComfyUI connection failed")
            return
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return
    
    # Generate ultra quality images
    results = generator.generate_ultra_quality_images()
    
    print(f"\n🏁 V100 Ultra Quality Generation完了: {datetime.now()}")

if __name__ == "__main__":
    main()