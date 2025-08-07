#!/bin/bash
set -e

echo "=== NVIDIA強制読み込みスクリプト ==="
echo "DKMSエラーを修正してGPUを強制的に有効化"

# 1. カーネル情報確認
echo "現在のカーネル: $(uname -r)"
lspci | grep -i nvidia

# 2. 古いモジュールをアンロード
echo "古いNVIDIAモジュールをアンロード..."
sudo rmmod nvidia_uvm 2>/dev/null || true
sudo rmmod nvidia_drm 2>/dev/null || true
sudo rmmod nvidia_modeset 2>/dev/null || true
sudo rmmod nvidia 2>/dev/null || true

# 3. 手動でDKMSを修正
echo "DKMSを手動修正..."
sudo dkms remove nvidia/580.65.06 --all 2>/dev/null || true
sudo dkms install nvidia/580.65.06

# 4. モジュールを手動読み込み
echo "NVIDIAモジュールを手動読み込み..."
sudo modprobe nvidia
sudo modprobe nvidia_modeset
sudo modprobe nvidia_drm
sudo modprobe nvidia_uvm

# 5. デバイスファイルを作成
echo "NVIDIAデバイスファイルを作成..."
sudo nvidia-smi -pm 1 || true
sudo chmod 666 /dev/nvidia* 2>/dev/null || true
sudo chmod 666 /dev/nvidiactl 2>/dev/null || true
sudo chmod 666 /dev/nvidia-uvm* 2>/dev/null || true

# 6. nvidia-smi強制実行
echo "nvidia-smi テスト..."
nvidia-smi || echo "nvidia-smi failed - trying alternative approach"

# 7. 代替アプローチ：runfileからインストール
if ! nvidia-smi; then
    echo "代替手段：runfileからNVIDIA 545をインストール"
    cd /tmp
    wget -q https://us.download.nvidia.com/XFree86/Linux-x86_64/545.29.06/NVIDIA-Linux-x86_64-545.29.06.run
    sudo chmod +x NVIDIA-Linux-x86_64-545.29.06.run
    sudo ./NVIDIA-Linux-x86_64-545.29.06.run --silent --no-opengl-files --no-x-check --no-nouveau-check
fi

# 8. 最終テスト
echo "=== 最終GPU動作テスト ==="
nvidia-smi
echo "✓ nvidia-smi 成功!"

# 9. GPU情報詳細表示
nvidia-smi -L
nvidia-smi -q -d MEMORY

echo "=== GPU修復完了 ==="