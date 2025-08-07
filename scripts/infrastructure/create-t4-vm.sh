#!/bin/bash

# T4 GPU付きVMインスタンスの作成設定
INSTANCE_NAME="image-gen-t4-$(date +%s)"
ZONE="us-central1-a"
MACHINE_TYPE="n1-standard-4"  # T4用マシンタイプ
BOOT_DISK_SIZE="200"
IMAGE_FAMILY="pytorch-latest-gpu"
IMAGE_PROJECT="deeplearning-platform-release"

echo "=== T4 GPU付きVMインスタンスを作成 ==="
echo "インスタンス名: $INSTANCE_NAME"
echo "マシンタイプ: $MACHINE_TYPE + T4 GPU"
echo "推定コスト: 約500円/時間 (A100の1/6)"
echo "5万円で約100時間稼働可能！"
echo ""

read -p "続行しますか？ (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "キャンセルしました"
    exit 1
fi

# VMインスタンスの作成
echo "T4 GPU VMを作成中..."
gcloud compute instances create $INSTANCE_NAME \
    --zone=$ZONE \
    --machine-type=$MACHINE_TYPE \
    --maintenance-policy=TERMINATE \
    --accelerator="type=nvidia-tesla-t4,count=1" \
    --image-family=$IMAGE_FAMILY \
    --image-project=$IMAGE_PROJECT \
    --boot-disk-size=$BOOT_DISK_SIZE \
    --boot-disk-type=pd-ssd \
    --metadata="install-nvidia-driver=True" \
    --scopes=https://www.googleapis.com/auth/cloud-platform \
    --preemptible

echo ""
echo "✅ T4 GPU VMが作成されました！"
echo ""
echo "接続方法:"
echo "  gcloud compute ssh $INSTANCE_NAME --zone=$ZONE"
echo ""
echo "画像生成を開始:"
echo "  cd gcp-image-generation"
echo "  python generate-images.py --num-images 500 --batch-size 2"
echo ""
echo "重要な操作:"
echo "  停止: gcloud compute instances stop $INSTANCE_NAME --zone=$ZONE"
echo "  削除: gcloud compute instances delete $INSTANCE_NAME --zone=$ZONE"
echo ""
echo "💰 コスト: T4は約500円/時間"
echo "🕐 5万円で最大100時間稼働可能"