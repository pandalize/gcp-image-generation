#!/usr/bin/env python3
"""
ComfyUI L4 GPU美女画像バッチ生成スクリプト
L4 GPUで高速に美女画像を大量生成
"""
import requests
import json
import time
import uuid
import os
from datetime import datetime

# ComfyUI Server Settings
SERVER_IP = "35.225.113.119"  # L4 GPU VM IP
SERVER_PORT = 8188
BASE_URL = f"http://{SERVER_IP}:{SERVER_PORT}"

# Beauty Generation Prompts (商用利用可能なSDXL対応)
BEAUTY_PROMPTS = [
    "beautiful woman, elegant dress, professional portrait, studio lighting, high quality, photorealistic",
    "stunning asian woman, flowing long hair, natural makeup, soft lighting, fashion photography", 
    "gorgeous woman, perfect skin, confident pose, commercial photography, cinematic lighting",
    "beautiful model, designer outfit, professional headshot, high fashion, editorial style",
    "elegant woman, sophisticated look, luxury background, premium portrait photography",
    "stunning beauty, natural pose, soft focus, professional photography, magazine quality",
    "beautiful woman, graceful expression, artistic lighting, fine art portrait",
    "gorgeous model, perfect features, commercial shoot, high-end fashion photography",
    "elegant lady, timeless beauty, classic portrait, studio quality lighting",
    "beautiful woman, confident smile, professional makeup, fashion editorial style"
]

# SDXL workflow template
WORKFLOW_TEMPLATE = {
    "3": {
        "inputs": {
            "seed": 0,  # Will be randomized
            "steps": 25,
            "cfg": 7.0,
            "sampler_name": "euler",
            "scheduler": "normal", 
            "denoise": 1.0,
            "model": ["4", 0],
            "positive": ["6", 0],
            "negative": ["7", 0],
            "latent_image": ["5", 0]
        },
        "class_type": "KSampler",
        "_meta": {"title": "KSampler"}
    },
    "4": {
        "inputs": {
            "ckpt_name": "sdxl_base_1.0.safetensors"
        },
        "class_type": "CheckpointLoaderSimple",
        "_meta": {"title": "Load Checkpoint"}
    },
    "5": {
        "inputs": {
            "width": 1024,
            "height": 1024,
            "batch_size": 1
        },
        "class_type": "EmptyLatentImage",
        "_meta": {"title": "Empty Latent Image"}
    },
    "6": {
        "inputs": {
            "text": "PROMPT_PLACEHOLDER",
            "clip": ["4", 1]
        },
        "class_type": "CLIPTextEncode",
        "_meta": {"title": "CLIP Text Encode (Prompt)"}
    },
    "7": {
        "inputs": {
            "text": "low quality, blurry, worst quality, bad anatomy, deformed, ugly",
            "clip": ["4", 1]
        },
        "class_type": "CLIPTextEncode",
        "_meta": {"title": "CLIP Text Encode (Negative)"}
    },
    "8": {
        "inputs": {
            "samples": ["3", 0],
            "vae": ["4", 2]
        },
        "class_type": "VAEDecode",
        "_meta": {"title": "VAE Decode"}
    },
    "9": {
        "inputs": {
            "filename_prefix": "L4_Beauty_",
            "images": ["8", 0]
        },
        "class_type": "SaveImage",
        "_meta": {"title": "Save Image"}
    }
}

def check_server():
    """Check if ComfyUI server is running"""
    try:
        response = requests.get(f"{BASE_URL}/system_stats", timeout=10)
        return response.status_code == 200
    except:
        return False

def queue_prompt(prompt_data):
    """Queue a prompt for generation"""
    try:
        response = requests.post(f"{BASE_URL}/prompt", json={"prompt": prompt_data}, timeout=30)
        if response.status_code == 200:
            return response.json()["prompt_id"]
        return None
    except Exception as e:
        print(f"Error queuing prompt: {e}")
        return None

def check_queue_status():
    """Check current queue status"""
    try:
        response = requests.get(f"{BASE_URL}/queue", timeout=10)
        if response.status_code == 200:
            data = response.json()
            running = len(data.get("queue_running", []))
            pending = len(data.get("queue_pending", []))
            return running, pending
        return 0, 0
    except:
        return 0, 0

def generate_beauty_batch(count=50):
    """Generate beauty images in batch"""
    print(f"🚀 Starting L4 GPU Beauty Generation Batch: {count} images")
    print(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not check_server():
        print("❌ ComfyUI server not accessible!")
        return
    
    generated_count = 0
    prompt_ids = []
    
    for i in range(count):
        # Select prompt from collection
        prompt = BEAUTY_PROMPTS[i % len(BEAUTY_PROMPTS)]
        
        # Create workflow with random seed
        import copy
        workflow = copy.deepcopy(WORKFLOW_TEMPLATE)
        workflow["3"]["inputs"]["seed"] = int(time.time() * 1000000) % 1000000 + i
        workflow["6"]["inputs"]["text"] = prompt
        
        # Queue the generation
        prompt_id = queue_prompt(workflow)
        if prompt_id:
            prompt_ids.append(prompt_id)
            generated_count += 1
            print(f"✅ Queued #{i+1}/{count}: {prompt[:50]}...")
        else:
            print(f"❌ Failed to queue #{i+1}")
        
        # Status check every 10 prompts
        if i % 10 == 9:
            running, pending = check_queue_status()
            print(f"📊 Queue Status - Running: {running}, Pending: {pending}")
            time.sleep(1)  # Brief pause
    
    print(f"🎯 Batch Complete: {generated_count}/{count} prompts queued")
    print(f"⏰ Queue time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Monitor completion
    print("\n🔄 Monitoring generation progress...")
    last_pending = None
    
    while True:
        running, pending = check_queue_status()
        if running == 0 and pending == 0:
            break
            
        if pending != last_pending:
            remaining = running + pending
            completed = generated_count - remaining
            print(f"🎨 Progress: {completed}/{generated_count} completed ({remaining} remaining)")
            last_pending = pending
            
        time.sleep(5)
    
    print(f"🎉 All {generated_count} beauty images generated!")
    print(f"⏰ Complete time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    print("🔥 L4 GPU ComfyUI Beauty Generator")
    print(f"🎯 Target: {SERVER_IP}:{SERVER_PORT}")
    
    # Generate 100 beauty images for maximum credit utilization
    generate_beauty_batch(100)