#!/usr/bin/env python3
"""
L4 GPU 20種類カスタムノード画像生成比較テスト
各カスタムノード（プロンプト技法）で5枚ずつ生成して比較
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

class L4CustomNodesTest:
    def __init__(self):
        self.server_ip = "localhost"  # ローカルのComfyUI
        self.port = 8188
        self.base_url = f"http://{self.server_ip}:{self.port}"
        self.output_dir = "/home/fujinoyuki/custom_nodes_comparison"
        self.create_output_dir()
        
    def create_output_dir(self):
        """Create output directory if it doesn't exist."""
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Output directory: {self.output_dir}")
    
    def get_20_custom_node_techniques(self):
        """20種類のカスタムノード技法（プロンプト最適化）"""
        return [
            {
                'name': '01_Impact_Face_Detailer',
                'description': 'Impact Pack Face Detailer風顔詳細強化',
                'positive': 'masterpiece, beautiful woman portrait, detailed face, perfect facial features, flawless skin, professional photography, studio lighting, enhanced face details, face focus',
                'negative': 'low quality, blurry, bad face, deformed face, ugly face, face artifacts',
                'cfg': 7.0,
                'steps': 35
            },
            {
                'name': '02_Ultimate_Upscale',
                'description': 'Ultimate SD Upscale風高解像度',
                'positive': 'ultra high resolution, detailed woman portrait, photorealistic, sharp details, crisp image, high definition, 4K quality, professional photography',
                'negative': 'low resolution, pixelated, blurry, soft focus, low quality',
                'cfg': 7.5,
                'steps': 40
            },
            {
                'name': '03_ControlNet_Canny',
                'description': 'ControlNet Canny風輪郭制御',
                'positive': 'beautiful woman, sharp edges, clean lines, precise contours, detailed features, clear boundaries, defined silhouette',
                'negative': 'soft edges, blurry lines, unclear contours, messy boundaries',
                'cfg': 7.0,
                'steps': 35
            },
            {
                'name': '04_Advanced_ControlNet',
                'description': 'Advanced ControlNet風複数制御',
                'positive': 'professional model, precise pose control, detailed anatomy, perfect proportions, controlled generation, multiple guidance',
                'negative': 'bad anatomy, wrong proportions, distorted pose, uncontrolled generation',
                'cfg': 6.8,
                'steps': 35
            },
            {
                'name': '05_Regional_Prompting',
                'description': 'Regional Prompter風エリア別制御',
                'positive': 'beautiful woman, [face: detailed beautiful face, perfect eyes] [body: elegant dress, graceful pose] [background: clean studio]',
                'negative': 'inconsistent regions, poor area control, conflicting styles',
                'cfg': 7.2,
                'steps': 38
            },
            {
                'name': '06_SDXL_Prompt_Styler',
                'description': 'SDXL Prompt Styler風スタイル最適化',
                'positive': 'photorealistic portrait style, fashion photography, magazine quality, professional lighting, commercial style, polished look',
                'negative': 'amateur style, poor styling, unprofessional look',
                'cfg': 7.5,
                'steps': 40
            },
            {
                'name': '07_Efficiency_Nodes',
                'description': 'Efficiency Nodes風効率化',
                'positive': 'efficient generation, optimized quality, beautiful woman, streamlined process, clean result, professional efficiency',
                'negative': 'inefficient process, poor optimization, messy result',
                'cfg': 7.0,
                'steps': 30
            },
            {
                'name': '08_WAS_Node_Suite',
                'description': 'WAS Node Suite風高機能処理',
                'positive': 'advanced processing, beautiful woman portrait, enhanced details, superior quality, complex workflow benefits',
                'negative': 'basic processing, simple workflow, limited enhancement',
                'cfg': 7.3,
                'steps': 35
            },
            {
                'name': '09_IPAdapter_Plus',
                'description': 'IPAdapter Plus風スタイル転送',
                'positive': 'style transfer enhanced, beautiful woman, artistic quality, refined aesthetics, consistent style application',
                'negative': 'poor style consistency, style transfer artifacts',
                'cfg': 6.5,
                'steps': 35
            },
            {
                'name': '10_AnimateDiff_Static',
                'description': 'AnimateDiff風静止画特化',
                'positive': 'high quality static image, beautiful woman, perfect stillness, no motion artifacts, crisp details',
                'negative': 'motion artifacts, animation residue, temporal inconsistency',
                'cfg': 7.0,
                'steps': 35
            },
            {
                'name': '11_Inspire_Pack',
                'description': 'Inspire Pack風創造性向上',
                'positive': 'inspiring beautiful woman, creative composition, artistic vision, masterpiece quality, imaginative result',
                'negative': 'uninspiring, boring composition, lack of creativity',
                'cfg': 7.8,
                'steps': 42
            },
            {
                'name': '12_Segment_Anything',
                'description': 'Segment Anything風精密分割',
                'positive': 'precisely segmented, beautiful woman, sharp boundaries, clean separation, detailed masking effects',
                'negative': 'poor segmentation, blurry boundaries, messy separation',
                'cfg': 7.0,
                'steps': 35
            },
            {
                'name': '13_Custom_Scripts',
                'description': 'Custom Scripts風拡張機能',
                'positive': 'enhanced features, beautiful woman, advanced scripting benefits, superior workflow results',
                'negative': 'basic features, limited scripting, standard workflow',
                'cfg': 7.2,
                'steps': 38
            },
            {
                'name': '14_Math_Expression',
                'description': 'Math Expression風数値最適化',
                'positive': 'mathematically optimized, beautiful woman, perfect proportions, calculated beauty, precise measurements',
                'negative': 'poorly calculated, wrong proportions, mathematical inconsistency',
                'cfg': 7.0,
                'steps': 35
            },
            {
                'name': '15_Quality_of_Life',
                'description': 'Quality of Life風利便性向上',
                'positive': 'user-friendly generated, beautiful woman, convenient results, smooth generation, improved usability',
                'negative': 'inconvenient results, poor usability, difficult workflow',
                'cfg': 7.5,
                'steps': 35
            },
            {
                'name': '16_Face_Restore',
                'description': 'Face Restore風顔修復特化',
                'positive': 'restored beautiful face, clear skin, perfect facial restoration, natural expression, enhanced facial quality',
                'negative': 'damaged face, restoration artifacts, unnatural expression',
                'cfg': 6.8,
                'steps': 40
            },
            {
                'name': '17_ControlAltAI',
                'description': 'ControlAltAI風プロ品質',
                'positive': 'professional grade, beautiful woman, commercial quality, studio standard, enterprise level results',
                'negative': 'amateur grade, non-commercial quality, basic standard',
                'cfg': 7.5,
                'steps': 40
            },
            {
                'name': '18_Image_Saver',
                'description': 'Image Saver風組織化保存',
                'positive': 'well organized output, beautiful woman, systematic generation, clean file management, structured results',
                'negative': 'disorganized output, poor file management, messy results',
                'cfg': 7.0,
                'steps': 35
            },
            {
                'name': '19_Video_Helper',
                'description': 'Video Helper Suite風静止画活用',
                'positive': 'video-quality static image, beautiful woman, cinematic quality, movie-grade details, high production value',
                'negative': 'low production value, non-cinematic, basic video quality',
                'cfg': 7.3,
                'steps': 38
            },
            {
                'name': '20_Multi_Node_Fusion',
                'description': '複数ノード融合効果',
                'positive': 'fusion of multiple enhancements, beautiful woman, combined node effects, ultimate quality, synergistic results',
                'negative': 'conflicting enhancements, poor node combination, reduced synergy',
                'cfg': 7.0,
                'steps': 45
            }
        ]
    
    def create_custom_workflow(self, config, index):
        """カスタムノード風技法のワークフロー作成"""
        
        positive = config.get('positive', '')
        negative = config.get('negative', '')
        steps = config.get('steps', 35)
        cfg = config.get('cfg', 7.0)
        
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
                    "text": f"masterpiece, ultra high quality, {positive}",
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
                    "steps": steps,
                    "cfg": cfg,
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
        """ComfyUIの出力から比較用ディレクトリにコピー"""
        try:
            comfyui_output = "/home/fujinoyuki/ComfyUI/output"
            
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
    
    def generate_all_custom_node_tests(self):
        """20種類のカスタムノード風技法で各5枚生成（5時間実行）"""
        print(f"🎛️  20種類カスタムノード風技法比較開始")
        print(f"📐 各技法で5枚ずつ生成（総計100枚）")
        print(f"🎯 L4 GPU + SDXL Base 1.0")
        print(f"⏰ 開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        configs = self.get_20_custom_node_techniques()
        print(f"Loaded {len(configs)} custom node techniques")
        
        total_start = time.time()
        total_successful = 0
        results_summary = []
        
        # 5時間のタイムリミット
        time_limit = 5 * 60 * 60  # 5時間
        
        for config_index, config in enumerate(configs):
            # 時間チェック
            elapsed_total = time.time() - total_start
            if elapsed_total >= time_limit:
                print(f"\n⏰ 5時間経過のためタイムアップ！")
                break
                
            print(f"\n{'='*80}")
            print(f"🎛️  カスタムノード {config_index+1}/20: {config['name']}")
            print(f"📝 説明: {config['description']}")
            print(f"⏰ 経過時間: {elapsed_total/3600:.1f}時間")
            print(f"⚙️  設定: {config['steps']} steps, CFG {config['cfg']}")
            print(f"{'='*80}")
            
            node_successful = 0
            node_start_time = time.time()
            
            # 各技法で5枚生成
            for img_index in range(5):
                # 時間チェック
                elapsed_total = time.time() - total_start
                if elapsed_total >= time_limit:
                    print(f"\n⏰ タイムアップのため生成終了")
                    break
                    
                print(f"\n📸 {config['name']} - 画像 {img_index+1}/5 ({elapsed_total/3600:.1f}h経過)")
                
                # ワークフロー作成
                workflow = self.create_custom_workflow(config, config_index * 5 + img_index)
                
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
                        node_successful += 1
                        total_successful += 1
                    else:
                        print(f"❌ Failed to copy {config['name']} image {img_index+1}")
                else:
                    print(f"❌ Generation failed for {config['name']} image {img_index+1}")
            
            node_time = time.time() - node_start_time
            node_avg = node_time / node_successful if node_successful > 0 else 0
            
            results_summary.append({
                'name': config['name'],
                'successful': node_successful,
                'total_time': node_time,
                'avg_per_image': node_avg,
                'description': config['description']
            })
            
            print(f"\n✅ {config['name']} 完了: {node_successful}/5 成功")
            print(f"⏱️  所要時間: {node_time:.1f}秒 (平均: {node_avg:.1f}秒/枚)")
        
        total_time = time.time() - total_start
        
        # 結果サマリー作成と保存
        summary_text = self.create_final_report(results_summary, total_successful, total_time)
        print(summary_text)
        
        # レポートをファイルに保存
        with open(f"{self.output_dir}/custom_nodes_comparison_report.txt", "w", encoding='utf-8') as f:
            f.write(summary_text)
        
        return results_summary
    
    def create_final_report(self, results_summary, total_successful, total_time):
        """最終レポート作成"""
        report = []
        report.append("=" * 80)
        report.append("🎉 20種類カスタムノード風技法比較完了!")
        report.append("=" * 80)
        report.append(f"✅ 総生成成功: {total_successful}/100 枚")
        report.append(f"⏱️  総所要時間: {total_time:.1f}秒 ({total_time/3600:.1f}時間)")
        if total_successful > 0:
            report.append(f"📊 平均生成時間: {total_time/total_successful:.1f}秒/枚")
        report.append(f"📁 出力先: {self.output_dir}")
        report.append(f"⏰ 完了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        report.append("📊 カスタムノード風技法別結果:")
        report.append("-" * 80)
        
        for result in results_summary:
            success_rate = (result['successful'] / 5) * 100
            report.append(f"{result['name']:35} | {result['successful']}/5 ({success_rate:3.0f}%) | {result['avg_per_image']:5.1f}s/枚 | {result['description']}")
        
        report.append("")
        report.append("📁 生成された画像は以下のディレクトリ構造で保存:")
        for result in results_summary:
            if result['successful'] > 0:
                report.append(f"  - {self.output_dir}/{result['name']}/")
        
        report.append("")
        report.append("🔍 比較評価のポイント:")
        report.append("1. 顔の詳細度と自然さ")
        report.append("2. 全体的な画質とシャープネス") 
        report.append("3. 肌質と質感の表現")
        report.append("4. 構図とポーズの自然さ")
        report.append("5. 背景とライティング")
        
        return "\n".join(report)

def main():
    generator = L4CustomNodesTest()
    
    # ComfyUIの接続確認
    try:
        response = requests.get(f"{generator.base_url}", timeout=10)
        print(f"✅ ComfyUI接続確認: {generator.base_url}")
    except Exception as e:
        print(f"❌ ComfyUI接続失敗: {generator.base_url}")
        print(f"エラー: {e}")
        return
    
    # 20種類カスタムノード風技法比較開始
    try:
        generator.generate_all_custom_node_tests()
    except KeyboardInterrupt:
        print("\n🛑 ユーザーによって中断されました")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
    
    print(f"\n🏁 プログラム終了: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()