#!/usr/bin/env python3
import sys
import os

# CUDAライブラリパスを設定
os.environ['LD_LIBRARY_PATH'] = '/usr/local/cuda/lib64:/usr/lib/x86_64-linux-gnu'

print("=== 画像生成開始 (修正版) ===")
print("CUDAライブラリ問題を回避...")

try:
    import torch
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    
    if not torch.cuda.is_available():
        print("警告: GPUが利用できません。CPUモードで実行します。")
        device = "cpu"
    else:
        device = "cuda"
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        
except ImportError as e:
    print(f"PyTorchインポートエラー: {e}")
    print("CPUモードで簡単な画像を生成します...")
    device = "cpu"

# Pillowで代替画像生成
print("\n=== Pillowで画像生成 (デモ) ===")
from PIL import Image, ImageDraw
import random
from datetime import datetime

output_dir = os.path.expanduser("~/generated_images")
os.makedirs(output_dir, exist_ok=True)

# AI風の画像を生成
prompts = [
    "Sunset over Mount Fuji",
    "Cyberpunk Tokyo",
    "Japanese Garden",
    "Space Station",
    "Magical Forest"
]

for i, prompt in enumerate(prompts, 1):
    print(f"[{i}/5] 生成中: {prompt}")
    
    # カラフルなパターンを生成
    img = Image.new('RGB', (512, 512))
    pixels = img.load()
    
    # ノイズパターンを生成（AI生成風）
    for x in range(512):
        for y in range(512):
            # プロンプトに基づいた色調整
            if "Sunset" in prompt:
                r = min(255, 200 + random.randint(0, 55))
                g = min(255, 100 + random.randint(0, 100))
                b = random.randint(0, 150)
            elif "Cyberpunk" in prompt:
                r = random.randint(0, 100)
                g = random.randint(100, 255)
                b = random.randint(200, 255)
            elif "Garden" in prompt:
                r = random.randint(50, 150)
                g = random.randint(150, 255)
                b = random.randint(50, 150)
            elif "Space" in prompt:
                r = random.randint(0, 50)
                g = random.randint(0, 50)
                b = random.randint(100, 255)
            else:  # Magical Forest
                r = random.randint(100, 200)
                g = random.randint(50, 255)
                b = random.randint(100, 200)
            
            pixels[x, y] = (r, g, b)
    
    # ぼかし効果を追加
    img = img.filter(Image.FILTER.SMOOTH_MORE)
    
    # テキストラベル追加
    draw = ImageDraw.Draw(img)
    draw.rectangle([(10, 460), (502, 502)], fill=(0, 0, 0, 128))
    draw.text((20, 470), prompt, fill=(255, 255, 255))
    
    # 保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/demo_{i}_{timestamp}.png"
    img.save(filename)
    print(f"   保存完了: {filename}")

print(f"\n=== デモ画像生成完了！ ===")
print(f"画像保存先: {output_dir}")
print("\n注: これはデモ画像です。実際のAI画像生成にはGPUドライバーの設定が必要です。")

# 実際のStable Diffusion実行を試みる
try:
    print("\n=== Stable Diffusion実行を試行中... ===")
    from diffusers import StableDiffusionPipeline
    
    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        low_cpu_mem_usage=True
    )
    pipe = pipe.to(device)
    
    prompt = "A beautiful Japanese temple in autumn"
    print(f"AI画像生成中: {prompt}")
    image = pipe(prompt, num_inference_steps=10).images[0]
    image.save(f"{output_dir}/ai_generated.png")
    print(f"AI画像保存完了: {output_dir}/ai_generated.png")
    
except Exception as e:
    print(f"Stable Diffusion実行エラー: {e}")
    print("GPUドライバーが完全にインストールされるまでお待ちください。")