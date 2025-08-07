# Claude作業メモ - GCP画像生成プロジェクト

## 📋 プロジェクト概要
- GCP A100/T4 GPUを使った大規模AI画像・動画生成
- 5万円の無料クレジットを3日で効率的に消費
- Stable Diffusion XL + Stable Video Diffusionパイプライン

## 🔧 作業ルール

### スクリプト作成・修正ルール
**❌ やらない：**
- Cloud Shellで `cat > script.sh << 'EOF'` を使ったスクリプト作成
- リモートでの直接ファイル編集

**✅ やること：**
1. ローカル（Claude Code）でスクリプトを作成・修正
2. GitHubにコミット・プッシュ
3. Cloud Shellで `git pull` して最新版を取得
4. 実行

### 理由
- バージョン管理の一貫性
- コードレビュー可能
- バックアップの確実性
- 複数環境での同期

## 📊 現在の状況

### GPUクォータ状況
- **NVIDIA_A100_GPUS**: 0台（要申請）
- **NVIDIA_T4_GPUS**: 1台（利用可能）
- **NVIDIA_V100_GPUS**: 1台（利用可能）
- **NVIDIA_L4_GPUS**: 1台（利用可能）✅ フル稼働中

### 実行中のリソース (2025-08-07 21:30)
- **gpu-l4-ai** (L4 GPU VM) 🔥 メインVM
  - マシンタイプ: g2-standard-4 (4 vCPUs, 16GB RAM)
  - GPU: NVIDIA L4 (23GB VRAM, CUDA 12.2)
  - ゾーン: us-central1-a
  - ステータス: RUNNING
  - 外部IP: 35.225.113.119
  - コスト: 約$0.75/時間
  - **ComfyUI稼働中**: ポート8188でWebUI利用可能

### 🎨 AI美女画像生成実績 - ComfyUI + SDXL
- **生成システム**: ComfyUI + SDXL Base 1.0 (6.5GB)
- **生成完了**: 9枚の高品質美女ポートレート
- **解像度**: 1024x1024
- **品質**: プロ品質スタジオライティング、ファッション誌レベル
- **VM保存先**: `~/ComfyUI/output/L4_Beauty_*.png`
- **ローカル保存**: `/Users/fujinoyuki/Desktop/gcp/comfyui_outputs/`
- **生成速度**: 約1-2分/枚（L4 GPU最適化）
- **バッチ生成**: 100枚自動生成スクリプト稼働中

### 無料クレジット状況 ⚠️ 緊急
- **初期クレジット**: 50,000円
- **現在の残高**: 約49,960円
- **プロジェクト作成日**: 2025-05-11
- **クレジット有効期限**: 2025-08-09（あと2日！）
- **使い切るために必要**: 1日あたり約25,000円の使用

### クレジット期限の確認方法
1. [プロモーションとクレジット画面](https://console.cloud.google.com/billing/016AA7-4DA69A-39272A/credits)
2. [請求レポート](https://console.cloud.google.com/billing/016AA7-4DA69A-39272A/reports)
3. コマンド: `gcloud projects describe gen-lang-client-0106774703`

### 🛠️ 技術的課題と解決履歴

#### Phase 1: GPU環境構築
1. **T4 GPUリソース枯渇問題**
   - us-central1でT4が利用不可
   - **解決**: L4 GPU採用（より高性能、23GB VRAM）

2. **NVIDIA driver問題**  
   - nvidia-smi通信エラー
   - **解決**: 手動デバイスファイル作成(`/dev/nvidia*`)

#### Phase 2: AI生成環境構築  
3. **Stable Diffusion依存関係衝突**
   - PyTorch/diffusers/xformersバージョン競合
   - **解決**: ComfyUIに移行（より安定、高機能）

4. **NumPy 2.x互換性問題**
   - torchとNumPy 2.xの競合
   - **解決**: numpy<2でダウングレード

5. **safetensors互換性**
   - transformersが要求するsafetensors>=0.4.3
   - **解決**: safetensors==0.4.3で固定

#### Phase 3: 大量生成システム
6. **ComfyUI API統合**
   - 手動生成から自動バッチ生成へ移行
   - **実装**: Python APIクライアント + バッチ処理ループ

## 🚀 次のステップ（期限まで48時間）

### 🎯 優先度1: クレジット最大化
1. **L4 GPU VM増設** (5-10台並列)
   - 現在1台 → 複数台同時稼働
   - 推定コスト: $0.75 × 10台 × 48時間 = $360

2. **大量バッチ生成**
   - 目標: 1,000-5,000枚の高品質画像
   - 美女ポートレート + 風景 + アート

3. **動画生成実装**
   - Stable Video Diffusion導入
   - 画像→動画変換パイプライン

### 🛠️ 技術仕様
- **生成エンジン**: ComfyUI + SDXL + SVD
- **最適化**: FP16, lowvram, バッチ処理
- **品質保証**: 商用利用可能モデルのみ
- **自動化**: API経由完全自動生成

### 💾 成果物管理
- VM上保存: `~/ComfyUI/output/`
- ローカル同期: `~/Desktop/gcp/final_outputs/`
- バックアップ: Cloud Storage

## 🎨 技術成果サマリー

### ✅ 達成した技術目標
1. **L4 GPU完全活用**: 23GB VRAM, CUDA 12.2
2. **ComfyUI統合**: 最新AI生成プラットフォーム
3. **SDXL導入**: 6.5GBの最高品質モデル  
4. **バッチ自動化**: API統合による大量生成
5. **品質保証**: プロ品質ポートレート生成確認

### 📊 パフォーマンス指標
- **生成速度**: 1-2分/枚（1024×1024）
- **VRAM効率**: 80%活用（18GB/23GB）
- **品質スコア**: ファッション誌レベル
- **稼働率**: 24時間連続稼働可能