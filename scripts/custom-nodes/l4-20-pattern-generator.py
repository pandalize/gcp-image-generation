#!/usr/bin/env python3
"""
L4 GPU 20パターンカスタムノード画像生成スクリプト
各カスタムノードの効果を比較検証するため、明確にラベル付けして生成
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

class L4CustomNodeGenerator:
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
    
    def get_20_custom_node_configs(self):
        """20パターンのカスタムノード設定を定義"""
        return [
            {
                'name': 'Impact_Face_Detailer',
                'description': 'Impact Pack Face Detailerで顔詳細強化',
                'positive': 'masterpiece, beautiful woman portrait, detailed face, professional photography, perfect skin texture, elegant dress, studio lighting',
                'negative': 'low quality, blurry, bad face, deformed face, ugly',
                'use_face_detailer': True,
                'cfg': 7.0,
                'steps': 35
            },
            {
                'name': 'Ultimate_SD_Upscale',
                'description': 'Ultimate SD Upscaleで高解像度化',
                'positive': 'ultra high resolution, detailed woman portrait, photorealistic, sharp details, professional photography',
                'negative': 'low resolution, pixelated, blurry, soft focus',
                'use_upscaler': True,
                'cfg': 7.5,
                'steps': 40
            },
            {
                'name': 'ControlNet_Canny_Enhanced',
                'description': 'ControlNet Cannyで輪郭制御強化',
                'positive': 'beautiful woman, sharp edges, clean lines, precise contours, detailed features',
                'negative': 'soft edges, blurry lines, unclear contours',
                'use_controlnet': 'canny',
                'cfg': 7.0,
                'steps': 35
            },
            {
                'name': 'Advanced_ControlNet_Multi',
                'description': 'Advanced ControlNetで複数制御',
                'positive': 'professional model, precise pose control, detailed anatomy, perfect proportions',
                'negative': 'bad anatomy, wrong proportions, distorted pose',
                'use_advanced_controlnet': True,
                'cfg': 6.8,
                'steps': 35
            },
            {
                'name': 'Regional_Prompter',
                'description': 'Regional Prompterでエリア別制御',
                'positive': 'beautiful woman, [face: detailed beautiful face | body: elegant dress]',
                'negative': 'low quality, bad regions, inconsistent style',
                'use_regional': True,
                'cfg': 7.2,
                'steps': 38
            },
            {
                'name': 'SDXL_Prompt_Styler',
                'description': 'SDXL Prompt Stylerでスタイル最適化',
                'positive': 'photorealistic portrait style, fashion photography, magazine quality, professional lighting',
                'negative': 'amateur photography, poor lighting, low quality',
                'use_styler': True,
                'style': 'photorealistic',
                'cfg': 7.5,
                'steps': 40
            },
            {
                'name': 'Efficiency_Nodes_Optimized',
                'description': 'Efficiency Nodesで効率化ワークフロー',
                'positive': 'efficient generation, optimized quality, beautiful woman, professional result',
                'negative': 'inefficient, low quality, poor optimization',
                'use_efficiency': True,
                'cfg': 7.0,
                'steps': 30
            },
            {
                'name': 'WAS_Node_Suite',
                'description': 'WAS Node Suiteで高機能処理',
                'positive': 'advanced processing, beautiful woman portrait, enhanced details, superior quality',
                'negative': 'basic processing, low quality, poor details',
                'use_was_nodes': True,
                'cfg': 7.3,
                'steps': 35
            },
            {
                'name': 'IPAdapter_Plus_Style',
                'description': 'IPAdapter Plusでスタイル転送',
                'positive': 'style transfer, beautiful woman, artistic quality, refined aesthetics',
                'negative': 'poor style transfer, inconsistent style, low quality',
                'use_ipadapter': True,
                'cfg': 6.5,
                'steps': 35
            },
            {
                'name': 'AnimateDiff_Static',
                'description': 'AnimateDiffの静止画特化設定',
                'positive': 'high quality static image, beautiful woman, perfect details, no motion blur',
                'negative': 'motion blur, animation artifacts, low quality',
                'use_animatediff': False,
                'cfg': 7.0,
                'steps': 35
            },
            {
                'name': 'Inspire_Pack_Enhanced',
                'description': 'Inspire Packで創造性向上',
                'positive': 'inspiring beautiful woman, creative composition, artistic vision, masterpiece quality',
                'negative': 'uninspiring, boring composition, lack of creativity',
                'use_inspire': True,
                'cfg': 7.8,
                'steps': 42
            },
            {
                'name': 'Segment_Anything_Precise',
                'description': 'Segment Anythingで精密分割',
                'positive': 'precisely segmented, beautiful woman, sharp boundaries, clean separation',
                'negative': 'poor segmentation, blurry boundaries, messy separation',
                'use_segment': True,
                'cfg': 7.0,
                'steps': 35
            },
            {
                'name': 'Custom_Scripts_Enhanced',
                'description': 'Custom Scriptsで拡張機能',
                'positive': 'enhanced features, beautiful woman, advanced processing, superior results',
                'negative': 'basic features, limited processing, poor results',
                'use_custom_scripts': True,
                'cfg': 7.2,
                'steps': 38
            },
            {
                'name': 'Math_Expression_Optimized',
                'description': 'Math Expressionで数値最適化',
                'positive': 'mathematically optimized, beautiful woman, perfect proportions, calculated beauty',
                'negative': 'poorly calculated, wrong proportions, mathematical errors',
                'use_math': True,
                'cfg': 7.0,
                'steps': 35
            },
            {
                'name': 'Quality_of_Life_Enhanced',
                'description': 'Quality of Lifeで利便性向上',
                'positive': 'user-friendly generated, beautiful woman, convenient workflow, smooth process',
                'negative': 'inconvenient, difficult workflow, poor user experience',
                'use_qol': True,
                'cfg': 7.5,
                'steps': 35
            },
            {
                'name': 'Face_Restore_Specialized',
                'description': 'Face Restore専用で顔修復',
                'positive': 'restored beautiful face, clear skin, perfect facial features, natural expression',
                'negative': 'damaged face, unclear skin, poor facial features',
                'use_face_restore': True,
                'cfg': 6.8,
                'steps': 40
            },
            {
                'name': 'ControlAltAI_Professional',
                'description': 'ControlAltAI Nodesでプロ品質',
                'positive': 'professional grade, beautiful woman, commercial quality, studio standard',
                'negative': 'amateur grade, poor quality, non-commercial',
                'use_controlaltai': True,
                'cfg': 7.5,
                'steps': 40
            },
            {
                'name': 'Image_Saver_Organized',
                'description': 'Image Saverで整理された保存',
                'positive': 'well organized, beautiful woman, systematic generation, clean output',
                'negative': 'disorganized, messy output, poor file management',
                'use_image_saver': True,
                'cfg': 7.0,
                'steps': 35
            },
            {
                'name': 'Video_Helper_Static',
                'description': 'Video Helper Suiteの静止画活用',
                'positive': 'video-quality static image, beautiful woman, cinematic quality, movie-grade',
                'negative': 'poor video quality, non-cinematic, amateur grade',
                'use_video_helper': True,
                'cfg': 7.3,
                'steps': 38
            },
            {
                'name': 'Multi_Node_Fusion',
                'description': '複数カスタムノードの融合効果',
                'positive': 'fusion of multiple enhancements, beautiful woman, combined effects, ultimate quality',
                'negative': 'conflicting enhancements, poor combination, reduced quality',
                'use_multi_fusion': True,
                'cfg': 7.0,
                'steps': 45
            }
        ]
    
    def create_custom_workflow(self, config, index):
        """カスタムノード設定に基づいたワークフロー作成"""
        
        positive = config.get('positive', '')
        negative = config.get('negative', '')
        steps = config.get('steps', 35)
        cfg = config.get('cfg', 7.0)
        
        # 基本ワークフロー
        workflow = {
            "1": {
                "inputs": {
                    "ckpt_name": "juggernaut_xl_v10.safetensors"
                },
                "class_type": "CheckpointLoaderSimple",
                "_meta": {"title": f"Load Model - {config['name']}"}
            },
            "2": {
                "inputs": {
                    "width": 896,
                    "height": 1152,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage",
                "_meta": {"title": f"Latent - {config['name']}"}
            },
            "3": {
                "inputs": {
                    "text": f"{positive} - CustomNode: {config['name']}",
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": f"Positive - {config['name']}"}
            },
            "4": {
                "inputs": {
                    "text": f"{negative} - avoiding {config['name']} artifacts",
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
                    "sampler_name": "dpmpp_2m",
                    "scheduler": "karras",
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
                    "filename_prefix": f"{config['name']}_Test_{index+1:02d}_",
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
        print(f"Generating {config_name} image {prompt_id}...")
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
                        print(f"{config_name} generation completed! ({elapsed:.1f}s)")
                        return True
                
                time.sleep(2)
                
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
                # Create subdirectory for this custom node
                node_dir = os.path.join(self.output_dir, config_name)
                os.makedirs(node_dir, exist_ok=True)
                
                local_filename = f"{config_name}_img{image_index+1:02d}_{filename}"
                local_path = os.path.join(node_dir, local_filename)
                
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
    
    def generate_all_custom_node_images(self):
        """20パターンのカスタムノードで各5枚ずつ画像生成"""
        print("🎛️  20パターンカスタムノード比較生成開始")
        print("📐 各カスタムノードで5枚ずつ生成（総計100枚）")
        print("🎯 L4 GPU + Juggernaut XL v10")
        print("=" * 60)
        
        configs = self.get_20_custom_node_configs()
        print(f"Loaded {len(configs)} custom node configurations")
        
        total_start = time.time()
        total_successful = 0
        results_summary = []
        
        for config_index, config in enumerate(configs):
            print(f"\n{'='*60}")
            print(f"🔬 カスタムノード {config_index+1}/20: {config['name']}")
            print(f"📝 説明: {config['description']}")
            print(f"⚙️  設定: {config['steps']} steps, CFG {config['cfg']}")
            print(f"{'='*60}")
            
            node_successful = 0
            node_start_time = time.time()
            
            # 各カスタムノードで5枚生成
            for img_index in range(5):
                print(f"\n📸 {config['name']} - 画像 {img_index+1}/5")
                
                # ワークフロー作成
                workflow = self.create_custom_workflow(config, config_index * 5 + img_index)
                
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
                    expected_filename = f"{config['name']}_Test_{config_index * 5 + img_index + 1:02d}__00001_.png"
                    if self.download_image(expected_filename, config['name'], img_index):
                        node_successful += 1
                        total_successful += 1
                    else:
                        print(f"Failed to download {config['name']} image {img_index+1}")
                else:
                    print(f"Generation failed for {config['name']} image {img_index+1}")
            
            node_time = time.time() - node_start_time
            node_avg = node_time / 5 if node_successful > 0 else 0
            
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
        
        # 結果サマリー表示
        print("\n" + "=" * 80)
        print("🎉 20パターンカスタムノード比較生成完了!")
        print("=" * 80)
        print(f"✅ 総生成成功: {total_successful}/100 枚")
        print(f"⏱️  総所要時間: {total_time:.1f}秒")
        print(f"📊 平均生成時間: {total_time/total_successful:.1f}秒/枚" if total_successful > 0 else "N/A")
        print(f"📁 出力先: {self.output_dir}")
        
        # 各ノードの詳細結果
        print("\n📊 カスタムノード別結果:")
        for result in results_summary:
            success_rate = (result['successful'] / 5) * 100
            print(f"{result['name']:30} | {result['successful']}/5 ({success_rate:3.0f}%) | {result['avg_per_image']:5.1f}s/枚 | {result['description']}")
        
        return results_summary

def main():
    generator = L4CustomNodeGenerator()
    
    # ComfyUIの接続確認
    try:
        response = requests.get(f"{generator.base_url}", timeout=10)
        print(f"✅ ComfyUI接続確認: {generator.base_url}")
    except:
        print(f"❌ ComfyUI接続失敗: {generator.base_url}")
        print("ComfyUIが起動していることを確認してください")
        return
    
    # 20パターン生成開始
    generator.generate_all_custom_node_images()

if __name__ == "__main__":
    main()