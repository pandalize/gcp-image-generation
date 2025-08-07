#!/bin/bash

# 全世界のリージョンでGPU VM自動検索＆作成スクリプト

INSTANCE_NAME="image-gen-gpu-$(date +%s)"
BOOT_DISK_SIZE="200"
IMAGE_FAMILY="ubuntu-accelerator-2404-amd64-with-nvidia-570"
IMAGE_PROJECT="ubuntu-os-accelerator-images"

# より多くのリージョン・ゾーンを網羅（優先順位順）
declare -a CONFIGS=(
    # T4 GPU（最も安価）- アジア太平洋
    "asia-southeast1-a:nvidia-tesla-t4:n1-standard-4:500"
    "asia-southeast1-b:nvidia-tesla-t4:n1-standard-4:500"
    "asia-southeast1-c:nvidia-tesla-t4:n1-standard-4:500"
    "asia-northeast1-a:nvidia-tesla-t4:n1-standard-4:500"
    "asia-northeast1-b:nvidia-tesla-t4:n1-standard-4:500"
    "asia-northeast1-c:nvidia-tesla-t4:n1-standard-4:500"
    "asia-east1-a:nvidia-tesla-t4:n1-standard-4:500"
    "asia-east1-b:nvidia-tesla-t4:n1-standard-4:500"
    "asia-east1-c:nvidia-tesla-t4:n1-standard-4:500"
    
    # T4 GPU - ヨーロッパ
    "europe-west1-b:nvidia-tesla-t4:n1-standard-4:500"
    "europe-west1-c:nvidia-tesla-t4:n1-standard-4:500"
    "europe-west1-d:nvidia-tesla-t4:n1-standard-4:500"
    "europe-west2-a:nvidia-tesla-t4:n1-standard-4:500"
    "europe-west2-b:nvidia-tesla-t4:n1-standard-4:500"
    "europe-west2-c:nvidia-tesla-t4:n1-standard-4:500"
    "europe-west4-a:nvidia-tesla-t4:n1-standard-4:500"
    "europe-west4-b:nvidia-tesla-t4:n1-standard-4:500"
    "europe-west4-c:nvidia-tesla-t4:n1-standard-4:500"
    
    # T4 GPU - 南米・その他
    "southamerica-east1-a:nvidia-tesla-t4:n1-standard-4:500"
    "southamerica-east1-b:nvidia-tesla-t4:n1-standard-4:500"
    "southamerica-east1-c:nvidia-tesla-t4:n1-standard-4:500"
    "australia-southeast1-a:nvidia-tesla-t4:n1-standard-4:500"
    "australia-southeast1-b:nvidia-tesla-t4:n1-standard-4:500"
    "australia-southeast1-c:nvidia-tesla-t4:n1-standard-4:500"
    
    # 米国の追加ゾーン
    "us-central1-a:nvidia-tesla-t4:n1-standard-4:500"
    "us-central1-b:nvidia-tesla-t4:n1-standard-4:500"
    "us-central1-c:nvidia-tesla-t4:n1-standard-4:500"
    "us-central1-f:nvidia-tesla-t4:n1-standard-4:500"
    "us-east1-b:nvidia-tesla-t4:n1-standard-4:500"
    "us-east1-c:nvidia-tesla-t4:n1-standard-4:500"
    "us-east1-d:nvidia-tesla-t4:n1-standard-4:500"
    "us-west1-a:nvidia-tesla-t4:n1-standard-4:500"
    "us-west1-b:nvidia-tesla-t4:n1-standard-4:500"
    "us-west1-c:nvidia-tesla-t4:n1-standard-4:500"
    "us-west2-a:nvidia-tesla-t4:n1-standard-4:500"
    "us-west2-b:nvidia-tesla-t4:n1-standard-4:500"
    "us-west2-c:nvidia-tesla-t4:n1-standard-4:500"
    "us-west4-a:nvidia-tesla-t4:n1-standard-4:500"
    "us-west4-b:nvidia-tesla-t4:n1-standard-4:500"
    "us-west4-c:nvidia-tesla-t4:n1-standard-4:500"
    
    # V100 GPU（高性能）
    "us-central1-a:nvidia-tesla-v100:n1-standard-8:2000"
    "us-central1-b:nvidia-tesla-v100:n1-standard-8:2000"
    "us-central1-f:nvidia-tesla-v100:n1-standard-8:2000"
    "us-east1-b:nvidia-tesla-v100:n1-standard-8:2000"
    "us-east1-c:nvidia-tesla-v100:n1-standard-8:2000"
    "us-west1-a:nvidia-tesla-v100:n1-standard-8:2000"
    "us-west1-b:nvidia-tesla-v100:n1-standard-8:2000"
    "europe-west4-a:nvidia-tesla-v100:n1-standard-8:2000"
    "europe-west4-b:nvidia-tesla-v100:n1-standard-8:2000"
    "asia-east1-a:nvidia-tesla-v100:n1-standard-8:2000"
    "asia-east1-c:nvidia-tesla-v100:n1-standard-8:2000"
    
    # P100 GPU（中程度）
    "us-central1-a:nvidia-tesla-p100:n1-standard-4:1000"
    "us-central1-b:nvidia-tesla-p100:n1-standard-4:1000"
    "us-central1-c:nvidia-tesla-p100:n1-standard-4:1000"
    "us-central1-f:nvidia-tesla-p100:n1-standard-4:1000"
    "us-east1-b:nvidia-tesla-p100:n1-standard-4:1000"
    "us-east1-c:nvidia-tesla-p100:n1-standard-4:1000"
    "us-west1-a:nvidia-tesla-p100:n1-standard-4:1000"
    "us-west1-b:nvidia-tesla-p100:n1-standard-4:1000"
    "europe-west1-b:nvidia-tesla-p100:n1-standard-4:1000"
    "europe-west1-c:nvidia-tesla-p100:n1-standard-4:1000"
    "asia-east1-a:nvidia-tesla-p100:n1-standard-4:1000"
    "asia-east1-c:nvidia-tesla-p100:n1-standard-4:1000"
)

