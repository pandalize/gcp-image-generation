#!/bin/bash

# 複数ゾーン・GPU自動チェック＆VM作成スクリプト

# 設定
INSTANCE_NAME="image-gen-gpu-$(date +%s)"
BOOT_DISK_SIZE="200"
IMAGE_FAMILY="ubuntu-accelerator-2404-amd64-with-nvidia-570"
IMAGE_PROJECT="ubuntu-os-accelerator-images"

# 試行するゾーンとGPU構成（優先順位順）
declare -a CONFIGS=(
    "us-central1-b:nvidia-tesla-t4:n1-standard-4:500"
    "us-central1-c:nvidia-tesla-t4:n1-standard-4:500"  
    "us-central1-f:nvidia-tesla-t4:n1-standard-4:500"
    "us-east1-b:nvidia-tesla-t4:n1-standard-4:500"
    "us-east1-c:nvidia-tesla-t4:n1-standard-4:500"
    "us-west1-b:nvidia-tesla-t4:n1-standard-4:500"
    "us-west2-b:nvidia-tesla-t4:n1-standard-4:500"
    "us-central1-a:nvidia-tesla-v100:n1-standard-8:2000"
    "us-central1-b:nvidia-tesla-v100:n1-standard-8:2000"
    "us-east1-b:nvidia-tesla-v100:n1-standard-8:2000"
    "us-central1-a:nvidia-tesla-p100:n1-standard-4:1000"
    "us-central1-b:nvidia-tesla-p100:n1-standard-4:1000"
)

echo "======================================================"
echo "🔍 GPU VM自動作成スクリプト"
echo "======================================================"
echo ""
echo "設定:"
echo "  インスタンス名: $INSTANCE_NAME"
echo "  イメージ: Ubuntu 24.04 + NVIDIA Driver 570"
echo "  試行候補: ${#CONFIGS[@]} 個のゾーン・GPU構成"
echo ""

# 利用可能性チェック関数
check_availability() {
    local zone=$1
    local gpu_type=$2
    local machine_type=$3
    
    gcloud compute instances create "test-check-$(date +%s)" \
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
        # 基本セットアップ
        apt-get update
        apt-get install -y python3-pip python3-venv git wget curl
        echo 'GPU VM準備完了' > /var/log/startup-complete.log" \
        --scopes=https://www.googleapis.com/auth/cloud-platform \
        --preemptible; then
        
        echo ""
        echo "✅ GPU VMの作成に成功しました！"
        echo ""
        echo "📋 VM情報:"
        echo "  名前: $INSTANCE_NAME"
        echo "  ゾーン: $zone"
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
echo "🔍 利用可能なGPU構成を検索中..."
echo ""

for config in "${CONFIGS[@]}"; do
    IFS=':' read -r zone gpu_type machine_type cost_per_hour <<< "$config"
    
    echo -n "  [$zone] $gpu_type + $machine_type (${cost_per_hour}円/h) ... "
    
    if check_availability "$zone" "$gpu_type" "$machine_type"; then
        echo "✅ 利用可能"
        echo ""
        echo "💡 利用可能な構成を発見："
        echo "  ゾーン: $zone"
        echo "  GPU: $gpu_type"  
        echo "  マシン: $machine_type"
        echo "  コスト: ${cost_per_hour}円/時間"
        echo ""
        
        read -p "この構成でVMを作成しますか？ (y/n): " -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            create_vm "$zone" "$gpu_type" "$machine_type" "$cost_per_hour"
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
echo "😞 すべてのGPU構成で利用可能なものが見つかりませんでした。"
echo ""
echo "💡 解決策:"
echo "1. 時間を置いて再実行"  
echo "2. 他のリージョンを試す"
echo "3. CPUのみのVMで代替"
echo "4. 他のクラウドプロバイダーを検討"
echo ""
echo "CPU VM作成スクリプト: ./create-cpu-vm.sh（代替案）"

exit 1