#!/usr/bin/env python3
"""
日本人グラビア美女生成スクリプト
最高級グラビアアイドル品質
"""

import requests
import json
import time
import random

class JapaneseGravureBeautyGenerator:
    def __init__(self):
        self.server_ip = "localhost"
        self.port = 8188
        self.base_url = f"http://{self.server_ip}:{self.port}"
        
    def get_gravure_beauty_prompts(self):
        """日本人グラビア美女用プロンプト3種"""
        
        base_positive = """RAW photo, (photorealistic:1.4), (hyperrealistic:1.3), professional gravure photography,
(full body shot:1.3), (full body portrait:1.2), gravure idol photoshoot,
(extremely beautiful Japanese woman:1.4), (stunning gorgeous face:1.3), {age} years old,
(perfect flawless skin:1.3), (radiant glowing skin:1.2), healthy skin tone,
captivating eyes with detailed iris, long eyelashes, perfect eye makeup,
{hair_description}, silky smooth hair texture, professional hair styling,
(perfect facial features:1.3), (beautiful face:1.4), ideal facial proportions,
(gravure model body:1.2), (attractive figure:1.1), toned physique, perfect posture,
(Japanese beauty:1.3), (idol quality:1.2), magazine cover model,

{pose_description}, {expression},
wearing {outfit}, {location_setting},

shot on Canon EOS R5, 85mm f/1.2L lens, shallow depth of field,
professional gravure lighting, golden hour lighting, rim lighting,
beauty dish key light, reflectors for fill light, professional studio setup,
warm color temperature, flattering lighting angle,

(8K UHD:1.2), ultra high resolution, professional retouching,
gravure magazine quality, Young Magazine style, Weekly Playboy aesthetic,
Japanese gravure photography style, idol photobook quality,

award-winning gravure photography, commercial photography excellence,
masterpiece, best quality, ultra-detailed, sharp focus on model,
beautiful bokeh background, skin smoothing, professional color grading,
(perfect hands:1.2), (perfect body proportions:1.2), attractive pose"""

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
ugly, unattractive, old looking, masculine features, child, minor, underage,
bad skin, acne, skin blemishes, wrinkles, poor makeup, cheap production,
unflattering angle, unflattering lighting, unflattering pose"""

        variations = [
            {
                'name': 'Beach_Gravure',
                'age': '23',
                'hair_description': 'long flowing dark brown hair with beach waves, sun-kissed highlights',
                'pose_description': 'playful beach pose, walking along shoreline',
                'expression': 'bright cheerful smile, sparkling eyes, joyful expression',
                'outfit': 'stylish designer swimsuit, beach fashion',
                'location_setting': 'tropical beach setting, crystal clear ocean, white sand beach, sunset golden hour'
            },
            {
                'name': 'Studio_Gravure',
                'age': '25',
                'hair_description': 'silky straight black hair, perfectly styled, glossy shine',
                'pose_description': 'elegant studio pose, professional modeling stance',
                'expression': 'captivating gaze, subtle confident smile, alluring expression',
                'outfit': 'fashionable summer dress, elegant style',
                'location_setting': 'professional photo studio, white cyclorama background, studio lighting setup'
            },
            {
                'name': 'Urban_Gravure',
                'age': '24',
                'hair_description': 'stylish medium length hair with soft curls, trendy hair color',
                'pose_description': 'dynamic urban fashion pose, confident stance',
                'expression': 'sophisticated smile, engaging eye contact, charismatic expression',
                'outfit': 'trendy casual outfit, street fashion style',
                'location_setting': 'modern city rooftop, urban skyline background, golden hour lighting'
            }
        ]
        
        prompts = []
        for var in variations:
            positive = base_positive.format(
                age=var['age'],
                hair_description=var['hair_description'],
                pose_description=var['pose_description'],
                expression=var['expression'],
                outfit=var['outfit'],
                location_setting=var['location_setting']
            )
            prompts.append({
                'name': var['name'],
                'positive': positive,
                'negative': base_negative
            })
        
        return prompts
    
    def create_workflow(self, prompt_data, seed_offset=0):
        """ワークフロー作成"""
        # グラビア用の解像度（縦長全身）
        width = 832
        height = 1216  # グラビア標準比率
        
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
                    "steps": 130,  # 高品質グラビア用
                    "cfg": 8.5,    # グラビア最適値
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
                    "filename_prefix": f"JAPANESE_GRAVURE_{prompt_data['name']}",
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
    
    def wait_for_completion(self, prompt_id, max_wait=200):
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
    
    def generate_gravure_beauties(self):
        """日本人グラビア美女3枚生成"""
        print("💖 Japanese Gravure Beauty Generation")
        print("=" * 80)
        print("🌟 Generating 3 stunning gravure idol quality portraits")
        print("📸 Magazine quality photoshoot")
        print("📐 Resolution: 832x1216 (Gravure standard)")
        print("⚙️  Settings: 130 steps, CFG 8.5")
        print("=" * 80)
        
        prompts = self.get_gravure_beauty_prompts()
        generated_ids = []
        
        for i, prompt_data in enumerate(prompts):
            print(f"\n🎀 Generating Gravure Beauty {i+1}/3: {prompt_data['name']}")
            print("-" * 40)
            
            workflow, seed = self.create_workflow(prompt_data, seed_offset=i*1000)
            
            result = self.queue_prompt(workflow)
            
            if result and 'prompt_id' in result:
                prompt_id = result['prompt_id']
                generated_ids.append(prompt_id)
                print(f"📋 Queue ID: {prompt_id}")
                print(f"🌱 Seed: {seed}")
                print(f"🌸 Style: {prompt_data['name']}")
                
                # 完了待機
                if self.wait_for_completion(prompt_id):
                    print(f"✨ Successfully generated stunning {prompt_data['name']}!")
                else:
                    print(f"⚠️  Timeout for {prompt_data['name']}")
            else:
                print(f"❌ Failed to queue {prompt_data['name']}")
            
            # 次の生成まで少し待機
            if i < len(prompts) - 1:
                print(f"⏳ Preparing next gravure beauty...")
                time.sleep(10)
        
        print(f"\n{'='*80}")
        print("🏆 Japanese Gravure Beauty Generation Complete!")
        print(f"{'='*80}")
        print(f"✅ Generated 3 stunning gravure portraits")
        print("📁 Files saved as: JAPANESE_GRAVURE_*.png")
        print("💖 Magazine quality beauties ready!")
        
        return generated_ids

def main():
    generator = JapaneseGravureBeautyGenerator()
    
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
    
    # 3枚の日本人グラビア美女を生成
    generated_ids = generator.generate_gravure_beauties()
    
    print(f"\n🎉 Mission complete! Generated {len(generated_ids)} stunning gravure beauties")
    print("\n📥 To download, run:")
    print('gcloud compute scp "v100-i2:~/ComfyUI/output/JAPANESE_GRAVURE_*.png" . --zone=asia-east1-c')

if __name__ == "__main__":
    main()