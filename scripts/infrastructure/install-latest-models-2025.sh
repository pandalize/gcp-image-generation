#!/bin/bash
echo "🔥 2025年最新SDXL高性能モデル導入"
echo "===================================="

cd ~/ComfyUI/models/checkpoints

echo "📥 最新リアルフォト特化モデルダウンロード"

# 1. Juggernaut XL v10 (2025年最高峰)
echo "🎯 Juggernaut XL v10 ダウンロード中..."
wget -O "juggernaut_xl_v10.safetensors" \
"https://civitai.com/api/download/models/456194?type=Model&format=SafeTensor&size=full&fp=fp16" \
|| echo "Juggernaut XL v10 ダウンロード失敗"

# 2. DevilishPhotoRealism SDXL (ハイパーリアル)
echo "😈 DevilishPhotoRealism SDXL ダウンロード中..."
wget -O "devilish_photo_realism_sdxl.safetensors" \
"https://civitai.com/api/download/models/198530?type=Model&format=SafeTensor&size=full&fp=fp16" \
|| echo "DevilishPhotoRealism SDXL ダウンロード失敗"

# 3. Realistic Vision v6.0 B1 (最新版)
echo "👁️ Realistic Vision v6.0 B1 ダウンロード中..."
wget -O "realistic_vision_v6_b1.safetensors" \
"https://civitai.com/api/download/models/245598?type=Model&format=SafeTensor&size=full&fp=fp16" \
|| echo "Realistic Vision v6.0 B1 ダウンロード失敗"

# 4. RealismEngine SDXL (顔特化)
echo "🤖 RealismEngine SDXL ダウンロード中..."
wget -O "realism_engine_sdxl.safetensors" \
"https://civitai.com/api/download/models/152309?type=Model&format=SafeTensor&size=full&fp=fp16" \
|| echo "RealismEngine SDXL ダウンロード失敗"

# 5. SDXL Lightning (超高速)
echo "⚡ SDXL Lightning ダウンロード中..."
wget -O "sdxl_lightning_4step.safetensors" \
"https://huggingface.co/ByteDance/SDXL-Lightning/resolve/main/sdxl_lightning_4step_unet.safetensors" \
|| echo "SDXL Lightning ダウンロード失敗"

echo "📊 ダウンロード完了確認"
ls -lh *.safetensors | tail -10

echo "💾 ディスク使用量確認"
df -h

echo ""
echo "🎉 2025年最新モデル導入完了!"
echo "利用可能モデル:"
echo "  🏆 Juggernaut XL v10 - 最高峰リアルフォト"
echo "  😈 DevilishPhotoRealism - ハイパーリアル・シネマティック" 
echo "  👁️ Realistic Vision v6.0 - 顔特化・解剖学精度"
echo "  🤖 RealismEngine - 肌質・ライティング特化"
echo "  ⚡ SDXL Lightning - 4ステップ超高速"
echo ""
echo "🚀 ComfyUI再起動でモデル反映！"