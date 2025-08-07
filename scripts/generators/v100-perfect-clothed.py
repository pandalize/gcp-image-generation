#!/usr/bin/env python3
"""
V100 Perfect Clothed Portrait Generator
Natural poses with proper clothing and improved anatomy
"""

import requests
import json
import time
import yaml
import os
import sys
from datetime import datetime
import base64

class V100PerfectClothed:
    def __init__(self):
        self.server_ip = "34.70.230.62"
        self.port = 8188
        self.base_url = f"http://{self.server_ip}:{self.port}"
        self.output_dir = "/Users/fujinoyuki/Desktop/gcp/outputs/perfect_clothed"
        self.create_output_dir()
        
    def create_output_dir(self):
        """Create output directory if it doesn't exist."""
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Output directory: {self.output_dir}")
    
    def get_perfect_clothed_prompts(self):
        """Get prompts for perfectly clothed portraits."""
        return [
            {
                'positive': 'masterpiece, ultra high quality, photorealistic portrait, beautiful woman, full body standing pose, wearing elegant black dress, professional fashion photography, perfect anatomy, natural proportions, graceful posture, hands at sides in natural position, perfect fingers, studio lighting, soft shadows, detailed fabric texture, confident expression, 8k resolution',
                'negative': 'nude, naked, revealing clothing, bad anatomy, deformed body, wrong proportions, extra limbs, missing limbs, bad hands, extra fingers, missing fingers, fused fingers, malformed hands, floating limbs, disconnected limbs, cropped body, cut off, low quality, blurry, distorted face',
                'steps': 40,
                'cfg': 7.0,
                'width': 896,
                'height': 1152,
                'description': 'Elegant Black Dress Portrait'
            },
            {
                'positive': 'professional photograph, stunning woman, full body portrait, wearing stylish business suit, formal attire, standing confidently, perfect human anatomy, natural body proportions, hands clasped professionally, detailed clothing texture, office background, natural lighting, photorealistic quality, masterpiece, ultra detailed',
                'negative': 'nude, naked, inappropriate clothing, bad anatomy, deformed, disproportionate body, extra arms, extra legs, bad hands, malformed fingers, floating body parts, incomplete body, cropped limbs, low quality, blurry, amateur photography',
                'steps': 40,
                'cfg': 7.0,
                'width': 896,
                'height': 1152,
                'description': 'Professional Business Suit'
            },
            {
                'positive': 'fashion photography, beautiful model, full body shot, wearing casual summer dress, comfortable clothing, relaxed standing pose, perfect body structure, natural human proportions, arms hanging naturally, perfect hand anatomy, outdoor setting, golden hour lighting, photorealistic, high quality, detailed fabric',
                'negative': 'nude, naked, revealing outfit, bad anatomy, deformed body, wrong body proportions, extra limbs, bad hands, extra fingers, missing fingers, floating elements, cropped body, incomplete figure, low quality, distorted',
                'steps': 40,
                'cfg': 7.0,
                'width': 896,
                'height': 1152,
                'description': 'Casual Summer Dress'
            },
            {
                'positive': 'portrait photography, elegant woman, full body view, wearing long winter coat, sophisticated fashion, standing pose, correct human anatomy, well-proportioned figure, hands in coat pockets naturally, detailed clothing, urban background, soft natural lighting, ultra high quality, photorealistic masterpiece',
                'negative': 'nude, naked, inappropriate attire, bad anatomy, deformed proportions, extra body parts, missing limbs, malformed hands, bad fingers, floating limbs, cropped body, incomplete figure, low quality, blurry, distorted face',
                'steps': 40,
                'cfg': 7.0,
                'width': 896,
                'height': 1152,
                'description': 'Winter Coat Fashion'
            },
            {
                'positive': 'high fashion photography, beautiful woman, full body portrait, wearing designer jeans and elegant blouse, modern casual style, natural standing position, perfect anatomy, realistic body proportions, hands positioned naturally, detailed clothing texture, studio setting, professional lighting, masterpiece quality, ultra detailed',
                'negative': 'nude, naked, revealing clothes, bad anatomy, deformed body, wrong proportions, extra limbs, missing body parts, bad hands, malformed fingers, floating elements, cropped figure, incomplete body, low quality, amateur',
                'steps': 40,
                'cfg': 7.0,
                'width': 896,
                'height': 1152,
                'description': 'Modern Casual Style'
            }
        ]
    
    def create_perfect_workflow(self, prompt_data, index):
        """Create workflow for perfect clothed portraits."""
        
        positive = prompt_data.get('positive', '')
        negative = prompt_data.get('negative', '')
        steps = prompt_data.get('steps', 40)
        cfg = prompt_data.get('cfg', 7.0)
        width = prompt_data.get('width', 896)
        height = prompt_data.get('height', 1152)
        
        workflow = {
            "1": {
                "inputs": {
                    "ckpt_name": "juggernaut_xl_v10.safetensors"
                },
                "class_type": "CheckpointLoaderSimple",
                "_meta": {"title": "Load Juggernaut XL v10"}
            },
            "2": {
                "inputs": {
                    "width": width,
                    "height": height,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage",
                "_meta": {"title": "Perfect Portrait Ratio"}
            },
            "3": {
                "inputs": {
                    "text": positive,
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "Perfect Clothed Positive"}
            },
            "4": {
                "inputs": {
                    "text": negative,
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "Anti-Nude Negative"}
            },
            "5": {
                "inputs": {
                    "seed": int(time.time()) + index * 2000,
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
                "_meta": {"title": "Perfect Quality Sampler"}
            },
            "6": {
                "inputs": {
                    "samples": ["5", 0],
                    "vae": ["1", 2]
                },
                "class_type": "VAEDecode",
                "_meta": {"title": "High Quality Decode"}
            },
            "7": {
                "inputs": {
                    "filename_prefix": f"Perfect_Clothed_{index+1:03d}_",
                    "images": ["6", 0]
                },
                "class_type": "SaveImage",
                "_meta": {"title": "Save Perfect Portrait"}
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
    
    def wait_for_completion(self, prompt_id):
        """Wait for image generation to complete."""
        print(f"Generating perfect clothed portrait {prompt_id}...")
        start_time = time.time()
        
        while True:
            try:
                # Get queue status
                queue_response = requests.get(f"{self.base_url}/queue", timeout=10)
                if queue_response.status_code == 200:
                    queue_data = queue_response.json()
                    
                    # Check if our prompt is still in queue
                    running = [item[1] for item in queue_data.get('queue_running', [])]
                    pending = [item[1] for item in queue_data.get('queue_pending', [])]
                    
                    if prompt_id not in running and prompt_id not in pending:
                        elapsed = time.time() - start_time
                        print(f"Perfect portrait completed! ({elapsed:.1f}s)")
                        return True
                
                time.sleep(2)
                
            except Exception as e:
                print(f"Error checking queue: {e}")
                time.sleep(5)
    
    def download_image(self, filename, index):
        """Download generated image."""
        try:
            # Try to get the image
            url = f"{self.base_url}/view"
            params = {"filename": filename, "subfolder": "", "type": "output"}
            
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                # Save to local file
                local_filename = f"perfect_clothed_{index+1:02d}_{filename}"
                local_path = os.path.join(self.output_dir, local_filename)
                
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                
                file_size = len(response.content) / 1024  # KB
                print(f"Downloaded: {local_filename} ({file_size:.1f}KB)")
                return True
            else:
                print(f"Failed to download {filename}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error downloading {filename}: {e}")
            return False
    
    def generate_perfect_images(self):
        """Generate perfect clothed portrait images."""
        print("🎨 Starting Perfect Clothed Portrait Generation")
        print("👗 All subjects will be properly clothed")
        print("📐 Optimized anatomy and natural poses (896x1152)")
        print("=" * 60)
        
        prompts = self.get_perfect_clothed_prompts()
        print(f"Loaded {len(prompts)} perfect portrait prompts")
        
        total_start = time.time()
        successful_downloads = 0
        
        for i, prompt_data in enumerate(prompts):
            print(f"\n📸 Generating perfect portrait {i+1}/{len(prompts)}")
            print(f"Style: {prompt_data.get('description', '')}")
            print(f"Settings: {prompt_data.get('steps', 40)} steps, CFG {prompt_data.get('cfg', 7.0)}, {prompt_data.get('width', 896)}x{prompt_data.get('height', 1152)}")
            
            # Create workflow
            workflow = self.create_perfect_workflow(prompt_data, i)
            
            # Queue the prompt
            result = self.queue_prompt(workflow)
            if not result:
                print("Failed to queue prompt, skipping...")
                continue
            
            prompt_id = result.get('prompt_id')
            if not prompt_id:
                print("No prompt ID received, skipping...")
                continue
            
            # Wait for completion
            if self.wait_for_completion(prompt_id):
                # Give a moment for file to be written
                time.sleep(2)
                
                # Try to find and download the generated image
                expected_filename = f"Perfect_Clothed_{i+1:03d}__00001_.png"
                if self.download_image(expected_filename, i):
                    successful_downloads += 1
                else:
                    print(f"Failed to download image {i+1}")
            else:
                print(f"Generation failed for image {i+1}")
        
        total_time = time.time() - total_start
        
        print("\n" + "=" * 60)
        print("🎉 PERFECT CLOTHED PORTRAIT GENERATION COMPLETE!")
        print(f"✅ Successfully generated: {successful_downloads}/{len(prompts)} images")
        print(f"⏱️  Total time: {total_time:.1f} seconds")
        if successful_downloads > 0:
            print(f"📊 Average per image: {total_time/successful_downloads:.1f} seconds")
            total_size = sum(os.path.getsize(os.path.join(self.output_dir, f)) 
                           for f in os.listdir(self.output_dir) if f.endswith('.png'))
            print(f"📦 Total size: {total_size/1024:.1f}KB")
        print(f"📁 Output directory: {self.output_dir}")

def main():
    generator = V100PerfectClothed()
    generator.generate_perfect_images()

if __name__ == "__main__":
    main()