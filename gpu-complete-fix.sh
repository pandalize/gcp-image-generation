#!/bin/bash
set -e
echo "=== L4 GPU完全修復スクリプト ==="
echo "目標: nvidia-smiを動作させてStable DiffusionでAI美女画像生成"
echo ""

# ログファイル設定
LOG_FILE=~/gpu_fix.log
exec > >(tee -a $LOG_FILE) 2>&1

echo "開始時刻: $(date)"
echo "GPU情報:"
lspci | grep -i nvidia || echo "GPU検出失敗"

# Step 1: システムクリーンアップ
echo ""
echo "=== Step 1: システム完全クリーンアップ ==="
sudo apt-get update
sudo apt-get remove --purge -y nvidia* libnvidia* cuda* 2>/dev/null || true
sudo apt-get autoremove -y
sudo apt-get autoclean

# 古いカーネルモジュール削除
sudo rmmod nvidia_uvm 2>/dev/null || true
sudo rmmod nvidia_drm 2>/dev/null || true  
sudo rmmod nvidia_modeset 2>/dev/null || true
sudo rmmod nvidia 2>/dev/null || true

# Step 2: 依存関係とツールのインストール  
echo ""
echo "=== Step 2: 基本パッケージインストール ==="
sudo apt-get install -y build-essential dkms
sudo apt-get install -y linux-headers-$(uname -r)
sudo apt-get install -y pkg-config
sudo apt-get install -y software-properties-common

# Step 3: NVIDIAの公式リポジトリ追加
echo ""
echo "=== Step 3: NVIDIA公式リポジトリ設定 ==="
wget -q https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update

# Step 4: 最新NVIDIAドライバーのインストール
echo ""
echo "=== Step 4: 最新NVIDIAドライバーインストール ==="
sudo apt-get install -y ubuntu-drivers-common

# 利用可能ドライバーを確認
echo "利用可能なドライバー:"
ubuntu-drivers devices

# L4用の最新ドライバーをインストール（535以上）
sudo apt-get install -y nvidia-driver-545 nvidia-dkms-545
sudo apt-get install -y nvidia-utils-545

# Step 5: CUDA 12.0ツールキットのインストール
echo ""
echo "=== Step 5: CUDA 12.0インストール ==="
sudo apt-get install -y cuda-toolkit-12-0

# Step 6: 環境変数の設定
echo ""
echo "=== Step 6: 環境変数設定 ==="
cat >> ~/.bashrc << 'EOF'

# CUDA 12.0 Environment
export CUDA_HOME=/usr/local/cuda-12.0
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
export CUDA_VISIBLE_DEVICES=0
EOF

# Step 7: udevルール設定
echo ""
echo "=== Step 7: GPU udevルール設定 ==="
cat | sudo tee /etc/udev/rules.d/70-nvidia.rules << 'EOF'
KERNEL=="nvidia", RUN+="/bin/bash -c '/usr/bin/nvidia-smi -L && /bin/chmod 666 /dev/nvidia*'"
KERNEL=="nvidia_uvm", RUN+="/bin/bash -c '/bin/chmod 666 /dev/nvidia-uvm*'"
SUBSYSTEM=="nvidia", RUN+="/bin/bash -c '/bin/chmod 666 /dev/nvidia*'"
EOF

sudo udevadm control --reload-rules

# Step 8: systemd nvidia-persistenced設定  
echo ""
echo "=== Step 8: NVIDIA Persistence Daemon設定 ==="
sudo systemctl enable nvidia-persistenced
sudo systemctl start nvidia-persistenced

# Step 9: Xorg設定（headless用）
echo ""
echo "=== Step 9: Headless GPU設定 ==="
sudo nvidia-xconfig --enable-all-gpus --separate-x-screens --use-display-device=none --virtual=1024x768

# Step 10: 再起動前のテスト準備
echo ""
echo "=== Step 10: 再起動後テスト準備 ==="

# GPU検証スクリプト作成
cat > ~/gpu_verification.py << 'EOF'
#!/usr/bin/env python3
import subprocess
import sys
import os

print("=== L4 GPU検証スクリプト ===")

# 1. nvidia-smi テスト
print("1. nvidia-smi テスト:")
try:
    result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=30)
    if result.returncode == 0:
        print("✓ nvidia-smi 成功!")
        print(result.stdout)
    else:
        print("✗ nvidia-smi 失敗")
        print(result.stderr)
except Exception as e:
    print(f"✗ nvidia-smi エラー: {e}")

# 2. CUDA コンパイラテスト
print("\n2. CUDA コンパイラテスト:")
try:
    result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True, timeout=10)
    if result.returncode == 0:
        print("✓ nvcc 動作確認")
        print(result.stdout)
    else:
        print("✗ nvcc 失敗")
except Exception as e:
    print(f"✗ nvcc エラー: {e}")

# 3. PyTorch GPU テスト
print("\n3. PyTorch GPU テスト:")
try:
    import torch
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"GPU count: {torch.cuda.device_count()}")
        print(f"GPU name: {torch.cuda.get_device_name(0)}")
        print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        
        # GPU計算テスト
        print("\n4. GPU計算テスト:")
        x = torch.rand(1000, 1000, device='cuda')
        y = torch.rand(1000, 1000, device='cuda') 
        z = torch.mm(x, y)
        print(f"✓ GPU行列計算成功: {z.shape}")
        print(f"✓ GPU memory used: {torch.cuda.memory_allocated() / 1e6:.1f} MB")
        
        # メモリクリア
        del x, y, z
        torch.cuda.empty_cache()
        print("✓ GPU memory cleared")
        
    else:
        print("✗ CUDA利用不可")
        
except ImportError:
    print("PyTorch未インストール")
except Exception as e:
    print(f"PyTorch GPU エラー: {e}")

print("\n=== 検証完了 ===")
EOF

chmod +x ~/gpu_verification.py

# AI画像生成環境セットアップスクリプト
cat > ~/setup_ai_generation.sh << 'EOF' 
#!/bin/bash
echo "=== AI画像生成環境セットアップ ==="

# GPU対応PyTorchインストール
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# AI画像生成ライブラリ
pip3 install diffusers==0.25.0
pip3 install transformers==4.36.0
pip3 install accelerate==0.25.0  
pip3 install safetensors==0.4.1
pip3 install xformers
pip3 install pillow opencv-python

echo "AI環境セットアップ完了"
EOF

chmod +x ~/setup_ai_generation.sh

echo ""
echo "=== GPU修復スクリプト完了 ==="
echo "次に実行:"
echo "1. sudo reboot (システム再起動)"
echo "2. python3 ~/gpu_verification.py (GPU動作検証)"  
echo "3. bash ~/setup_ai_generation.sh (AI環境構築)"
echo ""
echo "ログファイル: $LOG_FILE"
echo "再起動を実行します..."

sleep 5
sudo reboot