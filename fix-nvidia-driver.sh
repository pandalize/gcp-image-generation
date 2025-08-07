#!/bin/bash
set -e

echo "=== NVIDIA Driver 強制修正 ==="

# 1. 現在の状態確認
echo "Step 1: 現在の状態確認"
lspci | grep -i nvidia || echo "GPUが検出されません"

# 2. 既存ドライバーの完全削除
echo "Step 2: 既存ドライバーを完全削除"
sudo apt-get purge -y nvidia* libnvidia* cuda* 2>/dev/null || true
sudo apt-get autoremove -y
sudo apt-get autoclean

# 3. リポジトリの更新
echo "Step 3: リポジトリ更新"
sudo apt-get update

# 4. 推奨ドライバーの確認とインストール
echo "Step 4: 推奨NVIDIAドライバーのインストール"
sudo apt-get install -y ubuntu-drivers-common
sudo ubuntu-drivers devices
sudo ubuntu-drivers install

# 5. 手動で最新ドライバーをインストール（フォールバック）
echo "Step 5: 手動ドライバーインストール"
sudo apt-get install -y nvidia-driver-535 nvidia-utils-535

# 6. CUDA 11.8の直接インストール
echo "Step 6: CUDA 11.8直接インストール"
wget -q https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda_11.8.0_520.61.05_linux.run
sudo chmod +x cuda_11.8.0_520.61.05_linux.run
sudo ./cuda_11.8.0_520.61.05_linux.run --silent --toolkit --no-opengl-libs

# 7. 環境変数設定
echo "Step 7: 環境変数設定"
echo 'export PATH=/usr/local/cuda-11.8/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-11.8/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
echo 'export CUDA_HOME=/usr/local/cuda-11.8' >> ~/.bashrc

source ~/.bashrc

# 8. モジュール読み込み
echo "Step 8: NVIDIAモジュール読み込み"
sudo modprobe nvidia
sudo modprobe nvidia-uvm

# 9. デバイス権限設定
echo "Step 9: デバイス権限設定"
sudo chmod 666 /dev/nvidia* 2>/dev/null || true
sudo chmod 666 /dev/nvidiactl 2>/dev/null || true

# 10. 動作テスト
echo "Step 10: 動作テスト"
echo "nvidia-smi テスト:"
nvidia-smi || echo "nvidia-smi失敗 - 再起動が必要"

echo "CUDA動作テスト:"
nvcc --version || echo "nvcc利用不可"

# 11. Python GPU環境セットアップ
echo "Step 11: Python GPU環境"
python3 -m pip install --upgrade pip

# GPU対応PyTorchインストール
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# GPU動作確認スクリプト
cat > ~/gpu_test_simple.py << 'EOF'
import torch
print("PyTorch version:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("CUDA version:", torch.version.cuda)
    print("GPU count:", torch.cuda.device_count())
    print("GPU name:", torch.cuda.get_device_name(0))
    
    # 簡単なテンソル演算
    x = torch.rand(100, 100).cuda()
    y = x * 2
    print("GPU tensor test successful!")
    print("GPU tensor shape:", y.shape)
else:
    print("CUDA not available - check installation")
EOF

# テスト実行
echo "Python GPUテスト:"
python3 ~/gpu_test_simple.py

echo "=== 修正完了 ==="
echo "再起動が推奨されます: sudo reboot"