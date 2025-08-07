#!/bin/bash
set -e

echo "=== GPU画像生成環境セットアップ開始 ==="

# 1. システム更新とNVIDIAドライバーインストール
echo "1. NVIDIAドライバーをインストール中..."
sudo apt-get update
sudo apt-get install -y ubuntu-drivers-common
sudo ubuntu-drivers install --gpgpu
sudo apt-get install -y nvidia-cuda-toolkit

# 2. Python環境のセットアップ
echo "2. Python環境をセットアップ中..."
sudo apt-get install -y python3-pip python3-venv git

# 3. 仮想環境作成
echo "3. Python仮想環境を作成中..."
python3 -m venv ~/sdxl_env
source ~/sdxl_env/bin/activate

# 4. 必要なライブラリをインストール
echo "4. PyTorchとdiffusersをインストール中..."
pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install diffusers transformers accelerate safetensors xformers

# 5. 画像生成スクリプト作成
echo "5. 画像生成スクリプトを作成中..."
cat > ~/generate_images.py << 'EOF'
import torch
from diffusers import DiffusionPipeline
import os
from datetime import datetime

# GPUを使用
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Stable Diffusion XLパイプラインをロード
print("Loading Stable Diffusion XL...")
pipe = DiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16,
    use_safetensors=True,
    variant="fp16"
)
pipe = pipe.to(device)

# メモリ最適化
pipe.enable_xformers_memory_efficient_attention()
pipe.enable_vae_slicing()

# 出力ディレクトリ作成
output_dir = os.path.expanduser("~/generated_images")
os.makedirs(output_dir, exist_ok=True)

# プロンプトリスト
prompts = [
    "A majestic dragon flying over Mount Fuji at sunset, highly detailed, cinematic lighting",
    "A cyberpunk samurai in neon-lit Tokyo streets, rain, reflections, 8k quality",
    "A serene Japanese garden with cherry blossoms, koi pond, photorealistic",
    "Futuristic space station orbiting Earth, sci-fi, detailed machinery",
    "A magical forest with glowing mushrooms and fireflies, fantasy art style"
]

# 画像生成
print(f"\n=== {len(prompts)}枚の画像を生成開始 ===")
for i, prompt in enumerate(prompts, 1):
    print(f"\n[{i}/{len(prompts)}] 生成中: {prompt[:50]}...")
    
    # 生成
    image = pipe(
        prompt=prompt,
        negative_prompt="low quality, blurry, distorted",
        num_inference_steps=30,
        guidance_scale=7.5,
        height=1024,
        width=1024
    ).images[0]
    
    # 保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/image_{i}_{timestamp}.png"
    image.save(filename)
    print(f"   保存完了: {filename}")

print(f"\n=== 全画像生成完了！ ===")
print(f"画像保存先: {output_dir}")

# GPU使用状況を表示
if device == "cuda":
    print(f"\nGPU Memory: {torch.cuda.max_memory_allocated() / 1024**3:.2f} GB used")
EOF

echo "=== セットアップ完了 ==="
echo "画像生成を開始するには："
echo "1. source ~/sdxl_env/bin/activate"
echo "2. python ~/generate_images.py"