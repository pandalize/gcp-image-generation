#!/bin/bash
set -e

echo "=== クイック画像生成セットアップ ==="

# NVIDIAドライバーの簡易インストール
echo "1. CUDAツールキットをインストール..."
sudo apt-get update -qq
sudo apt-get install -y -qq nvidia-driver-535 nvidia-cuda-toolkit

# Python環境の高速セットアップ
echo "2. Python環境を準備..."
sudo apt-get install -y -qq python3-pip

# 必要最小限のライブラリをインストール
echo "3. 画像生成ライブラリをインストール..."
pip3 install -q torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip3 install -q diffusers transformers accelerate

# シンプルな画像生成スクリプト
echo "4. 画像を生成中..."
python3 << 'EOF'
import torch
from diffusers import StableDiffusionPipeline
import os

print("Loading model...")
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16
)
pipe = pipe.to("cuda")

os.makedirs("images", exist_ok=True)

prompts = [
    "A beautiful sunset over Mount Fuji",
    "A futuristic Tokyo cityscape",
    "A magical Japanese dragon"
]

for i, prompt in enumerate(prompts):
    print(f"Generating: {prompt}")
    image = pipe(prompt, num_inference_steps=20).images[0]
    image.save(f"images/image_{i}.png")
    print(f"Saved: images/image_{i}.png")

print("Done! Check the 'images' directory")
EOF

echo "=== 完了！images/ディレクトリを確認してください ==="