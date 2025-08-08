#!/usr/bin/env python3
"""
インターナショナル・サディスティック美女生成スクリプト
日本人要素を除いた世界的美女版
"""

import requests
import json
import time
import random

class InternationalSadisticBeautyGenerator:
    def __init__(self):
        self.server_ip = "localhost"
        self.port = 8188
        self.base_url = f"http://{self.server_ip}:{self.port}"
        
    def get_sadistic_beauty_prompts(self):
        """インターナショナル・サディスティック美女用プロンプト3種"""
        
        base_positive = """RAW photo, (photorealistic:1.4), (hyperrealistic:1.3), professional portrait photography,
(full body shot:1.3), dramatic portrait, dark aesthetic photography,
(extremely beautiful woman:1.4), (stunning gorgeous face:1.3), {age} years old, {ethnicity},
(perfect flawless skin:1.3), (radiant glowing skin:1.2), {skin_tone} skin tone,
{expression_description}, {eyes_description}, captivating intense gaze,
{hair_description}, sleek hair styling, professional hair work,
(perfect facial features:1.3), (beautiful face:1.4), sharp facial features,
(sadistic beauty:1.2), {personality_traits}, confident dominant presence,
{beauty_type}, (model quality:1.2), high fashion aesthetic,

{pose_description}, {body_language},
wearing {outfit}, {styling_details}, {accessories},
{location_setting}, {atmosphere},

shot on Canon EOS R5, 85mm f/1.2L lens, shallow depth of field,
{lighting_setup}, dramatic lighting, cinematic lighting,
moody atmosphere, dark aesthetic, high contrast lighting,
professional color grading, film noir influence,

(8K UHD:1.2), ultra high resolution, professional retouching,
high fashion photography quality, editorial excellence,
Helmut Newton inspired aesthetic, dark fashion photography,

award-winning portrait photography, artistic excellence,
masterpiece, best quality, ultra-detailed, sharp focus on subject,
dramatic bokeh background, professional post-processing,
(perfect hands:1.2), (perfect body proportions:1.2), striking composition"""

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
unflattering angle, unflattering lighting, cute, innocent, sweet, cheerful"""

        variations = [
            {
                'name': 'Nordic_Ice_Queen',
                'age': '27',
                'ethnicity': 'Scandinavian Nordic features',
                'skin_tone': 'alabaster',
                'beauty_type': 'Nordic ice queen beauty, Scandinavian elegance',
                'expression_description': 'cold calculating expression, icy cruel smile, superior Nordic gaze',
                'eyes_description': 'piercing ice-blue eyes, cold calculating stare, dramatic Nordic makeup',
                'hair_description': 'platinum blonde hair, sleek straight styling, Nordic goddess appearance',
                'personality_traits': 'ice queen dominance, Nordic superiority, cold calculating nature',
                'pose_description': 'regal dominant pose, queenly authority, Nordic royal stance',
                'body_language': 'intimidating Nordic presence, ice queen posture, royal dominance',
                'outfit': 'elegant black power dress, sophisticated Nordic fashion',
                'styling_details': 'minimalist Nordic styling, Scandinavian elegance, cold beauty',
                'accessories': 'silver jewelry, Nordic design elements, royal accessories',
                'location_setting': 'minimalist Nordic interior, glass and steel environment, cold modern setting',
                'atmosphere': 'cold Nordic atmosphere, ice queen domain, intimidating elegance',
                'lighting_setup': 'cold Nordic lighting, icy ambiance, harsh beautiful lighting'
            },
            {
                'name': 'Latin_Fire_Goddess',
                'age': '26',
                'ethnicity': 'Latin American features, Mediterranean beauty',
                'skin_tone': 'golden olive',
                'beauty_type': 'Latin fire goddess, Mediterranean passion',
                'expression_description': 'fiery passionate expression, dangerous sultry smile, burning intensity',
                'eyes_description': 'dark smoldering eyes, passionate fire, intense Latin gaze',
                'hair_description': 'long wavy dark hair, wild passionate styling, goddess-like flow',
                'personality_traits': 'fiery dominance, passionate control, Latin fire spirit',
                'pose_description': 'passionate dominant pose, Latin fire stance, goddess positioning',
                'body_language': 'fiery passionate presence, dangerous allure, Latin goddess grace',
                'outfit': 'form-fitting red dress, Latin passion fashion, fire goddess style',
                'styling_details': 'passionate Latin styling, fire goddess elements, sultry fashion',
                'accessories': 'gold jewelry, Latin design, passionate accessories',
                'location_setting': 'warm Latin atmosphere, passionate environment, fire goddess domain',
                'atmosphere': 'passionate fire atmosphere, Latin intensity, dangerous beauty',
                'lighting_setup': 'warm passionate lighting, fire goddess illumination, golden hour passion'
            },
            {
                'name': 'Slavic_Dark_Empress',
                'age': '28',
                'ethnicity': 'Eastern European Slavic features',
                'skin_tone': 'porcelain',
                'beauty_type': 'Slavic dark empress, Eastern European mystique',
                'expression_description': 'mysterious dark expression, enigmatic cruel smile, Slavic intensity',
                'eyes_description': 'deep mysterious eyes, Slavic soul, penetrating dark gaze',
                'hair_description': 'long straight dark hair, dramatic Slavic styling, empress elegance',
                'personality_traits': 'dark empress dominance, Slavic mystique, mysterious power',
                'pose_description': 'imperial dominant pose, empress authority, Slavic royal stance',
                'body_language': 'mysterious empress presence, dark royal posture, Slavic dominance',
                'outfit': 'dark royal outfit, empress fashion, Slavic elegance',
                'styling_details': 'dark imperial styling, empress elements, mysterious fashion',
                'accessories': 'dark precious jewelry, imperial accessories, Slavic design',
                'location_setting': 'dark palace interior, imperial setting, mysterious Slavic environment',
                'atmosphere': 'dark imperial atmosphere, mysterious empress domain, Slavic mystique',
                'lighting_setup': 'dramatic imperial lighting, dark empress illumination, mysterious shadows'
            }
        ]
        
        prompts = []
        for var in variations:
            positive = base_positive.format(
                age=var['age'],
                ethnicity=var['ethnicity'],
                skin_tone=var['skin_tone'],
                beauty_type=var['beauty_type'],
                expression_description=var['expression_description'],
                eyes_description=var['eyes_description'],
                hair_description=var['hair_description'],
                personality_traits=var['personality_traits'],
                pose_description=var['pose_description'],
                body_language=var['body_language'],
                outfit=var['outfit'],
                styling_details=var['styling_details'],
                accessories=var['accessories'],
                location_setting=var['location_setting'],
                atmosphere=var['atmosphere'],
                lighting_setup=var['lighting_setup']
            )
            prompts.append({
                'name': var['name'],
                'positive': positive,
                'negative': base_negative
            })
        
        return prompts
    
    def create_workflow(self, prompt_data, seed_offset=0):
        """ワークフロー作成"""
        # ドラマティックポートレート用解像度
        width = 896
        height = 1152
        
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
                    "steps": 120,
                    "cfg": 9.5,
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
                    "filename_prefix": f"INTERNATIONAL_SADISTIC_{prompt_data['name']}",
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
    
    def generate_international_sadistic_beauties(self):
        """インターナショナル・サディスティック美女3枚生成"""
        print("🌍 International Sadistic Beauty Generation")
        print("=" * 80)
        print("🌟 Generating 3 international dark goddess portraits")
        print("🎭 Nordic, Latin, and Slavic beauty types")
        print("📐 Resolution: 896x1152 (Portrait)")
        print("⚙️  Settings: 120 steps, CFG 9.5")
        print("=" * 80)
        
        prompts = self.get_sadistic_beauty_prompts()
        generated_ids = []
        
        for i, prompt_data in enumerate(prompts):
            print(f"\n🖤 Generating International Beauty {i+1}/3: {prompt_data['name']}")
            print("-" * 40)
            
            workflow, seed = self.create_workflow(prompt_data, seed_offset=i*1000)
            
            result = self.queue_prompt(workflow)
            
            if result and 'prompt_id' in result:
                prompt_id = result['prompt_id']
                generated_ids.append(prompt_id)
                print(f"📋 Queue ID: {prompt_id}")
                print(f"🌱 Seed: {seed}")
                print(f"👑 Style: {prompt_data['name']}")
                
                # 完了待機
                if self.wait_for_completion(prompt_id):
                    print(f"✨ Successfully generated stunning {prompt_data['name']}!")
                else:
                    print(f"⚠️  Timeout for {prompt_data['name']}")
            else:
                print(f"❌ Failed to queue {prompt_data['name']}")
            
            # 次の生成まで少し待機
            if i < len(prompts) - 1:
                print(f"⏳ Preparing next international goddess...")
                time.sleep(10)
        
        print(f"\n{'='*80}")
        print("🏆 International Sadistic Beauty Generation Complete!")
        print(f"{'='*80}")
        print(f"✅ Generated 3 international goddess portraits")
        print("📁 Files saved as: INTERNATIONAL_SADISTIC_*.png")
        print("🌍 World-class dark beauties ready!")
        
        return generated_ids

def main():
    generator = InternationalSadisticBeautyGenerator()
    
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
    
    # 3枚のインターナショナル・サディスティック美女を生成
    generated_ids = generator.generate_international_sadistic_beauties()
    
    print(f"\n🎉 Mission complete! Generated {len(generated_ids)} international dark goddesses")
    print("\n📥 To download, run:")
    print('gcloud compute scp "v100-i2:~/ComfyUI/output/INTERNATIONAL_SADISTIC_*.png" . --zone=asia-east1-c')

if __name__ == "__main__":
    main()