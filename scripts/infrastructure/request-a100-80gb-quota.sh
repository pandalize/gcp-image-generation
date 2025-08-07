#!/bin/bash
echo "🚀 A100 80GB クォータ申請ガイド"
echo "=================================="

echo ""
echo "📊 現在のA100 80GBクォータ状況:"
echo "NVIDIA_A100_80GB_GPUS: $(gcloud compute regions describe us-central1 --format='value(quotas[?metric=="NVIDIA_A100_80GB_GPUS"].usage,quotas[?metric=="NVIDIA_A100_80GB_GPUS"].limit)' | tr '\t' '/')"

echo ""
echo "⚠️  A100 80GBは割り当て申請が必須です！"
echo "デフォルト制限: 0台 → 1台に増量申請必要"

echo ""
echo "🔗 申請URL (自動で開きます):"
CONSOLE_URL="https://console.cloud.google.com/iam-admin/quotas?project=gen-lang-client-0106774703&pageState=(%22allQuotasTable%22:(%22f%22:%22%255B%257B_22k_22_3A_22_22_2C_22t_22_3A10_2C_22v_22_3A_22_5C_22NVIDIA_A100_80GB_GPUS_5C_22_22%257D%255D%22))"
echo "$CONSOLE_URL"

echo ""
echo "📝 申請手順:"
echo "1. 上記URLにアクセス（NVIDIA_A100_80GB_GPUSで絞り込み済み）"
echo "2. 'us-central1' のNVIDIA_A100_80GB_GPUS を選択"
echo "3. '割り当ての編集' をクリック"
echo "4. '新しい上限' に '1' を入力"
echo "5. 'リクエストの説明' に以下をコピペ:"

echo ""
echo "========== 申請理由（コピー用） =========="
cat << 'EOT'
研究目的でのAI画像・動画生成プロジェクトにおいて、大規模バッチ処理を実行します。

■ 用途：
- Stable Diffusion XL による高品質画像生成
- ComfyUI を使用したワークフロー自動化
- 商用利用可能モデルでの美女ポートレート生成

■ A100 80GB が必要な理由：
- 80GBの大容量VRAMで複数モデル同時ロード
- 大解像度画像（2048×2048以上）の高速生成
- バッチ処理での効率最適化

■ 使用期間：
- 48時間集中実験（クレジット期限: 2025-08-09）
- 期間終了後は自動削除予定

■ 責任ある使用：
- 適切なコスト管理とモニタリング実施
- 教育・研究目的での使用に限定
EOT
echo "=========================================="

echo ""
echo "💰 A100 80GB コスト情報:"
echo "- 時間単価: ~$5.00/時間"
echo "- 48時間: ~$240"
echo "- 残クレジット: 49,960円 → 十分カバー可能"

echo ""
echo "⏱️  申請処理時間:"
echo "- 通常: 1-3営業日"
echo "- 緊急: 数時間〜1日（理由を詳記）"

echo ""
echo "🔄 申請後の確認:"
echo "gcloud compute regions describe us-central1 --format='value(quotas[?metric==\"NVIDIA_A100_80GB_GPUS\"].limit)'"

echo ""
echo "🚀 承認後のVM作成コマンド:"
cat << 'EOF'
gcloud compute instances create gpu-a100-80gb-beast \
  --zone=us-central1-a \
  --machine-type=a2-highgpu-1g \
  --accelerator=type=nvidia-tesla-a100-80gb,count=1 \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=200GB \
  --boot-disk-type=pd-ssd
EOF