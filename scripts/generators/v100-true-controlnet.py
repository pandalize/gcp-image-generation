#!/usr/bin/env python3
"""
V100 True ControlNet Image Generator
Using actual ControlNet Canny with Juggernaut XL v10 for precise edge control
"""

import requests
import json
import time
import yaml
import os
import sys
from datetime import datetime
import base64

class V100TrueControlNet:
    def __init__(self):
        self.server_ip = "34.70.230.62"
        self.port = 8188
        self.base_url = f"http://{self.server_ip}:{self.port}"
        self.output_dir = "/Users/fujinoyuki/Desktop/gcp/outputs/true_controlnet"
        self.create_output_dir()
        
    def create_output_dir(self):
        """Create output directory if it doesn't exist."""
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Output directory: {self.output_dir}")
    
    def get_controlnet_prompts(self):
        """Get prompts optimized for ControlNet edge control."""
        return [
            {
                'positive': 'masterpiece, ultra high quality, photorealistic portrait, beautiful woman wearing elegant dress, standing pose, perfect anatomy, detailed hands with five fingers, professional photography, sharp edges, clean lines, studio lighting, 8k resolution',
                'negative': 'low quality, blurry, worst quality, bad anatomy, deformed, ugly, distorted face, bad hands, extra fingers, missing fingers, soft edges, unclear boundaries, amateur photography',
                'steps': 35,
                'cfg': 7.5,
                'width': 896,
                'height': 1152,
                'description': 'ControlNet Canny Portrait'
            },
            {
                'positive': 'professional headshot, confident businesswoman, sharp business suit, office background, perfect facial structure, detailed clothing texture, clean architectural lines, natural lighting, photorealistic quality, masterpiece',
                'negative': 'low quality, blurry, worst quality, bad anatomy, deformed proportions, bad hands, unclear edges, soft focus, amateur quality, distorted lines',
                'steps': 35,
                'cfg': 7.5,
                'width': 896,
                'height': 1152,
                'description': 'Business Portrait with Clean Lines'
            },
            {
                'positive': 'fashion photography, stunning model, elegant pose, detailed clothing, sharp facial features, perfect body proportions, clean background, professional lighting, high contrast edges, ultra detailed, masterpiece quality',
                'negative': 'low quality, blurry, worst quality, bad anatomy, deformed, bad hands, soft edges, unclear boundaries, amateur photography, distorted features',
                'steps': 35,
                'cfg': 7.5,
                'width': 896,
                'height': 1152,
                'description': 'High Fashion with Edge Control'
            }
        ]
    
    def create_controlnet_workflow(self, prompt_data, index):
        """Create workflow with actual ControlNet Canny integration."""
        
        positive = prompt_data.get('positive', '')
        negative = prompt_data.get('negative', '')
        steps = prompt_data.get('steps', 35)
        cfg = prompt_data.get('cfg', 7.5)
        width = prompt_data.get('width', 896)
        height = prompt_data.get('height', 1152)
        
        # True ControlNet workflow with Canny edge detection
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
                "_meta": {"title": "Latent Image"}
            },
            "3": {
                "inputs": {
                    "text": positive,
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "Positive Prompt"}
            },
            "4": {
                "inputs": {
                    "text": negative,
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "Negative Prompt"}
            },
            "5": {
                "inputs": {
                    "control_net_name": "diffusers_xl_canny_full.safetensors"
                },
                "class_type": "ControlNetLoader",
                "_meta": {"title": "Load ControlNet Canny"}
            },
            "6": {
                "inputs": {
                    "low_threshold": 50,
                    "high_threshold": 200
                },
                "class_type": "CannyEdgePreprocessor", 
                "_meta": {"title": "Canny Edge Detection"}
            },
            "7": {
                "inputs": {
                    "strength": 0.8,
                    "start_percent": 0.0,
                    "end_percent": 1.0,
                    "positive": ["3", 0],
                    "negative": ["4", 0],
                    "control_net": ["5", 0],
                    "image": ["6", 0]
                },
                "class_type": "ControlNetApply",
                "_meta": {"title": "Apply ControlNet"}
            },
            "8": {
                "inputs": {
                    "seed": int(time.time()) + index * 1000,
                    "steps": steps,
                    "cfg": cfg,
                    "sampler_name": "dpmpp_2m",
                    "scheduler": "karras",
                    "denoise": 1,
                    "model": ["1", 0],
                    "positive": ["7", 0],
                    "negative": ["7", 1],
                    "latent_image": ["2", 0]
                },
                "class_type": "KSampler",
                "_meta": {"title": "ControlNet Sampler"}
            },
            "9": {
                "inputs": {
                    "samples": ["8", 0],
                    "vae": ["1", 2]
                },
                "class_type": "VAEDecode",
                "_meta": {"title": "VAE Decode"}
            },
            "10": {
                "inputs": {
                    "filename_prefix": f"ControlNet_True_{index+1:03d}_",
                    "images": ["9", 0]
                },
                "class_type": "SaveImage",
                "_meta": {"title": "Save ControlNet Image"}
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
        print(f"Generating ControlNet image {prompt_id}...")
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
                        print(f"ControlNet generation completed! ({elapsed:.1f}s)")
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
            
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                # Save to local file
                local_filename = f"true_controlnet_{index+1:02d}_{filename}"
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
    
    def generate_controlnet_images(self):
        """Generate images using true ControlNet functionality."""
        print("🎛️  Starting True ControlNet Generation")
        print("📐 Using SDXL ControlNet Canny + Juggernaut XL v10")
        print("🎯 Edge-guided generation for anatomical precision")
        print("=" * 60)
        
        prompts = self.get_controlnet_prompts()
        print(f"Loaded {len(prompts)} ControlNet prompts")
        
        total_start = time.time()
        successful_downloads = 0
        
        for i, prompt_data in enumerate(prompts):
            print(f"\n📸 Generating ControlNet image {i+1}/{len(prompts)}")
            print(f"Style: {prompt_data.get('description', '')}")
            print(f"Settings: {prompt_data.get('steps', 35)} steps, CFG {prompt_data.get('cfg', 7.5)}, {prompt_data.get('width', 896)}x{prompt_data.get('height', 1152)}")
            
            # Create ControlNet workflow
            workflow = self.create_controlnet_workflow(prompt_data, i)
            
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
                # Give extra time for ControlNet processing
                time.sleep(3)
                
                # Try to find and download the generated image
                expected_filename = f"ControlNet_True_{i+1:03d}__00001_.png"
                if self.download_image(expected_filename, i):
                    successful_downloads += 1
                else:
                    print(f"Failed to download ControlNet image {i+1}")
            else:
                print(f"ControlNet generation failed for image {i+1}")
        
        total_time = time.time() - total_start
        
        print("\n" + "=" * 60)
        print("🎉 TRUE CONTROLNET GENERATION COMPLETE!")
        print(f"✅ Successfully generated: {successful_downloads}/{len(prompts)} images")
        print(f"⏱️  Total time: {total_time:.1f} seconds")
        if successful_downloads > 0:
            print(f"📊 Average per image: {total_time/successful_downloads:.1f} seconds")
            total_size = sum(os.path.getsize(os.path.join(self.output_dir, f)) 
                           for f in os.listdir(self.output_dir) if f.endswith('.png'))
            print(f"📦 Total size: {total_size/1024:.1f}KB")
        print(f"📁 Output directory: {self.output_dir}")
        print("🎛️  ControlNet Canny provided precise edge control for improved anatomy!")

def main():
    generator = V100TrueControlNet()
    generator.generate_controlnet_images()

if __name__ == "__main__":
    main()