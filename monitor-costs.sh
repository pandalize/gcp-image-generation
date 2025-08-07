#!/bin/bash

# コスト監視とアラート設定スクリプト

PROJECT_ID=$(gcloud config get-value project)
BUDGET_AMOUNT=50000  # 5万円
ALERT_THRESHOLDS="0.5 0.75 0.9 1.0"  # 50%, 75%, 90%, 100%でアラート

echo "=== コスト監視の設定 ==="

# 1. 予算アラートの作成
echo "1. 予算アラートを設定中..."
gcloud billing budgets create \
    --billing-account=$(gcloud billing accounts list --format="value(name)" --limit=1) \
    --display-name="Image Generation Budget" \
    --budget-amount=$BUDGET_AMOUNT \
    --threshold-rule=percent=0.5 \
    --threshold-rule=percent=0.75 \
    --threshold-rule=percent=0.9 \
    --threshold-rule=percent=1.0 \
    --all-updates-rule \
    --project=$PROJECT_ID

# 2. リアルタイムコスト確認関数
cat > check-current-cost.sh << 'EOF'
#!/bin/bash

echo "=== 現在のコスト状況 ==="
echo ""

# 実行中のインスタンス
echo "実行中のGPUインスタンス:"
gcloud compute instances list --filter="machineType:a2-highgpu" --format="table(name,status,machineType,creationTimestamp)"

# 実行時間の計算
INSTANCES=$(gcloud compute instances list --filter="machineType:a2-highgpu AND status=RUNNING" --format="value(name)")
TOTAL_HOURS=0
ESTIMATED_COST=0

for instance in $INSTANCES; do
    CREATED=$(gcloud compute instances describe $instance --zone=us-central1-a --format="value(creationTimestamp)")
    HOURS_RUN=$(( ($(date +%s) - $(date -d "$CREATED" +%s)) / 3600 ))
    COST=$((HOURS_RUN * 3000))
    echo "  - $instance: ${HOURS_RUN}時間実行中, 推定コスト: ${COST}円"
    TOTAL_HOURS=$((TOTAL_HOURS + HOURS_RUN))
    ESTIMATED_COST=$((ESTIMATED_COST + COST))
done

echo ""
echo "合計実行時間: ${TOTAL_HOURS}時間"
echo "推定累積コスト: ${ESTIMATED_COST}円"
echo "残り予算: $((50000 - ESTIMATED_COST))円"
echo ""

if [ $ESTIMATED_COST -gt 40000 ]; then
    echo "⚠️ 警告: コストが予算の80%を超えています！"
    echo "VMの停止を検討してください:"
    echo "gcloud compute instances stop --zone=us-central1-a \$(gcloud compute instances list --filter='machineType:a2-highgpu' --format='value(name)')"
fi
EOF

chmod +x check-current-cost.sh

# 3. 自動停止スクリプト
cat > auto-stop-at-budget.sh << 'EOF'
#!/bin/bash

MAX_BUDGET=45000  # 4.5万円で自動停止（安全マージン）

while true; do
    # コスト計算
    INSTANCES=$(gcloud compute instances list --filter="machineType:a2-highgpu AND status=RUNNING" --format="value(name)")
    ESTIMATED_COST=0
    
    for instance in $INSTANCES; do
        CREATED=$(gcloud compute instances describe $instance --zone=us-central1-a --format="value(creationTimestamp)")
        HOURS_RUN=$(( ($(date +%s) - $(date -d "$CREATED" +%s)) / 3600 ))
        COST=$((HOURS_RUN * 3000))
        ESTIMATED_COST=$((ESTIMATED_COST + COST))
    done
    
    echo "[$(date)] 現在のコスト: ${ESTIMATED_COST}円"
    
    if [ $ESTIMATED_COST -gt $MAX_BUDGET ]; then
        echo "予算上限に達しました！すべてのVMを停止します..."
        for instance in $INSTANCES; do
            gcloud compute instances stop $instance --zone=us-central1-a
        done
        echo "すべてのVMを停止しました。"
        break
    fi
    
    sleep 300  # 5分ごとにチェック
done
EOF

chmod +x auto-stop-at-budget.sh

echo ""
echo "コスト監視設定完了！"
echo ""
echo "使用方法:"
echo "  現在のコストを確認: ./check-current-cost.sh"
echo "  自動停止を有効化: ./auto-stop-at-budget.sh &"
echo ""
echo "手動でVMを停止:"
echo "  gcloud compute instances stop --zone=us-central1-a \$(gcloud compute instances list --filter='machineType:a2-highgpu' --format='value(name)')"