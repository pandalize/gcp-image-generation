#!/usr/bin/env python3
"""
V100 GPU 全身フォトリアリスティック人間生成 - 身体整合性評価
手指・解剖学的精度・姿勢の正確性を検証
"""

import requests
import json
import time
import os
from datetime import datetime

class V100FullBodyAnatomyTest:
    def __init__(self):
        self.server_ip = "localhost"
        self.port = 8188
        self.base_url = f"http://{self.server_ip}:{self.port}"
        
    def get_fullbody_anatomy_prompts(self):
        """身体整合性評価用全身プロンプト（3種類）"""
        return [
            {
                'name': 'FullBody_Hands_Focus_Test',
                'description': '手指の正確性重点テスト',
                'positive': 'RAW photo, full body shot, (highly detailed skin), (8k uhd:1.1), dslr, soft lighting, high quality, film grain, photorealistic, hyperrealistic, stunning beautiful woman, 25 years old, long wavy brown hair, hazel eyes, natural makeup, elegant full body pose, (perfect hands:1.3), (detailed fingers:1.3), (5 fingers each hand:1.4), (correct finger anatomy:1.3), hands visible, arms at sides, natural hand position, detailed fingernails, realistic hand proportions, professional full body photography, standing pose, white casual dress, clean studio background, natural lighting, depth of field, professional model photography, anatomically correct, perfect proportions, masterpiece, best quality',
                'negative': 'cropped, portrait only, close-up, anime, cartoon, graphic, text, painting, abstract, deformed hands, extra fingers, missing fingers, mutated hands, poorly drawn hands, malformed hands, 6 fingers, 4 fingers, extra thumbs, missing thumbs, twisted fingers, bent fingers unnaturally, floating hands, disconnected hands, hands behind back, hidden hands, blurry hands, low quality hands, distorted anatomy, bad anatomy, bad proportions, extra limbs, missing limbs, ugly, disfigured, mutation, amateur photography, cropped body parts, head only, torso only',
                'cfg': 10.0,
                'steps': 120,
                'width': 768,
                'height': 1152,
                'sampler': 'dpmpp_2m',
                'scheduler': 'karras'
            },
            {
                'name': 'FullBody_Anatomy_Precision_Test',
                'description': '全身解剖学的精度テスト',
                'positive': 'RAW photo, professional full body photography, (highly detailed skin), (8k uhd:1.1), dslr, soft lighting, high quality, film grain, photorealistic, hyperrealistic, gorgeous woman, 28 years old, shoulder-length blonde hair, blue eyes, natural beauty, (perfect anatomy:1.4), (correct proportions:1.3), (realistic body proportions:1.3), full body visible, head to toe, standing confidently, arms naturally positioned, (detailed hands:1.2), (perfect feet:1.2), (5 toes each foot:1.2), elegant posture, slim athletic build, wearing fitted blue jeans and white t-shirt, natural pose, studio lighting, clean background, depth of field, professional photography, anatomically accurate, realistic muscle definition, natural body language, award winning photography, masterpiece, ultra detailed',
                'negative': 'cropped image, partial body, portrait mode, close-up, anime, cartoon, painting, abstract, bad anatomy, wrong anatomy, extra limbs, missing limbs, extra arms, missing arms, extra legs, missing legs, deformed body, distorted proportions, unrealistic proportions, giant head, tiny head, long neck, short neck, extra fingers, missing fingers, deformed hands, malformed feet, extra toes, missing toes, floating limbs, disconnected body parts, unnatural pose, twisted body, contorted pose, amateur photography, low quality, blurry, pixelated',
                'cfg': 9.0,
                'steps': 100,
                'width': 768,
                'height': 1152,
                'sampler': 'dpmpp_2m',
                'scheduler': 'karras'
            },
            {
                'name': 'FullBody_Pose_Integrity_Test',
                'description': '姿勢・身体一体性テスト',
                'positive': 'RAW photo, professional full body portrait, (highly detailed skin), (8k uhd:1.1), dslr, natural lighting, high quality, film grain, photorealistic, hyperrealistic, beautiful woman, 26 years old, curly red hair, green eyes, freckles, natural smile, (full body composition:1.4), (complete figure:1.3), standing in natural relaxed pose, (both hands clearly visible:1.3), (both feet visible:1.2), arms hanging naturally, weight evenly distributed, confident posture, wearing casual summer dress, sandals, outdoor natural lighting, garden background with soft bokeh, professional fashion photography, perfect body language, natural expression, anatomically perfect, realistic proportions, magazine quality, masterpiece photography',
                'negative': 'cropped, partial figure, portrait only, headshot, torso only, anime, cartoon, illustration, painting, abstract, bad anatomy, incorrect anatomy, missing body parts, extra body parts, deformed limbs, twisted limbs, unnatural pose, stiff pose, robotic pose, awkward positioning, hands behind back, hidden hands, obscured feet, floating limbs, disconnected anatomy, poor proportions, distorted body, amateur photography, low quality, blurry, overexposed, underexposed, harsh shadows, flat lighting',
                'cfg': 8.5,
                'steps': 90,
                'width': 768,
                'height': 1152,
                'sampler': 'euler_ancestral',
                'scheduler': 'karras'
            }
        ]

    def create_fullbody_workflow(self, config):
        """全身生成ワークフロー作成"""
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
                    "filename_prefix": f"V100_FULLBODY_{config['name']}",
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
        print(f"🎨 Generating full body anatomy test: {name}...")
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

    def generate_fullbody_anatomy_tests(self):
        """全身身体整合性テスト実行"""
        configs = self.get_fullbody_anatomy_prompts()
        
        print(f"🚀 V100 Full Body Anatomy Test 開始 ({datetime.now()})")
        print(f"Model: Juggernaut XL v10")
        print(f"GPU: Tesla V100-SXM2-16GB")
        print(f"Resolution: 768x1152 (Portrait Full Body)")
        print(f"Tests: {len(configs)} anatomy evaluation tests")
        print("=" * 80)
        
        total_start = time.time()
        successful_generations = 0
        results = []
        
        for i, config in enumerate(configs, 1):
            print(f"\n{'='*60}")
            print(f"🧍 Anatomy Test {i}/{len(configs)}: {config['name']}")
            print(f"📝 Focus: {config['description']}")
            print(f"⚙️  Settings: {config['steps']} steps, CFG {config['cfg']}")
            print(f"📐 Resolution: {config['width']}x{config['height']}")
            print(f"{'='*60}")
            
            workflow = self.create_fullbody_workflow(config)
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
        print("🏁 V100 Full Body Anatomy Tests Complete!")
        print(f"{'='*60}")
        print(f"✅ Successful generations: {successful_generations}/{len(configs)}")
        print(f"⏱️  Total time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
        if successful_generations > 0:
            print(f"📊 Average per image: {total_time/successful_generations:.1f} seconds")
        print(f"📁 Output directory: /home/fujinoyuki/ComfyUI/output/")
        print(f"🏷️  File prefix: V100_FULLBODY_*")
        print(f"⏰ Completed at: {datetime.now()}")
        
        print("\n🧍 Anatomy Test Results:")
        print("-" * 60)
        for result in results:
            status_icon = "✅" if result['status'] == 'success' else "❌"
            print(f"{status_icon} {result['name']}")
            print(f"   Focus: {result['description']}")
            print(f"   Settings: {result['steps']}steps, CFG{result['cfg']} - {result['status']}")
        
        print("\n🔍 Evaluation Points:")
        print("- ✋ Hand anatomy (5 fingers, natural positioning)")
        print("- 🦶 Foot anatomy (5 toes, realistic proportions)")  
        print("- 👤 Body proportions (head-to-body ratio)")
        print("- 🤸 Pose naturalness (weight distribution, balance)")
        print("- 🧬 Anatomical accuracy (limb connections, muscle definition)")
        
        return results

def main():
    print("V100 Full Body Anatomy Test - 身体整合性評価")
    
    generator = V100FullBodyAnatomyTest()
    
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
    
    # Generate full body anatomy tests
    results = generator.generate_fullbody_anatomy_tests()
    
    print(f"\n🏁 Full Body Anatomy Test完了: {datetime.now()}")
    print("🧍 Check generated images for anatomical accuracy evaluation!")

if __name__ == "__main__":
    main()