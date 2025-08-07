#!/usr/bin/env python3
"""
V100 Ultra Quality Image Generator
Juggernaut XL v10 with 1536x1536, 40 steps, optimized quality settings
"""

import requests
import json
import time
import yaml
import os
import sys
from datetime import datetime
import base64

class V100UltraQuality:
    def __init__(self):
        self.server_ip = "34.70.230.62"
        self.port = 8188
        self.base_url = f"http://{self.server_ip}:{self.port}"
        self.prompts_file = "/Users/fujinoyuki/Desktop/gcp/prompts.yaml"
        self.output_dir = "/Users/fujinoyuki/Desktop/gcp/outputs/ultra_quality"
        self.create_output_dir()
        
    def create_output_dir(self):
        """Create output directory if it doesn't exist."""
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Output directory: {self.output_dir}")
    
    def load_prompts(self):
        """Load prompts from YAML file."""
        try:
            with open(self.prompts_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data['prompts']
        except Exception as e:
            print(f"Error loading prompts: {e}")
            return []
    
    def create_workflow(self, prompt_data, index):
        """Create workflow JSON for ultra-quality generation."""
        
        positive = prompt_data.get('positive', 'beautiful woman')
        negative = prompt_data.get('negative', 'low quality, bad anatomy')
        steps = prompt_data.get('steps', 40)
        cfg = prompt_data.get('cfg', 8.0)
        width = prompt_data.get('width', 1536)
        height = prompt_data.get('height', 1536)
        
        workflow = {
            "1": {
                "inputs": {
                    "ckpt_name": "juggernaut_xl_v10.safetensors"
                },
                "class_type": "CheckpointLoaderSimple",
                "_meta": {"title": "Load Checkpoint"}
            },
            "2": {
                "inputs": {
                    "width": width,
                    "height": height,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage",
                "_meta": {"title": "Empty Latent Image"}
            },
            "3": {
                "inputs": {
                    "text": positive,
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "CLIP Text Encode (Prompt)"}
            },
            "4": {
                "inputs": {
                    "text": negative,
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "CLIP Text Encode (Negative)"}
            },
            "5": {
                "inputs": {
                    "seed": int(time.time()) + index,
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
                "_meta": {"title": "KSampler"}
            },
            "6": {
                "inputs": {
                    "samples": ["5", 0],
                    "vae": ["1", 2]
                },
                "class_type": "VAEDecode",
                "_meta": {"title": "VAE Decode"}
            },
            "7": {
                "inputs": {
                    "filename_prefix": f"Ultra_Quality_{index+1:05d}_",
                    "images": ["6", 0]
                },
                "class_type": "SaveImage",
                "_meta": {"title": "Save Image"}
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
        print(f"Waiting for completion of prompt {prompt_id}...")
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
                        print(f"Generation completed! ({elapsed:.1f}s)")
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
                local_filename = f"ultra_quality_{index+1:02d}_{filename}"
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
    
    def get_generated_images(self):
        """Get list of generated images from server."""
        try:
            response = requests.get(f"{self.base_url}/view", timeout=10)
            if response.status_code == 200:
                return response.json()
            return []
        except:
            return []
    
    def generate_ultra_quality_images(self):
        """Generate all ultra-quality images from prompts.yaml."""
        print("🎨 Starting Ultra Quality Generation (1536x1536, 40 steps)")
        print("=" * 60)
        
        prompts = self.load_prompts()
        if not prompts:
            print("No prompts found!")
            return
        
        print(f"Loaded {len(prompts)} prompts")
        
        total_start = time.time()
        successful_downloads = 0
        
        for i, prompt_data in enumerate(prompts):
            print(f"\n📸 Generating image {i+1}/{len(prompts)}")
            print(f"Prompt: {prompt_data.get('positive', '')[:50]}...")
            print(f"Settings: {prompt_data.get('steps', 40)} steps, CFG {prompt_data.get('cfg', 8.0)}, {prompt_data.get('width', 1536)}x{prompt_data.get('height', 1536)}")
            
            # Create workflow
            workflow = self.create_workflow(prompt_data, i)
            
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
                # The filename should match the prefix pattern
                expected_filename = f"Ultra_Quality_{i+1:05d}__00001_.png"
                if self.download_image(expected_filename, i):
                    successful_downloads += 1
                else:
                    print(f"Failed to download image {i+1}")
            else:
                print(f"Generation failed for image {i+1}")
        
        total_time = time.time() - total_start
        
        print("\n" + "=" * 60)
        print("🎉 ULTRA QUALITY GENERATION COMPLETE!")
        print(f"✅ Successfully generated: {successful_downloads}/{len(prompts)} images")
        print(f"⏱️  Total time: {total_time:.1f} seconds")
        if successful_downloads > 0:
            print(f"📊 Average per image: {total_time/successful_downloads:.1f} seconds")
            total_size = sum(os.path.getsize(os.path.join(self.output_dir, f)) 
                           for f in os.listdir(self.output_dir) if f.endswith('.png'))
            print(f"📦 Total size: {total_size/1024:.1f}KB")
        print(f"📁 Output directory: {self.output_dir}")

def main():
    generator = V100UltraQuality()
    generator.generate_ultra_quality_images()

if __name__ == "__main__":
    main()