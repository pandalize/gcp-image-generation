#!/bin/bash

echo "=== 画像生成環境のセットアップ ==="

# CUDAの確認
echo "1. GPU/CUDAの確認..."
nvidia-smi
if [ $? -ne 0 ]; then
    echo "エラー: GPUが検出されません"
    exit 1
fi

# 必要なパッケージのインストール
echo "2. 必要なパッケージをインストール..."
pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install diffusers transformers accelerate xformers
pip install opencv-python pillow numpy
pip install gradio  # Web UIが必要な場合

# ディレクトリの作成
echo "3. 作業ディレクトリを作成..."
mkdir -p ~/image-generation
mkdir -p ~/image-generation/outputs
mkdir -p ~/image-generation/models

echo ""
echo "セットアップ完了！"
echo "次にgenerate-images.pyを実行して画像生成を開始できます。"