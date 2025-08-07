#!/bin/bash

echo "======================================================"
echo "🩺 GPU問題の根本原因診断スクリプト"
echo "======================================================"
echo ""
echo "すべてのGPU組み合わせが無効だった原因を調査します"
echo ""

# 基本情報の確認
echo "=== 1. 基本環境確認 ==="
echo "プロジェクトID: $(gcloud config get-value project)"
echo "アカウント: $(gcloud config get-value account)"
echo "デフォルトゾーン: $(gcloud config get-value compute/zone)"
echo "デフォルトリージョン: $(gcloud config get-value compute/region)"
echo ""

# APIの有効化状況確認
echo "=== 2. 必要なAPI有効化状況 ==="
echo "Compute Engine API:"
gcloud services list --enabled --filter="name:compute.googleapis.com" --format="value(name)" | head -1
echo "Cloud Billing API:"
gcloud services list --enabled --filter="name:cloudbilling.googleapis.com" --format="value(name)" | head -1
echo ""

# 課金アカウント状況
echo "=== 3. 課金アカウント確認 ==="
gcloud billing accounts list --format="table(name,displayName,open)"
echo ""
echo "プロジェクトの課金アカウント:"
gcloud billing projects describe $(gcloud config get-value project) --format="value(billingAccountName)" 2>/dev/null || echo "課金アカウント未設定または権限なし"
echo ""

# 最もシンプルなVMテスト
echo "=== 4. 基本VMテスト（GPUなし） ==="
echo "テスト: n1-standard-4 基本VM"
if gcloud compute instances create test-basic-vm \
    --zone=us-central1-a \
    --machine-type=n1-standard-4 \
    --dry-run > /dev/null 2>&1; then
    echo "  ✅ 基本VMは作成可能"
else
    echo "  ❌ 基本VMも作成不可 - 根本的な問題あり"
fi
echo ""

# イメージ指定テスト
echo "=== 5. イメージ指定テスト ==="
echo "テスト: Ubuntu 20.04 LTS"
if gcloud compute instances create test-ubuntu-vm \
    --zone=us-central1-a \
    --machine-type=n1-standard-4 \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --dry-run > /dev/null 2>&1; then
    echo "  ✅ Ubuntu 20.04イメージ利用可能"
else
    echo "  ❌ Ubuntu 20.04イメージ利用不可"
fi

echo "テスト: Ubuntu Accelerator Image"
if gcloud compute instances create test-accelerator-vm \
    --zone=us-central1-a \
    --machine-type=n1-standard-4 \
    --image-family=ubuntu-accelerator-2404-amd64-with-nvidia-570 \
    --image-project=ubuntu-os-accelerator-images \
    --dry-run > /dev/null 2>&1; then
    echo "  ✅ Ubuntu Acceleratorイメージ利用可能"
else
    echo "  ❌ Ubuntu Acceleratorイメージ利用不可"
fi
echo ""

# 詳細GPU テスト（エラー出力付き）
echo "=== 6. 詳細GPUテスト（エラー出力） ==="
echo ""
echo "T4 GPU テスト詳細:"
gcloud compute instances create test-t4-detailed \
    --zone=us-central1-a \
    --machine-type=n1-standard-4 \
    --maintenance-policy=TERMINATE \
    --accelerator="type=nvidia-tesla-t4,count=1" \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --metadata="install-nvidia-driver=True" \
    --dry-run 2>&1 | head -10
echo ""

echo "L4 GPU テスト詳細:"
gcloud compute instances create test-l4-detailed \
    --zone=us-central1-a \
    --machine-type=g2-standard-4 \
    --maintenance-policy=TERMINATE \
    --accelerator="type=nvidia-l4,count=1" \
    --image-family=ubuntu-accelerator-2404-amd64-with-nvidia-570 \
    --image-project=ubuntu-os-accelerator-images \
    --metadata="install-nvidia-driver=True" \
    --dry-run 2>&1 | head -10
echo ""

# クォータ詳細確認
echo "=== 7. GPU クォータ詳細 ==="
echo "us-central1のGPUクォータ:"
gcloud compute regions describe us-central1 --format="table(quotas.metric,quotas.limit,quotas.usage)" | grep -i gpu
echo ""

# 権限確認
echo "=== 8. IAM権限確認 ==="
echo "現在のユーザー権限:"
gcloud projects get-iam-policy $(gcloud config get-value project) --flatten="bindings[].members" --format="table(bindings.role)" --filter="bindings.members:$(gcloud config get-value account)" | head -10
echo ""

# GPU利用可能ゾーンの確認
echo "=== 9. GPU利用可能ゾーン確認 ==="
echo "T4 GPU利用可能ゾーン:"
gcloud compute accelerator-types list --filter="name:nvidia-tesla-t4" --format="table(zone)" | head -5
echo ""

echo "L4 GPU利用可能ゾーン:"
gcloud compute accelerator-types list --filter="name:nvidia-l4" --format="table(zone)" | head -5
echo ""

echo "======================================================"
echo "🩺 診断完了"
echo "======================================================"
echo ""
echo "💡 分析結果に基づいて問題を特定し、解決策を提示します"