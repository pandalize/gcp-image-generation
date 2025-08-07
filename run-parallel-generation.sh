#!/bin/bash

# 複数のVMで並列実行するスクリプト

NUM_VMS=3  # 起動するVM数
HOURS_TO_RUN=72  # 実行時間（時間）

echo "=== 並列画像生成の開始 ==="
echo "VM数: $NUM_VMS"
echo "実行時間: $HOURS_TO_RUN 時間"
echo "推定総コスト: $(($NUM_VMS * $HOURS_TO_RUN * 3000))円"
echo ""

read -p "続行しますか？ (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "キャンセルしました"
    exit 1
fi

# 複数のVMを起動
for i in $(seq 1 $NUM_VMS); do
    INSTANCE_NAME="image-gen-gpu-$i-$(date +%s)"
    echo "VM $i を作成中: $INSTANCE_NAME"
    
    gcloud compute instances create $INSTANCE_NAME \
        --zone=us-central1-a \
        --machine-type=a2-highgpu-1g \
        --maintenance-policy=TERMINATE \
        --accelerator="type=nvidia-tesla-a100,count=1" \
        --image-family=pytorch-latest-gpu \
        --image-project=deeplearning-platform-release \
        --boot-disk-size=200 \
        --boot-disk-type=pd-ssd \
        --metadata="install-nvidia-driver=True,startup-script=#!/bin/bash
            cd /home
            pip install torch torchvision diffusers transformers accelerate xformers
            wget https://raw.githubusercontent.com/your-repo/generate-images.py
            python generate-images.py --num-images 10000 --batch-size 8" \
        --scopes=https://www.googleapis.com/auth/cloud-platform \
        --preemptible &
done

wait

echo ""
echo "すべてのVMが起動しました！"
echo ""
echo "VMの状態を確認:"
echo "gcloud compute instances list"
echo ""
echo "コストを監視するには:"
echo "gcloud billing accounts get-iam-policy $(gcloud billing accounts list --format='value(name)' --limit=1)"