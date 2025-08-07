#!/bin/bash
echo "🔍 GCP GPU クォータ詳細確認スクリプト"
echo "=============================================="

echo ""
echo "📊 全リージョン GPU クォータ概要:"
gcloud compute project-info describe --format="value(quotas.metric,quotas.limit,quotas.usage)" | grep -i nvidia | while IFS=$'\t' read -r metric limit usage; do
    if [[ "$limit" != "0.0" ]]; then
        echo "✅ $metric: $usage/$limit"
    fi
done

echo ""
echo "📍 us-central1 リージョン 詳細:"
echo "NVIDIA_A100_GPUS: $(gcloud compute regions describe us-central1 --format='value(quotas[?metric=="NVIDIA_A100_GPUS"].limit,quotas[?metric=="NVIDIA_A100_GPUS"].usage)' | tr '\t' '/')"
echo "NVIDIA_A100_80GB_GPUS: $(gcloud compute regions describe us-central1 --format='value(quotas[?metric=="NVIDIA_A100_80GB_GPUS"].limit,quotas[?metric=="NVIDIA_A100_80GB_GPUS"].usage)' | tr '\t' '/')"
echo "NVIDIA_V100_GPUS: $(gcloud compute regions describe us-central1 --format='value(quotas[?metric=="NVIDIA_V100_GPUS"].limit,quotas[?metric=="NVIDIA_V100_GPUS"].usage)' | tr '\t' '/')"
echo "NVIDIA_L4_GPUS: $(gcloud compute regions describe us-central1 --format='value(quotas[?metric=="NVIDIA_L4_GPUS"].limit,quotas[?metric=="NVIDIA_L4_GPUS"].usage)' | tr '\t' '/')"
echo "NVIDIA_T4_GPUS: $(gcloud compute regions describe us-central1 --format='value(quotas[?metric=="NVIDIA_T4_GPUS"].limit,quotas[?metric=="NVIDIA_T4_GPUS"].usage)' | tr '\t' '/')"

echo ""
echo "💰 GPU コスト比較 (1時間あたり):"
echo "🔥 A100 (40GB):     ~$3.00-4.00/時間 ⚡ 最高性能"  
echo "🔥 A100 (80GB):     ~$4.00-5.00/時間 ⚡ 超大容量"
echo "💎 V100 (16GB):     ~$2.50-3.00/時間 💪 高性能"
echo "✨ L4 (23GB):       ~$0.75-1.00/時間 💰 現在使用中"
echo "⚡ T4 (16GB):       ~$0.50-0.75/時間 💸 最安値"

echo ""
echo "🎯 推奨アクション:"
echo "1. A100クォータ申請 → 最大性能での生成"
echo "2. 複数L4並列 → コスパ重視の大量生成"
echo "3. V100活用 → 高性能とコストのバランス"

echo ""
echo "📝 クォータ申請方法:"
echo "1. https://console.cloud.google.com/iam-admin/quotas"
echo "2. 'NVIDIA_A100_GPUS' で検索"  
echo "3. 'us-central1' 選択"
echo "4. '増加をリクエスト' → 数量指定"