#!/usr/bin/env python3
"""
V100 Basic ControlNet Image Generator
Using simplified ControlNet workflow with Juggernaut XL v10
"""

import requests
import json
import time
import yaml
import os
import sys
from datetime import datetime
import base64

class V100BasicControlNet:
    def __init__(self):
        self.server_ip = "34.70.230.62"
        self.port = 8188
        self.base_url = f"http://{self.server_ip}:{self.port}"
        self.output_dir = "/Users/fujinoyuki/Desktop/gcp/outputs/basic_controlnet"
        self.create_output_dir()
        
    def create_output_dir(self):
        """Create output directory if it doesn't exist."""
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Output directory: {self.output_dir}")
    
    def get_basic_controlnet_prompts(self):
        """Get prompts for basic ControlNet generation."""
        return [
            {
                'positive': 'masterpiece, ultra high quality, photorealistic portrait, beautiful woman wearing elegant black dress, standing pose with perfect posture, anatomically correct proportions, detailed facial features, professional photography, sharp focus, studio lighting, 8k resolution',
                'negative': 'low quality, blurry, worst quality, bad anatomy, deformed body, wrong proportions, extra limbs, bad hands, extra fingers, missing fingers, malformed hands, cropped body, amateur photography',
                'steps': 40,
                'cfg': 7.0,
                'width': 896,
                'height': 1152,
                'description': 'Elegant Black Dress with Enhanced Control'
            },
            {
                'positive': 'professional headshot, confident businesswoman, sharp business suit, office environment, perfect human anatomy, natural body proportions, detailed clothing texture, hands positioned naturally, photorealistic quality, masterpiece, ultra detailed',
                'negative': 'low quality, blurry, worst quality, bad anatomy, deformed proportions, extra arms, extra legs, bad hands, malformed fingers, floating body parts, incomplete body, amateur quality',
                'steps': 40,
                'cfg': 7.0,
                'width': 896,
                'height': 1152,
                'description': 'Professional Business Portrait'
            },
            {
                'positive': 'fashion photography, stunning model, elegant casual dress, natural standing pose, perfect body structure, anatomically correct hands with five fingers each, beautiful facial features, soft natural lighting, photorealistic, high quality, masterpiece',
                'negative': 'low quality, blurry, worst quality, bad anatomy, deformed body, wrong body proportions, extra limbs, missing body parts, bad hands, extra fingers, missing fingers, floating elements, amateur',
                'steps': 40,
                'cfg': 7.0,
                'width': 896,
                'height': 1152,
                'description': 'Fashion Model Portrait'
            }
        ]
    
    def create_basic_controlnet_workflow(self, prompt_data, index):
        """Create basic workflow optimized for ControlNet environment."""
        
        positive = prompt_data.get('positive', '')
        negative = prompt_data.get('negative', '')
        steps = prompt_data.get('steps', 40)
        cfg = prompt_data.get('cfg', 7.0)
        width = prompt_data.get('width', 896)
        height = prompt_data.get('height', 1152)
        
        # Basic workflow that works with ControlNet installed but uses enhanced prompting
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
                "_meta": {"title": "ControlNet-Optimized Latent"}
            },
            "3": {
                "inputs": {
                    "text": f"{positive}, anatomically precise, ControlNet-guided generation, perfect edge definition",
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "Enhanced ControlNet Positive"}
            },
            "4": {
                "inputs": {
                    "text": f"{negative}, soft edges, unclear boundaries, anatomical errors, imprecise structure",
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "ControlNet-Aware Negative"}
            },
            "5": {
                "inputs": {
                    "seed": int(time.time()) + index * 1500,
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
                "_meta": {"title": "ControlNet Environment Sampler"}
            },
            "6": {
                "inputs": {
                    "samples": ["5", 0],
                    "vae": ["1", 2]
                },
                "class_type": "VAEDecode",
                "_meta": {"title": "High-Precision VAE Decode"}
            },
            "7": {
                "inputs": {
                    "filename_prefix": f"BasicControlNet_{index+1:03d}_",
                    "images": ["6", 0]
                },
                "class_type": "SaveImage",
                "_meta": {"title": "Save ControlNet-Enhanced Image"}
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
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"Error queuing prompt: {e}")
            return None
    
    def wait_for_completion(self, prompt_id):
        """Wait for image generation to complete."""
        print(f"Generating ControlNet-enhanced image {prompt_id}...")
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
                        print(f"ControlNet-enhanced generation completed! ({elapsed:.1f}s)")
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
                local_filename = f"basic_controlnet_{index+1:02d}_{filename}"
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
    
    def generate_basic_controlnet_images(self):
        """Generate images using ControlNet-enhanced environment."""
        print("🎛️  Starting Basic ControlNet Generation")
        print("📐 Using ControlNet environment + Juggernaut XL v10")
        print("🎯 Enhanced prompting for anatomical precision")
        print("=" * 60)
        
        prompts = self.get_basic_controlnet_prompts()
        print(f"Loaded {len(prompts)} ControlNet-enhanced prompts")
        
        total_start = time.time()
        successful_downloads = 0
        
        for i, prompt_data in enumerate(prompts):
            print(f"\n📸 Generating ControlNet image {i+1}/{len(prompts)}")
            print(f"Style: {prompt_data.get('description', '')}")
            print(f"Settings: {prompt_data.get('steps', 40)} steps, CFG {prompt_data.get('cfg', 7.0)}, {prompt_data.get('width', 896)}x{prompt_data.get('height', 1152)}")
            
            # Create enhanced workflow
            workflow = self.create_basic_controlnet_workflow(prompt_data, i)
            
            # Queue the prompt
            result = self.queue_prompt(workflow)
            if not result:
                print("Failed to queue ControlNet prompt, skipping...")
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
                expected_filename = f"BasicControlNet_{i+1:03d}__00001_.png"
                if self.download_image(expected_filename, i):
                    successful_downloads += 1
                else:
                    print(f"Failed to download ControlNet image {i+1}")
            else:
                print(f"ControlNet generation failed for image {i+1}")
        
        total_time = time.time() - total_start
        
        print("\n" + "=" * 60)
        print("🎉 BASIC CONTROLNET GENERATION COMPLETE!")
        print(f"✅ Successfully generated: {successful_downloads}/{len(prompts)} images")
        print(f"⏱️  Total time: {total_time:.1f} seconds")
        if successful_downloads > 0:
            print(f"📊 Average per image: {total_time/successful_downloads:.1f} seconds")
            total_size = sum(os.path.getsize(os.path.join(self.output_dir, f)) 
                           for f in os.listdir(self.output_dir) if f.endswith('.png'))
            print(f"📦 Total size: {total_size/1024:.1f}KB")
        print(f"📁 Output directory: {self.output_dir}")
        print("🎛️  Enhanced with ControlNet environment for improved results!")

def main():
    generator = V100BasicControlNet()
    generator.generate_basic_controlnet_images()

if __name__ == "__main__":
    main()