#!/bin/bash
set -e

echo "=== NVIDIAデバイスファイル修復スクリプト ==="
echo "目標: /dev/nvidia* デバイスファイル作成でnvidia-smi動作"

# 1. 現在の状況確認
echo "Step 1: 現在の状況"
echo "GPU検出: $(lspci | grep -i nvidia)"
echo "モジュール: $(lsmod | grep nvidia | wc -l) 個のnvidiaモジュール読み込み済み"
echo "デバイス: $(ls /dev/nvidia* 2>/dev/null | wc -l) 個のnvidiaデバイス"

# 2. nvidia-smiバイナリの場所確認
echo -e "\nStep 2: nvidia-smi バイナリ確認"
which nvidia-smi || echo "nvidia-smi が見つかりません"
ls -la /usr/bin/nvidia-smi 2>/dev/null || echo "/usr/bin/nvidia-smi なし"

# 3. 手動でデバイスファイルを作成
echo -e "\nStep 3: NVIDIAデバイスファイル手動作成"

# nvidia-smiを使ってデバイスを初期化
echo "nvidia-smiでデバイス初期化試行..."
sudo nvidia-smi -pm 1 2>/dev/null || echo "nvidia-smi -pm 1 失敗"

# 手動でデバイス作成
echo "手動デバイスファイル作成..."

# メジャー番号取得
NVIDIA_MAJOR=$(grep nvidia /proc/devices | awk '{print $1}' | head -1)
if [ -z "$NVIDIA_MAJOR" ]; then
    echo "NVIDIAメジャー番号が見つかりません。カーネルモジュールを再読み込み..."
    sudo rmmod nvidia_uvm nvidia_drm nvidia_modeset nvidia 2>/dev/null || true
    sudo modprobe nvidia
    sudo modprobe nvidia_modeset  
    sudo modprobe nvidia_drm
    sudo modprobe nvidia_uvm
    sleep 2
    NVIDIA_MAJOR=$(grep nvidia /proc/devices | awk '{print $1}' | head -1)
fi

echo "NVIDIAメジャー番号: $NVIDIA_MAJOR"

if [ ! -z "$NVIDIA_MAJOR" ]; then
    # nvidiactl デバイス作成
    sudo mknod -m 666 /dev/nvidiactl c $NVIDIA_MAJOR 255 2>/dev/null || true
    
    # nvidia0 デバイス作成 (GPU 1台分)
    sudo mknod -m 666 /dev/nvidia0 c $NVIDIA_MAJOR 0 2>/dev/null || true
    
    # nvidia-uvm デバイス作成
    NVIDIA_UVM_MAJOR=$(grep nvidia-uvm /proc/devices | awk '{print $1}')
    if [ ! -z "$NVIDIA_UVM_MAJOR" ]; then
        sudo mknod -m 666 /dev/nvidia-uvm c $NVIDIA_UVM_MAJOR 0 2>/dev/null || true
    fi
    
    # 権限設定
    sudo chmod 666 /dev/nvidia* 2>/dev/null || true
    sudo chown root:root /dev/nvidia* 2>/dev/null || true
fi

# 4. デバイスファイル確認
echo -e "\nStep 4: デバイスファイル確認"
ls -la /dev/nvidia* 2>/dev/null || echo "NVIDIAデバイスファイルが見つかりません"

# 5. nvidia-smi テスト
echo -e "\nStep 5: nvidia-smi 動作テスト"
nvidia-smi || echo "nvidia-smi まだ失敗"

# 6. 代替手段: nvidia-modprobe使用
if ! nvidia-smi; then
    echo -e "\nStep 6: 代替手段 - nvidia-modprobe"
    sudo apt-get install -y nvidia-modprobe 2>/dev/null || true
    sudo nvidia-modprobe -u -c=0 || true
    sleep 2
    echo "nvidia-modprobe後のテスト:"
    nvidia-smi || echo "nvidia-modprobe後も失敗"
fi

# 7. 最終手段: nvidia-persistenced再起動
if ! nvidia-smi; then
    echo -e "\nStep 7: nvidia-persistenced 再起動"
    sudo systemctl stop nvidia-persistenced
    sudo systemctl start nvidia-persistenced
    sleep 3
    echo "persistenced再起動後のテスト:"
    nvidia-smi || echo "persistenced再起動後も失敗"
fi

# 8. udev ルール作成
echo -e "\nStep 8: udev ルール作成"
cat | sudo tee /etc/udev/rules.d/70-nvidia.rules << 'EOF'
KERNEL=="nvidia", RUN+="/bin/bash -c '/usr/bin/nvidia-smi -L && /bin/chmod 666 /dev/nvidia*'"
KERNEL=="nvidia_uvm", RUN+="/bin/bash -c '/bin/chmod 666 /dev/nvidia-uvm*'"
SUBSYSTEM=="nvidia", RUN+="/bin/bash -c '/bin/chmod 666 /dev/nvidia*'"
EOF

sudo udevadm control --reload-rules
sudo udevadm trigger

# 9. 最終テスト
echo -e "\nStep 9: 最終動作テスト"
sleep 2
if nvidia-smi; then
    echo "✅ SUCCESS: nvidia-smi 動作成功!"
    nvidia-smi -L
    nvidia-smi -q -d MEMORY | head -10
else
    echo "❌ nvidia-smi まだ動作しません"
    
    # 詳細デバッグ情報
    echo -e "\nデバッグ情報:"
    echo "プロセス: $(grep nvidia /proc/devices)"
    echo "デバイス: $(ls -la /dev/nvidia* 2>/dev/null)"
    echo "モジュール: $(lsmod | grep nvidia)"
fi

echo -e "\n=== 修復スクリプト完了 ==="