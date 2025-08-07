# V100インスタンス成功セットアップガイド

## 📋 概要
このドキュメントは、V100インスタンスでComfyUIを正常に動作させるまでに発生した問題と解決策をまとめています。新しいインスタンス作成時の参考にしてください。

## 🎯 成功した構成

### インスタンス仕様
```
名前: instance-20250807-125905
ゾーン: us-central1-c
マシンタイプ: n1-highmem-4
GPU: Tesla V100-SXM2-16GB
OS: Debian 12
```

### 重要な設定フラグ
```bash
python main.py --listen 0.0.0.0 --port 8188 --highvram --fast
```

## ⚠️ 発生した問題と解決策

### 1. BrokenPipeError 
**問題**: tqdmのプログレスバー出力でBrokenPipeエラー発生
```
[Errno 32] Broken pipe
File "/usr/bin/python3", line 35, in flush
```

**解決策**:
```bash
# tqmd出力を無効化
export TQDM_DISABLE=1
export PYTHONUNBUFFERED=1

# または最適化フラグで回避
python main.py --listen 0.0.0.0 --port 8188 --highvram --fast
```

### 2. CPU-VAE性能問題
**問題**: `--cpu-vae`フラグでVAE処理をCPUに回すと大幅に性能低下

**解決策**: GPU VAEを使用（デフォルト）
```bash
# ❌ 避けるべき設定
python main.py --cpu-vae

# ✅ 推奨設定
python main.py --highvram --fast
```

### 3. サンプラー名エラー
**問題**: 
```
sampler_name: 'euler_a' not in (list of length 40)
```

**解決策**: 正しいサンプラー名を使用
```python
# ❌ 間違い
"sampler_name": "euler_a"

# ✅ 正解
"sampler_name": "euler"
```

### 4. CUDA/PyTorch互換性問題
**問題**: PyTorchバージョンとCUDAの不整合
```
CUDA unknown error
torch.uint64 attribute error
```

**解決策**: 互換性のあるバージョンを使用
```bash
pip install torch==2.4.0+cu118 torchvision==0.15.2+cu118 torchaudio==2.0.2+cu118 --index-url https://download.pytorch.org/whl/cu118
```

### 5. NumPy互換性問題
**問題**: NumPy 2.x系での互換性エラー

**解決策**: NumPy 1.x系に固定
```bash
pip install "numpy<2" 
```

## 🚀 完全セットアップスクリプト

```bash
#!/bin/bash
# V100完全セットアップスクリプト

echo "🔧 V100 ComfyUI完全セットアップ"

# システム更新
sudo apt update && sudo apt upgrade -y

# Python環境
sudo apt install -y python3-pip python3-venv git curl

# NVIDIA ドライバー
sudo apt install -y nvidia-driver-535
sudo nvidia-persistenced --persistence-mode

# ComfyUI取得
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# Python仮想環境
python3 -m venv comfyui_env
source comfyui_env/bin/activate

# 依存関係インストール（順序重要）
pip install --upgrade pip
pip install "numpy<2"
pip install torch==2.4.0+cu118 torchvision==0.15.2+cu118 torchaudio==2.0.2+cu118 --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt

# モデルダウンロード
cd models/checkpoints
wget https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
cd ../..

# 最適化環境変数
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:1024
export CUDA_VISIBLE_DEVICES=0
export TQDM_DISABLE=1
export PYTHONUNBUFFERED=1

# ComfyUI起動（最適化フラグ）
nohup python main.py --listen 0.0.0.0 --port 8188 --highvram --fast > comfyui.log 2>&1 &

echo "✅ セットアップ完了"
echo "🌐 アクセス: http://[EXTERNAL_IP]:8188"
```

## 📊 性能チェックコマンド

### GPU状態確認
```bash
nvidia-smi
```

### ComfyUI動作確認
```bash
curl -s http://localhost:8188/system_stats | jq '.devices[0]'
```

### メモリ使用量確認
```bash
free -h
```

## 🎨 テスト用ワークフロー

シンプルなテスト生成で動作確認：

```python
workflow = {
    "3": {
        "inputs": {
            "seed": 12345,
            "steps": 15,
            "cfg": 7.0,
            "sampler_name": "euler",  # 重要: euler_a ではない
            "scheduler": "normal",
            "denoise": 1.0,
            "model": ["4", 0],
            "positive": ["6", 0], 
            "negative": ["7", 0],
            "latent_image": ["5", 0]
        },
        "class_type": "KSampler"
    },
    "4": {"inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"}, "class_type": "CheckpointLoaderSimple"},
    "5": {"inputs": {"width": 512, "height": 512, "batch_size": 1}, "class_type": "EmptyLatentImage"},
    "6": {"inputs": {"text": "beautiful woman, photorealistic", "clip": ["4", 1]}, "class_type": "CLIPTextEncode"},
    "7": {"inputs": {"text": "low quality, blurry", "clip": ["4", 1]}, "class_type": "CLIPTextEncode"},
    "8": {"inputs": {"samples": ["3", 0], "vae": ["4", 2]}, "class_type": "VAEDecode"},
    "9": {"inputs": {"filename_prefix": "test_", "images": ["8", 0]}, "class_type": "SaveImage"}
}
```

## 🔍 トラブルシューティング

### 1. ComfyUIが起動しない
```bash
# ログ確認
tail -f comfyui.log

# プロセス確認
ps aux | grep python

# ポート確認
netstat -tlnp | grep 8188
```

### 2. GPU認識しない
```bash
# ドライバー確認
nvidia-smi

# CUDA確認
python -c "import torch; print(torch.cuda.is_available())"

# 再起動
sudo reboot
```

### 3. メモリ不足
```bash
# スワップ追加
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 📈 最適化のポイント

### 1. 高性能設定
- `--highvram`: 高VRAMモード
- `--fast`: 高速モード
- GPU VAE使用（CPU-VAE避ける）

### 2. バッチサイズ調整
- V100 16GB: バッチサイズ1-2が安全
- 高解像度: 768x1024まで推奨

### 3. モデル選択
- SDXL Base 1.0が安定
- Realistic Vision等も良好

## 🎯 成功指標

以下が確認できれば正常動作：
- ✅ GPU認識 (Tesla V100-SXM2-16GB)
- ✅ VRAM使用量表示
- ✅ API応答 (system_stats)
- ✅ 画像生成成功
- ✅ 画像ダウンロード可能

## 📝 備考

### 重要な教訓
1. **CPU-VAE は性能殺し**: BrokenPipeエラー対策で一時使用したが大幅性能低下
2. **フラグの組み合わせが重要**: `--highvram --fast`が最適
3. **サンプラー名に注意**: `euler_a`は使えない、`euler`を使用
4. **バッチ処理**: 100枚生成時は10枚ずつに分割推奨

### V100の真の性能
- 最適化前: 遅い、品質低下
- 最適化後: L4と同等以上の性能発揮

---

**作成日**: 2025-08-07  
**最終更新**: 2025-08-07  
**対象**: Tesla V100-SXM2-16GB + ComfyUI 0.3.49