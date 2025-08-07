#!/bin/bash

# 複数のGPU VMで並列動画生成を実行

NUM_VMS=5  # A100 GPU VM数
VIDEOS_PER_VM=20  # 各VMで生成する動画数
TOTAL_VIDEOS=$((NUM_VMS * VIDEOS_PER_VM))

echo "=== 大規模並列動画生成プロジェクト ==="
echo "VM数: $NUM_VMS"
echo "各VMの動画数: $VIDEOS_PER_VM"
echo "総動画数: $TOTAL_VIDEOS"
echo "推定時間: 24-48時間"
echo "推定コスト: 約50,000円"
echo ""

# VM作成関数
create_video_vm() {
    local VM_ID=$1
    local INSTANCE_NAME="video-gen-gpu-${VM_ID}-$(date +%s)"
    
    echo "VM $VM_ID を作成中: $INSTANCE_NAME"
    
    gcloud compute instances create $INSTANCE_NAME \
        --zone=us-central1-a \
        --machine-type=a2-highgpu-1g \
        --maintenance-policy=TERMINATE \
        --accelerator="type=nvidia-tesla-a100,count=1" \
        --image-family=pytorch-latest-gpu \
        --image-project=deeplearning-platform-release \
        --boot-disk-size=500 \
        --boot-disk-type=pd-ssd \
        --metadata="install-nvidia-driver=True,startup-script=#!/bin/bash
            # 環境セットアップ
            cd /home
            git clone https://github.com/pandalize/gcp-image-generation.git
            cd gcp-image-generation/video-generation
            
            # パッケージインストール
            pip install torch torchvision diffusers transformers accelerate xformers
            pip install opencv-python-headless imageio imageio-ffmpeg moviepy
            pip install stable-video-diffusion tqdm
            
            # 動画生成開始
            python image-to-video-pipeline.py --mode massive --num-videos $VIDEOS_PER_VM
            
            # 結果をCloud Storageにアップロード
            gsutil -m cp -r outputs/videos gs://your-bucket/video-outputs/vm-${VM_ID}/
            
            # 完了後自動シャットダウン
            sudo shutdown -h now" \
        --scopes=https://www.googleapis.com/auth/cloud-platform \
        --preemptible &
}

# Cloud Storageバケットの作成
echo "Cloud Storageバケットを作成..."
gsutil mb -p $(gcloud config get-value project) gs://video-generation-outputs-$(date +%s)/ 2>/dev/null

# 複数VMを並列起動
echo "VMを並列起動中..."
for i in $(seq 1 $NUM_VMS); do
    create_video_vm $i
done

wait

echo ""
echo "すべてのVMが起動しました！"
echo ""
echo "進捗を監視:"
echo "  watch 'gcloud compute instances list --filter=\"name:video-gen-gpu\"'"
echo ""
echo "ログを確認:"
echo "  gcloud compute instances get-serial-port-output <instance-name> --zone=us-central1-a"
echo ""
echo "生成された動画を確認:"
echo "  gsutil ls -l gs://your-bucket/video-outputs/"