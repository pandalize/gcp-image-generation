#!/usr/bin/env python3
"""
V100 高品質チューニング実験スクリプト
CFG・Steps・Sampler・解像度の最適組み合わせを探求
"""

import requests
import json
import time
import os
import random
from datetime import datetime

class AdvancedQualityTuningExperiments:
    def __init__(self):
        self.server_ip = "localhost"
        self.port = 8188
        self.base_url = f"http://{self.server_ip}:{self.port}"
        
    def get_experimental_configurations(self):
        """実験的品質設定集"""
        return [
            {
                'name': 'Ultra_High_Steps_Experiment',
                'description': 'ウルトラ高ステップ数実験 (150-200 steps)',
                'cfg_range': (7.0, 9.0),
                'steps_range': (150, 200),
                'samplers': ['dpmpp_2m', 'euler_ancestral'],
                'resolutions': [(1024, 1024), (896, 1152), (768, 1344)]
            },
            {
                'name': 'Extreme_CFG_Experiment', 
                'description': '極限CFG実験 (12.0-15.0)',
                'cfg_range': (12.0, 15.0),
                'steps_range': (80, 120),
                'samplers': ['dpmpp_2m', 'dpmpp_sde'],
                'resolutions': [(1024, 1024), (832, 1216)]
            },
            {
                'name': 'Low_CFG_High_Steps',
                'description': '低CFG・高Steps組み合わせ',
                'cfg_range': (3.0, 5.0),
                'steps_range': (120, 180),
                'samplers': ['euler', 'dpmpp_2m'],
                'resolutions': [(1024, 1024), (1152, 896)]
            },
            {
                'name': 'Sampler_Comparison_Test',
                'description': 'サンプラー詳細比較テスト',
                'cfg_range': (7.5, 8.5),
                'steps_range': (90, 110),
                'samplers': ['dpmpp_2m', 'dpmpp_sde', 'euler', 'euler_ancestral', 'heun', 'dpm_2', 'lms'],
                'resolutions': [(1024, 1024)]
            },
            {
                'name': 'High_Resolution_Test',
                'description': '高解像度品質テスト',
                'cfg_range': (7.0, 9.0),
                'steps_range': (100, 140),
                'samplers': ['dpmpp_2m', 'euler_ancestral'],
                'resolutions': [(1280, 1280), (1024, 1536), (768, 1536), (1536, 1024)]
            },
            {
                'name': 'Balanced_Optimal_Test',
                'description': 'バランス最適化テスト',
                'cfg_range': (7.5, 9.5),
                'steps_range': (80, 120),
                'samplers': ['dpmpp_2m', 'euler_ancestral'],
                'resolutions': [(1024, 1024), (896, 1152), (1152, 896)]
            }
        ]
    
    def get_premium_prompts(self):
        """プレミアム品質プロンプト集"""
        return [
            {
                'style': 'Cinematic_Portrait_Master',
                'positive': 'cinematic portrait masterpiece, award winning photography, professional lighting, film grain, depth of field, bokeh, dramatic composition, magazine cover quality, ultra detailed skin, perfect face, symmetrical features, natural beauty, elegant pose, sophisticated styling, premium production value, masterpiece photography, 8K ultra sharp, photorealistic, hyperrealistic',
                'negative': 'low quality, amateur, poor lighting, distorted, deformed, bad anatomy, extra limbs, blurry, pixelated, oversaturated, cartoon, anime, painting, sketch'
            },
            {
                'style': 'Fashion_Editorial_Excellence',
                'positive': 'high fashion editorial photography, luxury brand campaign, professional model, flawless makeup, designer fashion, studio lighting perfection, commercial photography, Vogue style, sophisticated elegance, premium quality, award winning fashion photography, ultra detailed, perfect proportions, natural pose, editorial excellence, masterpiece',
                'negative': 'amateur fashion, cheap clothing, poor styling, bad makeup, unprofessional, low fashion, casual wear, distorted proportions, bad pose'
            },
            {
                'style': 'Artistic_Portrait_Vision', 
                'positive': 'artistic portrait photography, creative vision, innovative composition, fine art photography, gallery worthy, museum quality, artistic lighting, creative shadows, artistic excellence, contemporary art, portrait artistry, professional fine art, creative masterpiece, artistic innovation, award winning art photography',
                'negative': 'commercial, generic, ordinary, predictable, boring composition, amateur art, poor creativity, unimaginative, cliche'
            },
            {
                'style': 'Technical_Perfection_Test',
                'positive': 'technical photography perfection, perfect exposure, flawless focus, optimal depth of field, precise lighting, color accuracy, contrast perfection, sharpness excellence, technical mastery, professional grade, broadcast quality, print ready, technical excellence, pixel perfect, ultra sharp detail',
                'negative': 'poor exposure, soft focus, bad lighting, color cast, poor contrast, technical flaws, compression artifacts, noise, blur, distortion'
            }
        ]
    
    def get_subject_variations_premium(self):
        """プレミアム被写体バリエーション"""
        return [
            "stunning supermodel, 25 years old, perfect facial features, natural platinum blonde hair, piercing blue eyes, flawless skin",
            "elegant fashion model, 27 years old, sophisticated brunette, warm brown eyes, natural makeup, graceful expression",
            "beautiful portrait subject, 26 years old, lustrous black hair, captivating dark eyes, subtle makeup, confident gaze",
            "professional model, 24 years old, wavy auburn hair, emerald green eyes, natural beauty, serene expression",
            "gorgeous woman, 28 years old, sleek dark hair, hazel eyes, minimal makeup, elegant poise",
            "striking model, 25 years old, honey blonde hair, amber eyes, professional makeup, intense gaze"
        ]
    
    def create_experimental_workflow(self, experiment_config, prompt_config, subject):
        """実験的ワークフロー作成"""
        # ランダムパラメータ選択
        cfg = round(random.uniform(experiment_config['cfg_range'][0], experiment_config['cfg_range'][1]), 1)
        steps = random.randint(experiment_config['steps_range'][0], experiment_config['steps_range'][1])
        sampler = random.choice(experiment_config['samplers'])
        width, height = random.choice(experiment_config['resolutions'])
        
        # プロンプト構築
        positive_parts = [
            "RAW photo, (highly detailed skin:1.2), (8k uhd:1.1), dslr, professional photography, masterpiece, best quality",
            prompt_config['positive'],
            subject,
            "perfect lighting, ultra sharp, photorealistic, hyperrealistic, award winning photography"
        ]
        
        negative_parts = [
            "worst quality, low quality, normal quality, lowres, blurry, pixelated, jpeg artifacts, grainy, noise",
            prompt_config['negative'],
            "child, loli, young, old, amateur, unprofessional, bad quality"
        ]
        
        positive_prompt = ", ".join(positive_parts)
        negative_prompt = ", ".join(negative_parts)
        
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
                    "text": positive_prompt,
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "3": {
                "inputs": {
                    "text": negative_prompt,
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
                    "filename_prefix": f"EXPERIMENT_{experiment_config['name']}_{prompt_config['style']}",
                    "images": ["6", 0]
                },
                "class_type": "SaveImage"
            }
        }
        
        return workflow, {
            'experiment': experiment_config['name'],
            'style': prompt_config['style'],
            'steps': steps,
            'cfg': cfg,
            'sampler': sampler,
            'resolution': f"{width}x{height}"
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

    def get_queue_info(self):
        """キュー情報取得"""
        try:
            response = requests.get(f"{self.base_url}/queue", timeout=10)
            return response.json()
        except Exception as e:
            print(f"Error getting queue info: {e}")
            return None

    def run_quality_tuning_experiments(self, target_images=50):
        """品質チューニング実験実行"""
        experiments = self.get_experimental_configurations()
        prompts = self.get_premium_prompts()
        subjects = self.get_subject_variations_premium()
        
        print(f"🧪 V100 Advanced Quality Tuning Experiments")
        print(f"🎯 Target: {target_images} experimental images")
        print(f"⚙️  Experiments: {len(experiments)} configurations")
        print(f"🎨 Prompts: {len(prompts)} premium styles")
        print(f"👥 Subjects: {len(subjects)} variations")
        print("=" * 80)
        
        generated_count = 0
        experiment_stats = {exp['name']: 0 for exp in experiments}
        
        while generated_count < target_images:
            # ランダム組み合わせ選択
            experiment = random.choice(experiments)
            prompt = random.choice(prompts)
            subject = random.choice(subjects)
            
            try:
                workflow, params = self.create_experimental_workflow(experiment, prompt, subject)
                result = self.queue_prompt(workflow)
                
                if result and 'prompt_id' in result:
                    prompt_id = result['prompt_id']
                    
                    print(f"\n🧪 Experiment {generated_count + 1}/{target_images}")
                    print(f"📊 Config: {params['experiment']}")
                    print(f"🎨 Style: {params['style']}")
                    print(f"⚙️  Settings: {params['steps']}steps, CFG{params['cfg']}, {params['sampler']}")
                    print(f"📐 Resolution: {params['resolution']}")
                    print(f"🆔 Queue ID: {prompt_id}")
                    
                    generated_count += 1
                    experiment_stats[experiment['name']] += 1
                    
                    # 進捗報告
                    if generated_count % 10 == 0:
                        progress = (generated_count / target_images) * 100
                        print(f"\n📊 Progress: {generated_count}/{target_images} ({progress:.1f}%)")
                        print("🧪 Experiment Statistics:")
                        for exp_name, count in experiment_stats.items():
                            if count > 0:
                                print(f"   {exp_name}: {count} images")
                    
                    # キュー制御
                    while True:
                        queue_info = self.get_queue_info()
                        if queue_info:
                            running = len(queue_info.get('queue_running', []))
                            pending = len(queue_info.get('queue_pending', []))
                            if running + pending < 3:  # キューに余裕がある
                                break
                        print("⏳ Queue management, waiting...")
                        time.sleep(20)
                
                else:
                    print(f"❌ Failed to queue experiment")
                    time.sleep(5)
                
            except Exception as e:
                print(f"❌ Error during experiment: {e}")
                time.sleep(10)
        
        # 最終レポート
        print(f"\n{'='*80}")
        print("🧪 V100 Advanced Quality Tuning Experiments Complete!")
        print(f"{'='*80}")
        print(f"📊 Total Experiments: {generated_count}")
        
        print(f"\n🧪 Final Experiment Statistics:")
        for exp_name, count in sorted(experiment_stats.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                percentage = (count / generated_count) * 100
                print(f"   {exp_name}: {count} images ({percentage:.1f}%)")
        
        return generated_count

def main():
    print("V100 Advanced Quality Tuning Experiments")
    
    experiments = AdvancedQualityTuningExperiments()
    
    # ComfyUI接続確認
    try:
        response = requests.get(f"{experiments.base_url}/system_stats", timeout=10)
        if response.status_code == 200:
            print("✅ V100 ComfyUI connection successful")
        else:
            print("❌ V100 ComfyUI connection failed")
            return
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return
    
    # 実験実行
    total_generated = experiments.run_quality_tuning_experiments(50)
    
    print(f"\n🎉 Experiments completed! Generated {total_generated} experimental images")
    print(f"📁 Check /home/fujinoyuki/ComfyUI/output/ for EXPERIMENT_* files")

if __name__ == "__main__":
    main()