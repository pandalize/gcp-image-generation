#!/bin/bash
set -e

echo "=== NVIDIA 535 安定版インストール ==="
echo "DKMSを回避してプリコンパイル済みドライバーを使用"

# 1. 全てのNVIDIAコンポーネントを削除
echo "Step 1: 完全クリーンアップ"
sudo apt-get purge -y nvidia* libnvidia* cuda* 2>/dev/null || true
sudo apt-get autoremove -y
sudo apt-get autoclean

# 2. Ubuntu標準のNVIDIA 535をインストール
echo "Step 2: Ubuntu標準のNVIDIA 535をインストール"
sudo apt-get update
sudo apt-get install -y nvidia-driver-535-server nvidia-utils-535-server

# 3. 基本的なCUDAライブラリのみインストール
echo "Step 3: 軽量CUDA環境"
sudo apt-get install -y nvidia-cuda-toolkit

# 4. モジュール読み込み
echo "Step 4: モジュール読み込み"
sudo modprobe nvidia || echo "modprobe nvidia failed"
sudo modprobe nvidia_uvm || echo "modprobe nvidia_uvm failed"

# 5. デバイス権限設定
echo "Step 5: デバイス権限"
sudo chmod 666 /dev/nvidia* 2>/dev/null || true
sudo chmod 666 /dev/nvidiactl 2>/dev/null || true

# 6. nvidia-smiテスト
echo "Step 6: nvidia-smi テスト"
nvidia-smi || echo "nvidia-smi 失敗 - 再起動が必要かもしれません"

# 7. 手動でデバイス作成
if ! nvidia-smi; then
    echo "Step 7: 手動でNVIDIAデバイス作成"
    sudo nvidia-smi -pm 1 2>/dev/null || true
    
    # nvidia-modeset有効化
    echo 'nvidia-drm.modeset=1' | sudo tee -a /etc/modprobe.d/nvidia-drm-nomodeset.conf
    
    # 再起動
    echo "再起動が必要です..."
    sleep 3
    sudo reboot
fi

echo "=== NVIDIA 535インストール完了 ==="