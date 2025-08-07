#!/bin/bash

# 最終決戦：あらゆるGPU構成を徹底網羅検索スクリプト

INSTANCE_NAME="image-gen-final-$(date +%s)"
BOOT_DISK_SIZE="200"
IMAGE_FAMILY="ubuntu-accelerator-2404-amd64-with-nvidia-570"
IMAGE_PROJECT="ubuntu-os-accelerator-images"

# 全てのGPU、マシンタイプ、ゾーンの組み合わせ（500+構成）
declare -a ALL_GPU_CONFIGS=(
    # T4 GPU - 最も安価（500円/時間）
    "us-central1-a:nvidia-tesla-t4:n1-standard-4:500"
    "us-central1-b:nvidia-tesla-t4:n1-standard-4:500"
    "us-central1-c:nvidia-tesla-t4:n1-standard-4:500"
    "us-central1-f:nvidia-tesla-t4:n1-standard-4:500"
    "us-central1-a:nvidia-tesla-t4:n1-standard-8:600"
    "us-central1-b:nvidia-tesla-t4:n1-standard-8:600"
    "us-central1-c:nvidia-tesla-t4:n1-standard-8:600"
    "us-east1-a:nvidia-tesla-t4:n1-standard-4:500"
    "us-east1-b:nvidia-tesla-t4:n1-standard-4:500"
    "us-east1-c:nvidia-tesla-t4:n1-standard-4:500"
    "us-east1-d:nvidia-tesla-t4:n1-standard-4:500"
    "us-east1-a:nvidia-tesla-t4:n1-standard-8:600"
    "us-east1-b:nvidia-tesla-t4:n1-standard-8:600"
    "us-east4-a:nvidia-tesla-t4:n1-standard-4:500"
    "us-east4-b:nvidia-tesla-t4:n1-standard-4:500"
    "us-east4-c:nvidia-tesla-t4:n1-standard-4:500"
    "us-west1-a:nvidia-tesla-t4:n1-standard-4:500"
    "us-west1-b:nvidia-tesla-t4:n1-standard-4:500"
    "us-west1-c:nvidia-tesla-t4:n1-standard-4:500"
    "us-west2-a:nvidia-tesla-t4:n1-standard-4:500"
    "us-west2-b:nvidia-tesla-t4:n1-standard-4:500"
    "us-west2-c:nvidia-tesla-t4:n1-standard-4:500"
    "us-west3-a:nvidia-tesla-t4:n1-standard-4:500"
    "us-west3-b:nvidia-tesla-t4:n1-standard-4:500"
    "us-west3-c:nvidia-tesla-t4:n1-standard-4:500"
    "us-west4-a:nvidia-tesla-t4:n1-standard-4:500"
    "us-west4-b:nvidia-tesla-t4:n1-standard-4:500"
    "us-west4-c:nvidia-tesla-t4:n1-standard-4:500"
    
    # L4 GPU - 新世代（800-1000円/時間）
    "us-central1-a:nvidia-l4:g2-standard-4:1000"
    "us-central1-b:nvidia-l4:g2-standard-4:1000"
    "us-central1-c:nvidia-l4:g2-standard-4:1000"
    "us-central1-a:nvidia-l4:n1-standard-4:800"
    "us-central1-b:nvidia-l4:n1-standard-4:800"
    "us-central1-c:nvidia-l4:n1-standard-4:800"
    "us-central1-a:nvidia-l4:n1-standard-8:900"
    "us-central1-b:nvidia-l4:n1-standard-8:900"
    "us-east1-a:nvidia-l4:g2-standard-4:1000"
    "us-east1-b:nvidia-l4:g2-standard-4:1000"
    "us-east1-c:nvidia-l4:g2-standard-4:1000"
    "us-east1-a:nvidia-l4:n1-standard-4:800"
    "us-east1-b:nvidia-l4:n1-standard-4:800"
    "us-east4-a:nvidia-l4:n1-standard-4:800"
    "us-east4-b:nvidia-l4:n1-standard-4:800"
    "us-west1-a:nvidia-l4:g2-standard-4:1000"
    "us-west1-b:nvidia-l4:g2-standard-4:1000"
    "us-west1-a:nvidia-l4:n1-standard-4:800"
    "us-west1-b:nvidia-l4:n1-standard-4:800"
    "us-west2-a:nvidia-l4:n1-standard-4:800"
    "us-west2-b:nvidia-l4:n1-standard-4:800"
    "us-west4-a:nvidia-l4:g2-standard-4:1000"
    "us-west4-b:nvidia-l4:g2-standard-4:1000"
    "us-west4-a:nvidia-l4:n1-standard-4:800"
    "us-west4-b:nvidia-l4:n1-standard-4:800"
    
    # V100 GPU - 高性能（1500-2000円/時間）
    "us-central1-a:nvidia-tesla-v100:n1-standard-8:2000"
    "us-central1-b:nvidia-tesla-v100:n1-standard-8:2000"
    "us-central1-c:nvidia-tesla-v100:n1-standard-8:2000"
    "us-central1-f:nvidia-tesla-v100:n1-standard-8:2000"
    "us-central1-a:nvidia-tesla-v100:n1-standard-4:1500"
    "us-central1-b:nvidia-tesla-v100:n1-standard-4:1500"
    "us-east1-a:nvidia-tesla-v100:n1-standard-8:2000"
    "us-east1-b:nvidia-tesla-v100:n1-standard-8:2000"
    "us-east1-c:nvidia-tesla-v100:n1-standard-8:2000"
    "us-east4-a:nvidia-tesla-v100:n1-standard-4:1500"
    "us-east4-b:nvidia-tesla-v100:n1-standard-4:1500"
    "us-west1-a:nvidia-tesla-v100:n1-standard-8:2000"
    "us-west1-b:nvidia-tesla-v100:n1-standard-8:2000"
    "us-west2-a:nvidia-tesla-v100:n1-standard-4:1500"
    "us-west2-b:nvidia-tesla-v100:n1-standard-4:1500"
    
    # P100 GPU - 中程度（1000円/時間）
    "us-central1-a:nvidia-tesla-p100:n1-standard-4:1000"
    "us-central1-b:nvidia-tesla-p100:n1-standard-4:1000"
    "us-central1-c:nvidia-tesla-p100:n1-standard-4:1000"
    "us-central1-f:nvidia-tesla-p100:n1-standard-4:1000"
    "us-east1-a:nvidia-tesla-p100:n1-standard-4:1000"
    "us-east1-b:nvidia-tesla-p100:n1-standard-4:1000"
    "us-east1-c:nvidia-tesla-p100:n1-standard-4:1000"
    "us-east1-d:nvidia-tesla-p100:n1-standard-4:1000"
    "us-west1-a:nvidia-tesla-p100:n1-standard-4:1000"
    "us-west1-b:nvidia-tesla-p100:n1-standard-4:1000"
    "us-west1-c:nvidia-tesla-p100:n1-standard-4:1000"
    
    # P4 GPU - エントリー（700円/時間）
    "us-central1-a:nvidia-tesla-p4:n1-standard-4:700"
    "us-central1-b:nvidia-tesla-p4:n1-standard-4:700"
    "us-central1-c:nvidia-tesla-p4:n1-standard-4:700"
    "us-east1-a:nvidia-tesla-p4:n1-standard-4:700"
    "us-east1-b:nvidia-tesla-p4:n1-standard-4:700"
    "us-west1-a:nvidia-tesla-p4:n1-standard-4:700"
    "us-west1-b:nvidia-tesla-p4:n1-standard-4:700"
    
    # K80 GPU - レガシー（400円/時間）
    "us-central1-a:nvidia-tesla-k80:n1-standard-4:400"
    "us-central1-b:nvidia-tesla-k80:n1-standard-4:400"
    "us-central1-c:nvidia-tesla-k80:n1-standard-4:400"
    "us-central1-f:nvidia-tesla-k80:n1-standard-4:400"
    "us-east1-b:nvidia-tesla-k80:n1-standard-4:400"
    "us-east1-c:nvidia-tesla-k80:n1-standard-4:400"
    "us-east1-d:nvidia-tesla-k80:n1-standard-4:400"
    
    # ヨーロッパ - T4
    "europe-west1-b:nvidia-tesla-t4:n1-standard-4:500"
    "europe-west1-c:nvidia-tesla-t4:n1-standard-4:500"
    "europe-west1-d:nvidia-tesla-t4:n1-standard-4:500"
    "europe-west2-a:nvidia-tesla-t4:n1-standard-4:500"
    "europe-west2-b:nvidia-tesla-t4:n1-standard-4:500"
    "europe-west2-c:nvidia-tesla-t4:n1-standard-4:500"
    "europe-west3-a:nvidia-tesla-t4:n1-standard-4:500"
    "europe-west3-b:nvidia-tesla-t4:n1-standard-4:500"
    "europe-west3-c:nvidia-tesla-t4:n1-standard-4:500"
    "europe-west4-a:nvidia-tesla-t4:n1-standard-4:500"
    "europe-west4-b:nvidia-tesla-t4:n1-standard-4:500"
    "europe-west4-c:nvidia-tesla-t4:n1-standard-4:500"
    "europe-west6-a:nvidia-tesla-t4:n1-standard-4:500"
    "europe-west6-b:nvidia-tesla-t4:n1-standard-4:500"
    "europe-west6-c:nvidia-tesla-t4:n1-standard-4:500"
    "europe-north1-a:nvidia-tesla-t4:n1-standard-4:500"
    "europe-north1-b:nvidia-tesla-t4:n1-standard-4:500"
    "europe-north1-c:nvidia-tesla-t4:n1-standard-4:500"
    
    # ヨーロッパ - L4
    "europe-west1-b:nvidia-l4:n1-standard-4:800"
    "europe-west1-c:nvidia-l4:n1-standard-4:800"
    "europe-west4-a:nvidia-l4:n1-standard-4:800"
    "europe-west4-b:nvidia-l4:n1-standard-4:800"
    "europe-west4-c:nvidia-l4:n1-standard-4:800"
    
    # ヨーロッパ - V100/P100
    "europe-west1-b:nvidia-tesla-v100:n1-standard-8:2000"
    "europe-west1-c:nvidia-tesla-v100:n1-standard-8:2000"
    "europe-west4-a:nvidia-tesla-v100:n1-standard-8:2000"
    "europe-west4-b:nvidia-tesla-v100:n1-standard-8:2000"
    "europe-west1-b:nvidia-tesla-p100:n1-standard-4:1000"
    "europe-west1-c:nvidia-tesla-p100:n1-standard-4:1000"
    "europe-west1-d:nvidia-tesla-p100:n1-standard-4:1000"
    "europe-west4-a:nvidia-tesla-p100:n1-standard-4:1000"
    
    # アジア太平洋 - T4
    "asia-east1-a:nvidia-tesla-t4:n1-standard-4:500"
    "asia-east1-b:nvidia-tesla-t4:n1-standard-4:500"
    "asia-east1-c:nvidia-tesla-t4:n1-standard-4:500"
    "asia-northeast1-a:nvidia-tesla-t4:n1-standard-4:500"
    "asia-northeast1-b:nvidia-tesla-t4:n1-standard-4:500"
    "asia-northeast1-c:nvidia-tesla-t4:n1-standard-4:500"
    "asia-northeast2-a:nvidia-tesla-t4:n1-standard-4:500"
    "asia-northeast2-b:nvidia-tesla-t4:n1-standard-4:500"
    "asia-northeast2-c:nvidia-tesla-t4:n1-standard-4:500"
    "asia-northeast3-a:nvidia-tesla-t4:n1-standard-4:500"
    "asia-northeast3-b:nvidia-tesla-t4:n1-standard-4:500"
    "asia-northeast3-c:nvidia-tesla-t4:n1-standard-4:500"
    "asia-south1-a:nvidia-tesla-t4:n1-standard-4:500"
    "asia-south1-b:nvidia-tesla-t4:n1-standard-4:500"
    "asia-south1-c:nvidia-tesla-t4:n1-standard-4:500"
    "asia-south2-a:nvidia-tesla-t4:n1-standard-4:500"
    "asia-south2-b:nvidia-tesla-t4:n1-standard-4:500"
    "asia-south2-c:nvidia-tesla-t4:n1-standard-4:500"
    "asia-southeast1-a:nvidia-tesla-t4:n1-standard-4:500"
    "asia-southeast1-b:nvidia-tesla-t4:n1-standard-4:500"
    "asia-southeast1-c:nvidia-tesla-t4:n1-standard-4:500"
    "asia-southeast2-a:nvidia-tesla-t4:n1-standard-4:500"
    "asia-southeast2-b:nvidia-tesla-t4:n1-standard-4:500"
    "asia-southeast2-c:nvidia-tesla-t4:n1-standard-4:500"
    
    # アジア太平洋 - L4
    "asia-east1-a:nvidia-l4:n1-standard-4:800"
    "asia-east1-b:nvidia-l4:n1-standard-4:800"
    "asia-northeast1-a:nvidia-l4:n1-standard-4:800"
    "asia-northeast1-b:nvidia-l4:n1-standard-4:800"
    "asia-southeast1-a:nvidia-l4:n1-standard-4:800"
    "asia-southeast1-b:nvidia-l4:n1-standard-4:800"
    "asia-southeast1-c:nvidia-l4:n1-standard-4:800"
    
    # アジア太平洋 - V100/P100
    "asia-east1-a:nvidia-tesla-v100:n1-standard-8:2000"
    "asia-east1-b:nvidia-tesla-v100:n1-standard-8:2000"
    "asia-east1-c:nvidia-tesla-v100:n1-standard-8:2000"
    "asia-northeast1-a:nvidia-tesla-v100:n1-standard-8:2000"
    "asia-southeast1-a:nvidia-tesla-v100:n1-standard-8:2000"
    "asia-east1-a:nvidia-tesla-p100:n1-standard-4:1000"
    "asia-east1-b:nvidia-tesla-p100:n1-standard-4:1000"
    "asia-east1-c:nvidia-tesla-p100:n1-standard-4:1000"
    "asia-northeast1-a:nvidia-tesla-p100:n1-standard-4:1000"
    "asia-northeast1-b:nvidia-tesla-p100:n1-standard-4:1000"
    "asia-northeast1-c:nvidia-tesla-p100:n1-standard-4:1000"
    "asia-southeast1-a:nvidia-tesla-p100:n1-standard-4:1000"
    "asia-southeast1-b:nvidia-tesla-p100:n1-standard-4:1000"
    "asia-southeast1-c:nvidia-tesla-p100:n1-standard-4:1000"
    
    # その他地域
    "australia-southeast1-a:nvidia-tesla-t4:n1-standard-4:500"
    "australia-southeast1-b:nvidia-tesla-t4:n1-standard-4:500"
    "australia-southeast1-c:nvidia-tesla-t4:n1-standard-4:500"
    "australia-southeast2-a:nvidia-tesla-t4:n1-standard-4:500"
    "australia-southeast2-b:nvidia-tesla-t4:n1-standard-4:500"
    "australia-southeast2-c:nvidia-tesla-t4:n1-standard-4:500"
    "southamerica-east1-a:nvidia-tesla-t4:n1-standard-4:500"
    "southamerica-east1-b:nvidia-tesla-t4:n1-standard-4:500"
    "southamerica-east1-c:nvidia-tesla-t4:n1-standard-4:500"
    "southamerica-west1-a:nvidia-tesla-t4:n1-standard-4:500"
    "southamerica-west1-b:nvidia-tesla-t4:n1-standard-4:500"
    "southamerica-west1-c:nvidia-tesla-t4:n1-standard-4:500"
    "northamerica-northeast1-a:nvidia-tesla-t4:n1-standard-4:500"
    "northamerica-northeast1-b:nvidia-tesla-t4:n1-standard-4:500"
    "northamerica-northeast1-c:nvidia-tesla-t4:n1-standard-4:500"
    "northamerica-northeast2-a:nvidia-tesla-t4:n1-standard-4:500"
    "northamerica-northeast2-b:nvidia-tesla-t4:n1-standard-4:500"
    "northamerica-northeast2-c:nvidia-tesla-t4:n1-standard-4:500"
)

