#!/bin/bash
echo "🚀 V100 ウルトラ性能モード"
echo "=========================="

echo "🛑 現在のプロセス停止"
pkill -f "python main.py"
sleep 3

echo "⚡ 最高性能設定"
cd ~/ComfyUI
source comfyui_env/bin/activate

# GPU最適化環境変数（より攻撃的）
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:2048
export CUDA_VISIBLE_DEVICES=0
export CUDA_LAUNCH_BLOCKING=0
export TORCH_CUDNN_V8_API_ENABLED=1
export CUDA_CACHE_MAXSIZE=2147483647

echo "🔧 GPU周波数最大化"
sudo nvidia-smi -pm 1
sudo nvidia-smi -ac 877,1530  # V100最大クロック設定

echo "💾 システム最適化"
# CPUガバナー設定
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# ディスクI/O最適化
echo mq-deadline | sudo tee /sys/block/sda/queue/scheduler

# メモリ最適化
echo 1 | sudo tee /proc/sys/vm/drop_caches
echo 10 | sudo tee /proc/sys/vm/swappiness

echo "🚀 ComfyUI超高性能起動"
nohup python main.py --listen 0.0.0.0 --port 8188 \
  --highvram \
  --fast \
  --dont-print-server \
  --preview-method none \
  > ~/comfyui_ultra.log 2>&1 &

echo "⏳ 起動待機"
sleep 15

echo "📊 最終確認"
nvidia-smi
curl -s http://localhost:8188/system_stats | head -20

echo ""
echo "🔥 V100ウルトラ性能モード完了!"
echo "起動: http://34.70.230.62:8188"