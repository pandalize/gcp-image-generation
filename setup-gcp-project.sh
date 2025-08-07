#!/bin/bash

# GCPプロジェクトの初期設定
PROJECT_ID="image-gen-project-$(date +%s)"
REGION="us-central1"
ZONE="us-central1-a"

echo "=== GCP画像生成プロジェクトのセットアップ ==="

# プロジェクトIDの設定
echo "1. プロジェクトを作成または選択..."
gcloud projects create $PROJECT_ID --name="Image Generation Project" 2>/dev/null || \
read -p "既存のプロジェクトIDを入力してください: " PROJECT_ID

gcloud config set project $PROJECT_ID

# 必要なAPIの有効化
echo "2. 必要なAPIを有効化中..."
gcloud services enable compute.googleapis.com
gcloud services enable storage-api.googleapis.com
gcloud services enable monitoring.googleapis.com

# 請求アカウントのリンク
echo "3. 請求アカウントをリンク..."
BILLING_ACCOUNT=$(gcloud billing accounts list --format="value(name)" --limit=1)
if [ ! -z "$BILLING_ACCOUNT" ]; then
    gcloud billing projects link $PROJECT_ID --billing-account=$BILLING_ACCOUNT
    echo "請求アカウントをリンクしました: $BILLING_ACCOUNT"
else
    echo "警告: 請求アカウントが見つかりません。手動でリンクしてください。"
fi

# デフォルトのリージョンとゾーンを設定
gcloud config set compute/region $REGION
gcloud config set compute/zone $ZONE

echo "プロジェクトID: $PROJECT_ID"
echo "リージョン: $REGION"
echo "ゾーン: $ZONE"
echo ""
echo "セットアップ完了！次にcreate-gpu-vm.shを実行してVMを作成してください。"