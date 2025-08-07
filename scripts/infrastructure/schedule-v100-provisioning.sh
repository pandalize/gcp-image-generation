#!/bin/bash

# V100自動確保スケジュール実行スクリプト
# 日本時間午前3時に自動実行開始

SCRIPT_DIR="/Users/fujinoyuki/Desktop/gcp/scripts/infrastructure"
PROVISIONER_SCRIPT="$SCRIPT_DIR/v100-auto-provisioner.sh"
LOG_FILE="/tmp/v100_scheduler.log"

# ログ関数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 現在時刻と目標時刻チェック
check_time_until_3am() {
    current_hour=$(date +%H)
    current_min=$(date +%M)
    
    # 午前3時までの秒数を計算
    if [[ $current_hour -lt 3 ]]; then
        # 今日の午前3時
        hours_until=$((3 - current_hour))
        mins_until=$((0 - current_min))
        if [[ $mins_until -lt 0 ]]; then
            hours_until=$((hours_until - 1))
            mins_until=$((60 + mins_until))
        fi
    elif [[ $current_hour -eq 3 ]]; then
        # 既に午前3時
        hours_until=0
        mins_until=0
    else
        # 明日の午前3時
        hours_until=$((24 - current_hour + 3))
        mins_until=$((0 - current_min))
        if [[ $mins_until -lt 0 ]]; then
            hours_until=$((hours_until - 1))
            mins_until=$((60 + mins_until))
        fi
    fi
    
    total_seconds=$((hours_until * 3600 + mins_until * 60))
    echo $total_seconds
}

main() {
    log "=== V100 Auto Provisioning Scheduler Started ==="
    log "Current time: $(date)"
    log "Provisioner script: $PROVISIONER_SCRIPT"
    
    # スクリプト存在確認
    if [[ ! -f "$PROVISIONER_SCRIPT" ]]; then
        log "ERROR: Provisioner script not found: $PROVISIONER_SCRIPT"
        exit 1
    fi
    
    # 実行権限確認
    if [[ ! -x "$PROVISIONER_SCRIPT" ]]; then
        log "Making provisioner script executable..."
        chmod +x "$PROVISIONER_SCRIPT"
    fi
    
    # 午前3時までの待機時間計算
    seconds_until_3am=$(check_time_until_3am)
    hours=$((seconds_until_3am / 3600))
    minutes=$(((seconds_until_3am % 3600) / 60))
    
    if [[ $seconds_until_3am -eq 0 ]]; then
        log "Already 3:00 AM! Starting V100 provisioning immediately..."
    else
        log "Time until 3:00 AM: ${hours}h ${minutes}m (${seconds_until_3am} seconds)"
        log "Waiting until 3:00 AM to start V100 provisioning..."
        
        # 定期的にステータス更新
        while [[ $seconds_until_3am -gt 0 ]]; do
            if [[ $seconds_until_3am -gt 3600 ]]; then
                # 1時間以上残っている場合は30分ごと
                sleep 1800
                seconds_until_3am=$(check_time_until_3am)
                hours=$((seconds_until_3am / 3600))
                minutes=$(((seconds_until_3am % 3600) / 60))
                log "Time remaining until 3:00 AM: ${hours}h ${minutes}m"
            elif [[ $seconds_until_3am -gt 600 ]]; then
                # 10分以上残っている場合は5分ごと
                sleep 300
                seconds_until_3am=$(check_time_until_3am)
                minutes=$((seconds_until_3am / 60))
                log "Time remaining until 3:00 AM: ${minutes} minutes"
            else
                # 10分未満の場合は1分ごと
                sleep 60
                seconds_until_3am=$(check_time_until_3am)
                if [[ $seconds_until_3am -gt 0 ]]; then
                    log "Time remaining until 3:00 AM: ${seconds_until_3am} seconds"
                fi
            fi
        done
    fi
    
    # 午前3時になったのでV100確保開始
    log "=== 3:00 AM REACHED - STARTING V100 PROVISIONING ==="
    log "Executing: $PROVISIONER_SCRIPT"
    
    # バックグラウンドで実行（端末を閉じても継続）
    nohup "$PROVISIONER_SCRIPT" > "/tmp/v100_provisioning_output.log" 2>&1 &
    provisioner_pid=$!
    
    log "V100 provisioner started with PID: $provisioner_pid"
    log "Monitor progress: tail -f /tmp/v100_provisioning.log"
    log "Full output: tail -f /tmp/v100_provisioning_output.log"
    
    # プロセス監視を少し行う
    sleep 10
    if ps -p $provisioner_pid > /dev/null; then
        log "V100 provisioner is running successfully"
        log "Scheduler task completed - provisioner will continue until V100 is secured"
    else
        log "WARNING: V100 provisioner may have exited early"
        log "Check logs for details: /tmp/v100_provisioning_output.log"
    fi
    
    log "=== Scheduler task completed ==="
}

# バックグラウンド実行の場合
if [[ "$1" == "--background" ]]; then
    nohup "$0" > "$LOG_FILE" 2>&1 &
    echo "V100 scheduler started in background"
    echo "Monitor: tail -f $LOG_FILE"
    exit 0
fi

main "$@"