#!/usr/bin/env python3
"""
究極フォトリアリスティック美女生成スクリプト
GitHub研究から学んだ全てのテクニックを統合
"""

import requests
import json
import time
import os
from datetime import datetime

class UltimatePhotorealisticBeautyGenerator:
    def __init__(self):
        self.server_ip = "localhost"
        self.port = 8188
        self.base_url = f"http://{self.server_ip}:{self.port}"
        
    def get_ultimate_prompt(self):
        """究極のフォトリアリスティック美女プロンプト"""
        positive = """RAW photo, (photorealistic:1.4), (hyperrealistic:1.3), professional portrait photography, 
stunning beautiful woman, 25 years old, flawless natural beauty, captivating eyes with detailed iris, 
long flowing hair with individual strands visible, perfect facial symmetry, natural skin texture with subtle imperfections, 
(highly detailed skin:1.3), visible skin pores, subsurface scattering, 

professional fashion model, elegant pose, confident expression with subtle smile, 
wearing elegant designer dress, sophisticated styling, 

shot on Hasselblad H6D-400c, 85mm lens, f/1.4 aperture, shallow depth of field, 
professional studio lighting setup, softbox key light, rim lighting for hair, 
golden hour ambient lighting, Rembrandt lighting on face, 

(8K UHD:1.2), ultra high resolution, film grain, Kodak Portra 400 film emulation, 
professional color grading, fashion editorial style, Vogue magazine aesthetic, 
Annie Leibovitz inspired composition, 

award-winning photography, museum-quality fine art portrait, commercial beauty campaign quality, 
masterpiece, best quality, ultra-detailed, sharp focus throughout subject, 
beautiful bokeh background, professional retouching, editorial excellence"""

        negative = """(worst quality:1.4), (low quality:1.4), (normal quality:1.3), lowres, bad anatomy, bad hands, 
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
ugly, unattractive, repulsive, revolting, cheap production, low budget"""
        
        return positive, negative
    
    def create_ultimate_workflow(self, seed_offset=0):
        """究極品質ワークフロー作成"""
        positive, negative = self.get_ultimate_prompt()
        
        # 最適設定
        steps = 120
        cfg = 9.5
        sampler = "dpmpp_2m"
        scheduler = "karras"
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
                    "text": positive,
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "3": {
                "inputs": {
                    "text": negative,
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
                    "steps": steps,
                    "cfg": cfg,
                    "sampler_name": sampler,
                    "scheduler": scheduler,
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
                    "filename_prefix": f"ULTIMATE_BEAUTY",
                    "images": ["6", 0]
                },
                "class_type": "SaveImage"
            }
        }
        
        return workflow, {
            'steps': steps,
            'cfg': cfg,
            'sampler': sampler,
            'resolution': f"{width}x{height}",
            'seed': seed
        }
    
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
        print(f"⏳ Waiting for completion of {prompt_id}...")
        waited = 0
        
        while waited < max_wait:
            try:
                response = requests.get(f"{self.base_url}/queue", timeout=10)
                if response.status_code == 200:
                    queue_info = response.json()
                    running = queue_info.get('queue_running', [])
                    pending = queue_info.get('queue_pending', [])
                    
                    # Check if prompt is still in queue
                    in_queue = False
                    for item in running + pending:
                        if len(item) > 1 and isinstance(item[1], dict):
                            if item[1].get('prompt_id') == prompt_id:
                                in_queue = True
                                break
                    
                    if not in_queue:
                        print(f"✅ Generation completed!")
                        return True
            except:
                pass
            
            time.sleep(5)
            waited += 5
            if waited % 30 == 0:
                print(f"   Still generating... ({waited}s elapsed)")
        
        return False
    
    def download_latest_image(self, image_number):
        """最新画像をダウンロード"""
        try:
            # V100から最新のULTIMATE_BEAUTY画像を取得
            local_dir = f"/Users/fujinoyuki/Desktop/gcp/outputs/ultimate_beauty_{datetime.now().strftime('%Y%m%d')}"
            os.makedirs(local_dir, exist_ok=True)
            
            cmd = f'gcloud compute scp "v100-i2:~/ComfyUI/output/ULTIMATE_BEAUTY_*.png" {local_dir}/ --zone=asia-east1-c'
            os.system(cmd)
            
            # ダウンロードした画像を確認
            import glob
            downloaded = glob.glob(f"{local_dir}/ULTIMATE_BEAUTY_*.png")
            if downloaded:
                latest = max(downloaded, key=os.path.getctime)
                size_mb = os.path.getsize(latest) / (1024*1024)
                print(f"📥 Downloaded: {os.path.basename(latest)} ({size_mb:.1f}MB)")
                return latest
        except Exception as e:
            print(f"Download error: {e}")
        return None
    
    def generate_ultimate_beauties(self, count=10):
        """究極美女を指定枚数生成"""
        print("🌟 Ultimate Photorealistic Beauty Generation")
        print("=" * 80)
        print(f"🎯 Target: {count} ultimate quality portraits")
        print(f"⚙️  Settings: 120 steps, CFG 9.5, 896x1152")
        print(f"📸 Style: Museum-quality fine art portrait")
        print("=" * 80)
        
        generated_files = []
        
        for i in range(count):
            print(f"\n🎨 Generating Image {i+1}/{count}")
            print("-" * 40)
            
            # ワークフロー作成
            workflow, params = self.create_ultimate_workflow(seed_offset=i*1000)
            
            # キューに追加
            result = self.queue_prompt(workflow)
            
            if result and 'prompt_id' in result:
                prompt_id = result['prompt_id']
                print(f"📋 Queue ID: {prompt_id}")
                print(f"🌱 Seed: {params['seed']}")
                
                # 完了待機
                if self.wait_for_completion(prompt_id):
                    # ダウンロード
                    time.sleep(3)  # ファイル保存待ち
                    downloaded = self.download_latest_image(i+1)
                    if downloaded:
                        generated_files.append(downloaded)
                        print(f"✨ Success! Total generated: {len(generated_files)}")
                else:
                    print(f"⚠️  Timeout waiting for generation")
            else:
                print(f"❌ Failed to queue prompt")
            
            # 次の生成まで少し待機
            if i < count - 1:
                print(f"⏳ Waiting before next generation...")
                time.sleep(10)
        
        # 最終レポート
        print(f"\n{'='*80}")
        print("🏆 Ultimate Beauty Generation Complete!")
        print(f"{'='*80}")
        print(f"✅ Successfully generated: {len(generated_files)} images")
        
        if generated_files:
            print("\n📁 Generated Files:")
            for f in generated_files:
                print(f"   - {os.path.basename(f)}")
            print(f"\n📂 All files saved to: {os.path.dirname(generated_files[0])}")
        
        return generated_files

def main():
    generator = UltimatePhotorealisticBeautyGenerator()
    
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
    
    # 10枚の究極美女を生成
    generated_files = generator.generate_ultimate_beauties(10)
    
    print(f"\n🎉 Mission accomplished! Generated {len(generated_files)} ultimate beauty portraits")

if __name__ == "__main__":
    main()