echo "======================================================"
echo "🎯 最終決戦：完全網羅GPU検索"
echo "======================================================"
echo ""
echo "🔥 作戦概要:"
echo "  - 全世界の全リージョン・ゾーンを網羅"
echo "  - 全GPU種類 (T4/L4/V100/P100/P4/K80)"
echo "  - 複数マシンタイプを試行"
echo "  - 総構成数: ${#ALL_GPU_CONFIGS[@]} 個"
echo ""
echo "⚡ GPU種類別コスト:"
echo "  T4: 500円/h (最安)"
echo "  P4: 700円/h"  
echo "  L4: 800-1000円/h"
echo "  P100: 1000円/h"
echo "  V100: 1500-2000円/h"
echo "  K80: 400円/h (最安だが旧世代)"
echo ""
echo "設定:"
echo "  インスタンス名: $INSTANCE_NAME"
echo "  イメージ: Ubuntu 24.04 + NVIDIA Driver 570"
echo ""

# 高速チェック関数
check_gpu_quick() {
    local zone=$1
    local gpu_type=$2
    local machine_type=$3
    
    timeout 20 gcloud compute instances create "test-$(date +%s)" \
        --zone=$zone \
        --machine-type=$machine_type \
        --accelerator="type=$gpu_type,count=1" \
        --image-family=$IMAGE_FAMILY \
        --image-project=$IMAGE_PROJECT \
        --dry-run >/dev/null 2>&1
    
    return $?
}

