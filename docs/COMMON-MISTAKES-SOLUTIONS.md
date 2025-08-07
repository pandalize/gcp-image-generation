# GCP GPU インスタンス 共通失敗パターンと解決策

## 🚨 よくある失敗パターン

### 1. プロジェクトID間違い
**症状**: 
```
ERROR: The resource 'projects/wrong-project-id' was not found
```

**原因**: 古いプロジェクトIDを使用

**解決策**:
```bash
# 現在のプロジェクトID確認
gcloud config get-value project

# 正しいプロジェクトIDを使用
gcloud compute instances list --project=gen-lang-client-0106774703
```

### 2. ゾーン間違い
**症状**: インスタンスが見つからない

**解決策**:
```bash
# インスタンス検索
gcloud compute instances list --filter="name:instance-*"

# 正しいゾーンでSSH
gcloud compute ssh INSTANCE-NAME --zone=us-central1-c
```

### 3. モデルファイル不足
**症状**: 
```
FileNotFoundError: sd_xl_base_1.0.safetensors
```

**解決策**:
```bash
cd ~/ComfyUI/models/checkpoints
wget https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
```

### 4. 環境変数リセット
**症状**: 再起動後にCUDA環境が失われる

**解決策**: ~/.bashrcに追加
```bash
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:1024
export CUDA_VISIBLE_DEVICES=0
export PYTHONUNBUFFERED=1
```

## 🔧 事前チェックリスト

### インスタンス作成前
- [ ] クォータ確認済み
- [ ] プロジェクトID確認済み
- [ ] 予算設定済み

### セットアップ時
- [ ] NVIDIA ドライバー最新版
- [ ] Python仮想環境使用
- [ ] PyTorch CUDA版インストール
- [ ] NumPy 1.x系固定

### 起動時
- [ ] GPU認識確認
- [ ] API応答確認
- [ ] テスト生成実行

## 🎯 成功パターン

### 1. 段階的セットアップ
1. システム更新
2. ドライバーインストール
3. Python環境構築
4. 依存関係インストール
5. テスト実行

### 2. ログ確認習慣
```bash
# 常にログを確認
tail -f comfyui.log

# エラーを見逃さない
grep -i error comfyui.log
```

### 3. バックアップ取得
```bash
# 作業環境のスナップショット
gcloud compute disks snapshot DISK-NAME --zone=ZONE
```

## 📊 性能最適化チェック

### GPU使用率
```bash
watch -n 1 nvidia-smi
```

### メモリ使用量
```bash
free -h && nvidia-smi --query-gpu=memory.used,memory.total --format=csv
```

### プロセス監視
```bash
htop
```

## 🔄 復旧手順

### ComfyUI再起動
```bash
pkill -f "python main.py"
cd ~/ComfyUI
source comfyui_env/bin/activate
python main.py --listen 0.0.0.0 --port 8188 --highvram --fast
```

### 完全再セットアップ
```bash
# 環境削除
rm -rf ~/ComfyUI

# 最初からセットアップ実行
curl -s https://raw.githubusercontent.com/your-repo/setup-script.sh | bash
```