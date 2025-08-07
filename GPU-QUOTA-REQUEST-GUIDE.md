# GCP GPU クォータ増加申請ガイド

## 🚨 問題の概要

- **地域別クォータ**: T4=1台、V100=1台、L4=1台 ✅
- **グローバルクォータ**: GPUS_ALL_REGIONS = 0台 ❌
- **結果**: どの地域でもGPUが使用不可

## 📋 申請手順（詳細版）

### ステップ1: GCPコンソールにアクセス

1. **ブラウザで開く**:
   ```
   https://console.cloud.google.com/iam-admin/quotas
   ```

2. **プロジェクトを確認**:
   - 右上のプロジェクト選択で正しいプロジェクトが選択されていることを確認
   - プロジェクトID: `your-project-id`

### ステップ2: クォータページの操作

1. **左メニューから選択**:
   ```
   IAMと管理 → 割り当て (Quotas)
   ```

2. **検索フィルターを使用**:
   - 検索ボックスに入力: `GPUS_ALL_REGIONS`
   - または: `Compute Engine API` を選択後、GPUで絞り込み

3. **対象クォータを特定**:
   ```
   サービス: Compute Engine API
   名前: GPUS_ALL_REGIONS
   現在の制限: 0
   使用量: 0
   場所: global
   ```

### ステップ3: クォータ増加申請

1. **クォータ行を選択**:
   - `GPUS_ALL_REGIONS` の行にチェックを入れる

2. **編集ボタンをクリック**:
   - ページ上部の「割り当てを編集」または「EDIT QUOTAS」ボタン

3. **申請フォーム記入**:
   ```
   新しい制限値: 1
   
   申請理由（日本語）:
   AI画像生成プロジェクトでGPUを使用したいため、GPUS_ALL_REGIONSクォータを0から1に増加をお願いします。
   具体的にはStable Diffusion XLを使用した大量画像生成を予定しており、T4またはL4 GPUを1台利用予定です。
   
   申請理由（英語）:
   I would like to increase the GPUS_ALL_REGIONS quota from 0 to 1 for an AI image generation project.
   I plan to use Stable Diffusion XL for bulk image generation with a single T4 or L4 GPU.
   
   連絡先: （あなたのGoogleアカウントのメールアドレス）
   ```

4. **申請を送信**:
   - 「リクエストを送信」または「SUBMIT REQUEST」ボタンをクリック

## ⏱️ 承認時間の目安

| 申請タイプ | 期待時間 | 条件 |
|-----------|---------|------|
| **即時〜2時間** | 最速 | 小規模増加 + 明確な理由 |
| **6〜24時間** | 標準 | 通常の処理時間 |
| **1〜2営業日** | 最長 | 金曜夜・週末申請 |

## 📧 承認通知の確認

### 承認メールの確認
```
件名: [Google Cloud Platform] Quota increase request approved
内容: Your request to increase quotas has been approved...
```

### GCPコンソールでの確認
1. **クォータページで再確認**:
   ```bash
   # CLIでも確認可能
   gcloud compute project-info describe --format="table(quotas.metric,quotas.limit)" | grep GPUS_ALL_REGIONS
   ```

2. **期待する結果**:
   ```
   GPUS_ALL_REGIONS: 1.0
   ```

## 🚀 承認後の次ステップ

### 1. GPU VM作成テスト
```bash
# T4 GPUで即座にテスト
./create-t4-vm-ubuntu.sh
```

### 2. 成功確認
```bash
# SSH接続してGPU確認
gcloud compute ssh image-gen-t4-XXXXX --zone=us-central1-a
nvidia-smi
```

### 3. 画像生成開始
```bash
cd gcp-image-generation
python generate-images.py --num-images 1000 --gpu-optimized
```

## 🛠️ 申請が却下された場合

### 再申請のポイント
1. **より詳細な理由**:
   - プロジェクトの技術的詳細
   - 予想される計算負荷
   - 期間限定使用の明記

2. **段階的申請**:
   - まず地域別クォータ (NVIDIA_T4) を申請
   - 承認後にグローバルクォータを申請

3. **サポートへの問い合わせ**:
   ```
   https://console.cloud.google.com/support
   ```

## 📞 緊急時の代替手段

### 1. CPU VMでの並列処理
```bash
./create-cpu-vm.sh
```
- 即座に利用可能
- 16vCPU で CPU並列処理
- 約200円/時間 × 250時間 = 50,000円

### 2. 他クラウドサービス
- **RunPod**: GPU特化、即座利用可能
- **AWS EC2**: p3.2xlarge (V100)
- **Azure**: NC6s_v3 (V100)

### 3. ローカル + クラウドハイブリッド
- ローカルで少量テスト
- クラウドで本格運用

## 📝 申請状況の追跡

### GCPコンソールでの確認
```
https://console.cloud.google.com/support/cases
```

### 申請番号の記録
- 申請時に発行される Case ID を記録
- 例: `Case #12345678`

## ⚠️ 重要な注意点

1. **プロジェクトごとの申請**: 他プロジェクトでは再度申請が必要
2. **地域制限**: GPUS_ALL_REGIONS ≠ 地域別クォータ
3. **削除後の再利用**: VM削除後はクォータが回復
4. **課金対象**: GPU使用時間に対して課金発生

## 🎯 申請成功のコツ

✅ **具体的な用途を記載**
✅ **期間限定である旨を明記**  
✅ **小規模な増加から開始**
✅ **営業時間内の申請**
✅ **英語での申請理由併記**

---

**申請URL**: https://console.cloud.google.com/iam-admin/quotas

このガイドに従って申請すれば、高確率で24時間以内に承認されるはずです。