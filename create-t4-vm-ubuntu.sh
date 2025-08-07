#!/bin/bash

# T4 GPU付きVM作成（Ubuntu 20.04ベース）
INSTANCE_NAME="image-gen-t4-$(date +%s)"
ZONE="us-central1-a"
MACHINE_TYPE="n1-standard-4"
BOOT_DISK_SIZE="200"

echo "=== T4 GPU付きVM作成（Ubuntu 24.04 + NVIDIA Driver 570） ==="
echo "インスタンス名: $INSTANCE_NAME"
echo "マシンタイプ: $MACHINE_TYPE + T4 GPU"
echo "推定コスト: 約500円/時間"
echo "5万円で約100時間稼働可能"
echo ""

read -p "続行しますか？ (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "キャンセルしました"
    exit 1
fi

echo "T4 GPU VMを作成中..."

# VM作成（適切なエラーハンドリング付き）
if gcloud compute instances create $INSTANCE_NAME \
    --zone=$ZONE \
    --machine-type=$MACHINE_TYPE \
    --maintenance-policy=TERMINATE \
    --accelerator="type=nvidia-tesla-t4,count=1" \
    --image-family=ubuntu-accelerator-2404-amd64-with-nvidia-570 \
    --image-project=ubuntu-os-accelerator-images \
    --boot-disk-size=$BOOT_DISK_SIZE \
    --boot-disk-type=pd-ssd \
    --metadata="install-nvidia-driver=True,startup-script=#!/bin/bash
    # 基本パッケージをインストール
    apt-get update
    apt-get install -y python3-pip python3-venv git wget curl
    
    # NVIDIAドライバーとCUDAの準備
    # これらは自動インストールされるまで待機" \
    --scopes=https://www.googleapis.com/auth/cloud-platform \
    --preemptible; then
    
    echo ""
    echo "✅ T4 GPU VMが正常に作成されました！"
    echo ""
    echo "📋 次のステップ:"
    echo "1. VMの準備完了を待つ（3-5分）"
    echo "2. SSH接続: gcloud compute ssh $INSTANCE_NAME --zone=$ZONE"
    echo "3. 画像生成環境をセットアップ"
    echo ""
    echo "🔧 VM管理コマンド:"
    echo "  状態確認: gcloud compute instances describe $INSTANCE_NAME --zone=$ZONE --format='value(status)'"
    echo "  停止: gcloud compute instances stop $INSTANCE_NAME --zone=$ZONE"
    echo "  削除: gcloud compute instances delete $INSTANCE_NAME --zone=$ZONE"
    echo ""
    echo "💰 重要: T4は約500円/時間です！"
    
else
    echo ""
    echo "❌ VM作成でエラーが発生しました"
    echo "可能な原因:"
    echo "- GPUクォータ不足"
    echo "- リージョン/ゾーンでのT4利用不可"
    echo "- 課金アカウントの問題"
    echo ""
    echo "解決方法:"
    echo "1. クォータ確認: gcloud compute regions describe us-central1 --format='value(quotas[name=NVIDIA_T4_GPUS].limit)'"
    echo "2. 他のゾーンを試す: --zone=us-central1-b"
    echo "3. 課金アカウント確認: gcloud billing accounts list"
    exit 1
fi