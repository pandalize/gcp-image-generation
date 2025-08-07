#!/usr/bin/env python3
"""
商用利用可能な高性能モデルで美女画像を大量生成
License: 商用利用可能なモデルのみ使用
"""
import os
import sys
import subprocess
import time
from datetime import datetime
from pathlib import Path

print("=== 商用美女画像生成システム ===")

# 出力ディレクトリ
output_dir = Path.home() / "commercial_beauty_images"
output_dir.mkdir(exist_ok=True)

# CUDAとGPU設定
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:128'

def install_requirements():
    """必要なパッケージをインストール"""
    packages = [
        "torch==2.0.1+cu118 torchvision==0.15.2+cu118 --index-url https://download.pytorch.org/whl/cu118",
        "diffusers==0.21.4",
        "transformers==4.35.2",
        "accelerate==0.25.0",
        "safetensors==0.4.1",
        "opencv-python-headless",
        "pillow",
        "numpy",
        "requests"
    ]
    
    for package in packages:
        print(f"Installing: {package}")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install"] + package.split(), 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to install {package}")
            continue

def check_gpu():
    """GPU状態をチェック"""
    try:
        import torch
        print(f"PyTorch version: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
            return True
        else:
            print("GPU not available - using CPU mode")
            return False
    except ImportError:
        print("PyTorch not installed - installing dependencies...")
        return False

def create_beauty_generator():
    """商用利用可能な美女画像生成モデルを設定"""
    script_content = '''
import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from PIL import Image
import os
from datetime import datetime
import random
import gc

# GPU設定
device = "cuda" if torch.cuda.is_available() else "cpu"
torch.cuda.empty_cache()

print(f"Using device: {device}")
print("Loading commercial-use model: Realistic Vision v4.0...")

# 商用利用可能な高品質モデル
model_id = "SG161222/Realistic_Vision_V4.0"

try:
    # パイプライン設定
    pipe = StableDiffusionPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        safety_checker=None,
        requires_safety_checker=False,
        use_safetensors=True
    )
    
    # スケジューラーを高品質設定
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
    pipe = pipe.to(device)
    
    # メモリ最適化
    pipe.enable_attention_slicing()
    pipe.enable_sequential_cpu_offload()
    if hasattr(pipe, 'enable_model_cpu_offload'):
        pipe.enable_model_cpu_offload()
    
    print("Model loaded successfully!")
    
    # 高品質美女プロンプト集（商用利用向け）
    beauty_prompts = [
        "beautiful elegant woman, professional portrait, soft lighting, high fashion, detailed face, symmetrical features, natural makeup, commercial photography style, 8k, ultra realistic",
        "stunning asian woman, business professional, confident smile, modern office background, natural beauty, perfect skin, commercial headshot style, high resolution",
        "gorgeous european model, fashion portrait, studio lighting, elegant pose, natural expression, commercial beauty photography, ultra detailed, 8k quality",
        "beautiful woman in casual style, natural lighting, genuine smile, lifestyle photography, modern fashion, commercial quality, high definition",
        "elegant business woman, professional attire, confident pose, corporate portrait, natural beauty, commercial photography style, ultra realistic, 8k",
        "stunning fashion model, haute couture dress, professional studio lighting, elegant pose, commercial fashion photography, high fashion beauty, ultra detailed",
        "beautiful woman in summer dress, golden hour lighting, natural beauty, outdoor portrait, commercial lifestyle photography, high quality, 8k resolution",
        "gorgeous professional woman, executive style, confident expression, modern corporate setting, natural makeup, commercial portrait photography",
        "elegant woman in evening wear, sophisticated pose, professional lighting, formal portrait, commercial beauty photography, ultra realistic",
        "beautiful casual portrait, natural lighting, genuine expression, lifestyle fashion, commercial photography quality, high resolution beauty shot"
    ]
    
    # ネガティブプロンプト（品質向上用）
    negative_prompt = "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name, deformed, disfigured, ugly, duplicate"
    
    # バッチ生成
    batch_size = 50  # クレジット消費のため大量生成
    
    for batch in range(5):  # 5バッチ = 250枚
        print(f"\\n=== Batch {batch + 1}/5 ===")
        
        for i in range(batch_size):
            try:
                # ランダムにプロンプトを選択
                prompt = random.choice(beauty_prompts)
                
                # 品質設定を変更
                width = random.choice([768, 832, 896])
                height = random.choice([768, 832, 896])
                steps = random.choice([25, 30, 35])
                guidance = random.uniform(7.0, 9.0)
                
                print(f"Generating image {i+1}/{batch_size}: {width}x{height}, {steps} steps")
                
                # 画像生成
                image = pipe(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    width=width,
                    height=height,
                    num_inference_steps=steps,
                    guidance_scale=guidance,
                    num_images_per_prompt=1
                ).images[0]
                
                # ファイル名生成
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                filename = f"beauty_commercial_{batch+1}_{i+1:02d}_{timestamp}.png"
                filepath = os.path.join("commercial_beauty_images", filename)
                
                # 保存
                image.save(filepath, quality=95, optimize=True)
                print(f"   Saved: {filename}")
                
                # メモリクリア
                del image
                torch.cuda.empty_cache()
                gc.collect()
                
                # GPU温度管理のため少し待機
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error generating image {i+1}: {e}")
                continue
        
        print(f"Batch {batch + 1} completed!")
        
        # バッチ間の休憩
        print("Cooling down GPU...")
        time.sleep(10)
    
    total_images = len(os.listdir("commercial_beauty_images"))
    print(f"\\n=== Generation Complete! ===")
    print(f"Total images generated: {total_images}")
    print(f"Output directory: commercial_beauty_images/")
    
    # GPU使用状況
    if device == "cuda":
        print(f"Max GPU Memory Used: {torch.cuda.max_memory_allocated() / 1e9:.2f} GB")

except Exception as e:
    print(f"Error: {e}")
    print("Trying fallback CPU generation...")
    
    # フォールバック: CPUで簡易生成
    from PIL import Image, ImageDraw
    import random
    
    for i in range(10):
        img = Image.new('RGB', (768, 768))
        draw = ImageDraw.Draw(img)
        
        # 美的なグラデーション
        for y in range(768):
            r = min(255, 200 + int(y/15))
            g = min(255, 150 + int(y/12))
            b = min(255, 180 + int(y/10))
            draw.rectangle([(0, y), (768, y+1)], fill=(r, g, b))
        
        draw.text((20, 720), f"Commercial Beauty Demo {i+1}", fill=(255, 255, 255))
        
        filename = f"commercial_beauty_images/fallback_beauty_{i+1:02d}.png"
        img.save(filename)
        print(f"Fallback image saved: {filename}")
'''
    
    with open("beauty_generator.py", "w") as f:
        f.write(script_content)
    
    return "beauty_generator.py"

def main():
    """メイン実行関数"""
    print("Step 1: Checking GPU status...")
    gpu_available = check_gpu()
    
    if not gpu_available:
        print("Step 2: Installing PyTorch and dependencies...")
        install_requirements()
    
    print("Step 3: Creating beauty image generator...")
    script_file = create_beauty_generator()
    
    print("Step 4: Starting commercial beauty image generation...")
    print("This will generate 250+ high-quality commercial-use beauty images")
    print("Estimated time: 30-60 minutes")
    print("Estimated cost: $15-25")
    
    return script_file

if __name__ == "__main__":
    script_file = main()
    print(f"\\nGeneration script created: {script_file}")
    print("Run with: python beauty_generator.py")