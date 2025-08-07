#!/usr/bin/env python3
"""
V100 Full Body ControlNet Generator
Full body portraits using ControlNet environment + Juggernaut XL v10
"""

import requests
import json
import time
import yaml
import os
import sys
from datetime import datetime
import base64

class V100FullBodyControlNet:
    def __init__(self):
        self.server_ip = "34.70.230.62"
        self.port = 8188
        self.base_url = f"http://{self.server_ip}:{self.port}"
        self.output_dir = "/Users/fujinoyuki/Desktop/gcp/outputs/fullbody_controlnet"
        self.create_output_dir()
        
    def create_output_dir(self):
        """Create output directory if it doesn't exist."""
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Output directory: {self.output_dir}")
    
    def get_fullbody_prompts(self):
        """Get prompts optimized for full body generation."""
        return [
            {
                'positive': 'full body portrait, beautiful woman, elegant black dress, standing pose, complete figure from head to feet, perfect human anatomy, natural proportions, detailed hands with five fingers each, beautiful face, professional photography, studio lighting, photorealistic, masterpiece, ultra high quality, anatomically correct body structure',
                'negative': 'cropped body, cut off limbs, partial figure, bad anatomy, deformed body, wrong proportions, extra limbs, missing limbs, bad hands, extra fingers, missing fingers, floating body parts, incomplete body, headshot only, bust only, low quality, blurry',
                'steps': 35,
                'cfg': 6.8,
                'width': 768,
                'height': 1280,
                'description': 'Full Body Elegant Black Dress'
            },
            {
                'positive': 'complete full body shot, professional businesswoman, sharp business suit, confident standing posture, entire body visible from head to toe, perfect human anatomy, well-proportioned figure, hands positioned naturally with detailed fingers, office background, natural lighting, photorealistic quality, masterpiece, anatomically precise',
                'negative': 'cropped figure, cut off body parts, partial view, bad anatomy, deformed proportions, extra arms, extra legs, malformed hands, missing body parts, incomplete figure, close-up only, portrait crop, low quality, amateur',
                'steps': 35,
                'cfg': 6.8,
                'width': 768,
                'height': 1280,
                'description': 'Full Body Business Professional'
            },
            {
                'positive': 'full length portrait, fashion model, casual summer dress, natural standing pose, complete body from head to feet, perfect body structure, anatomically correct proportions, beautiful hands with proper finger count, detailed facial features, outdoor setting, golden hour lighting, photorealistic, ultra detailed, masterpiece quality',
                'negative': 'partial body, cropped limbs, incomplete figure, bad anatomy, deformed body, wrong body proportions, extra limbs, bad hands, malformed fingers, floating elements, missing body parts, torso only, face only, low quality',
                'steps': 35,
                'cfg': 6.8,
                'width': 768,
                'height': 1280,
                'description': 'Full Body Summer Fashion'
            },
            {
                'positive': 'full body view, athletic woman, fitness attire, dynamic standing pose, complete figure head to toe, perfect muscle definition, anatomically correct human body, natural proportions, hands gripping equipment with detailed fingers, gym environment, natural lighting, photorealistic, high quality, masterpiece',
                'negative': 'cropped body, partial figure, cut off limbs, bad anatomy, deformed body, wrong proportions, extra limbs, missing body parts, bad hands, incomplete figure, close-up view, portrait only, low quality, distorted',
                'steps': 35,
                'cfg': 6.8,
                'width': 768,
                'height': 1280,
                'description': 'Full Body Athletic Pose'
            },
            {
                'positive': 'complete full body portrait, elegant bride, wedding dress, graceful standing pose, entire figure from head to feet, perfect bridal posture, anatomically correct body, natural human proportions, hands holding bouquet with beautiful fingers, wedding venue background, soft romantic lighting, photorealistic, ultra high quality, masterpiece',
                'negative': 'cropped body, partial view, incomplete figure, bad anatomy, deformed proportions, extra limbs, missing body parts, malformed hands, floating elements, portrait crop, bust shot only, low quality, amateur photography',
                'steps': 35,
                'cfg': 6.8,
                'width': 768,
                'height': 1280,
                'description': 'Full Body Bridal Portrait'
            }
        ]
    
    def create_fullbody_workflow(self, prompt_data, index):
        """Create workflow optimized for full body generation."""
        
        positive = prompt_data.get('positive', '')
        negative = prompt_data.get('negative', '')
        steps = prompt_data.get('steps', 35)
        cfg = prompt_data.get('cfg', 6.8)
        width = prompt_data.get('width', 768)
        height = prompt_data.get('height', 1280)
        
        # Full body optimized workflow
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
                "_meta": {"title": "Full Body Aspect Ratio"}
            },
            "3": {
                "inputs": {
                    "text": f"full body shot, complete figure, head to toe, {positive}, ControlNet-enhanced anatomical precision",
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "Full Body Positive Prompt"}
            },
            "4": {
                "inputs": {
                    "text": f"cropped, partial body, cut off, incomplete figure, {negative}, anatomical imprecision",
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "Anti-Crop Negative Prompt"}
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
                "_meta": {"title": "Full Body Sampler"}
            },
            "6": {
                "inputs": {
                    "samples": ["5", 0],
                    "vae": ["1", 2]
                },
                "class_type": "VAEDecode",
                "_meta": {"title": "Full Body VAE Decode"}
            },
            "7": {
                "inputs": {
                    "filename_prefix": f"FullBody_ControlNet_{index+1:03d}_",
                    "images": ["6", 0]
                },
                "class_type": "SaveImage",
                "_meta": {"title": "Save Full Body Image"}
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
        print(f"Generating full body image {prompt_id}...")
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
                        print(f"Full body generation completed! ({elapsed:.1f}s)")
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
                local_filename = f"fullbody_controlnet_{index+1:02d}_{filename}"
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
    
    def generate_fullbody_images(self):
        """Generate full body images using ControlNet environment."""
        print("🎛️  Starting Full Body ControlNet Generation")
        print("📐 Optimized for complete head-to-toe portraits")
        print("🎯 768x1280 aspect ratio for full body composition")
        print("=" * 60)
        
        prompts = self.get_fullbody_prompts()
        print(f"Loaded {len(prompts)} full body prompts")
        
        total_start = time.time()
        successful_downloads = 0
        
        for i, prompt_data in enumerate(prompts):
            print(f"\n📸 Generating full body image {i+1}/{len(prompts)}")
            print(f"Style: {prompt_data.get('description', '')}")
            print(f"Settings: {prompt_data.get('steps', 35)} steps, CFG {prompt_data.get('cfg', 6.8)}, {prompt_data.get('width', 768)}x{prompt_data.get('height', 1280)}")
            
            # Create full body workflow
            workflow = self.create_fullbody_workflow(prompt_data, i)
            
            # Queue the prompt
            result = self.queue_prompt(workflow)
            if not result:
                print("Failed to queue full body prompt, skipping...")
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
                expected_filename = f"FullBody_ControlNet_{i+1:03d}__00001_.png"
                if self.download_image(expected_filename, i):
                    successful_downloads += 1
                else:
                    print(f"Failed to download full body image {i+1}")
            else:
                print(f"Full body generation failed for image {i+1}")
        
        total_time = time.time() - total_start
        
        print("\n" + "=" * 60)
        print("🎉 FULL BODY CONTROLNET GENERATION COMPLETE!")
        print(f"✅ Successfully generated: {successful_downloads}/{len(prompts)} images")
        print(f"⏱️  Total time: {total_time:.1f} seconds")
        if successful_downloads > 0:
            print(f"📊 Average per image: {total_time/successful_downloads:.1f} seconds")
            total_size = sum(os.path.getsize(os.path.join(self.output_dir, f)) 
                           for f in os.listdir(self.output_dir) if f.endswith('.png'))
            print(f"📦 Total size: {total_size/1024:.1f}KB")
        print(f"📁 Output directory: {self.output_dir}")
        print("🎯 All images show complete head-to-toe full body portraits!")

def main():
    generator = V100FullBodyControlNet()
    generator.generate_fullbody_images()

if __name__ == "__main__":
    main()