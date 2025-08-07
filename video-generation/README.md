# GCP AI動画生成プロジェクト

A100 GPUを使用した大規模AI動画生成システム。画像生成から動画変換まで完全自動化。

## 🎬 プロジェクト概要

**画像→動画の定番ワークフロー：**
1. **Stable Diffusion XL**で高品質キーフレーム生成
2. **Stable Video Diffusion**で画像を動画化
3. **AnimateDiff**でスムーズなアニメーション
4. 高度なエフェクトと後処理

## 📊 コスト・パフォーマンス

| 構成 | 時間単価 | 24時間 | 生成可能数 |
|------|---------|--------|-----------|
| A100 x1 | 3,000円 | 72,000円 | 動画100本 |
| A100 x3 | 9,000円 | 216,000円 | 動画300本 |
| A100 x5 | 15,000円 | 360,000円 | 動画500本 |

**5万円で生成可能：**
- 約16時間稼働
- 約50-70本の高品質動画（各30秒）
- 数千枚のキーフレーム画像

## 🚀 クイックスタート

### 1. 環境セットアップ

```bash
# VMにSSH接続後
cd video-generation
bash setup-video-env.sh
```

### 2. 単一動画生成

```bash
# 基本的な画像→動画変換
python image-to-video-pipeline.py \
  --mode single \
  --prompts "sunset over ocean" "tropical beach" "waves crashing" \
  --output my_video.mp4
```

### 3. 大量生成モード

```bash
# 100本の動画を自動生成
python image-to-video-pipeline.py \
  --mode massive \
  --num-videos 100
```

### 4. 並列処理（複数VM）

```bash
# 5台のVMで並列実行
bash parallel-video-generation.sh
```

## 🎨 生成される動画の種類

### 基本パイプライン
- **解像度**: 768x768 → 1920x1080（アップスケール）
- **フレームレート**: 30fps
- **動画長**: 15-30秒
- **スタイル**: フォトリアル、アニメ、油絵風など

### 高度なエフェクト
```bash
# クリエイティブモード（スタイル変換付き）
python advanced-video-effects.py --mode creative

# タイムラプス生成
python advanced-video-effects.py --mode timelapse \
  --prompt "flower blooming time-lapse"

# モーフィング動画
python advanced-video-effects.py --mode morphing
```

## 📁 プロジェクト構造

```
video-generation/
├── setup-video-env.sh              # 環境構築
├── image-to-video-pipeline.py      # メインパイプライン
├── advanced-video-effects.py       # 高度なエフェクト
├── parallel-video-generation.sh    # 並列処理
└── outputs/
    ├── images/     # キーフレーム画像
    ├── videos/     # 生成動画
    └── final/      # 最終出力
```

## 🛠️ 技術スタック

### モデル
- **Stable Diffusion XL**: キーフレーム生成
- **Stable Video Diffusion**: img2vid変換
- **AnimateDiff**: アニメーション生成
- **ControlNet**: 詳細制御（オプション）

### ライブラリ
- PyTorch + CUDA
- Diffusers (Hugging Face)
- OpenCV + MoviePy
- FFmpeg

## ⚡ パフォーマンス最適化

### GPU最適化
- xFormers有効化
- Mixed Precision (FP16)
- バッチ処理
- メモリ効率化

### 処理速度
- キーフレーム: 3-5秒/枚
- 動画変換: 30-60秒/本
- 総合: 1-2分/動画

## 💰 コスト管理

### 自動停止機能
```bash
# コスト上限で自動停止（4.5万円）
./auto-stop-at-budget.sh &

# リアルタイムコスト確認
./check-current-cost.sh
```

### 推奨設定（5万円予算）
1. **高速消費**: A100 x3台、6時間
2. **バランス**: A100 x2台、8時間
3. **長時間**: A100 x1台、16時間

## 📈 スケーリング

### Cloud Storage連携
```bash
# 生成物を自動アップロード
gsutil -m cp -r outputs/videos gs://your-bucket/
```

### 分散処理
- 最大10台まで並列可能
- 自動負荷分散
- 障害時の自動リトライ

## 🎯 ユースケース

1. **コンテンツ制作**
   - YouTube/TikTok動画
   - 広告素材
   - VFXプロトタイプ

2. **アート作品**
   - ジェネラティブアート
   - ミュージックビデオ
   - インスタレーション

3. **研究開発**
   - モデル評価
   - データセット生成
   - 技術デモ

## ⚠️ 注意事項

- VMは起動中常に課金
- 使用後は必ず停止/削除
- Preemptible VMは24時間で停止
- ストレージコストも考慮

## 🧹 クリーンアップ

```bash
# すべてのVMを停止
gcloud compute instances stop \
  $(gcloud compute instances list --filter="name:video-gen" --format="value(name)") \
  --zone=us-central1-a

# リソース削除
gcloud compute instances delete \
  $(gcloud compute instances list --filter="name:video-gen" --format="value(name)") \
  --zone=us-central1-a
```

## 📝 トラブルシューティング

### CUDA/GPUエラー
```bash
# GPUステータス確認
nvidia-smi

# CUDAバージョン確認
nvcc --version
```

### メモリ不足
- バッチサイズを減らす
- 解像度を下げる
- gradient_checkpointing有効化

### 生成が遅い
- xFormersが有効か確認
- FP16を使用
- 不要なログを無効化

## 🔗 関連リソース

- [Stable Diffusion XL](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0)
- [Stable Video Diffusion](https://huggingface.co/stabilityai/stable-video-diffusion-img2vid-xt)
- [AnimateDiff](https://github.com/guoyww/AnimateDiff)

---

**Made with ❤️ for efficient GCP credit consumption**