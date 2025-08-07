#!/bin/bash

# GPU付きVMインスタンスの作成設定
INSTANCE_NAME="image-gen-gpu-$(date +%s)"
ZONE="us-central1-a"
MACHINE_TYPE="a2-highgpu-1g"  # NVIDIA A100 40GB x1
BOOT_DISK_SIZE="200"
IMAGE_FAMILY="pytorch-latest-gpu"
IMAGE_PROJECT="deeplearning-platform-release"

echo "=== GPU付きVMインスタンスを作成 ==="
echo "インスタンス名: $INSTANCE_NAME"
echo "マシンタイプ: $MACHINE_TYPE (A100 GPU x1)"
echo "推定コスト: 約3,000円/時間"
echo ""

read -p "続行しますか？ (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "キャンセルしました"
    exit 1
fi

# VMインスタンスの作成
gcloud compute instances create $INSTANCE_NAME \
    --zone=$ZONE \
    --machine-type=$MACHINE_TYPE \
    --maintenance-policy=TERMINATE \
    --accelerator="type=nvidia-tesla-a100,count=1" \
    --image-family=$IMAGE_FAMILY \
    --image-project=$IMAGE_PROJECT \
    --boot-disk-size=$BOOT_DISK_SIZE \
    --boot-disk-type=pd-ssd \
    --metadata="install-nvidia-driver=True" \
    --scopes=https://www.googleapis.com/auth/cloud-platform \
    --preemptible

echo ""
echo "VMが作成されました！"
echo ""
echo "SSHで接続するには:"
echo "gcloud compute ssh $INSTANCE_NAME --zone=$ZONE"
echo ""
echo "重要: VMは起動している間、料金が発生します！"
echo "停止するには: gcloud compute instances stop $INSTANCE_NAME --zone=$ZONE"
echo "削除するには: gcloud compute instances delete $INSTANCE_NAME --zone=$ZONE"
echo ""
echo "次にsetup-image-gen.shをVMにコピーして実行してください:"
echo "gcloud compute scp setup-image-gen.sh $INSTANCE_NAME:~/ --zone=$ZONE"
echo "gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command='bash ~/setup-image-gen.sh'"