#!/usr/bin/env python3
"""
L4 GPU リモート 20パターンプロンプト比較生成
SDXL Base 1.0を使用、リモートで5時間実行
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

class L4RemoteComparison:
    def __init__(self):
        self.server_ip = "localhost"  # ローカルのComfyUI
        self.port = 8188
        self.base_url = f"http://{self.server_ip}:{self.port}"
        self.output_dir = "/home/fujinoyuki/comparison_outputs"
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
        print(f"🎨 Generating {config_name}...")
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
                        print(f"✅ {config_name} completed! ({elapsed:.1f}s)")
                        return True
                
                time.sleep(3)
                
            except Exception as e:
                print(f"Error checking queue: {e}")
                time.sleep(5)
    
    def copy_generated_image(self, config_name, image_index):
        """ComfyUIの出力ディレクトリから比較用ディレクトリにコピー"""
        try:
            comfyui_output = "/home/fujinoyuki/ComfyUI/output"
            
            # 最新の生成画像を探す
            import glob
            pattern = f"{comfyui_output}/{config_name}_*"
            files = glob.glob(pattern)
            
            if not files:
                print(f"No files found for pattern: {pattern}")
                return False
                
            # 最新ファイルを取得
            latest_file = max(files, key=os.path.getctime)
            
            # コピー先を作成
            style_dir = os.path.join(self.output_dir, config_name)
            os.makedirs(style_dir, exist_ok=True)
            
            # ファイル名を生成
            import shutil
            filename = os.path.basename(latest_file)
            new_filename = f"{config_name}_img{image_index+1:02d}_{filename}"
            dest_path = os.path.join(style_dir, new_filename)
            
            shutil.copy2(latest_file, dest_path)
            
            file_size = os.path.getsize(dest_path) / 1024
            print(f"📸 Copied: {new_filename} ({file_size:.1f}KB)")
            return True
            
        except Exception as e:
            print(f"Error copying image: {e}")
            return False
    
    def generate_all_variations(self):
        """20パターンで各5枚ずつ画像生成（5時間実行）"""
        print(f"🎨 20パターン プロンプト比較生成開始")
        print(f"📐 各スタイルで5枚ずつ生成（総計100枚）")
        print(f"🎯 L4 GPU + SDXL Base 1.0")
        print(f"⏰ 開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        configs = self.get_20_prompt_variations()
        print(f"Loaded {len(configs)} prompt configurations")
        
        total_start = time.time()
        total_successful = 0
        results_summary = []
        
        # 5時間のタイムリミット設定
        time_limit = 5 * 60 * 60  # 5時間
        
        for config_index, config in enumerate(configs):
            # 時間チェック
            elapsed_total = time.time() - total_start
            if elapsed_total >= time_limit:
                print(f"\n⏰ 5時間経過のためタイムアップ！")
                break
                
            print(f"\n{'='*80}")
            print(f"🎨 スタイル {config_index+1}/20: {config['name']}")
            print(f"📝 説明: {config['description']}")
            print(f"⏰ 経過時間: {elapsed_total/3600:.1f}時間")
            print(f"{'='*80}")
            
            style_successful = 0
            style_start_time = time.time()
            
            # 各スタイルで5枚生成
            for img_index in range(5):
                # 時間チェック
                elapsed_total = time.time() - total_start
                if elapsed_total >= time_limit:
                    print(f"\n⏰ タイムアップのため生成終了")
                    break
                    
                print(f"\n📸 {config['name']} - 画像 {img_index+1}/5 ({elapsed_total/3600:.1f}h経過)")
                
                # ワークフロー作成
                workflow = self.create_basic_workflow(config, config_index * 5 + img_index)
                
                # プロンプトをキューに追加
                result = self.queue_prompt(workflow)
                if not result:
                    print(f"❌ Failed to queue {config['name']} image {img_index+1}")
                    continue
                
                prompt_id = result.get('prompt_id')
                if not prompt_id:
                    print(f"❌ No prompt ID for {config['name']} image {img_index+1}")
                    continue
                
                # 生成完了を待機
                if self.wait_for_completion(prompt_id, config['name']):
                    time.sleep(3)
                    
                    # 生成画像をコピー
                    if self.copy_generated_image(config['name'], img_index):
                        style_successful += 1
                        total_successful += 1
                    else:
                        print(f"❌ Failed to copy {config['name']} image {img_index+1}")
                else:
                    print(f"❌ Generation failed for {config['name']} image {img_index+1}")
            
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
        
        # 結果サマリー表示とファイル保存
        summary_text = self.create_final_report(results_summary, total_successful, total_time)
        print(summary_text)
        
        # レポートをファイルに保存
        with open(f"{self.output_dir}/generation_report.txt", "w", encoding='utf-8') as f:
            f.write(summary_text)
        
        return results_summary
    
    def create_final_report(self, results_summary, total_successful, total_time):
        """最終レポート作成"""
        report = []
        report.append("=" * 80)
        report.append("🎉 20パターン プロンプト比較生成完了!")
        report.append("=" * 80)
        report.append(f"✅ 総生成成功: {total_successful}/100 枚")
        report.append(f"⏱️  総所要時間: {total_time:.1f}秒 ({total_time/3600:.1f}時間)")
        if total_successful > 0:
            report.append(f"📊 平均生成時間: {total_time/total_successful:.1f}秒/枚")
        report.append(f"📁 出力先: {self.output_dir}")
        report.append(f"⏰ 完了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        report.append("📊 プロンプトスタイル別結果:")
        report.append("-" * 80)
        
        for result in results_summary:
            success_rate = (result['successful'] / 5) * 100
            report.append(f"{result['name']:25} | {result['successful']}/5 ({success_rate:3.0f}%) | {result['avg_per_image']:5.1f}s/枚 | {result['description']}")
        
        report.append("")
        report.append("📁 生成された画像は以下のディレクトリ構造で保存されています:")
        for result in results_summary:
            if result['successful'] > 0:
                report.append(f"  - {self.output_dir}/{result['name']}/")
        
        return "\n".join(report)

def main():
    generator = L4RemoteComparison()
    
    # ComfyUIの接続確認
    try:
        response = requests.get(f"{generator.base_url}", timeout=10)
        print(f"✅ ComfyUI接続確認: {generator.base_url}")
    except Exception as e:
        print(f"❌ ComfyUI接続失敗: {generator.base_url}")
        print(f"エラー: {e}")
        print("ComfyUIが起動していることを確認してください")
        return
    
    # 20パターン生成開始
    try:
        generator.generate_all_variations()
    except KeyboardInterrupt:
        print("\n🛑 ユーザーによって中断されました")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
    
    print(f"\n🏁 プログラム終了: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()