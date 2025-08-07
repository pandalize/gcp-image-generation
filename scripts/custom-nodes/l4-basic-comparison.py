#!/usr/bin/env python3
"""
L4 GPU 基本カスタムノード画像生成スクリプト
SDXL Base 1.0を使用して20パターンのプロンプト比較
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

class L4BasicComparison:
    def __init__(self):
        self.server_ip = "34.41.25.140"
        self.port = 8188
        self.base_url = f"http://{self.server_ip}:{self.port}"
        self.output_dir = "/Users/fujinoyuki/Desktop/gcp/outputs/custom_node_comparison"
        self.create_output_dir()
        
    def create_output_dir(self):
        """Create output directory if it doesn't exist."""
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Output directory: {self.output_dir}")
    
    def get_20_prompt_variations(self):
        """20パターンのプロンプトバリエーション"""
        return [
            {
                'name': 'Basic_Portrait',
                'description': '基本ポートレート',
                'positive': 'beautiful woman portrait, professional photography, studio lighting',
                'negative': 'low quality, blurry, amateur',
            },
            {
                'name': 'Photorealistic_Style',
                'description': 'フォトリアル特化',
                'positive': 'photorealistic, ultra detailed, professional model, sharp focus, 8k resolution',
                'negative': 'anime, cartoon, painting, artistic, stylized',
            },
            {
                'name': 'Fashion_Photography',
                'description': 'ファッション写真',
                'positive': 'fashion photography, elegant dress, magazine cover, professional lighting, beauty shot',
                'negative': 'casual clothing, amateur photography, poor lighting',
            },
            {
                'name': 'Studio_Professional',
                'description': 'スタジオプロフェッショナル',
                'positive': 'studio portrait, professional headshot, commercial photography, perfect lighting',
                'negative': 'outdoor, natural light, candid shot',
            },
            {
                'name': 'High_Fashion_Model',
                'description': 'ハイファッションモデル',
                'positive': 'high fashion model, runway style, avant-garde, editorial photography, dramatic lighting',
                'negative': 'casual style, everyday clothing, simple lighting',
            },
            {
                'name': 'Beauty_Shot',
                'description': 'ビューティーショット',
                'positive': 'beauty shot, flawless skin, perfect makeup, cosmetic advertisement, glamour photography',
                'negative': 'no makeup, natural look, candid shot',
            },
            {
                'name': 'Corporate_Headshot',
                'description': 'コーポレートヘッドショット',
                'positive': 'corporate headshot, business professional, clean background, confident expression',
                'negative': 'casual attire, messy background, unprofessional',
            },
            {
                'name': 'Artistic_Portrait',
                'description': 'アーティスティックポートレート',
                'positive': 'artistic portrait, creative lighting, artistic composition, fine art photography',
                'negative': 'commercial style, standard lighting, basic composition',
            },
            {
                'name': 'Glamour_Photography',
                'description': 'グラマー写真',
                'positive': 'glamour photography, elegant pose, sophisticated styling, luxury aesthetic',
                'negative': 'simple pose, basic styling, plain aesthetic',
            },
            {
                'name': 'Portrait_Lighting',
                'description': 'ポートレートライティング特化',
                'positive': 'perfect portrait lighting, Rembrandt lighting, professional photography setup',
                'negative': 'flat lighting, harsh shadows, poor lighting setup',
            },
            {
                'name': 'Editorial_Style',
                'description': 'エディトリアルスタイル',
                'positive': 'editorial style, magazine photography, sophisticated composition, professional model',
                'negative': 'amateur style, snapshot photography, basic composition',
            },
            {
                'name': 'Skin_Detail_Focus',
                'description': '肌質詳細フォーカス',
                'positive': 'detailed skin texture, perfect skin, flawless complexion, high resolution details',
                'negative': 'poor skin texture, skin imperfections, low detail',
            },
            {
                'name': 'Expression_Focus',
                'description': '表情フォーカス',
                'positive': 'expressive eyes, natural smile, engaging expression, emotional connection',
                'negative': 'blank expression, forced smile, disconnected look',
            },
            {
                'name': 'Hair_Detail_Enhanced',
                'description': '髪質詳細強化',
                'positive': 'detailed hair texture, flowing hair, perfect hair styling, volumous hair',
                'negative': 'flat hair, poor hair texture, messy styling',
            },
            {
                'name': 'Background_Professional',
                'description': 'プロ背景設定',
                'positive': 'professional background, clean backdrop, studio setting, perfect background lighting',
                'negative': 'distracting background, poor backdrop, messy setting',
            },
            {
                'name': 'Color_Grading_Enhanced',
                'description': 'カラーグレーディング強化',
                'positive': 'perfect color grading, cinematic colors, professional color correction, vibrant yet natural',
                'negative': 'poor color grading, washed out colors, oversaturated, unnatural colors',
            },
            {
                'name': 'Composition_Perfect',
                'description': '完璧構図',
                'positive': 'perfect composition, rule of thirds, balanced framing, professional cropping',
                'negative': 'poor composition, unbalanced, bad framing, amateur cropping',
            },
            {
                'name': 'Depth_of_Field',
                'description': '被写界深度効果',
                'positive': 'shallow depth of field, perfect focus, beautiful bokeh, professional lens quality',
                'negative': 'everything in focus, no depth, flat image, amateur lens',
            },
            {
                'name': 'Mood_Lighting',
                'description': 'ムードライティング',
                'positive': 'moody lighting, dramatic shadows, atmospheric lighting, cinematic mood',
                'negative': 'flat lighting, no mood, basic illumination, documentary style',
            },
            {
                'name': 'Ultra_Sharp_Details',
                'description': '超シャープ詳細',
                'positive': 'ultra sharp details, crystal clear, perfect focus, high definition, razor sharp',
                'negative': 'soft focus, blurry details, out of focus, low definition',
            }
        ]
    
    def create_basic_workflow(self, config, index):
        """基本ワークフロー作成（SDXL Base 1.0使用）"""
        
        positive = config.get('positive', '')
        negative = config.get('negative', '')
        
        workflow = {
            "1": {
                "inputs": {
                    "ckpt_name": "sdxl_base_1.0.safetensors"
                },
                "class_type": "CheckpointLoaderSimple",
                "_meta": {"title": f"Load SDXL - {config['name']}"}
            },
            "2": {
                "inputs": {
                    "width": 1024,
                    "height": 1024,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage",
                "_meta": {"title": f"Latent - {config['name']}"}
            },
            "3": {
                "inputs": {
                    "text": f"masterpiece, {positive}, ultra high quality, professional photography",
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": f"Positive - {config['name']}"}
            },
            "4": {
                "inputs": {
                    "text": f"low quality, worst quality, {negative}, amateur, blurry, distorted",
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": f"Negative - {config['name']}"}
            },
            "5": {
                "inputs": {
                    "seed": int(time.time()) + index * 1000,
                    "steps": 35,
                    "cfg": 7.0,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1,
                    "model": ["1", 0],
                    "positive": ["3", 0],
                    "negative": ["4", 0],
                    "latent_image": ["2", 0]
                },
                "class_type": "KSampler",
                "_meta": {"title": f"Sampler - {config['name']}"}
            },
            "6": {
                "inputs": {
                    "samples": ["5", 0],
                    "vae": ["1", 2]
                },
                "class_type": "VAEDecode",
                "_meta": {"title": f"VAE Decode - {config['name']}"}
            },
            "7": {
                "inputs": {
                    "filename_prefix": f"{config['name']}_",
                    "images": ["6", 0]
                },
                "class_type": "SaveImage",
                "_meta": {"title": f"Save - {config['name']}"}
            }
        }
        
        return {"prompt": workflow}
    
    def queue_prompt(self, workflow):
        """Queue a prompt for generation."""
        try:
            response = requests.post(f"{self.base_url}/prompt", json=workflow, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error queuing prompt: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error queuing prompt: {e}")
            return None
    
    def wait_for_completion(self, prompt_id, config_name):
        """Wait for image generation to complete."""
        print(f"Generating {config_name}...")
        start_time = time.time()
        
        while True:
            try:
                queue_response = requests.get(f"{self.base_url}/queue", timeout=10)
                if queue_response.status_code == 200:
                    queue_data = queue_response.json()
                    
                    running = [item[1] for item in queue_data.get('queue_running', [])]
                    pending = [item[1] for item in queue_data.get('queue_pending', [])]
                    
                    if prompt_id not in running and prompt_id not in pending:
                        elapsed = time.time() - start_time
                        print(f"{config_name} completed! ({elapsed:.1f}s)")
                        return True
                
                time.sleep(3)
                
            except Exception as e:
                print(f"Error checking queue: {e}")
                time.sleep(5)
    
    def download_image(self, filename, config_name, image_index):
        """Download generated image."""
        try:
            url = f"{self.base_url}/view"
            params = {"filename": filename, "subfolder": "", "type": "output"}
            
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                # Create subdirectory for this style
                style_dir = os.path.join(self.output_dir, config_name)
                os.makedirs(style_dir, exist_ok=True)
                
                local_filename = f"{config_name}_img{image_index+1:02d}_{filename}"
                local_path = os.path.join(style_dir, local_filename)
                
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                
                file_size = len(response.content) / 1024
                print(f"Downloaded: {local_filename} ({file_size:.1f}KB)")
                return True
            else:
                print(f"Failed to download {filename}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error downloading {filename}: {e}")
            return False
    
    def generate_all_variations(self):
        """20パターンで各5枚ずつ画像生成"""
        print("🎨 20パターン プロンプト比較生成開始")
        print("📐 各スタイルで5枚ずつ生成（総計100枚）")
        print("🎯 L4 GPU + SDXL Base 1.0")
        print("=" * 60)
        
        configs = self.get_20_prompt_variations()
        print(f"Loaded {len(configs)} prompt configurations")
        
        total_start = time.time()
        total_successful = 0
        results_summary = []
        
        for config_index, config in enumerate(configs):
            print(f"\n{'='*60}")
            print(f"🎨 スタイル {config_index+1}/20: {config['name']}")
            print(f"📝 説明: {config['description']}")
            print(f"{'='*60}")
            
            style_successful = 0
            style_start_time = time.time()
            
            # 各スタイルで5枚生成
            for img_index in range(5):
                print(f"\n📸 {config['name']} - 画像 {img_index+1}/5")
                
                # ワークフロー作成
                workflow = self.create_basic_workflow(config, config_index * 5 + img_index)
                
                # プロンプトをキューに追加
                result = self.queue_prompt(workflow)
                if not result:
                    print(f"Failed to queue {config['name']} image {img_index+1}")
                    continue
                
                prompt_id = result.get('prompt_id')
                if not prompt_id:
                    print(f"No prompt ID for {config['name']} image {img_index+1}")
                    continue
                
                # 生成完了を待機
                if self.wait_for_completion(prompt_id, config['name']):
                    time.sleep(2)
                    
                    # 生成画像をダウンロード
                    expected_filename = f"{config['name']}__00001_.png"
                    if self.download_image(expected_filename, config['name'], img_index):
                        style_successful += 1
                        total_successful += 1
                    else:
                        print(f"Failed to download {config['name']} image {img_index+1}")
                else:
                    print(f"Generation failed for {config['name']} image {img_index+1}")
            
            style_time = time.time() - style_start_time
            style_avg = style_time / style_successful if style_successful > 0 else 0
            
            results_summary.append({
                'name': config['name'],
                'successful': style_successful,
                'total_time': style_time,
                'avg_per_image': style_avg,
                'description': config['description']
            })
            
            print(f"\n✅ {config['name']} 完了: {style_successful}/5 成功")
            print(f"⏱️  所要時間: {style_time:.1f}秒 (平均: {style_avg:.1f}秒/枚)")
        
        total_time = time.time() - total_start
        
        # 結果サマリー表示
        print("\n" + "=" * 80)
        print("🎉 20パターン プロンプト比較生成完了!")
        print("=" * 80)
        print(f"✅ 総生成成功: {total_successful}/100 枚")
        print(f"⏱️  総所要時間: {total_time:.1f}秒")
        print(f"📊 平均生成時間: {total_time/total_successful:.1f}秒/枚" if total_successful > 0 else "N/A")
        print(f"📁 出力先: {self.output_dir}")
        
        # 各スタイルの詳細結果
        print("\n📊 プロンプトスタイル別結果:")
        for result in results_summary:
            success_rate = (result['successful'] / 5) * 100
            print(f"{result['name']:25} | {result['successful']}/5 ({success_rate:3.0f}%) | {result['avg_per_image']:5.1f}s/枚 | {result['description']}")
        
        return results_summary

def main():
    generator = L4BasicComparison()
    
    # ComfyUIの接続確認
    try:
        response = requests.get(f"{generator.base_url}", timeout=10)
        print(f"✅ ComfyUI接続確認: {generator.base_url}")
    except:
        print(f"❌ ComfyUI接続失敗: {generator.base_url}")
        print("ComfyUIが起動していることを確認してください")
        return
    
    # 20パターン生成開始
    generator.generate_all_variations()

if __name__ == "__main__":
    main()