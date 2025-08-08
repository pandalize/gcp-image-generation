#!/usr/bin/env python3
"""
V100 特化テーマ別高品質生成
ファッション・アート・ビューティー・エディトリアル特化プロンプト
"""

import requests
import json
import time
import os
import random
from datetime import datetime

class SpecializedThemeGeneration:
    def __init__(self):
        self.server_ip = "localhost"
        self.port = 8188
        self.base_url = f"http://{self.server_ip}:{self.port}"
        
    def get_fashion_editorial_themes(self):
        """ファッション雑誌エディトリアル特化"""
        return [
            {
                'theme': 'Luxury_Fashion_Editorial',
                'description': 'ラグジュアリーファッション雑誌風',
                'base_prompt': 'luxury fashion editorial photography, high fashion magazine, Vogue style, professional model, designer fashion, studio lighting, commercial photography, award winning fashion photography, editorial excellence, sophisticated styling, premium fashion shoot',
                'clothing_styles': [
                    'haute couture evening gown, designer luxury',
                    'high fashion business suit, tailored perfection',
                    'avant-garde designer dress, artistic fashion',
                    'luxury cashmere coat, elegant sophistication',
                    'designer cocktail dress, evening elegance'
                ],
                'settings': {
                    'cfg_range': (8.0, 10.0),
                    'steps_range': (100, 140),
                    'samplers': ['dpmpp_2m', 'euler_ancestral']
                }
            },
            {
                'theme': 'Street_Fashion_Editorial',
                'description': 'ストリートファッション現代的',
                'base_prompt': 'contemporary street fashion photography, urban style editorial, modern fashion photography, lifestyle magazine, contemporary style, street style editorial, fashion week photography, modern elegance, urban sophistication',
                'clothing_styles': [
                    'contemporary street wear, modern urban style',
                    'designer casual luxury, elevated street style',
                    'modern minimalist fashion, clean contemporary',
                    'urban chic outfit, stylish casual luxury',
                    'contemporary designer pieces, modern sophistication'
                ],
                'settings': {
                    'cfg_range': (7.5, 9.5),
                    'steps_range': (90, 120),
                    'samplers': ['dpmpp_2m', 'euler']
                }
            },
            {
                'theme': 'Vintage_Fashion_Revival',
                'description': 'ヴィンテージファッション復活',
                'base_prompt': 'vintage fashion photography revival, retro elegance, classic fashion editorial, timeless style, vintage haute couture, classic fashion photography, retro glamour, vintage luxury fashion, timeless elegance',
                'clothing_styles': [
                    'vintage haute couture dress, classic elegance',
                    'retro designer suit, timeless sophistication',
                    'vintage evening gown, old Hollywood glamour',
                    'classic designer pieces, vintage luxury',
                    'retro fashion ensemble, nostalgic elegance'
                ],
                'settings': {
                    'cfg_range': (8.5, 11.0),
                    'steps_range': (110, 150),
                    'samplers': ['dpmpp_2m', 'dpmpp_sde']
                }
            }
        ]
    
    def get_beauty_portrait_themes(self):
        """ビューティーポートレート特化"""
        return [
            {
                'theme': 'Luxury_Beauty_Campaign',
                'description': 'ラグジュアリー美容キャンペーン',
                'base_prompt': 'luxury beauty campaign photography, cosmetics advertisement, flawless skin, professional makeup artistry, beauty commercial photography, luxury skincare campaign, premium beauty photography, high-end cosmetics, beauty editorial excellence',
                'makeup_styles': [
                    'flawless natural makeup, glowing skin perfection',
                    'dramatic evening makeup, bold elegance',
                    'soft romantic makeup, natural beauty enhancement',
                    'high fashion editorial makeup, artistic beauty',
                    'classic red lip makeup, timeless glamour'
                ],
                'settings': {
                    'cfg_range': (9.0, 12.0),
                    'steps_range': (120, 160),
                    'samplers': ['dpmpp_2m', 'euler_ancestral']
                }
            },
            {
                'theme': 'Natural_Beauty_Portrait',
                'description': '自然美ポートレート',
                'base_prompt': 'natural beauty portrait photography, organic beauty, minimal makeup, natural skin texture, authentic beauty, clean beauty aesthetic, natural light portrait, genuine beauty photography, organic skin care campaign',
                'makeup_styles': [
                    'minimal natural makeup, authentic beauty',
                    'no makeup natural look, pure beauty',
                    'subtle enhancement, natural glow',
                    'fresh faced beauty, organic elegance',
                    'barely there makeup, natural perfection'
                ],
                'settings': {
                    'cfg_range': (7.0, 9.0),
                    'steps_range': (80, 110),
                    'samplers': ['euler', 'dpmpp_2m']
                }
            }
        ]
    
    def get_artistic_portrait_themes(self):
        """アーティスティックポートレート特化"""
        return [
            {
                'theme': 'Fine_Art_Photography',
                'description': 'ファインアート写真',
                'base_prompt': 'fine art portrait photography, gallery worthy, museum quality, artistic photography, contemporary art, portrait artistry, creative vision, innovative composition, artistic excellence, fine art aesthetic, art photography masterpiece',
                'artistic_styles': [
                    'dramatic chiaroscuro lighting, Renaissance inspired',
                    'minimalist artistic composition, modern art aesthetic',
                    'surreal artistic portrait, creative vision',
                    'abstract artistic elements, contemporary art',
                    'classical art inspired portrait, timeless artistry'
                ],
                'settings': {
                    'cfg_range': (8.0, 10.5),
                    'steps_range': (100, 140),
                    'samplers': ['dpmpp_sde', 'euler_ancestral']
                }
            },
            {
                'theme': 'Conceptual_Art_Portrait',
                'description': 'コンセプチュアルアートポートレート',
                'base_prompt': 'conceptual art portrait, creative concept photography, artistic storytelling, narrative portrait, conceptual photography, artistic interpretation, creative artistry, conceptual vision, art concept photography',
                'artistic_styles': [
                    'symbolic artistic elements, conceptual meaning',
                    'metaphorical portrait composition, artistic narrative',
                    'abstract conceptual art, creative interpretation',
                    'philosophical art portrait, deep meaning',
                    'conceptual artistic vision, innovative creativity'
                ],
                'settings': {
                    'cfg_range': (7.5, 9.5),
                    'steps_range': (90, 130),
                    'samplers': ['dpmpp_sde', 'euler']
                }
            }
        ]
    
    def get_editorial_themes(self):
        """雑誌エディトリアル特化"""
        return [
            {
                'theme': 'Magazine_Cover_Quality',
                'description': '雑誌表紙クオリティ',
                'base_prompt': 'magazine cover photography, cover model quality, editorial excellence, magazine quality, cover story photography, professional magazine shoot, cover model perfection, editorial photography, magazine standard',
                'cover_concepts': [
                    'confident business woman, executive portrait',
                    'elegant evening wear, sophisticated glamour',
                    'contemporary fashion icon, modern style',
                    'luxury lifestyle portrait, affluent elegance',
                    'artistic fashion editorial, creative vision'
                ],
                'settings': {
                    'cfg_range': (8.5, 11.0),
                    'steps_range': (110, 150),
                    'samplers': ['dpmpp_2m', 'euler_ancestral']
                }
            }
        ]
    
    def get_premium_subjects(self):
        """プレミアム被写体"""
        return [
            "stunning supermodel, 26 years old, perfect bone structure, captivating blue eyes, platinum blonde hair",
            "elegant fashion model, 24 years old, sophisticated features, warm brown eyes, lustrous brunette hair",
            "gorgeous editorial model, 28 years old, striking features, emerald green eyes, rich auburn hair",
            "professional model, 25 years old, classic beauty, hazel eyes, silky black hair",
            "beautiful portrait subject, 27 years old, refined features, deep brown eyes, honey blonde hair"
        ]
    
    def create_specialized_workflow(self, theme_config, subject, style_element):
        """特化ワークフロー作成"""
        settings = theme_config['settings']
        
        # ランダムパラメータ選択
        cfg = round(random.uniform(settings['cfg_range'][0], settings['cfg_range'][1]), 1)
        steps = random.randint(settings['steps_range'][0], settings['steps_range'][1])
        sampler = random.choice(settings['samplers'])
        
        # 解像度選択（ポートレート重視）
        resolutions = [
            (1024, 1024),  # Square
            (896, 1152),   # Portrait
            (832, 1216),   # Tall Portrait
            (768, 1344),   # Magazine Portrait
            (1152, 896)    # Landscape for variety
        ]
        width, height = random.choice(resolutions)
        
        # プロンプト構築
        positive_parts = [
            "RAW photo, (highly detailed skin:1.2), (8k uhd:1.1), professional photography, masterpiece, best quality",
            theme_config['base_prompt'],
            subject,
            style_element,
            "award winning photography, ultra sharp, photorealistic, hyperrealistic, perfect lighting, professional excellence"
        ]
        
        negative_parts = [
            "worst quality, low quality, normal quality, lowres, blurry, pixelated, jpeg artifacts, grainy, noise",
            "amateur, unprofessional, poor quality, bad lighting, distorted, deformed, bad anatomy, extra limbs",
            "child, loli, young, old, amateur photography, poor styling, cheap production"
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
                    "filename_prefix": f"THEME_{theme_config['theme']}",
                    "images": ["6", 0]
                },
                "class_type": "SaveImage"
            }
        }
        
        return workflow, {
            'theme': theme_config['theme'],
            'description': theme_config['description'],
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

    def run_specialized_theme_generation(self, target_images=80):
        """特化テーマ生成実行"""
        all_themes = (
            self.get_fashion_editorial_themes() +
            self.get_beauty_portrait_themes() +
            self.get_artistic_portrait_themes() +
            self.get_editorial_themes()
        )
        
        subjects = self.get_premium_subjects()
        
        print(f"🎨 V100 Specialized Theme Generation")
        print(f"🎯 Target: {target_images} specialized images")
        print(f"🎭 Themes: {len(all_themes)} specialized categories")
        print(f"👥 Subjects: {len(subjects)} premium models")
        print("=" * 80)
        
        generated_count = 0
        theme_stats = {theme['theme']: 0 for theme in all_themes}
        
        while generated_count < target_images:
            # ランダム組み合わせ選択
            theme = random.choice(all_themes)
            subject = random.choice(subjects)
            
            # テーマに応じたスタイル要素選択
            style_elements_key = None
            if 'clothing_styles' in theme:
                style_elements_key = 'clothing_styles'
            elif 'makeup_styles' in theme:
                style_elements_key = 'makeup_styles'
            elif 'artistic_styles' in theme:
                style_elements_key = 'artistic_styles'
            elif 'cover_concepts' in theme:
                style_elements_key = 'cover_concepts'
            
            if style_elements_key:
                style_element = random.choice(theme[style_elements_key])
            else:
                style_element = "elegant styling, sophisticated presentation"
            
            try:
                workflow, params = self.create_specialized_workflow(theme, subject, style_element)
                result = self.queue_prompt(workflow)
                
                if result and 'prompt_id' in result:
                    prompt_id = result['prompt_id']
                    
                    print(f"\n🎭 Theme Image {generated_count + 1}/{target_images}")
                    print(f"🎨 Theme: {params['theme']}")
                    print(f"📝 Description: {params['description']}")
                    print(f"⚙️  Settings: {params['steps']}steps, CFG{params['cfg']}, {params['sampler']}")
                    print(f"📐 Resolution: {params['resolution']}")
                    print(f"🆔 Queue ID: {prompt_id}")
                    
                    generated_count += 1
                    theme_stats[theme['theme']] += 1
                    
                    # 進捗報告
                    if generated_count % 10 == 0:
                        progress = (generated_count / target_images) * 100
                        print(f"\n📊 Progress: {generated_count}/{target_images} ({progress:.1f}%)")
                        print("🎭 Theme Statistics:")
                        for theme_name, count in theme_stats.items():
                            if count > 0:
                                print(f"   {theme_name}: {count} images")
                    
                    # キュー制御
                    while True:
                        queue_info = self.get_queue_info()
                        if queue_info:
                            running = len(queue_info.get('queue_running', []))
                            pending = len(queue_info.get('queue_pending', []))
                            if running + pending < 4:  # キューに余裕がある
                                break
                        print("⏳ Queue management...")
                        time.sleep(25)
                
                else:
                    print(f"❌ Failed to queue theme image")
                    time.sleep(5)
                
            except Exception as e:
                print(f"❌ Error during theme generation: {e}")
                time.sleep(10)
        
        # 最終レポート
        print(f"\n{'='*80}")
        print("🎭 V100 Specialized Theme Generation Complete!")
        print(f"{'='*80}")
        print(f"📊 Total Theme Images: {generated_count}")
        
        print(f"\n🎨 Final Theme Statistics:")
        for theme_name, count in sorted(theme_stats.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                percentage = (count / generated_count) * 100
                print(f"   {theme_name}: {count} images ({percentage:.1f}%)")
        
        return generated_count

def main():
    print("V100 Specialized Theme Generation")
    
    generator = SpecializedThemeGeneration()
    
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
    
    # 特化テーマ生成実行
    total_generated = generator.run_specialized_theme_generation(80)
    
    print(f"\n🎉 Theme generation completed! Generated {total_generated} specialized images")
    print(f"📁 Check /home/fujinoyuki/ComfyUI/output/ for THEME_* files")

if __name__ == "__main__":
    main()