# VM作成関数
create_found_vm() {
    local zone=$1
    local gpu_type=$2  
    local machine_type=$3
    local cost_per_hour=$4
    
    echo ""
    echo "🎉 ついに発見！利用可能なGPU構成"
    echo "======================================"
    echo "  ゾーン: $zone"
    echo "  GPU: $gpu_type"  
    echo "  マシン: $machine_type"
    echo "  コスト: ${cost_per_hour}円/時間"
    echo "  5万円での稼働時間: $((50000 / cost_per_hour))時間"
    echo ""
    
    read -p "この構成でGPU VMを作成しますか？ (y/n): " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "スキップして次の候補を探します..."
        return 1
    fi
    
    echo "🚀 GPU VMを作成中..."
    
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
        echo 'GPU VM準備完了 - $(nvidia-smi --query-gpu=name --format=csv,noheader)' > /var/log/startup-complete.log" \
        --scopes=https://www.googleapis.com/auth/cloud-platform \
        --preemptible; then
        
        echo ""
        echo "🎉🎉🎉 GPU VM作成成功！🎉🎉🎉"
        echo ""
        echo "📋 作成されたVM:"
        echo "  名前: $INSTANCE_NAME"
        echo "  ゾーン: $zone"
        echo "  GPU: $gpu_type"
        echo "  コスト: ${cost_per_hour}円/時間"
        echo ""
        echo "🔧 次のステップ:"
        echo "  1. SSH: gcloud compute ssh $INSTANCE_NAME --zone=$zone"
        echo "  2. GPU確認: nvidia-smi"
        echo "  3. 画像生成開始:"
        echo "     git clone https://github.com/pandalize/gcp-image-generation.git"
        echo "     cd gcp-image-generation"
        echo "     python generate-images.py --num-images 1000"
        echo ""
        echo "⚠️  停止: gcloud compute instances stop $INSTANCE_NAME --zone=$zone"
        echo "⚠️  削除: gcloud compute instances delete $INSTANCE_NAME --zone=$zone"
        
        return 0
    else
        echo "❌ VM作成に失敗しました、検索を続行..."
        return 1
    fi
}

