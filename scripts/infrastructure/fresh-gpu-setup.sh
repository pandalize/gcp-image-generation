#!/bin/bash
set -e

echo "=== フレッシュL4 GPU VM完全セットアップ ==="
echo "目標: 一発でnvidia-smiとAI画像生成を動作させる"
echo "VM: gpu-l4-ai (G2-standard-4, L4 GPU)"
echo ""

LOG_FILE=~/fresh_gpu_setup.log
exec > >(tee -a $LOG_FILE) 2>&1

echo "開始時刻: $(date)"
echo "システム情報:"
uname -a
lspci | grep -i nvidia

# Step 1: システム更新
echo ""
echo "=== Step 1: システム基本設定 ==="
sudo apt-get update -q
export DEBIAN_FRONTEND=noninteractive
sudo apt-get install -y build-essential linux-headers-$(uname -r) pkg-config

# Step 2: 正しいNVIDIAドライバーインストール
echo ""
echo "=== Step 2: NVIDIA Driver 535 安定版インストール ==="
sudo apt-get install -y ubuntu-drivers-common

# 推奨ドライバーを確認
echo "利用可能なドライバー:"
ubuntu-drivers devices

# 安定版535をインストール（DKMSエラー回避）
sudo apt-get install -y nvidia-driver-535 nvidia-utils-535

# Step 3: CUDA 11.8インストール（L4対応）
echo ""
echo "=== Step 3: CUDA 11.8インストール ==="
wget -q https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update -q
sudo apt-get install -y cuda-toolkit-11-8

# Step 4: 環境変数設定
echo ""
echo "=== Step 4: 環境変数設定 ==="
cat >> ~/.bashrc << 'EOF'

# CUDA 11.8 Environment for L4 GPU
export CUDA_HOME=/usr/local/cuda-11.8
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
export CUDA_VISIBLE_DEVICES=0
EOF

source ~/.bashrc

# Step 5: GPU動作テスト用スクリプト作成
echo ""
echo "=== Step 5: テストスクリプト準備 ==="
cat > ~/test_l4_gpu.py << 'EOF'
#!/usr/bin/env python3
import subprocess
import sys

print("=== L4 GPU完全動作テスト ===")

# nvidia-smi テスト
print("1. nvidia-smi テスト:")
try:
    result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=30)
    if result.returncode == 0:
        print("✓ nvidia-smi 成功!")
        print(result.stdout)
        gpu_working = True
    else:
        print("✗ nvidia-smi 失敗")
        print(result.stderr)
        gpu_working = False
except Exception as e:
    print(f"✗ nvidia-smi エラー: {e}")
    gpu_working = False

# PyTorch GPU テスト
print("\n2. PyTorch GPU テスト:")
try:
    import torch
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available() and gpu_working:
        print(f"CUDA version: {torch.version.cuda}")
        print(f"GPU count: {torch.cuda.device_count()}")
        print(f"GPU name: {torch.cuda.get_device_name(0)}")
        print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        
        # GPU計算テスト
        print("\n3. GPU計算能力テスト:")
        import time
        
        start_time = time.time()
        x = torch.rand(2000, 2000, device='cuda')
        y = torch.rand(2000, 2000, device='cuda') 
        z = torch.mm(x, y)
        gpu_time = time.time() - start_time
        
        print(f"✓ L4 GPU行列計算成功: {z.shape}")
        print(f"✓ 計算時間: {gpu_time:.3f}秒")
        print(f"✓ GPU performance: {(2000**3 * 2) / gpu_time / 1e9:.2f} GFLOPS")
        
        del x, y, z
        torch.cuda.empty_cache()
        print("✓ GPU memory cleared")
        
        return True
        
    else:
        print("✗ CUDA利用不可またはnvidia-smi失敗")
        return False
        
except ImportError:
    print("PyTorch未インストール - インストールが必要")
    return False
except Exception as e:
    print(f"PyTorch GPU エラー: {e}")
    return False

EOF

chmod +x ~/test_l4_gpu.py

# Step 6: AI画像生成環境構築スクリプト
echo ""
echo "=== Step 6: AI画像生成環境スクリプト準備 ==="
cat > ~/install_ai_packages.sh << 'EOF'
#!/bin/bash
set -e

echo "=== AI画像生成環境構築 ==="

# Python環境準備
echo "Python環境準備..."
sudo apt-get install -y python3-pip python3-venv

# 専用仮想環境作成
echo "AI専用仮想環境作成..."
python3 -m venv ~/ai_env
source ~/ai_env/bin/activate

# GPU対応PyTorchインストール
echo "GPU対応PyTorchインストール..."
pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# AI画像生成ライブラリ
echo "AI画像生成ライブラリインストール..."
pip install diffusers==0.25.0
pip install transformers==4.36.0  
pip install accelerate==0.25.0
pip install safetensors==0.4.1
pip install pillow opencv-python-headless
pip install xformers  # L4用メモリ効率化

echo "✓ AI環境構築完了"
echo "使用方法: source ~/ai_env/bin/activate"
EOF

chmod +x ~/install_ai_packages.sh

echo ""
echo "=== フレッシュGPUセットアップ完了 ==="
echo "次の手順:"
echo "1. sudo reboot (ドライバー有効化のため再起動)"
echo "2. python3 ~/test_l4_gpu.py (GPU動作確認)"
echo "3. bash ~/install_ai_packages.sh (AI環境構築)"
echo ""
echo "再起動を実行します..."
sleep 5
sudo reboot