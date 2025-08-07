#!/usr/bin/env python3
"""
V100 Anatomically Correct Full Body Generator
Fixed aspect ratio and settings for proper body proportions
"""

import requests
import json
import time
import yaml
import os
import sys
from datetime import datetime
import base64

class V100AnatomicallyCorrect:
    def __init__(self):
        self.server_ip = "34.70.230.62"
        self.port = 8188
        self.base_url = f"http://{self.server_ip}:{self.port}"
        self.output_dir = "/Users/fujinoyuki/Desktop/gcp/outputs/anatomically_correct"
        self.create_output_dir()
        
    def create_output_dir(self):
        """Create output directory if it doesn't exist."""
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Output directory: {self.output_dir}")
    
    def get_anatomically_correct_prompts(self):
        """Get prompts optimized for anatomical correctness."""
        return [
            {
                'positive': 'professional full body portrait, beautiful woman, standing pose, correct human anatomy, natural proportions, perfect body structure, detailed hands with five fingers each, elegant dress, studio lighting, photorealistic, high quality, masterpiece',
                'negative': 'cropped, cut off, bad anatomy, deformed body, wrong proportions, extra limbs, missing limbs, bad hands, extra fingers, missing fingers, fused fingers, malformed hands, floating limbs, disconnected body parts, low quality',
                'steps': 35,
                'cfg': 6.5,
                'width': 832,
                'height': 1216,
                'description': 'Correct Proportions Portrait'
            },
            {
                'positive': 'full body shot, asian woman, natural standing pose, anatomically correct proportions, complete figure from head to feet, proper body structure, beautiful hands with normal fingers, flowing hair, soft lighting, realistic, ultra detailed',
                'negative': 'partial body, cropped limbs, bad anatomy, deformed, disproportionate, extra arms, extra legs, bad hands, malformed fingers, floating body parts, incomplete body, cut off feet, low quality',
                'steps': 35,
                'cfg': 6.5,
                'width': 832,
                'height': 1216,
                'description': 'Natural Full Body Pose'
            },
            {
                'positive': 'complete full body view, fitness model, athletic pose, correct human anatomy, well-proportioned body, natural muscle definition, hands in natural position with proper finger count, gym attire, natural lighting, photorealistic quality',
                'negative': 'cropped body, incomplete figure, bad anatomy, deformed proportions, extra limbs, missing body parts, malformed hands, wrong finger count, floating elements, anatomical errors, low quality',
                'steps': 35,
                'cfg': 6.5,
                'width': 832,
                'height': 1216,
                'description': 'Athletic Full Body'
            }
        ]
    
    def create_anatomical_workflow(self, prompt_data, index):
        """Create workflow optimized for anatomical correctness."""
        
        positive = prompt_data.get('positive', '')
        negative = prompt_data.get('negative', '')
        steps = prompt_data.get('steps', 35)
        cfg = prompt_data.get('cfg', 6.5)
        width = prompt_data.get('width', 832)
        height = prompt_data.get('height', 1216)
        
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
                "_meta": {"title": "Portrait Aspect Ratio"}
            },
            "3": {
                "inputs": {
                    "text": positive,
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "Anatomical Positive"}
            },
            "4": {
                "inputs": {
                    "text": negative,
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "Anti-Deformation Negative"}
            },
            "5": {
                "inputs": {
                    "seed": int(time.time()) + index * 1500,
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
                "_meta": {"title": "Anatomical Sampler"}
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
                    "filename_prefix": f"Anatomical_Correct_{index+1:03d}_",
                    "images": ["6", 0]
                },
                "class_type": "SaveImage",
                "_meta": {"title": "Save Correct Anatomy"}
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
        print(f"Generating anatomically correct image {prompt_id}...")
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
                        print(f"Anatomical generation completed! ({elapsed:.1f}s)")
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
                local_filename = f"anatomical_{index+1:02d}_{filename}"
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
    
    def generate_anatomical_images(self):
        """Generate anatomically correct images."""
        print("🎨 Starting Anatomically Correct Generation")
        print("📐 Optimized for proper body proportions (832x1216)")
        print("=" * 60)
        
        prompts = self.get_anatomically_correct_prompts()
        print(f"Loaded {len(prompts)} anatomical prompts")
        
        total_start = time.time()
        successful_downloads = 0
        
        for i, prompt_data in enumerate(prompts):
            print(f"\n📸 Generating anatomical image {i+1}/{len(prompts)}")
            print(f"Description: {prompt_data.get('description', '')}")
            print(f"Settings: {prompt_data.get('steps', 35)} steps, CFG {prompt_data.get('cfg', 6.5)}, {prompt_data.get('width', 832)}x{prompt_data.get('height', 1216)}")
            
            # Create workflow
            workflow = self.create_anatomical_workflow(prompt_data, i)
            
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
                expected_filename = f"Anatomical_Correct_{i+1:03d}__00001_.png"
                if self.download_image(expected_filename, i):
                    successful_downloads += 1
                else:
                    print(f"Failed to download image {i+1}")
            else:
                print(f"Generation failed for image {i+1}")
        
        total_time = time.time() - total_start
        
        print("\n" + "=" * 60)
        print("🎉 ANATOMICALLY CORRECT GENERATION COMPLETE!")
        print(f"✅ Successfully generated: {successful_downloads}/{len(prompts)} images")
        print(f"⏱️  Total time: {total_time:.1f} seconds")
        if successful_downloads > 0:
            print(f"📊 Average per image: {total_time/successful_downloads:.1f} seconds")
            total_size = sum(os.path.getsize(os.path.join(self.output_dir, f)) 
                           for f in os.listdir(self.output_dir) if f.endswith('.png'))
            print(f"📦 Total size: {total_size/1024:.1f}KB")
        print(f"📁 Output directory: {self.output_dir}")

def main():
    generator = V100AnatomicallyCorrect()
    generator.generate_anatomical_images()

if __name__ == "__main__":
    main()