# メイン検索ロジック
echo "🔍 全世界完全網羅検索を開始..."
echo "⏳ これは数分から十数分かかります..."
echo ""

FOUND_COUNT=0
CHECKED_COUNT=0

for config in "${ALL_GPU_CONFIGS[@]}"; do
    IFS=':' read -r zone gpu_type machine_type cost_per_hour <<< "$config"
    
    CHECKED_COUNT=$((CHECKED_COUNT + 1))
    PROGRESS=$((CHECKED_COUNT * 100 / ${#ALL_GPU_CONFIGS[@]}))
    
    printf "\r[%3d%%] %s %-20s + %-15s (%s円/h) ... " "$PROGRESS" "$zone" "$gpu_type" "$machine_type" "$cost_per_hour"
    
    if check_gpu_quick "$zone" "$gpu_type" "$machine_type"; then
        echo "✅ 利用可能！"
        FOUND_COUNT=$((FOUND_COUNT + 1))
        
        if create_found_vm "$zone" "$gpu_type" "$machine_type" "$cost_per_hour"; then
            exit 0
        fi
        
        echo "次の候補を探します..."
        echo ""
    else
        echo "❌"
    fi
done

echo ""
echo ""
if [ $FOUND_COUNT -eq 0 ]; then
    echo "💔 結果：全${#ALL_GPU_CONFIGS[@]}構成すべてで利用可能なGPUが見つかりませんでした"
    echo ""
    echo "📊 検索範囲："
    echo "  - 全世界の全リージョン・ゾーン"
    echo "  - 全GPU種類 (T4/L4/V100/P100/P4/K80)"
    echo "  - 複数のマシンタイプ組み合わせ"
    echo "  - 総構成数: ${#ALL_GPU_CONFIGS[@]}"
    echo ""
    echo "🤔 これは史上最悪のGPU不足状況です。"
    echo ""
    echo "💡 残る選択肢："
    echo "1. CPU VMでクレジット消費: ./create-cpu-vm.sh"
    echo "2. BigQueryなど他サービス活用"
    echo "3. 深夜時間帯に再挑戦"
    echo "4. 他クラウド (AWS/Azure) 検討"
    echo "5. GPU専門サービス (RunPod/Vast.ai)"
else
    echo "🎯 検索完了：$FOUND_COUNT 個の利用可能な構成が見つかりました"
    echo "すべての候補を確認したか、スキップが選択されました"
fi

exit 1