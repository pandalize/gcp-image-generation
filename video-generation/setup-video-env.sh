#!/bin/bash

echo "=== 動画生成環境のセットアップ ==="

# CUDAの確認
echo "1. GPU/CUDAの確認..."
nvidia-smi
if [ $? -ne 0 ]; then
    echo "エラー: GPUが検出されません"
    exit 1
fi

# 動画生成用パッケージのインストール
echo "2. 動画生成パッケージをインストール..."
pip install --upgrade pip

# 画像生成用
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install diffusers transformers accelerate xformers

# 動画生成用
pip install opencv-python-headless imageio imageio-ffmpeg
pip install stable-video-diffusion
pip install animatediff

# 画像→動画変換用
pip install moviepy Pillow numpy scipy
pip install git+https://github.com/huggingface/diffusers.git

# 追加ツール
pip install tqdm matplotlib gradio

# FFmpegのインストール
echo "3. FFmpegをインストール..."
apt-get update && apt-get install -y ffmpeg

# ディレクトリ構造の作成
echo "4. 作業ディレクトリを作成..."
mkdir -p ~/video-generation/{inputs,outputs,temp,models}
mkdir -p ~/video-generation/outputs/{images,videos,final}

echo ""
echo "セットアップ完了！"
echo "動画生成パイプラインを実行できます。"