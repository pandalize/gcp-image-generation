#!/usr/bin/env python3
"""
インターナショナル・ダークスタイル美女生成スクリプト
Dark_Elegance, Corporate_Dominance, Artistic_Darkness
"""

import requests
import json
import time
import random

class InternationalDarkStylesGenerator:
    def __init__(self):
        self.server_ip = "localhost"
        self.port = 8188
        self.base_url = f"http://{self.server_ip}:{self.port}"
        
    def get_dark_style_prompts(self):
        """インターナショナル・ダークスタイル美女用プロンプト3種"""
        
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
                'name': 'Dark_Elegance',
                'age': '26',
                'ethnicity': 'European mixed features, international beauty',
                'skin_tone': 'porcelain',
                'beauty_type': 'gothic elegance, dark sophistication',
                'expression_description': 'mysterious sultry expression, slight sadistic smile, knowing look',
                'eyes_description': 'piercing dark eyes, intense calculating gaze, smoky eye makeup',
                'hair_description': 'long straight black hair, dramatic styling, glossy finish',
                'personality_traits': 'commanding presence, mysterious allure, sophisticated dominance',
                'pose_description': 'confident dominant pose, hands on hips, authoritative stance',
                'body_language': 'powerful body language, intimidating elegance, controlled grace',
                'outfit': 'black leather outfit, form-fitting design, edgy fashion',
                'styling_details': 'dark gothic styling, punk rock elements, rebellious fashion',
                'accessories': 'statement choker, dark jewelry, punk accessories',
                'location_setting': 'dark urban setting, industrial background, moody environment',
                'atmosphere': 'dramatic atmosphere, dark and mysterious mood, gothic aesthetic',
                'lighting_setup': 'dramatic side lighting, strong shadows, noir lighting'
            },
            {
                'name': 'Corporate_Dominance',
                'age': '28',
                'ethnicity': 'Scandinavian Nordic features, professional elegance',
                'skin_tone': 'alabaster',
                'beauty_type': 'corporate power beauty, executive elegance',
                'expression_description': 'cold calculating expression, subtle cruel smile, superior look',
                'eyes_description': 'sharp intelligent eyes, cold stare, professional makeup',
                'hair_description': 'sleek pulled-back hair, severe styling, business-like appearance',
                'personality_traits': 'corporate dominance, intellectual superiority, ruthless elegance',
                'pose_description': 'authoritative business pose, crossed arms, power stance',
                'body_language': 'intimidating corporate presence, controlling posture, executive confidence',
                'outfit': 'sharp business suit, tailored perfection, power dressing',
                'styling_details': 'professional power styling, executive fashion, authoritative look',
                'accessories': 'expensive watch, designer glasses, executive accessories',
                'location_setting': 'modern office setting, glass and steel environment, corporate backdrop',
                'atmosphere': 'cold professional atmosphere, corporate power dynamic, intimidating environment',
                'lighting_setup': 'harsh office lighting, fluorescent ambiance, cold lighting'
            },
            {
                'name': 'Artistic_Darkness',
                'age': '25',
                'ethnicity': 'Mediterranean mixed features, artistic beauty',
                'skin_tone': 'olive',
                'beauty_type': 'avant-garde artistic beauty, creative elegance',
                'expression_description': 'enigmatic artistic expression, mysterious smile, creative intensity',
                'eyes_description': 'deep artistic eyes, creative fire, dramatic makeup',
                'hair_description': 'artistic avant-garde hair, creative styling, unconventional beauty',
                'personality_traits': 'artistic dominance, creative control, avant-garde spirit',
                'pose_description': 'artistic dramatic pose, creative positioning, avant-garde stance',
                'body_language': 'artistic expression, creative dominance, unconventional grace',
                'outfit': 'avant-garde fashion, artistic clothing, creative design',
                'styling_details': 'artistic styling, creative fashion, unconventional beauty',
                'accessories': 'artistic jewelry, creative accessories, avant-garde elements',
                'location_setting': 'art gallery setting, creative space, artistic environment',
                'atmosphere': 'creative atmosphere, artistic mood, avant-garde aesthetic',
                'lighting_setup': 'artistic lighting, creative shadows, gallery lighting'
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
                    "filename_prefix": f"DARK_STYLES_{prompt_data['name']}",
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
    
    def generate_dark_style_beauties(self):
        """ダークスタイル美女3枚生成"""
        print("🖤 International Dark Styles Beauty Generation")
        print("=" * 80)
        print("🌟 Generating 3 dark aesthetic style portraits")
        print("🎭 Gothic, Corporate, and Artistic styles")
        print("📐 Resolution: 896x1152 (Portrait)")
        print("⚙️  Settings: 120 steps, CFG 9.5")
        print("=" * 80)
        
        prompts = self.get_dark_style_prompts()
        generated_ids = []
        
        for i, prompt_data in enumerate(prompts):
            print(f"\n🖤 Generating Dark Style {i+1}/3: {prompt_data['name']}")
            print("-" * 40)
            
            workflow, seed = self.create_workflow(prompt_data, seed_offset=i*1000)
            
            result = self.queue_prompt(workflow)
            
            if result and 'prompt_id' in result:
                prompt_id = result['prompt_id']
                generated_ids.append(prompt_id)
                print(f"📋 Queue ID: {prompt_id}")
                print(f"🌱 Seed: {seed}")
                print(f"🎭 Style: {prompt_data['name']}")
                
                # 完了待機
                if self.wait_for_completion(prompt_id):
                    print(f"✨ Successfully generated stunning {prompt_data['name']}!")
                else:
                    print(f"⚠️  Timeout for {prompt_data['name']}")
            else:
                print(f"❌ Failed to queue {prompt_data['name']}")
            
            # 次の生成まで少し待機
            if i < len(prompts) - 1:
                print(f"⏳ Preparing next dark style...")
                time.sleep(10)
        
        print(f"\n{'='*80}")
        print("🏆 International Dark Styles Generation Complete!")
        print(f"{'='*80}")
        print(f"✅ Generated 3 dark style portraits")
        print("📁 Files saved as: DARK_STYLES_*.png")
        print("🖤 Dark aesthetic beauties ready!")
        
        return generated_ids

def main():
    generator = InternationalDarkStylesGenerator()
    
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
    
    # 3枚のダークスタイル美女を生成
    generated_ids = generator.generate_dark_style_beauties()
    
    print(f"\n🎉 Mission complete! Generated {len(generated_ids)} dark style beauties")
    print("\n📥 To download, run:")
    print('gcloud compute scp "v100-i2:~/ComfyUI/output/DARK_STYLES_*.png" . --zone=asia-east1-c')

if __name__ == "__main__":
    main()