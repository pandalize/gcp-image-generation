#!/bin/bash

# L4 GPU付きVM作成スクリプト（最新GPU、在庫がある可能性大）

INSTANCE_NAME="image-gen-l4-$(date +%s)"
BOOT_DISK_SIZE="200"
IMAGE_FAMILY="ubuntu-accelerator-2404-amd64-with-nvidia-570"
IMAGE_PROJECT="ubuntu-os-accelerator-images"

# L4 GPUに対応したゾーンとマシンタイプ
declare -a L4_CONFIGS=(
    "us-central1-a:nvidia-l4:g2-standard-4:1000"
    "us-central1-b:nvidia-l4:g2-standard-4:1000"
    "us-central1-c:nvidia-l4:g2-standard-4:1000"
    "us-east1-a:nvidia-l4:g2-standard-4:1000"
    "us-east1-b:nvidia-l4:g2-standard-4:1000"
    "us-east1-c:nvidia-l4:g2-standard-4:1000"
    "us-west1-a:nvidia-l4:g2-standard-4:1000"
    "us-west1-b:nvidia-l4:g2-standard-4:1000"
    "us-west4-a:nvidia-l4:g2-standard-4:1000"
    "us-west4-b:nvidia-l4:g2-standard-4:1000"
    "europe-west1-b:nvidia-l4:g2-standard-4:1000"
    "europe-west1-c:nvidia-l4:g2-standard-4:1000"
    "europe-west4-a:nvidia-l4:g2-standard-4:1000"
    "europe-west4-b:nvidia-l4:g2-standard-4:1000"
    "asia-southeast1-a:nvidia-l4:g2-standard-4:1000"
    "asia-southeast1-b:nvidia-l4:g2-standard-4:1000"
    "asia-southeast1-c:nvidia-l4:g2-standard-4:1000"
)

echo "======================================================"
echo "🚀 L4 GPU VM作成スクリプト"
echo "======================================================"
echo ""
echo "💡 L4 GPU の特徴:"
echo "  - 最新のAda Lovelaceアーキテクチャ"
echo "  - T4より高性能、V100並みの能力"
echo "  - 推定コスト: 約1,000円/時間"
echo "  - 5万円で約50時間稼働可能"
echo "  - 在庫がある可能性が最も高い"
echo ""
echo "設定:"
echo "  インスタンス名: $INSTANCE_NAME"
echo "  イメージ: Ubuntu 24.04 + NVIDIA Driver 570"
echo "  試行候補: ${#L4_CONFIGS[@]} 個のL4対応ゾーン"
echo ""

# 利用可能性チェック関数
check_l4_availability() {
    local zone=$1
    local gpu_type=$2
    local machine_type=$3
    
    timeout 30 gcloud compute instances create "test-l4-$(date +%s)" \
        --zone=$zone \
        --machine-type=$machine_type \
        --accelerator="type=$gpu_type,count=1" \
        --image-family=$IMAGE_FAMILY \
        --image-project=$IMAGE_PROJECT \
        --dry-run > /dev/null 2>&1
    
    return $?
}

# VM作成関数
create_l4_vm() {
    local zone=$1
    local gpu_type=$2  
    local machine_type=$3
    local cost_per_hour=$4
    
    echo "🚀 L4 GPU VMを作成中..."
    echo "  ゾーン: $zone"
    echo "  GPU: $gpu_type"  
    echo "  マシン: $machine_type"
    echo "  コスト: ${cost_per_hour}円/時間"
    echo ""
    
    if gcloud compute instances create $INSTANCE_NAME \
        --zone=$zone \
        --machine-type=$machine_type \
        --maintenance-policy=TERMINATE \
        --accelerator="type=$gpu_type,count=1" \
        --image-family=$IMAGE_FAMILY \
        --image-project=$IMAGE_PROJECT \
        --boot-disk-size=$BOOT_DISK_SIZE \
        --boot-disk-type=pd-ssd \
        --metadata="install-nvidia-driver=True,startup-script=#!/bin/bash
        # L4 GPU用セットアップ
        apt-get update
        apt-get install -y python3-pip python3-venv git wget curl
        echo 'L4 GPU VM準備完了' > /var/log/startup-complete.log
        echo 'GPU情報:' >> /var/log/startup-complete.log
        nvidia-smi >> /var/log/startup-complete.log" \
        --scopes=https://www.googleapis.com/auth/cloud-platform \
        --preemptible; then
        
        echo ""
        echo "🎉 L4 GPU VMの作成に成功しました！"
        echo ""
        echo "📋 VM情報:"
        echo "  名前: $INSTANCE_NAME"
        echo "  ゾーン: $zone"
        echo "  GPU: NVIDIA L4 (Ada Lovelace)"
        echo "  性能: T4の約2倍、V100に近い性能"
        echo "  コスト: ${cost_per_hour}円/時間"
        echo "  5万円での稼働時間: $((50000 / cost_per_hour))時間"
        echo ""
        echo "🔧 次のステップ:"
        echo "  1. SSH接続: gcloud compute ssh $INSTANCE_NAME --zone=$zone"
        echo "  2. GPU確認: nvidia-smi"
        echo "  3. リポジトリ取得: git clone https://github.com/pandalize/gcp-image-generation.git"
        echo "  4. 画像生成開始:"
        echo "     cd gcp-image-generation"
        echo "     python generate-images.py --num-images 1000 --batch-size 4"
        echo ""
        echo "💡 L4最適化設定:"
        echo "  - バッチサイズ 4-8 推奨"
        echo "  - 1024x1024解像度対応"
        echo "  - FP16での高速生成"
        echo ""
        echo "⚠️  重要な管理コマンド:"
        echo "  停止: gcloud compute instances stop $INSTANCE_NAME --zone=$zone"
        echo "  削除: gcloud compute instances delete $INSTANCE_NAME --zone=$zone"
        
        return 0
    else
        echo "❌ L4 VM作成に失敗しました"
        return 1
    fi
}

# メインロジック
echo "🔍 L4 GPU利用可能ゾーンを検索中..."
echo ""

for config in "${L4_CONFIGS[@]}"; do
    IFS=':' read -r zone gpu_type machine_type cost_per_hour <<< "$config"
    
    echo -n "  [$zone] $gpu_type + $machine_type (${cost_per_hour}円/h) ... "
    
    if check_l4_availability "$zone" "$gpu_type" "$machine_type"; then
        echo "✅ 利用可能"
        echo ""
        echo "💡 L4 GPUが利用可能です！"
        echo "  ゾーン: $zone"
        echo "  性能: T4の約2倍"  
        echo "  コスト: ${cost_per_hour}円/時間"
        echo ""
        
        read -p "この構成でL4 GPU VMを作成しますか？ (y/n): " -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            create_l4_vm "$zone" "$gpu_type" "$machine_type" "$cost_per_hour"
            if [ $? -eq 0 ]; then
                exit 0
            fi
        else
            echo "スキップして次の候補を探します..."
            echo ""
        fi
    else
        echo "❌ 利用不可"
    fi
done

echo ""
echo "😞 すべてのL4構成で利用可能なものが見つかりませんでした。"
echo ""
echo "💡 次の手順:"
echo "1. 数時間後に再実行"
echo "2. CPU VMで代替: ./create-cpu-vm.sh"  
echo "3. 他のクラウドサービスを検討"

exit 1