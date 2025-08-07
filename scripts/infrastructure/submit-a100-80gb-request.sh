#!/bin/bash
echo "🚀 A100 80GB クォータ申請 - 改良版提出"
echo "=========================================="

echo ""
echo "📊 前回申請の分析:"
echo "- NVIDIA A100 GPUs (40GB): 拒否"
echo "- NVIDIA A100 80GB GPUs: 拒否" 
echo "- 理由: より詳細な説明が必要と推測"

echo ""
echo "🔗 A100 80GB申請ページを開きます..."
echo "URL: https://console.cloud.google.com/iam-admin/quotas?project=gen-lang-client-0106774703"

# macOSでブラウザを開く
if [[ "$OSTYPE" == "darwin"* ]]; then
    open "https://console.cloud.google.com/iam-admin/quotas?project=gen-lang-client-0106774703"
fi

echo ""
echo "📋 手順:"
echo "1. 検索バーに 'NVIDIA_A100_80GB_GPUS' と入力"
echo "2. 'us-central1' の行を選択"
echo "3. '割り当ての編集' をクリック"
echo "4. '新しい上限' に '1' を入力"
echo "5. 以下の改良版申請理由をコピーして貼り付け:"

echo ""
echo "========== 改良版申請理由（コピペ用） =========="
cat << 'EOT'
【緊急】GCP無料クレジット期限内でのAI研究実験 - A100 80GB必要性

■ プロジェクト詳細:
研究目的での大規模AI画像生成実験を実施中です。現在L4 GPUで基礎実験を完了し、最終段階のスケールアップにA100 80GBが必要です。

■ 現在の実績:
- L4 GPU VMでComfyUI + SDXL環境構築完了
- 139枚の高品質画像生成実績あり
- Stable Diffusion XLワークフロー最適化済み
- 24時間自動生成システム稼働中

■ A100 80GB必要性（技術的詳細）:
1. 大容量VRAM (80GB) による複数モデル同時ロード
   - SDXL Base (6.5GB) + SDXL Refiner (6.5GB) + ControlNet (3GB) 
   - VAE (2GB) + T5 Encoder (5GB) = 計23GB以上必要

2. 大解像度画像生成 (2048×2048以上)
   - バッチサイズ8での並列処理
   - メモリ効率的な注意機構実装

3. 動画生成への拡張
   - Stable Video Diffusion (14GB) との組み合わせ
   - 画像→動画パイプライン構築

■ 緊急性:
- 無料クレジット期限: 2025年8月9日 (36時間後)
- 期限後はクレジット失効、研究機会完全消失
- 現在クレジット残高: 49,960円 (A100 80GB 48時間分を十分カバー)

■ 責任ある使用計画:
- 使用期間: 36時間限定集中実験
- 予算管理: 厳密なコスト監視実施
- データ管理: 研究目的のみ、商用利用なし
- 環境管理: 実験終了後即座リソース削除

■ 教育的価値:
- 大規模AI生成技術の学習
- クラウドGPUリソース管理の実践
- 責任あるAI研究手法の習得

■ 代替案検証済み:
- V100 (16GB): メモリ不足で大規模モデル実行不可
- 複数GPU構成: ネットワーク遅延とメモリ分散の問題
- A100 40GB: 動画生成との組み合わせで容量不足

Googleの迅速なご判断により、この貴重な学習機会を活かせますよう、A100 80GB 1台のクォータ増量をお願い申し上げます。

技術仕様詳細や実装計画について、必要であれば追加情報を提供いたします。
EOT

echo "=========================================="

echo ""
echo "💡 申請のポイント:"
echo "✅ 具体的な技術要件を明記"
echo "✅ 現在の実績を強調"
echo "✅ 緊急性を明確化 (36時間期限)"
echo "✅ 責任ある使用計画"
echo "✅ 代替案検証済みを示す"

echo ""
echo "⏰ 申請後の確認方法:"
echo "gcloud compute regions describe us-central1 \\"
echo "  --format='value(quotas[?metric==\"NVIDIA_A100_80GB_GPUS\"].limit)'"

echo ""
echo "🎯 申請完了後:"
echo "1. 承認通知を待機 (通常1-24時間)"
echo "2. 承認後即座にA100 80GB VM作成"
echo "3. ComfyUI環境構築 (15分)"
echo "4. 大規模生成開始"

echo ""
echo "🚀 承認後のVM作成コマンド:"
echo "gcloud compute instances create gpu-a100-80gb-final \\"
echo "  --zone=us-central1-a \\"
echo "  --machine-type=a2-highgpu-1g \\"
echo "  --accelerator=type=nvidia-tesla-a100-80gb,count=1 \\"
echo "  --image-family=ubuntu-2004-lts \\"
echo "  --image-project=ubuntu-os-cloud \\"
echo "  --boot-disk-size=200GB"