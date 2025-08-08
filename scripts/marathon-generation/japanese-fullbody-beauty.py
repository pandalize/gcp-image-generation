#!/usr/bin/env python3
"""
日本人美女・全身ポートレート生成スクリプト
究極プロンプトに日本人要素と全身構図を追加
"""

import requests
import json
import time
import random

class JapaneseFullBodyBeautyGenerator:
    def __init__(self):
        self.server_ip = "localhost"
        self.port = 8188
        self.base_url = f"http://{self.server_ip}:{self.port}"
        
    def get_japanese_fullbody_prompts(self):
        """日本人・全身ポートレート用プロンプト3種"""
        
        base_positive = """RAW photo, (photorealistic:1.4), (hyperrealistic:1.3), professional portrait photography,
(full body shot:1.3), (full body portrait:1.2), standing pose, head to toe visible, full length portrait,
stunning beautiful Japanese woman, {age} years old, {description},
flawless natural beauty, captivating eyes with detailed iris,
{hair_style}, perfect facial symmetry, natural skin texture with subtle imperfections,
(highly detailed skin:1.3), visible skin pores, subsurface scattering,
(Japanese beauty:1.2), Asian features, elegant Japanese aesthetic,

professional fashion model, {pose_style}, confident expression with subtle smile,
wearing {outfit}, sophisticated styling, {shoes},

shot on Hasselblad H6D-400c, 50mm lens, f/5.6 aperture, full body framing,
professional studio lighting setup, softbox key light, rim lighting for hair,
golden hour ambient lighting, Rembrandt lighting on face,
(studio backdrop:1.1), fashion photography studio setting,

(8K UHD:1.2), ultra high resolution, film grain, Kodak Portra 400 film emulation,
professional color grading, fashion editorial style, Vogue magazine aesthetic,
Annie Leibovitz inspired composition,

award-winning photography, museum-quality fine art portrait, commercial beauty campaign quality,
masterpiece, best quality, ultra-detailed, sharp focus throughout subject,
beautiful bokeh background, professional retouching, editorial excellence,
(perfect hands:1.2), (perfect feet:1.1), natural body proportions"""

        base_negative = """(worst quality:1.4), (low quality:1.4), (normal quality:1.3), lowres, bad anatomy, bad hands,
((monochrome)), ((grayscale)), collapsed eyeshadow, multiple eyebrows, (cropped), oversaturated,
extra limbs, missing limbs, deformed hands, long neck, long body, imperfect eyes,
cross-eyed, closed eyes, poorly drawn face, poorly drawn hands, poorly drawn eyes,
mutation, deformed iris, deformed pupils, deformed limbs, missing arms, missing legs,
extra arms, extra legs, mutated hands, fused fingers, too many fingers,
duplicate, morbid, mutilated, out of frame, body out of frame, blurry, bad art,
bad anatomy, 3d render, anime, cartoon, animated, illustration, painting, drawing,
sketch, artwork, graphic, digital art, cgi, rendered,
amateur photography, amateur, unprofessional, poor lighting, harsh shadows,
flat lighting, overexposed, underexposed, bad composition, instagram filter,
snapchat filter, plastic skin, airbrushed, overly smooth skin, wax figure,
fake, artificial, synthetic, mannequin, doll-like, unrealistic proportions,
distorted features, unnatural pose, stiff expression, dead eyes, vacant stare,
ugly, unattractive, repulsive, revolting, cheap production, low budget,
bad full body proportions, cut off body parts, partial body, torso only,
head only, upper body only, missing feet, cut off at knees"""

        variations = [
            {
                'name': 'Elegant_Kimono',
                'age': '25',
                'description': 'traditional Japanese beauty with modern elegance',
                'hair_style': 'long straight black hair with traditional Japanese styling',
                'pose_style': 'graceful standing pose with traditional Japanese posture',
                'outfit': 'elegant modern kimono with contemporary design, beautiful obi belt',
                'shoes': 'traditional Japanese geta sandals'
            },
            {
                'name': 'Modern_Fashion',
                'age': '27',
                'description': 'contemporary Japanese beauty with sophisticated style',
                'hair_style': 'sleek shoulder-length hair with subtle brown highlights',
                'pose_style': 'confident fashion model pose, weight shifted to one hip',
                'outfit': 'designer business suit, tailored blazer and pencil skirt',
                'shoes': 'elegant high heels'
            },
            {
                'name': 'Casual_Elegance',
                'age': '24',
                'description': 'natural Japanese beauty with relaxed sophistication',
                'hair_style': 'long wavy hair with natural movement',
                'pose_style': 'relaxed standing pose with natural body language',
                'outfit': 'elegant casual dress, flowing midi length',
                'shoes': 'stylish flat shoes'
            }
        ]
        
        prompts = []
        for var in variations:
            positive = base_positive.format(
                age=var['age'],
                description=var['description'],
                hair_style=var['hair_style'],
                pose_style=var['pose_style'],
                outfit=var['outfit'],
                shoes=var['shoes']
            )
            prompts.append({
                'name': var['name'],
                'positive': positive,
                'negative': base_negative
            })
        
        return prompts
    
    def create_workflow(self, prompt_data, seed_offset=0):
        """ワークフロー作成"""
        # 全身用の解像度（縦長）
        width = 768
        height = 1344  # 全身が収まる縦長比率
        
        seed = int(time.time() * 1000000 + seed_offset) % (2**32)
        
        workflow = {
            "1": {
                "inputs": {
                    "ckpt_name": "juggernaut_v10.safetensors"
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "2": {
                "inputs": {
                    "text": prompt_data['positive'],
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "3": {
                "inputs": {
                    "text": prompt_data['negative'],
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "4": {
                "inputs": {
                    "width": width,
                    "height": height,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "5": {
                "inputs": {
                    "seed": seed,
                    "steps": 120,  # 全身は高ステップ数で品質確保
                    "cfg": 9.0,
                    "sampler_name": "dpmpp_2m",
                    "scheduler": "karras",
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
                    "filename_prefix": f"JAPANESE_FULLBODY_{prompt_data['name']}",
                    "images": ["6", 0]
                },
                "class_type": "SaveImage"
            }
        }
        
        return workflow, seed
    
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
    
    def wait_for_completion(self, prompt_id, max_wait=180):
        """生成完了まで待機"""
        print(f"⏳ Waiting for {prompt_id}...")
        waited = 0
        
        while waited < max_wait:
            try:
                response = requests.get(f"{self.base_url}/queue", timeout=10)
                if response.status_code == 200:
                    queue_info = response.json()
                    running = queue_info.get('queue_running', [])
                    pending = queue_info.get('queue_pending', [])
                    
                    in_queue = False
                    for item in running + pending:
                        if len(item) > 1 and isinstance(item[1], dict):
                            if item[1].get('prompt_id') == prompt_id:
                                in_queue = True
                                break
                    
                    if not in_queue:
                        print(f"✅ Completed!")
                        return True
            except:
                pass
            
            time.sleep(5)
            waited += 5
            if waited % 30 == 0:
                print(f"   Still generating... ({waited}s)")
        
        return False
    
    def generate_japanese_fullbody_beauties(self):
        """日本人全身美女3枚生成"""
        print("🎌 Japanese Full Body Beauty Generation")
        print("=" * 80)
        print("🎯 Generating 3 full body portraits of Japanese beauties")
        print("📐 Resolution: 768x1344 (Full body aspect ratio)")
        print("⚙️  Settings: 120 steps, CFG 9.0")
        print("=" * 80)
        
        prompts = self.get_japanese_fullbody_prompts()
        generated_ids = []
        
        for i, prompt_data in enumerate(prompts):
            print(f"\n🎨 Generating Image {i+1}/3: {prompt_data['name']}")
            print("-" * 40)
            
            workflow, seed = self.create_workflow(prompt_data, seed_offset=i*1000)
            
            result = self.queue_prompt(workflow)
            
            if result and 'prompt_id' in result:
                prompt_id = result['prompt_id']
                generated_ids.append(prompt_id)
                print(f"📋 Queue ID: {prompt_id}")
                print(f"🌱 Seed: {seed}")
                print(f"👘 Style: {prompt_data['name']}")
                
                # 完了待機
                if self.wait_for_completion(prompt_id):
                    print(f"✨ Successfully generated {prompt_data['name']}!")
                else:
                    print(f"⚠️  Timeout for {prompt_data['name']}")
            else:
                print(f"❌ Failed to queue {prompt_data['name']}")
            
            # 次の生成まで少し待機
            if i < len(prompts) - 1:
                print(f"⏳ Preparing next generation...")
                time.sleep(10)
        
        print(f"\n{'='*80}")
        print("🏆 Japanese Full Body Generation Complete!")
        print(f"{'='*80}")
        print(f"✅ Generated 3 full body portraits")
        print("📁 Files saved as: JAPANESE_FULLBODY_*.png")
        
        return generated_ids

def main():
    generator = JapaneseFullBodyBeautyGenerator()
    
    # ComfyUI接続確認
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
    
    # 3枚の日本人全身美女を生成
    generated_ids = generator.generate_japanese_fullbody_beauties()
    
    print(f"\n🎉 Mission complete! Generated {len(generated_ids)} Japanese full body portraits")
    print("\n📥 To download, run:")
    print('gcloud compute scp "v100-i2:~/ComfyUI/output/JAPANESE_FULLBODY_*.png" . --zone=asia-east1-c')

if __name__ == "__main__":
    main()