echo "======================================================"
echo "🌍 全世界GPU VM検索スクリプト"
echo "======================================================"
echo ""
echo "設定:"
echo "  インスタンス名: $INSTANCE_NAME"
echo "  イメージ: Ubuntu 24.04 + NVIDIA Driver 570"
echo "  試行候補: ${#CONFIGS[@]} 個の全世界ゾーン・GPU構成"
echo "  対象リージョン: アジア、ヨーロッパ、南米、オーストラリア、米国"
echo ""

# 利用可能性チェック関数（高速化）
check_availability() {
    local zone=$1
    local gpu_type=$2
    local machine_type=$3
    
    timeout 30 gcloud compute instances create "test-check-$(date +%s)" \
        --zone=$zone \
        --machine-type=$machine_type \
        --accelerator="type=$gpu_type,count=1" \
        --image-family=$IMAGE_FAMILY \
        --image-project=$IMAGE_PROJECT \
        --dry-run > /dev/null 2>&1
    
    return $?
}

# VM作成関数
create_vm() {
    local zone=$1
    local gpu_type=$2  
    local machine_type=$3
    local cost_per_hour=$4
    
    echo "🚀 VM作成を開始..."
    echo "  ゾーン: $zone"
    echo "  GPU: $gpu_type"  
    echo "  マシン: $machine_type"
    echo "  コスト: ${cost_per_hour}円/時間"
    echo "  地域: $(echo $zone | cut -d'-' -f1-2)"
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
        apt-get update
        apt-get install -y python3-pip python3-venv git wget curl
        echo 'GPU VM準備完了' > /var/log/startup-complete.log" \
        --scopes=https://www.googleapis.com/auth/cloud-platform \
        --preemptible; then
        
        echo ""
        echo "🎉 GPU VMの作成に成功しました！"
        echo ""
        echo "📋 VM情報:"
        echo "  名前: $INSTANCE_NAME"
        echo "  ゾーン: $zone ($(echo $zone | cut -d'-' -f1-2))"
        echo "  GPU: $gpu_type"
        echo "  コスト: ${cost_per_hour}円/時間"
        echo "  5万円での稼働時間: $((50000 / cost_per_hour))時間"
        echo ""
        echo "🔧 次のステップ:"
        echo "  1. SSH接続: gcloud compute ssh $INSTANCE_NAME --zone=$zone"
        echo "  2. 環境確認: nvidia-smi"
        echo "  3. リポジトリ取得: git clone https://github.com/pandalize/gcp-image-generation.git"
        echo "  4. 画像生成開始: cd gcp-image-generation && python generate-images.py"
        echo ""
        echo "⚠️  重要な管理コマンド:"
        echo "  停止: gcloud compute instances stop $INSTANCE_NAME --zone=$zone"
        echo "  削除: gcloud compute instances delete $INSTANCE_NAME --zone=$zone"
        
        return 0
    else
        echo "❌ VM作成に失敗しました"
        return 1
    fi
}

# メインロジック
echo "🔍 全世界でGPU構成を検索中..."
echo "⏳ これには数分かかる場合があります..."
echo ""

FOUND_COUNT=0

for config in "${CONFIGS[@]}"; do
    IFS=':' read -r zone gpu_type machine_type cost_per_hour <<< "$config"
    
    region=$(echo $zone | cut -d'-' -f1-2)
    echo -n "  [$region/$zone] $gpu_type (${cost_per_hour}円/h) ... "
    
    if check_availability "$zone" "$gpu_type" "$machine_type"; then
        echo "✅ 利用可能"
        FOUND_COUNT=$((FOUND_COUNT + 1))
        
        echo ""
        echo "💡 利用可能な構成を発見："
        echo "  地域: $region"
        echo "  ゾーン: $zone"
        echo "  GPU: $gpu_type"  
        echo "  マシン: $machine_type"
        echo "  コスト: ${cost_per_hour}円/時間"
        echo ""
        
        read -p "この構成でVMを作成しますか？ (y/n/s[kip]): " -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            create_vm "$zone" "$gpu_type" "$machine_type" "$cost_per_hour"
            if [ $? -eq 0 ]; then
                exit 0
            fi
        elif [[ $REPLY =~ ^[Ss]$ ]]; then
            echo "スキップして次の候補を探します..."
            echo ""
        else
            echo "検索を終了します"
            exit 0
        fi
    else
        echo "❌ 利用不可"
    fi
done

echo ""
if [ $FOUND_COUNT -eq 0 ]; then
    echo "😞 全世界のすべてのGPU構成で利用可能なものが見つかりませんでした。"
    echo ""
    echo "💡 解決策:"
    echo "1. 数時間後に再実行（GPU需要が高い時間帯を避ける）"  
    echo "2. CPU VMで代替: ./create-cpu-vm.sh"
    echo "3. 他のクラウドプロバイダー（AWS、Azure）を検討"
    echo "4. GPU専門サービス（Runpod、Vast.ai）を検討"
else
    echo "🔍 検索完了: $FOUND_COUNT 個の利用可能な構成が見つかりました"
    echo "すべての利用可能な構成を確認したか、スキップ/終了が選択されました"
fi

exit 1