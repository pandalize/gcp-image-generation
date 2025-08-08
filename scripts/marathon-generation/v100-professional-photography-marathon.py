#!/usr/bin/env python3
"""
V100 GPU 10時間マラソン - プロフェッショナル写真品質大量生成
世界的写真家スタイル + 最高品質チューニング
"""

import requests
import json
import time
import os
import random
from datetime import datetime, timedelta

class V100ProfessionalPhotographyMarathon:
    def __init__(self):
        self.server_ip = "localhost"
        self.port = 8188
        self.base_url = f"http://{self.server_ip}:{self.port}"
        self.session_start = datetime.now()
        self.marathon_duration = 10 * 60 * 60  # 10時間
        self.target_images = 200  # 目標200枚
        
    def get_professional_photographer_styles(self):
        """世界的写真家スタイルプロンプト集"""
        return [
            {
                'style': 'Annie_Leibovitz_Conceptual',
                'description': 'アニー・リーボヴィッツ風コンセプチュアル肖像',
                'positive': 'professional portrait photography by Annie Leibovitz, conceptual portrait, dramatic staging, natural lighting with subtle key light, intimate celebrity portrait style, narrative elements, engaging dramatic composition, sophisticated lighting setup, editorial photography, Vogue magazine style, award winning portrait, masterpiece photography, ultra detailed, 8K quality',
                'negative': 'amateur photography, flat lighting, generic pose, no concept, boring composition',
                'cfg_range': (8.0, 10.0),
                'steps_range': (80, 120),
                'samplers': ['dpmpp_2m', 'euler_ancestral']
            },
            {
                'style': 'Peter_Lindbergh_Cinematic',
                'description': 'ピーター・リンドバーグ風シネマティック',
                'positive': 'black and white photography by Peter Lindbergh, cinematic composition, natural candid style, authentic beauty, raw unidealized portrait, fashion photography, supermodel portrait, cinematic lighting, dramatic shadows, film grain, professional b&w photography, Hasselblad camera, 85mm lens, high contrast, artistic portrait',
                'negative': 'color photography, over-polished, fake beauty, amateur lighting, digital artifacts',
                'cfg_range': (7.0, 9.0),
                'steps_range': (70, 100),
                'samplers': ['euler_ancestral', 'dpmpp_sde']
            },
            {
                'style': 'Mario_Testino_Glamour',
                'description': 'マリオ・テスティーノ風グラマー',
                'positive': 'glamorous portrait photography by Mario Testino, luxury fashion photography, sophisticated composition, warm natural lighting, vibrant colors, high fashion editorial, celebrity portrait, refined elegance, professional studio lighting, Vogue style, high-end fashion photography, perfect skin, flawless makeup, designer fashion, award winning photography',
                'negative': 'low fashion, amateur styling, poor lighting, cheap production, dull colors',
                'cfg_range': (8.5, 11.0),
                'steps_range': (90, 130),
                'samplers': ['dpmpp_2m', 'dpmpp_sde']
            },
            {
                'style': 'Richard_Avedon_Minimalist',
                'description': 'リチャード・アヴェドン風ミニマル',
                'positive': 'portrait photography by Richard Avedon, minimalist white background, dramatic lighting, intense expression, fashion photography, high contrast, professional studio portrait, medium format camera, 150mm lens, clean composition, editorial photography, timeless portrait, black and white or color, artistic excellence',
                'negative': 'cluttered background, poor contrast, amateur lighting, busy composition',
                'cfg_range': (7.5, 9.5),
                'steps_range': (75, 110),
                'samplers': ['euler', 'dpmpp_2m']
            },
            {
                'style': 'Helmut_Newton_Fashion',
                'description': 'ヘルムート・ニュートン風ファッション',
                'positive': 'fashion photography by Helmut Newton, sophisticated fashion portrait, dramatic lighting, high fashion editorial, professional model, elegant pose, luxury fashion, black and white or color, strong composition, editorial excellence, provocative fashion photography, artistic fashion portrait',
                'negative': 'amateur fashion, poor styling, weak composition, low quality fashion',
                'cfg_range': (8.0, 10.5),
                'steps_range': (85, 125),
                'samplers': ['dpmpp_2m', 'euler_ancestral']
            },
            {
                'style': 'Irving_Penn_Studio',
                'description': 'アーヴィング・ペン風スタジオ',
                'positive': 'studio portrait photography by Irving Penn, controlled studio lighting, professional fashion photography, clean background, precise composition, medium format quality, fashion editorial, timeless portrait style, professional model, elegant fashion, sophisticated lighting setup, award winning studio photography',
                'negative': 'natural lighting, outdoor setting, amateur studio setup, poor lighting control',
                'cfg_range': (7.8, 9.8),
                'steps_range': (80, 115),
                'samplers': ['dpmpp_2m', 'euler']
            }
        ]
    
    def get_technical_quality_presets(self):
        """技術的品質プリセット"""
        return {
            'ultra_quality': {
                'base_positive': 'RAW photo, (highly detailed skin:1.2), (8k uhd:1.1), dslr, soft lighting, high quality, film grain, Fujifilm XT3, photorealistic, hyperrealistic, ultra detailed face, beautiful detailed eyes, detailed skin texture, natural skin imperfections, subsurface scattering, realistic, portrait photography, professional photography, 85mm lens, depth of field, bokeh, natural lighting, studio lighting, perfect face, symmetrical face',
                'base_negative': 'worst quality, low quality, normal quality, lowres, blurry, pixelated, jpeg artifacts, grainy, noise, distorted, deformed, ugly, bad anatomy, bad proportions, extra limbs, cloned face, malformed limbs, gross proportions, missing arms, missing legs, extra arms, extra legs, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed face, ugly face, bad face',
                'steps_min': 80,
                'steps_max': 150,
                'cfg_min': 8.0,
                'cfg_max': 12.0
            },
            'premium_quality': {
                'base_positive': 'professional photography, high resolution, detailed skin, natural lighting, sharp focus, depth of field, bokeh, award winning photography, masterpiece, best quality',
                'base_negative': 'low quality, blurry, amateur photography, poor lighting, distorted, deformed, bad anatomy, extra limbs, mutated hands',
                'steps_min': 60,
                'steps_max': 100,
                'cfg_min': 7.0,
                'cfg_max': 9.5
            }
        }
    
    def get_subject_variations(self):
        """被写体バリエーション"""
        return [
            "stunning beautiful woman, 25 years old, wavy brown hair, hazel eyes, natural makeup",
            "elegant woman, 30 years old, straight blonde hair, blue eyes, professional makeup",
            "gorgeous woman, 28 years old, curly black hair, brown eyes, subtle makeup",
            "beautiful woman, 26 years old, long red hair, green eyes, natural beauty",
            "professional model, 24 years old, short brunette hair, grey eyes, fashion makeup",
            "sophisticated woman, 32 years old, platinum blonde hair, amber eyes, editorial makeup",
            "attractive woman, 27 years old, dark brown hair, dark eyes, minimal makeup",
            "fashion model, 23 years old, honey blonde hair, blue-green eyes, high fashion makeup"
        ]
    
    def get_clothing_styles(self):
        """服装スタイル"""
        return [
            "elegant black dress, designer fashion",
            "white silk blouse, professional attire",
            "vintage designer dress, classic elegance",
            "haute couture gown, luxury fashion",
            "casual chic outfit, contemporary style",
            "business suit, professional styling",
            "evening gown, formal elegance",
            "artistic fashion piece, avant-garde style"
        ]
    
    def create_professional_workflow(self, style_config, subject, clothing, quality_preset):
        """プロフェッショナル品質ワークフロー作成"""
        # プロンプト構築
        positive_parts = [
            quality_preset['base_positive'],
            style_config['positive'],
            subject,
            clothing,
            "gorgeous, stunning, masterpiece, award winning photography, best quality"
        ]
        
        negative_parts = [
            quality_preset['base_negative'],
            style_config['negative'],
            "child, loli, young, old, mature, fat, amateur, unprofessional"
        ]
        
        positive_prompt = ", ".join(positive_parts)
        negative_prompt = ", ".join(negative_parts)
        
        # パラメータ調整
        cfg_min, cfg_max = style_config['cfg_range']
        steps_min, steps_max = style_config['steps_range']
        
        cfg = round(random.uniform(max(cfg_min, quality_preset['cfg_min']), 
                                 min(cfg_max, quality_preset['cfg_max'])), 1)
        steps = random.randint(max(steps_min, quality_preset['steps_min']), 
                             min(steps_max, quality_preset['steps_max']))
        sampler = random.choice(style_config['samplers'])
        
        seed = int(time.time() * 1000000) % (2**32)
        
        # 解像度バリエーション
        resolutions = [
            (1024, 1024),  # Square
            (896, 1152),   # Portrait
            (832, 1216),   # Tall Portrait
            (768, 1344),   # Very Tall Portrait
            (1152, 896),   # Landscape
            (1216, 832)    # Wide Landscape
        ]
        width, height = random.choice(resolutions)
        
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
                    "filename_prefix": f"MARATHON_{style_config['style']}",
                    "images": ["6", 0]
                },
                "class_type": "SaveImage"
            }
        }
        
        return workflow, {
            'style': style_config['style'],
            'description': style_config['description'],
            'steps': steps,
            'cfg': cfg,
            'sampler': sampler,
            'resolution': f"{width}x{height}",
            'subject': subject[:50] + "..." if len(subject) > 50 else subject
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

    def get_generated_count(self):
        """生成済み画像カウント"""
        try:
            response = requests.get(f"http://localhost:8022/count_images?pattern=MARATHON_*", timeout=5)
            if response.status_code == 200:
                return int(response.text)
        except:
            pass
        return 0

    def run_marathon_generation(self):
        """10時間マラソン生成実行"""
        styles = self.get_professional_photographer_styles()
        subjects = self.get_subject_variations()
        clothing = self.get_clothing_styles()
        quality_presets = self.get_technical_quality_presets()
        
        print(f"🏁 V100 10時間プロフェッショナル写真マラソン開始!")
        print(f"📅 開始時刻: {self.session_start}")
        print(f"⏰ 終了予定: {self.session_start + timedelta(hours=10)}")
        print(f"🎯 目標: {self.target_images}枚の最高品質画像")
        print(f"📸 スタイル: {len(styles)}種類の世界的写真家スタイル")
        print("=" * 80)
        
        generated_count = 0
        error_count = 0
        style_stats = {style['style']: 0 for style in styles}
        
        while True:
            elapsed = time.time() - self.session_start.timestamp()
            
            # 10時間経過チェック
            if elapsed >= self.marathon_duration:
                print(f"\n⏰ 10時間経過！マラソン完了")
                break
            
            # 目標達成チェック
            if generated_count >= self.target_images:
                print(f"\n🎯 目標{self.target_images}枚達成！")
                break
            
            # ランダムな組み合わせ選択
            style = random.choice(styles)
            subject = random.choice(subjects)
            outfit = random.choice(clothing)
            
            # 品質プリセット選択（80%で最高品質）
            quality_key = 'ultra_quality' if random.random() < 0.8 else 'premium_quality'
            quality_preset = quality_presets[quality_key]
            
            try:
                workflow, params = self.create_professional_workflow(
                    style, subject, outfit, quality_preset)
                
                result = self.queue_prompt(workflow)
                
                if result and 'prompt_id' in result:
                    prompt_id = result['prompt_id']
                    
                    print(f"\n📸 Image {generated_count + 1}")
                    print(f"🎨 Style: {params['style']}")
                    print(f"⚙️  Settings: {params['steps']}steps, CFG{params['cfg']}, {params['sampler']}")
                    print(f"📐 Resolution: {params['resolution']}")
                    print(f"📋 Queue ID: {prompt_id}")
                    print(f"⏱️  Elapsed: {elapsed/3600:.1f}h")
                    
                    generated_count += 1
                    style_stats[style['style']] += 1
                    
                    # 進捗報告
                    if generated_count % 10 == 0:
                        remaining_time = (self.marathon_duration - elapsed) / 3600
                        progress = (generated_count / self.target_images) * 100
                        
                        print(f"\n📊 Progress Report:")
                        print(f"   Generated: {generated_count}/{self.target_images} ({progress:.1f}%)")
                        print(f"   Time remaining: {remaining_time:.1f} hours")
                        print(f"   Generation rate: {generated_count/(elapsed/3600):.1f} images/hour")
                        
                        print(f"\n🎨 Style Statistics:")
                        for style_name, count in style_stats.items():
                            if count > 0:
                                print(f"   {style_name}: {count} images")
                    
                    # キューが満杯にならないよう制御
                    while True:
                        queue_info = self.get_queue_info()
                        if queue_info:
                            running = len(queue_info.get('queue_running', []))
                            pending = len(queue_info.get('queue_pending', []))
                            total_queue = running + pending
                            
                            if total_queue < 5:  # キューに余裕がある
                                break
                        
                        print("⏳ Queue full, waiting...")
                        time.sleep(30)
                
                else:
                    error_count += 1
                    print(f"❌ Failed to queue prompt (error #{error_count})")
                    time.sleep(5)
                
            except Exception as e:
                error_count += 1
                print(f"❌ Error during generation (#{error_count}): {e}")
                time.sleep(10)
        
        # 最終レポート
        final_elapsed = time.time() - self.session_start.timestamp()
        
        print(f"\n{'='*80}")
        print("🏁 V100 Professional Photography Marathon Complete!")
        print(f"{'='*80}")
        print(f"⏱️  Total Time: {final_elapsed/3600:.2f} hours")
        print(f"📸 Images Generated: {generated_count}")
        print(f"📊 Generation Rate: {generated_count/(final_elapsed/3600):.1f} images/hour")
        print(f"❌ Errors: {error_count}")
        
        print(f"\n🎨 Final Style Statistics:")
        for style_name, count in sorted(style_stats.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                percentage = (count / generated_count) * 100
                print(f"   {style_name}: {count} images ({percentage:.1f}%)")
        
        return generated_count

def main():
    print("V100 Professional Photography Marathon - 10 Hours Ultimate Quality Generation")
    
    marathon = V100ProfessionalPhotographyMarathon()
    
    # ComfyUI接続確認
    try:
        response = requests.get(f"{marathon.base_url}/system_stats", timeout=10)
        if response.status_code == 200:
            print("✅ V100 ComfyUI connection successful")
        else:
            print("❌ V100 ComfyUI connection failed")
            return
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return
    
    # マラソン実行
    total_generated = marathon.run_marathon_generation()
    
    print(f"\n🎉 Marathon completed! Generated {total_generated} professional quality images")
    print(f"📁 Check /home/fujinoyuki/ComfyUI/output/ for MARATHON_* files")

if __name__ == "__main__":
    main()