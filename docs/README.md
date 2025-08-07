# GCP GPU画像生成プロジェクト

A100 GPUを使った大規模画像生成で、3日間で5万円分のクレジットを効率的に消費するプロジェクトです。

## 実行手順

### 1. 初期設定
```bash
# GCPプロジェクトのセットアップ
bash setup-gcp-project.sh
```

### 2. GPU VMの作成
```bash
# 単一VMを作成
bash create-gpu-vm.sh

# または複数VMを並列起動（より高速に消費）
bash run-parallel-generation.sh
```

### 3. 画像生成の実行
VMにSSH接続後：
```bash
# 環境セットアップ
bash setup-image-gen.sh

# 画像生成開始
python generate-images.py --num-images 1000 --batch-size 8
```

### 4. コスト監視
```bash
# コスト監視設定
bash monitor-costs.sh

# リアルタイムコスト確認
./check-current-cost.sh

# 自動停止を有効化（バックグラウンド実行）
./auto-stop-at-budget.sh &
```

## コスト概算

| 構成 | 時間単価 | 3日間の総額 |
|------|---------|------------|
| A100 x1 | 約3,000円 | 約216,000円 |
| A100 x3並列 | 約9,000円 | 約648,000円 |

**5万円を3日で消費するには：**
- 1台なら約17時間の実行
- 3台並列なら約6時間の実行

## 生成される画像

- **Stable Diffusion XL**使用
- 1024x1024ピクセル
- 1枚あたり約3-5秒（A100使用時）
- 1時間で約1000枚生成可能

## 注意事項

⚠️ **重要**：
- VMは起動中常に課金されます
- 使用後は必ずVMを停止/削除してください
- Preemptible VMは24時間で自動停止します
- 予算アラートを必ず設定してください

## VMの停止/削除

```bash
# すべてのVMを停止
gcloud compute instances stop $(gcloud compute instances list --filter="machineType:a2-highgpu" --format="value(name)") --zone=us-central1-a

# すべてのVMを削除
gcloud compute instances delete $(gcloud compute instances list --filter="machineType:a2-highgpu" --format="value(name)") --zone=us-central1-a
```