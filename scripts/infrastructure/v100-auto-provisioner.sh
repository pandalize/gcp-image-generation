#!/bin/bash

# V100 GPU自動確保スクリプト
# 日本時間午前3時から確保できるまでリトライ
# 2025年8月7日作成

# 設定
TARGET_TIME="03:00"  # 日本時間午前3時
INSTANCE_NAME="v100-controlnet-juggernaut"
ZONES=("us-central1-a" "us-central1-b" "us-central1-c" "us-central1-f" "us-west1-a" "us-west1-b" "asia-east1-a" "us-east1-a" "us-east1-c")
MACHINE_TYPE="n1-highmem-4"
GPU_TYPE="nvidia-tesla-v100"
GPU_COUNT=1
DISK_SIZE="200GB"
IMAGE_FAMILY="debian-12"
IMAGE_PROJECT="debian-cloud"
MAX_ATTEMPTS=100
LOG_FILE="/tmp/v100_provisioning.log"

# ログ関数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 現在時刻チェック関数
is_target_time() {
    current_time=$(date +%H:%M)
    target_hour=$(echo $TARGET_TIME | cut -d: -f1)
    current_hour=$(echo $current_time | cut -d: -f1)
    
    # 午前3時〜6時の間を許可
    if [[ $current_hour -ge $target_hour && $current_hour -lt 06 ]]; then
        return 0
    else
        return 1
    fi
}

# V100インスタンス作成試行
try_create_instance() {
    local zone=$1
    local attempt=$2
    
    log "Attempt $attempt: Trying to create V100 instance in zone $zone"
    
    # インスタンス作成コマンド実行
    gcloud compute instances create "$INSTANCE_NAME" \
        --zone="$zone" \
        --machine-type="$MACHINE_TYPE" \
        --accelerator="type=$GPU_TYPE,count=$GPU_COUNT" \
        --image-family="$IMAGE_FAMILY" \
        --image-project="$IMAGE_PROJECT" \
        --boot-disk-size="$DISK_SIZE" \
        --boot-disk-type="pd-ssd" \
        --maintenance-policy="TERMINATE" \
        --restart-on-failure \
        --metadata="startup-script=#!/bin/bash
# NVIDIA Driver自動インストール
apt-get update
apt-get install -y wget curl
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
echo 'deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://nvidia.github.io/libnvidia-container/stable/deb/$(ARCH) /' | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
apt-get update
apt-get install -y nvidia-driver-535 nvidia-utils-535
nvidia-smi -pm 1
echo 'V100 GPU setup complete' > /tmp/gpu_setup_done" 2>&1
    
    local exit_code=$?
    
    if [[ $exit_code -eq 0 ]]; then
        log "SUCCESS: V100 instance created successfully in zone $zone!"
        log "Instance name: $INSTANCE_NAME"
        log "Zone: $zone"
        log "External IP: $(gcloud compute instances describe $INSTANCE_NAME --zone=$zone --format='value(networkInterfaces[0].accessConfigs[0].natIP)' 2>/dev/null)"
        return 0
    else
        log "FAILED: Could not create V100 instance in zone $zone"
        return 1
    fi
}

# 時刻待機関数
wait_for_target_time() {
    log "Waiting for target time: $TARGET_TIME JST"
    
    while ! is_target_time; do
        current_time=$(date +%H:%M)
        log "Current time: $current_time, waiting for $TARGET_TIME..."
        sleep 300  # 5分ごとにチェック
    done
    
    log "Target time reached! Starting V100 provisioning..."
}

# メイン実行ループ
main() {
    log "=== V100 Auto Provisioner Started ==="
    log "Target time: $TARGET_TIME JST"
    log "Instance name: $INSTANCE_NAME"
    log "Max attempts: $MAX_ATTEMPTS (5 min intervals = ~8 hours total)"
    log "Estimated end time: 11:00 AM JST"
    log "Zones to try: ${ZONES[@]}"
    
    # 時刻待機（午前3時まで）
    if ! is_target_time; then
        wait_for_target_time
    else
        log "Already in target time window, starting immediately"
    fi
    
    local attempt=1
    local success=false
    
    # 確保できるまでリトライ
    while [[ $attempt -le $MAX_ATTEMPTS ]] && [[ "$success" == "false" ]]; do
        log "=== Attempt $attempt/$MAX_ATTEMPTS ==="
        
        # 全ゾーンを順番に試行
        for zone in "${ZONES[@]}"; do
            log "Trying zone: $zone"
            
            if try_create_instance "$zone" "$attempt"; then
                success=true
                log "=== V100 INSTANCE PROVISIONED SUCCESSFULLY ==="
                
                # 成功通知とセットアップ開始
                log "Starting automated setup..."
                
                # ComfyUI + ControlNet + Juggernaut XL v10自動セットアップ
                sleep 60  # インスタンス起動待機
                
                log "Initiating ComfyUI setup on V100 instance..."
                gcloud compute ssh "$INSTANCE_NAME" --zone="$zone" --command="
                # 基本パッケージインストール
                sudo apt-get update && sudo apt-get install -y python3 python3-pip git
                
                # ComfyUI取得
                cd /home/\$(whoami)
                git clone https://github.com/comfyanonymous/ComfyUI.git
                cd ComfyUI
                pip3 install -r requirements.txt
                
                # ディレクトリ作成
                mkdir -p models/checkpoints models/controlnet custom_nodes
                
                echo 'V100 ComfyUI setup initiated' > /tmp/comfyui_setup_started
                " &
                
                log "V100 instance setup initiated in background"
                break
            fi
            
            # ゾーン間で30秒待機
            sleep 30
        done
        
        if [[ "$success" == "false" ]]; then
            attempt=$((attempt + 1))
            log "All zones failed for attempt $attempt. Waiting 5 minutes before retry..."
            log "Estimated completion time: $((5 * (MAX_ATTEMPTS - attempt + 1))) minutes remaining"
            sleep 300  # 5分待機
        fi
    done
    
    if [[ "$success" == "false" ]]; then
        log "FAILED: Could not provision V100 instance after $MAX_ATTEMPTS attempts"
        log "Recommendation: Try manual provisioning or wait for different time"
        exit 1
    else
        log "SUCCESS: V100 auto-provisioning completed!"
        log "Next steps:"
        log "1. SSH to instance: gcloud compute ssh $INSTANCE_NAME --zone=<successful_zone>"
        log "2. Check ComfyUI setup: cat /tmp/comfyui_setup_started"
        log "3. Complete ControlNet + Juggernaut XL v10 setup"
        exit 0
    fi
}

# スクリプト実行
main "$@"