# Claude作業メモ - GCP画像生成プロジェクト

## 📋 プロジェクト概要
- GCP V100 GPUを使った大規模AI画像生成
- リアルな女性画像100枚生成システム構築完了

## 🔧 V100 成功セットアップ要点

### 重要な設定
- **起動フラグ**: `python main.py --listen 0.0.0.0 --port 8188 --highvram --fast`
- **サンプラー名**: `"euler"` (euler_a は使用不可)
- **PyTorch**: `torch==2.4.0+cu118`
- **NumPy**: `"numpy<2"` で1.x系固定

### 避けるべき設定
- `--cpu-vae`: 大幅性能低下
- `--normalvram --disable-smart-memory`: 最適化無効化
- NumPy 2.x: 互換性問題
- サンプラー `euler_a`: 存在しないため400エラー

## 📊 現在の状況

### プロジェクト情報
- **プロジェクトID**: `gen-lang-client-0106774703`
- **V100インスタンス**: `instance-20250807-125905` (us-central1-c)
- **GPU**: Tesla V100-SXM2-16GB (16GB VRAM)

### 生成実績
- ✅ テスト画像生成成功
- ✅ YAML 30枚生成完了
- ✅ 最適化後5枚高品質生成完了
- 🔄 リアル女性100枚生成実行中

### 解決した問題
1. **BrokenPipeエラー**: tqdm出力問題 → 最適化フラグで解決
2. **CPU-VAE性能問題**: GPU VAE復活で解決
3. **サンプラー名エラー**: euler_a → euler に修正
4. **CUDA/PyTorch互換性**: バージョン固定で解決

## 🎯 成功パターン

### セットアップ手順
1. システム更新・ドライバーインストール
2. Python仮想環境構築
3. 正しいバージョンの依存関係インストール
4. 環境変数設定
5. 最適化フラグでComfyUI起動

### 性能確認コマンド
```bash
nvidia-smi  # GPU状態確認
curl -s http://localhost:8188/system_stats  # API確認
```

## 🚨 新インスタンス作成時の注意点
詳細は以下ドキュメント参照：
- `/docs/V100-SETUP-SUCCESS-GUIDE.md`
- `/docs/COMMON-MISTAKES-SOLUTIONS.md`

## 💡 学習内容
- V100の真の性能は適切な設定で発揮される
- CPU-VAE設定は緊急回避策でしかない
- バッチ処理（10枚ずつ）が安定動作の鍵
- サンプラー名の正確性が重要