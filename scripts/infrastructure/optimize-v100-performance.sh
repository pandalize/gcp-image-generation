#!/bin/bash
echo "⚡ V100性能最適化スクリプト"
echo "=========================="

echo "🛑 現在のComfyUI停止"
pkill -f "python main.py"
sleep 3

echo "🎯 GPU最適化設定"
cd ~/ComfyUI
source comfyui_env/bin/activate

# GPU最適化環境変数
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:1024
export CUDA_VISIBLE_DEVICES=0
export CUDA_LAUNCH_BLOCKING=0

echo "🚀 V100フル性能モード起動"
# CPU-VAEを削除してGPU VAEに戻す
nohup python main.py --listen 0.0.0.0 --port 8188 \
  --highvram \
  --fast \
  > ~/comfyui_optimized.log 2>&1 &

echo "⏳ 起動待機"
sleep 15

echo "📊 V100性能確認"
nvidia-smi

echo "🔍 API確認"
curl -s http://localhost:8188/system_stats | head -20

echo ""
echo "⚡ V100最適化完了!"
echo "高性能モード: http://34.70.230.62:8188"