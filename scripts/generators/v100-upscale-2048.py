#!/usr/bin/env python3
"""
V100 High-Resolution Upscale Generator
Upscale images from 1536x1536 to 2048x2048 for maximum quality
"""

import requests
import json
import time
import yaml
import os
import sys
from datetime import datetime
import base64

class V100Upscale2048:
    def __init__(self):
        self.server_ip = "34.70.230.62"
        self.port = 8188
        self.base_url = f"http://{self.server_ip}:{self.port}"
        self.output_dir = "/Users/fujinoyuki/Desktop/gcp/outputs/upscale_2048"
        self.create_output_dir()
        
    def create_output_dir(self):
        """Create output directory if it doesn't exist."""
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Output directory: {self.output_dir}")
    
    def get_upscale_prompts(self):
        """Get prompts for 2048px upscale generation."""
        return [
            {
                'positive': '8K resolution, ultra high quality, masterpiece, photorealistic, beautiful woman, elegant pose, full body portrait, professional photography, detailed skin texture, perfect anatomy, detailed hands with perfect fingers, studio lighting, sharp focus, hyper detailed, crisp image quality',
                'negative': 'low quality, blurry, worst quality, bad anatomy, deformed, ugly, distorted face, bad hands, missing fingers, extra fingers, amateur, low resolution, pixelated, artifacts, compression artifacts, jpeg artifacts, noise',
                'steps': 45,
                'cfg': 8.5,
                'width': 2048,
                'height': 2048,
                'description': 'Ultra High Resolution Portrait'
            },
            {
                'positive': '2048px, ultra detailed, hyperrealistic, stunning fashion model, dynamic pose, full body shot, perfect proportions, detailed facial features, beautiful hands with elegant fingers, high fashion photography, dramatic lighting, magazine quality, 8K masterpiece, crystal clear',
                'negative': 'low quality, blurry, worst quality, bad anatomy, deformed, ugly, distorted face, bad hands, missing fingers, extra fingers, amateur, cartoon, anime, painting, compression, artifacts',
                'steps': 45,
                'cfg': 8.5,
                'width': 2048,
                'height': 2048,
                'description': 'High Fashion Ultra Resolution'
            },
            {
                'positive': '8K quality, photorealistic masterpiece, natural beauty, outdoor portrait, golden hour lighting, full body composition, hands naturally positioned with perfect finger detail, professional model, ultra high resolution, detailed skin, tack sharp focus, cinematic quality, pristine image',
                'negative': 'low quality, blurry, worst quality, bad anatomy, deformed, ugly, distorted face, bad hands, missing fingers, extra fingers, amateur, overexposed, underexposed, noise, grain, artifacts',
                'steps': 45,
                'cfg': 8.5,
                'width': 2048,
                'height': 2048,
                'description': 'Natural Ultra High Resolution'
            }
        ]
    
    def create_upscale_workflow(self, prompt_data, index):
        """Create high-resolution upscale workflow."""
        
        positive = prompt_data.get('positive', '')
        negative = prompt_data.get('negative', '')
        steps = prompt_data.get('steps', 45)
        cfg = prompt_data.get('cfg', 8.5)
        width = prompt_data.get('width', 2048)
        height = prompt_data.get('height', 2048)
        
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
                "_meta": {"title": "Ultra High Resolution Latent"}
            },
            "3": {
                "inputs": {
                    "text": positive,
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "High Quality Positive"}
            },
            "4": {
                "inputs": {
                    "text": negative,
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "Anti-Artifact Negative"}
            },
            "5": {
                "inputs": {
                    "seed": int(time.time()) + index * 2000,
                    "steps": steps,
                    "cfg": cfg,
                    "sampler_name": "dpmpp_2m_sde",
                    "scheduler": "karras",
                    "denoise": 1,
                    "model": ["1", 0],
                    "positive": ["3", 0],
                    "negative": ["4", 0],
                    "latent_image": ["2", 0]
                },
                "class_type": "KSampler",
                "_meta": {"title": "Ultra Quality Sampler"}
            },
            "6": {
                "inputs": {
                    "samples": ["5", 0],
                    "vae": ["1", 2]
                },
                "class_type": "VAEDecode",
                "_meta": {"title": "High-Res VAE Decode"}
            },
            "7": {
                "inputs": {
                    "filename_prefix": f"Upscale_2048_{index+1:03d}_",
                    "images": ["6", 0]
                },
                "class_type": "SaveImage",
                "_meta": {"title": "Save 2048px Image"}
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
        print(f"Waiting for 2048px generation of prompt {prompt_id}...")
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
                        print(f"2048px generation completed! ({elapsed:.1f}s)")
                        return True
                
                time.sleep(3)
                
            except Exception as e:
                print(f"Error checking queue: {e}")
                time.sleep(5)
    
    def download_image(self, filename, index):
        """Download generated image."""
        try:
            # Try to get the image
            url = f"{self.base_url}/view"
            params = {"filename": filename, "subfolder": "", "type": "output"}
            
            response = requests.get(url, params=params, timeout=60)
            if response.status_code == 200:
                # Save to local file
                local_filename = f"upscale_2048_{index+1:02d}_{filename}"
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
    
    def generate_upscale_images(self):
        """Generate 2048px upscaled images."""
        print("🎨 Starting 2048px Upscale Generation")
        print("=" * 60)
        
        prompts = self.get_upscale_prompts()
        print(f"Loaded {len(prompts)} upscale prompts")
        
        total_start = time.time()
        successful_downloads = 0
        
        for i, prompt_data in enumerate(prompts):
            print(f"\n📸 Generating 2048px image {i+1}/{len(prompts)}")
            print(f"Description: {prompt_data.get('description', '')}")
            print(f"Settings: {prompt_data.get('steps', 45)} steps, CFG {prompt_data.get('cfg', 8.5)}, {prompt_data.get('width', 2048)}x{prompt_data.get('height', 2048)}")
            
            # Create workflow
            workflow = self.create_upscale_workflow(prompt_data, i)
            
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
                # Give extra time for large file to be written
                time.sleep(3)
                
                # Try to find and download the generated image
                expected_filename = f"Upscale_2048_{i+1:03d}__00001_.png"
                if self.download_image(expected_filename, i):
                    successful_downloads += 1
                else:
                    print(f"Failed to download image {i+1}")
            else:
                print(f"Generation failed for image {i+1}")
        
        total_time = time.time() - total_start
        
        print("\n" + "=" * 60)
        print("🎉 2048PX UPSCALE GENERATION COMPLETE!")
        print(f"✅ Successfully generated: {successful_downloads}/{len(prompts)} images")
        print(f"⏱️  Total time: {total_time:.1f} seconds")
        if successful_downloads > 0:
            print(f"📊 Average per image: {total_time/successful_downloads:.1f} seconds")
            total_size = sum(os.path.getsize(os.path.join(self.output_dir, f)) 
                           for f in os.listdir(self.output_dir) if f.endswith('.png'))
            print(f"📦 Total size: {total_size/1024:.1f}KB")
        print(f"📁 Output directory: {self.output_dir}")

def main():
    generator = V100Upscale2048()
    generator.generate_upscale_images()

if __name__ == "__main__":
    main()