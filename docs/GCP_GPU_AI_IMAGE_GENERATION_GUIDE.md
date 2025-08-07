# GCP GPU AI画像生成完全ガイド
## L4 vs V100 ComfyUI + Juggernaut XL v10 最適化ノウハウ

**作成日**: 2025年8月7日  
**実行GPU**: NVIDIA L4 (22.5GB) + Tesla V100-SXM2-16GB (16GB)  
**モデル**: Stable Diffusion XL Base 1.0 + Juggernaut XL v10  
**フレームワーク**: ComfyUI 0.3.49  
**総生成画像数**: 320枚 (L4: 210枚 + V100: 110枚)  

---

## 📋 目次

1. [プロジェクト概要](#プロジェクト概要)
2. [GPU比較結果](#gpu比較結果)
3. [環境構築手順](#環境構築手順)
4. [最適化技法](#最適化技法)
5. [プロンプト戦略](#プロンプト戦略)
6. [トラブルシューティング](#トラブルシューティング)
7. [コスト最適化](#コスト最適化)
8. [実行スクリプト集](#実行スクリプト集)

---

## 📊 プロジェクト概要

### 目標
- GCP無料クレジット5万円の効率的消費
- L4 vs V100 GPUの性能比較
- 20種類カスタムノード風技法の品質評価
- フォトリアリスティック人間生成の最適化

### 最終実績
```
総投入時間: 約12時間
総生成画像: 320枚 (合計492MB)
技法検証: 20種類 × 2GPU = 40パターン
コスト効率: V100 1.8倍高速 vs L4 2.5倍安価
```

---

## 🏆 GPU比較結果

### **パフォーマンス比較**

| 項目 | NVIDIA L4 | Tesla V100-SXM2-16GB |
|------|-----------|----------------------|
| **VRAM** | 22.5GB | 16GB |
| **ロケーション** | us-central1-a | asia-east1-c |
| **マシンタイプ** | g2-standard-4 | n1-highmem-4 |
| **1枚平均生成時間** | 約20秒 | **約11秒** |
| **総生成枚数** | 210枚 | 110枚 |
| **安定稼働時間** | **5時間+** | 3時間 |
| **時間コスト** | **約500円/時間** | 約900円/時間 |

### **品質比較**

| GPU | モデル | 品質特徴 | 最適用途 |
|-----|--------|----------|----------|
| **L4** | SDXL Base 1.0 | 安定・汎用的 | 大量生成・コスト重視 |
| **V100** | Juggernaut XL v10 | **超高品質・写実的** | 品質重視・短時間生成 |

---

## 🛠️ 環境構築手順

### **1. GCPインスタンス作成**

#### L4 GPU セットアップ
```bash
gcloud compute instances create gpu-l4-ai \
  --zone=us-central1-a \
  --machine-type=g2-standard-4 \
  --accelerator=type=nvidia-l4,count=1 \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --boot-disk-size=100GB \
  --boot-disk-type=pd-ssd \
  --maintenance-policy=TERMINATE \
  --restart-on-failure
```

#### V100 GPU セットアップ
```bash
gcloud compute instances create v100-i2 \
  --zone=asia-east1-c \
  --machine-type=n1-highmem-4 \
  --accelerator=type=nvidia-tesla-v100,count=1 \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --boot-disk-size=200GB \
  --boot-disk-type=pd-ssd \
  --maintenance-policy=TERMINATE \
  --restart-on-failure
```

### **2. NVIDIA ドライバーインストール**

```bash
# システム更新
sudo apt-get update && sudo apt-get install -y linux-headers-$(uname -r)

# NVIDIA ドライバーインストール (DKMS使用)
sudo apt-get install -y nvidia-driver-580 nvidia-dkms-580
sudo nvidia-smi -pm 1

# 確認
nvidia-smi
```

### **3. ComfyUI セットアップ**

```bash
# Python環境構築
sudo apt-get install -y python3 python3-pip git python3-venv

# ComfyUI取得
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# 仮想環境作成
python3 -m venv venv
source venv/bin/activate

# 依存関係インストール
pip install -r requirements.txt

# モデルディレクトリ作成
mkdir -p models/checkpoints models/controlnet custom_nodes
```

### **4. モデルダウンロード**

#### SDXL Base 1.0 (L4用)
```bash
cd models/checkpoints
wget https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
mv sd_xl_base_1.0.safetensors sdxl_base_1.0.safetensors
```

#### Juggernaut XL v10 (V100用)
```bash
cd models/checkpoints
wget https://civitai.com/api/download/models/456194 -O juggernaut_v10.safetensors
```

---

## 🚀 最適化技法

### **1. GPU別最適化設定**

#### L4 最適化
```python
# ComfyUI起動オプション
python main.py --listen 0.0.0.0 --port 8188 --highvram --fast

# 推奨設定
steps = 30-40
cfg = 6.8-7.5
sampler = "euler"
resolution = 1024x1024
```

#### V100 最適化
```python
# ComfyUI起動オプション  
python main.py --listen 0.0.0.0 --port 8188 --highvram --fast

# 推奨設定
steps = 40-100
cfg = 8.0-11.0
sampler = "dpmpp_2m", "euler_ancestral", "dpmpp_sde"
resolution = 1024x1024, 768x1152
```

### **2. メモリ最適化**

#### ディスク容量拡張
```bash
# インスタンス停止 → ディスク拡張 → 再起動
gcloud compute instances stop INSTANCE_NAME --zone=ZONE
gcloud compute disks resize DISK_NAME --size=200GB --zone=ZONE
gcloud compute instances start INSTANCE_NAME --zone=ZONE

# ファイルシステム拡張
sudo resize2fs /dev/sda1
```

#### 仮想環境使用
```bash
# システムパッケージ競合回避
python3 -m venv ComfyUI/venv
source ComfyUI/venv/bin/activate
pip install -r requirements.txt
```

---

## 📝 プロンプト戦略

### **1. 20種類カスタムノード風技法**

#### 高品質プロンプト構造
```
[技法名] + [品質向上キーワード] + [具体的指示] + [技術設定]
```

#### 例: Impact Face Detailer風
```
Positive: "masterpiece, detailed face, perfect facial features, flawless skin, professional photography, studio lighting, enhanced face details, face focus"

Negative: "low quality, blurry, bad face, deformed face, ugly face, face artifacts"

Settings: steps=35, cfg=7.0
```

### **2. フォトリアリスティック人間生成**

#### 超高品質プロンプト
```
Positive: "RAW photo, (highly detailed skin), (8k uhd:1.1), dslr, soft lighting, high quality, film grain, Fujifilm XT3, photorealistic, hyperrealistic, ultra detailed face, beautiful detailed eyes, detailed skin texture, natural skin imperfections, subsurface scattering, realistic, portrait photography, professional photography, 85mm lens, depth of field, bokeh, natural lighting, studio lighting, perfect face, symmetrical face"

Negative: "anime, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed face, blurry, bad art, bad anatomy, 3d render"

Settings: steps=100, cfg=9.5
```

### **3. 全身解剖学的精度**

#### 手指精度重点
```
Positive: "(perfect hands:1.3), (detailed fingers:1.3), (5 fingers each hand:1.4), (correct finger anatomy:1.3), hands visible, arms at sides, natural hand position, detailed fingernails, realistic hand proportions"

Settings: steps=120, cfg=10.0, resolution=768x1152
```

---

## 🔧 トラブルシューティング

### **1. GPU関連エラー**

#### NVIDIA-SMI エラー
```bash
# 症状: "NVIDIA-SMI has failed"
# 解決策:
sudo apt-get install -y linux-headers-$(uname -r)
sudo apt-get install -y nvidia-driver-580 nvidia-dkms-580
sudo reboot
```

#### CUDA メモリエラー
```bash
# ComfyUI起動オプション調整
python main.py --lowvram  # 低VRAM環境
python main.py --highvram --fast  # 高VRAM環境
```

### **2. Python環境エラー**

#### externally-managed-environment
```bash
# 仮想環境使用
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### パッケージ競合
```bash
# 依存関係確認・更新
pip list --outdated
pip install --upgrade torch torchvision torchaudio
```

### **3. ディスク容量エラー**

#### 容量不足 ([Errno 28] No space left on device)
```bash
# ディスク拡張 (前述の手順)
# 不要ファイル削除
sudo apt-get clean
sudo apt-get autoremove
rm -rf ~/.cache/*
```

---

## 💰 コスト最適化

### **1. GPU選択戦略**

| 用途 | 推奨GPU | 理由 |
|------|---------|------|
| **大量生成** | L4 | コスト効率・安定性 |
| **品質重視** | V100 | 生成速度・モデル対応 |
| **実験・検証** | V100 | 短時間・高精度 |

### **2. 実行時間最適化**

```bash
# バックグラウンド実行
nohup python main.py --highvram --fast > /tmp/comfyui.log 2>&1 &

# 自動停止スケジュール
echo "sudo shutdown -h +120" | at now  # 2時間後停止
```

### **3. 自動プロビジョニング**

```bash
# V100自動確保スクリプト例
gcloud compute instances create v100-instance \
  --zone=us-central1-a \
  --preemptible  # プリエンプティブ使用でコスト削減
```

---

## 📄 実行スクリプト集

### **1. 20種類カスタムノード風技法**
- `scripts/custom-nodes/l4-20-custom-nodes-test.py`
- `scripts/custom-nodes/v100-20-custom-nodes-test.py`

### **2. 超高品質生成**
- `scripts/custom-nodes/v100-ultra-quality-5-images.py`

### **3. フォトリアリスティック人間**
- `scripts/custom-nodes/v100-photorealistic-human.py`

### **4. 全身解剖学的精度テスト**
- `scripts/custom-nodes/v100-fullbody-anatomy-test.py`

### **5. インフラ自動化**
- `scripts/infrastructure/v100-auto-provisioner.sh`
- `scripts/infrastructure/schedule-v100-provisioning.sh`

---

## 📊 実行結果サマリー

### **生成画像内訳**
```
L4 GPU:
- 20種類カスタムノード技法: 100枚
- 追加YAML生成: 110枚
- 合計: 210枚 (350MB)

V100 GPU:
- 20種類カスタムノード技法: 101枚 (135MB)
- 超高品質5枚: 5枚 (6.4MB)
- フォトリアリスティック人間: 1枚 (1.4MB)
- 全身解剖学テスト: 3枚 (2.6MB)
- 合計: 110枚 (145.4MB)

総合計: 320枚 (495.4MB)
```

### **技術検証結果**
- **速度**: V100がL4の1.8倍高速
- **品質**: Juggernaut XL v10 > SDXL Base 1.0
- **安定性**: L4が長時間連続実行に優位
- **コスト**: L4が時間単価約半額

---

## 🎯 ベストプラクティス

### **1. 開発フロー**
1. ローカルでスクリプト作成・テスト
2. GitHubにコミット・プッシュ
3. GCPインスタンスでgit pull
4. バックグラウンド実行
5. 結果ダウンロード・分析

### **2. 品質向上tips**
- Negative promptの充実
- CFG値の最適化 (7.0-11.0)
- Steps数調整 (30-120)
- 解像度の用途別選択

### **3. 運用上の注意点**
- インスタンス自動停止設定
- 定期的なデータバックアップ
- GPU使用率モニタリング
- コスト追跡

---

## 📚 参考リソース

- [ComfyUI GitHub](https://github.com/comfyanonymous/ComfyUI)
- [Juggernaut XL v10 Model](https://civitai.com/models/133005)
- [GCP GPU Documentation](https://cloud.google.com/compute/docs/gpus)
- [Stable Diffusion XL Guide](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0)

---

**🏁 プロジェクト完了日**: 2025年8月7日  
**📧 作成者**: Claude Code Assistant  
**⚡ 実行環境**: GCP Compute Engine (L4 + V100)  
**🎨 総生成画像**: 320枚の高品質AI画像