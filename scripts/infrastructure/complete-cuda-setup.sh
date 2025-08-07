#!/bin/bash
set -e

echo "=== 完全CUDA環境セットアップ ==="
echo "L4 GPU用の完全なCUDA環境を構築します"

# 1. システム更新
echo "Step 1: システム更新"
sudo apt-get update -q
sudo apt-get upgrade -y -q

# 2. 既存のNVIDIAドライバーを削除
echo "Step 2: 既存ドライバーのクリーンアップ"
sudo apt-get purge -y nvidia* libnvidia* 2>/dev/null || true
sudo apt-get autoremove -y
sudo apt-get autoclean

# 3. 最新のNVIDIAドライバーをインストール
echo "Step 3: NVIDIA Driver 535をインストール"
sudo apt-get install -y ubuntu-drivers-common
sudo ubuntu-drivers install --gpgpu nvidia-driver-535

# 4. CUDA 11.8ツールキットをインストール
echo "Step 4: CUDA 11.8 Toolkitをインストール"
wget -q https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update -q
sudo apt-get install -y cuda-toolkit-11-8 cuda-drivers

# 5. cuDNNのインストール
echo "Step 5: cuDNNをインストール"
sudo apt-get install -y libcudnn8 libcudnn8-dev

# 6. 環境変数の設定
echo "Step 6: 環境変数を設定"
cat >> ~/.bashrc << 'EOF'

# CUDA Environment
export CUDA_HOME=/usr/local/cuda-11.8
export PATH=$PATH:$CUDA_HOME/bin
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
export CUDA_VISIBLE_DEVICES=0
EOF

source ~/.bashrc

# 7. Python環境のセットアップ
echo "Step 7: Python環境をセットアップ"
sudo apt-get install -y python3-pip python3-venv python3-dev
python3 -m pip install --upgrade pip

# 8. 仮想環境作成
echo "Step 8: 専用仮想環境を作成"
python3 -m venv ~/ai_beauty_env
source ~/ai_beauty_env/bin/activate

# 9. GPU対応PyTorchのインストール
echo "Step 9: GPU対応PyTorchをインストール"
pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 torchaudio==2.0.2+cu118 --index-url https://download.pytorch.org/whl/cu118

# 10. AI画像生成ライブラリのインストール
echo "Step 10: AI画像生成ライブラリをインストール"
pip install diffusers==0.21.4
pip install transformers==4.33.2
pip install accelerate==0.24.1
pip install safetensors==0.4.0
pip install opencv-python-headless
pip install pillow
pip install xformers==0.0.22.post7
pip install compel

# 11. システム再起動が必要
echo "Step 11: システムを再起動します..."
echo "再起動後に nvidia-smi で動作確認してください"

# 再起動前にGPUテストスクリプトを作成
cat > ~/test_gpu.py << 'EOF'
#!/usr/bin/env python3
import torch
import subprocess

print("=== GPU動作テスト ===")

# nvidia-smiの実行
try:
    result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
    print("nvidia-smi output:")
    print(result.stdout)
except Exception as e:
    print(f"nvidia-smi error: {e}")

# PyTorchでのGPU確認
print(f"\nPyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"GPU count: {torch.cuda.device_count()}")
    print(f"GPU name: {torch.cuda.get_device_name(0)}")
    print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    
    # 簡単なGPUテスト
    print("\nGPUテストを実行...")
    x = torch.rand(1000, 1000).cuda()
    y = torch.rand(1000, 1000).cuda()
    z = torch.mm(x, y)
    print(f"GPU計算テスト成功: {z.shape}")
else:
    print("GPU利用不可 - セットアップを確認してください")
EOF

chmod +x ~/test_gpu.py

echo "=== CUDAセットアップ完了 ==="
echo ""
echo "【重要】システム再起動が必要です"
echo "再起動後に以下を実行してください："
echo "1. source ~/ai_beauty_env/bin/activate"
echo "2. python3 ~/test_gpu.py"
echo ""
echo "再起動します..."
sleep 5
sudo reboot