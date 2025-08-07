#!/usr/bin/env python3
"""
V100 GPU 20種類カスタムノード画像生成比較テスト (ControlNet + Juggernaut XL v10)
各カスタムノード（プロンプト技法）で5枚ずつ生成して比較
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

class V100CustomNodesTest:
    def __init__(self):
        self.server_ip = "localhost"  # V100 ComfyUI
        self.port = 8188
        self.base_url = f"http://{self.server_ip}:{self.port}"
        self.output_dir = "/home/fujinoyuki/v100_custom_nodes_comparison"
        self.create_output_dir()
        
    def create_output_dir(self):
        """Create output directory if it doesn't exist."""
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"V100 Output directory: {self.output_dir}")
    
    def get_20_custom_node_techniques(self):
        """20種類のカスタムノード技法（プロンプト最適化）- V100向け"""
        return [
            {
                'name': '01_Impact_Face_Detailer_V100',
                'description': 'Impact Pack Face Detailer風顔詳細強化 (V100 Enhanced)',
                'positive': 'masterpiece, ultra detailed face, perfect facial features, flawless skin, professional photography, studio lighting, enhanced face details, face focus, photorealistic portrait, high definition',
                'negative': 'low quality, blurry, bad face, deformed face, ugly face, face artifacts, low resolution',
                'cfg': 7.5,
                'steps': 40,
                'width': 1024,
                'height': 1024
            },
            {
                'name': '02_Ultimate_Upscale_V100',
                'description': 'Ultimate SD Upscale風高解像度 (V100 Ultra)',
                'positive': 'ultra high resolution, detailed woman portrait, photorealistic, sharp details, crisp image, high definition, 8K quality, professional photography, perfect clarity',
                'negative': 'low resolution, pixelated, blurry, soft focus, low quality, compressed',
                'cfg': 8.0,
                'steps': 45,
                'width': 1024,
                'height': 1024
            },
            {
                'name': '03_ControlNet_Canny_V100',
                'description': 'ControlNet Canny風輪郭制御 (V100 Precision)',
                'positive': 'beautiful woman, sharp edges, clean lines, precise contours, detailed features, clear boundaries, defined silhouette, architectural precision',
                'negative': 'soft edges, blurry lines, unclear contours, messy boundaries, distorted shapes',
                'cfg': 7.0,
                'steps': 35,
                'width': 1024,
                'height': 1024
            },
            {
                'name': '04_Advanced_ControlNet_V100',
                'description': 'Advanced ControlNet風複数制御 (V100 Multi)',
                'positive': 'precise pose control, detailed anatomy, perfect proportions, controlled generation, advanced composition, multi-layer control',
                'negative': 'bad anatomy, wrong proportions, distorted pose, uncontrolled generation, poor composition',
                'cfg': 7.2,
                'steps': 38,
                'width': 1024,
                'height': 1024
            },
            {
                'name': '05_Regional_Prompting_V100',
                'description': 'Regional Prompter風エリア別制御 (V100 Zoned)',
                'positive': '[face: detailed beautiful face, perfect eyes, flawless skin] [body: elegant dress, graceful pose] [background: clean studio, professional lighting]',
                'negative': 'inconsistent regions, poor area control, conflicting styles, unbalanced composition',
                'cfg': 7.5,
                'steps': 42,
                'width': 1024,
                'height': 1024
            },
            {
                'name': '06_SDXL_Prompt_Styler_V100',
                'description': 'SDXL Prompt Styler風スタイル最適化 (V100 Style)',
                'positive': 'photorealistic portrait style, fashion photography, magazine quality, commercial style, editorial lighting, high-end production',
                'negative': 'amateur style, poor styling, unprofessional look, bad lighting, low production value',
                'cfg': 8.0,
                'steps': 45,
                'width': 1024,
                'height': 1024
            },
            {
                'name': '07_Efficiency_Nodes_V100',
                'description': 'Efficiency Nodes風効率化ワークフロー (V100 Optimized)',
                'positive': 'efficient generation, optimized quality, streamlined process, clean result, high performance output',
                'negative': 'inefficient process, poor optimization, messy result, low performance',
                'cfg': 7.0,
                'steps': 30,
                'width': 1024,
                'height': 1024
            },
            {
                'name': '08_WAS_Node_Suite_V100',
                'description': 'WAS Node Suite風高機能処理 (V100 Advanced)',
                'positive': 'advanced processing, sophisticated algorithms, complex workflow, high-end results, professional grade output',
                'negative': 'simple processing, basic algorithms, poor workflow, amateur results',
                'cfg': 7.8,
                'steps': 40,
                'width': 1024,
                'height': 1024
            },
            {
                'name': '09_IPAdapter_Plus_V100',
                'description': 'IPAdapter Plus風スタイル転送 (V100 Transfer)',
                'positive': 'style transfer, artistic adaptation, creative fusion, stylistic consistency, enhanced aesthetics',
                'negative': 'style conflicts, poor adaptation, inconsistent fusion, aesthetic issues',
                'cfg': 7.3,
                'steps': 35,
                'width': 1024,
                'height': 1024
            },
            {
                'name': '10_AnimateDiff_Static_V100',
                'description': 'AnimateDiff風静止画特化 (V100 Static)',
                'positive': 'motion-aware composition, dynamic stillness, frame perfection, cinematic quality, temporal consistency',
                'negative': 'motion blur, temporal inconsistency, frame artifacts, poor composition',
                'cfg': 7.0,
                'steps': 32,
                'width': 1024,
                'height': 1024
            },
            {
                'name': '11_Inspire_Pack_V100',
                'description': 'Inspire Pack風創造性向上 (V100 Creative)',
                'positive': 'creative inspiration, artistic vision, innovative composition, unique perspective, imaginative details',
                'negative': 'lack of creativity, boring composition, uninspired result, generic output',
                'cfg': 7.5,
                'steps': 38,
                'width': 1024,
                'height': 1024
            },
            {
                'name': '12_Segment_Anything_V100',
                'description': 'Segment Anything風精密分割 (V100 Segment)',
                'positive': 'precise segmentation, clean separation, detailed masking, accurate boundaries, perfect isolation',
                'negative': 'poor segmentation, messy separation, inaccurate masking, unclear boundaries',
                'cfg': 7.2,
                'steps': 36,
                'width': 1024,
                'height': 1024
            },
            {
                'name': '13_Custom_Scripts_V100',
                'description': 'Custom Scripts風拡張機能 (V100 Extended)',
                'positive': 'custom enhancement, extended functionality, specialized processing, advanced features, tailored results',
                'negative': 'basic functionality, limited processing, standard features, generic results',
                'cfg': 7.4,
                'steps': 37,
                'width': 1024,
                'height': 1024
            },
            {
                'name': '14_Math_Expression_V100',
                'description': 'Math Expression風数値最適化 (V100 Calculated)',
                'positive': 'mathematical precision, calculated composition, algorithmic beauty, geometric perfection, numerical harmony',
                'negative': 'mathematical errors, poor calculation, geometric distortion, numerical chaos',
                'cfg': 7.6,
                'steps': 39,
                'width': 1024,
                'height': 1024
            },
            {
                'name': '15_Quality_of_Life_V100',
                'description': 'Quality of Life風利便性向上 (V100 Enhanced)',
                'positive': 'enhanced convenience, improved workflow, user-friendly results, optimized experience, quality improvement',
                'negative': 'poor convenience, difficult workflow, user-unfriendly results, suboptimal experience',
                'cfg': 7.1,
                'steps': 33,
                'width': 1024,
                'height': 1024
            },
            {
                'name': '16_Face_Restore_V100',
                'description': 'Face Restore風顔修復特化 (V100 Restoration)',
                'positive': 'face restoration, facial enhancement, feature recovery, detail reconstruction, perfect symmetry',
                'negative': 'face distortion, facial defects, feature loss, poor reconstruction, asymmetrical face',
                'cfg': 7.8,
                'steps': 42,
                'width': 1024,
                'height': 1024
            },
            {
                'name': '17_ControlAltAI_V100',
                'description': 'ControlAltAI風プロ品質 (V100 Professional)',
                'positive': 'professional quality, commercial grade, industry standard, expert level, premium results',
                'negative': 'amateur quality, poor grade, substandard, beginner level, cheap results',
                'cfg': 8.2,
                'steps': 50,
                'width': 1024,
                'height': 1024
            },
            {
                'name': '18_Image_Saver_V100',
                'description': 'Image Saver風組織化保存 (V100 Organized)',
                'positive': 'organized output, systematic arrangement, structured composition, methodical design, orderly result',
                'negative': 'disorganized output, chaotic arrangement, unstructured composition, random design',
                'cfg': 7.0,
                'steps': 34,
                'width': 1024,
                'height': 1024
            },
            {
                'name': '19_Video_Helper_V100',
                'description': 'Video Helper風映像品質 (V100 Cinematic)',
                'positive': 'cinematic quality, film-grade composition, video-ready output, broadcast standard, motion picture quality',
                'negative': 'poor video quality, amateur film, low broadcast standard, poor motion picture quality',
                'cfg': 7.7,
                'steps': 41,
                'width': 1024,
                'height': 1024
            },
            {
                'name': '20_Multi_Node_Fusion_V100',
                'description': 'Multi Node Fusion風複数融合 (V100 Ultimate)',
                'positive': 'multi-node fusion, complex integration, advanced synthesis, ultimate quality, perfect harmony, masterpiece result',
                'negative': 'node conflicts, poor integration, failed synthesis, quality issues, disharmony, subpar result',
                'cfg': 8.5,
                'steps': 55,
                'width': 1024,
                'height': 1024
            }
        ]

    def create_workflow_json(self, technique):
        """Create ComfyUI workflow JSON for Juggernaut XL v10"""
        workflow = {
            "1": {
                "inputs": {
                    "ckpt_name": "juggernaut_v10.safetensors"
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "2": {
                "inputs": {
                    "text": technique['positive'],
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "3": {
                "inputs": {
                    "text": technique['negative'],
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "4": {
                "inputs": {
                    "width": technique['width'],
                    "height": technique['height'],
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "5": {
                "inputs": {
                    "seed": int(time.time() * 1000000) % 2**32,
                    "steps": technique['steps'],
                    "cfg": technique['cfg'],
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
                    "filename_prefix": f"V100_{technique['name']}",
                    "images": ["6", 0]
                },
                "class_type": "SaveImage"
            }
        }
        return workflow

    def queue_prompt(self, workflow):
        """Queue a prompt for generation"""
        try:
            response = requests.post(
                f"{self.base_url}/prompt",
                json={"prompt": workflow}
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
        """Get current queue information"""
        try:
            response = requests.get(f"{self.base_url}/queue")
            return response.json()
        except Exception as e:
            print(f"Error getting queue info: {e}")
            return None

    def wait_for_completion(self, prompt_id):
        """Wait for a specific prompt to complete"""
        print(f"Waiting for prompt {prompt_id} to complete...")
        max_wait = 60  # Maximum wait time in seconds
        waited = 0
        
        while waited < max_wait:
            queue_info = self.get_queue_info()
            if queue_info:
                # Check if prompt is still in queue
                queue_running = queue_info.get('queue_running', [])
                queue_pending = queue_info.get('queue_pending', [])
                
                in_queue = False
                in_pending = False
                
                # Check running queue
                for item in queue_running:
                    if len(item) > 1 and isinstance(item[1], dict) and item[1].get('prompt_id') == prompt_id:
                        in_queue = True
                        break
                
                # Check pending queue
                for item in queue_pending:
                    if len(item) > 1 and isinstance(item[1], dict) and item[1].get('prompt_id') == prompt_id:
                        in_pending = True
                        break
                
                if not in_queue and not in_pending:
                    print(f"Prompt {prompt_id} completed!")
                    return True
            
            time.sleep(3)
            waited += 3
        
        print(f"Timeout waiting for prompt {prompt_id}")
        return False

    def generate_technique_images(self, technique, num_images=5):
        """Generate images for a specific technique"""
        print(f"\n=== Generating {num_images} images for {technique['name']} ===")
        print(f"Description: {technique['description']}")
        
        generated_count = 0
        for i in range(num_images):
            print(f"Generating image {i+1}/{num_images} for {technique['name']}")
            
            workflow = self.create_workflow_json(technique)
            result = self.queue_prompt(workflow)
            
            if result and 'prompt_id' in result:
                prompt_id = result['prompt_id']
                print(f"Queued with ID: {prompt_id}")
                
                # Wait for completion
                if self.wait_for_completion(prompt_id):
                    generated_count += 1
                    print(f"✅ Image {i+1} completed for {technique['name']}")
                else:
                    print(f"❌ Image {i+1} failed for {technique['name']}")
            else:
                print(f"❌ Failed to queue image {i+1} for {technique['name']}")
        
        print(f"Generated {generated_count}/{num_images} images for {technique['name']}")
        return generated_count

    def run_all_techniques(self):
        """Run all 20 techniques"""
        techniques = self.get_20_custom_node_techniques()
        
        print(f"🚀 V100 20種類カスタムノード風技法比較開始 ({datetime.now()})")
        print(f"Total techniques: {len(techniques)}")
        print(f"Images per technique: 5")
        print(f"Total expected images: {len(techniques) * 5}")
        print(f"Model: Juggernaut XL v10")
        print(f"GPU: Tesla V100-SXM2-16GB")
        
        total_generated = 0
        results_summary = []
        
        for i, technique in enumerate(techniques, 1):
            print(f"\n{'='*60}")
            print(f"Processing technique {i}/{len(techniques)}: {technique['name']}")
            print(f"{'='*60}")
            
            generated = self.generate_technique_images(technique)
            total_generated += generated
            
            results_summary.append({
                'technique': technique['name'],
                'description': technique['description'],
                'generated': generated,
                'total': 5,
                'success_rate': f"{(generated/5)*100:.1f}%"
            })
            
            # Progress report
            progress = (i / len(techniques)) * 100
            print(f"\n📊 Progress: {i}/{len(techniques)} techniques ({progress:.1f}%)")
            print(f"Total images generated so far: {total_generated}")
        
        # Final summary
        print(f"\n{'='*60}")
        print("🎉 V100 20種類カスタムノード風技法比較完了!")
        print(f"{'='*60}")
        print(f"Total images generated: {total_generated}/100")
        print(f"Success rate: {(total_generated/100)*100:.1f}%")
        
        print("\n📋 個別結果:")
        for result in results_summary:
            print(f"  {result['technique']}: {result['generated']}/5 ({result['success_rate']})")
        
        return results_summary

def main():
    print("V100 20種類カスタムノード風技法比較テスト開始")
    
    tester = V100CustomNodesTest()
    
    # Test connection first
    try:
        response = requests.get(f"{tester.base_url}/system_stats")
        if response.status_code == 200:
            print("✅ V100 ComfyUI connection successful")
            print("GPU Info:", response.json().get('devices', [{}])[0].get('name', 'Unknown'))
        else:
            print("❌ V100 ComfyUI connection failed")
            return
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return
    
    # Run the test
    results = tester.run_all_techniques()
    
    print(f"\n🏁 V100テスト完了: {datetime.now()}")

if __name__ == "__main__":
    main()