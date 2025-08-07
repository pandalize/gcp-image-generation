#!/bin/bash
echo "🔧 V100 CUDA環境修復スクリプト"
echo "=================================="

echo "📋 現在の状況確認"
nvidia-smi
echo ""

echo "🔄 CUDAコンテキストリセット"
sudo nvidia-smi -r || echo "GPUリセット完了"

echo "🧹 古いPyTorchアンインストール"
cd ~/ComfyUI
source comfyui_env/bin/activate
pip uninstall -y torch torchvision torchaudio

echo "🔧 CUDA 11.8対応PyTorchインストール（V100互換）"
pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 torchaudio==2.0.2+cu118 --index-url https://download.pytorch.org/whl/cu118

echo "🎯 CUDA環境変数設定"
export CUDA_VISIBLE_DEVICES=0
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/nvidia/current:$LD_LIBRARY_PATH

echo "✅ GPU認識テスト"
python -c "
import torch
print('PyTorch version:', torch.__version__)
print('CUDA available:', torch.cuda.is_available())
print('CUDA version:', torch.version.cuda if hasattr(torch.version, 'cuda') else 'None')
if torch.cuda.is_available():
    print('Device count:', torch.cuda.device_count())
    print('Device name:', torch.cuda.get_device_name(0))
    print('GPU Memory:', torch.cuda.get_device_properties(0).total_memory // 1024**3, 'GB')
    print('CUDA Capability:', torch.cuda.get_device_capability(0))
"

echo "🚀 ComfyUI GPUモード起動"
nohup python main.py --listen 0.0.0.0 --port 8188 > ~/comfyui_gpu_fixed.log 2>&1 &

echo "⏳ 起動待機"
sleep 10

echo "🔍 起動状況確認"
curl -s http://localhost:8188/system_stats | head -10 || echo "起動中..."

echo "📋 最終確認"
echo "ComfyUIログ:"
tail -10 ~/comfyui_gpu_fixed.log

echo ""
echo "🎉 修復完了！"
echo "ComfyUI GPU起動: http://34.70.230.62:8188"