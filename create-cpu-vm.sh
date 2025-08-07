#!/bin/bash

# CPU専用VM作成スクリプト（GPU利用不可時の代替案）

INSTANCE_NAME="image-gen-cpu-$(date +%s)"
ZONE="us-central1-b"
MACHINE_TYPE="e2-standard-8"  # 8 vCPU, 32GB RAM
BOOT_DISK_SIZE="200"
IMAGE_FAMILY="ubuntu-2204-lts"
IMAGE_PROJECT="ubuntu-os-cloud"

echo "======================================================"
echo "💻 CPU専用VM作成（GPU代替案）"
echo "======================================================"
echo ""
echo "⚠️  警告: CPUのみでの画像生成は非常に時間がかかります"
echo "  - GPU比で100-1000倍遅い"
echo "  - 軽量モデルのテスト用途推奨"
echo "  - 本格的な画像生成にはGPU必須"
echo ""
echo "設定:"
echo "  インスタンス名: $INSTANCE_NAME"
echo "  マシンタイプ: $MACHINE_TYPE (8 vCPU, 32GB RAM)"
echo "  推定コスト: 約80円/時間"
echo "  5万円での稼働時間: 約600時間"
echo ""

read -p "CPUのみで続行しますか？ (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "キャンセルしました"
    echo "GPUが利用可能になったら ./find-and-create-gpu-vm.sh を実行してください"
    exit 1
fi

echo "CPU専用VMを作成中..."

if gcloud compute instances create $INSTANCE_NAME \
    --zone=$ZONE \
    --machine-type=$MACHINE_TYPE \
    --image-family=$IMAGE_FAMILY \
    --image-project=$IMAGE_PROJECT \
    --boot-disk-size=$BOOT_DISK_SIZE \
    --boot-disk-type=pd-ssd \
    --metadata="startup-script=#!/bin/bash
    # 基本セットアップ
    apt-get update
    apt-get install -y python3-pip python3-venv git wget curl build-essential
    echo 'CPU VM準備完了' > /var/log/startup-complete.log" \
    --scopes=https://www.googleapis.com/auth/cloud-platform \
    --preemptible; then
    
    echo ""
    echo "✅ CPU専用VMの作成に成功しました！"
    echo ""
    echo "📋 VM情報:"
    echo "  名前: $INSTANCE_NAME" 
    echo "  ゾーン: $ZONE"
    echo "  スペック: 8 vCPU, 32GB RAM"
    echo "  コスト: 約80円/時間"
    echo ""
    echo "🔧 次のステップ:"
    echo "  1. SSH接続: gcloud compute ssh $INSTANCE_NAME --zone=$ZONE"
    echo "  2. リポジトリ取得: git clone https://github.com/pandelize/gcp-image-generation.git"
    echo "  3. CPU用軽量設定:"
    echo "     cd gcp-image-generation"
    echo "     pip install torch torchvision diffusers transformers --index-url https://download.pytorch.org/whl/cpu"
    echo "     python generate-images.py --num-images 10 --batch-size 1"
    echo ""
    echo "💡 CPU最適化のヒント:"
    echo "  - 小さいバッチサイズ（1-2）を使用"
    echo "  - 低解像度（512x512）で生成"
    echo "  - 軽量モデルを選択"  
    echo "  - 生成枚数を少なくして時間節約"
    echo ""
    echo "⚠️  管理コマンド:"
    echo "  停止: gcloud compute instances stop $INSTANCE_NAME --zone=$ZONE"
    echo "  削除: gcloud compute instances delete $INSTANCE_NAME --zone=$ZONE"
    
else
    echo ""
    echo "❌ CPU VM作成に失敗しました"
    exit 1
fi