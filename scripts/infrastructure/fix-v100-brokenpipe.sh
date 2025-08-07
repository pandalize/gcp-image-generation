#!/bin/bash
echo "🔧 V100 BrokenPipe エラー修正スクリプト"
echo "========================================"

echo "📋 現在の状況確認"
ps aux | grep python | grep -v grep
echo ""

echo "🛑 ComfyUIプロセス終了"
pkill -f "python main.py"
sleep 5

echo "🔄 システムリソースクリーンアップ"
sudo sync
sudo sysctl vm.drop_caches=1

echo "📊 GPU状態確認とリセット"
nvidia-smi
sudo nvidia-smi --gpu-reset || echo "GPU Reset not available"

echo "🧹 Python環境クリーンアップ"
cd ~/ComfyUI
source comfyui_env/bin/activate

# メモリ使用量を最適化するためのPython設定
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
export CUDA_VISIBLE_DEVICES=0

echo "🎯 tqdmの出力リダイレクト対策"
pip install --upgrade tqdm
pip install --upgrade --no-deps --force-reinstall tqdm

echo "⚙️ ComfyUI設定最適化"
# stderr出力を無効化してBrokenPipeを回避
export PYTHONUNBUFFERED=1
export TQDM_DISABLE=1

echo "🚀 ComfyUI GPU最適化起動"
# より安全な設定で起動
python main.py --listen 0.0.0.0 --port 8188 \
  --disable-smart-memory \
  --normalvram \
  --cpu-vae \
  > ~/comfyui_fixed.log 2>&1 &

echo "⏳ 起動待機"
sleep 15

echo "🔍 起動確認"
curl -s http://localhost:8188/system_stats | head -10 || echo "API応答待機中..."

echo "📋 プロセス確認"
ps aux | grep python | grep -v grep

echo "📄 最新ログ"
tail -10 ~/comfyui_fixed.log

echo ""
echo "🎉 修正完了!"
echo "ComfyUI起動: http://34.70.230.62:8188"
echo "ログファイル: ~/comfyui_fixed.log"