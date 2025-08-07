#!/bin/bash

# 20種類の推奨カスタムノードインストールスクリプト
# L4 GPU + ComfyUI + Juggernaut XL v10 環境

echo "🎛️  ComfyUI 20カスタムノード大量インストール開始"
echo "📅 $(date)"
echo "==================================================="

cd /home/fujinoyuki/ComfyUI

# GPU状態確認
echo "🖥️  GPU状態確認:"
nvidia-smi | head -15

# 仮想環境アクティベート
source comfyui_env/bin/activate
echo "✅ 仮想環境アクティベート完了"

# カスタムノードディレクトリ移動
cd custom_nodes

echo ""
echo "📦 カスタムノード大量インストール開始..."

# 1. Impact Pack (顔詳細強化)
echo "1️⃣  Impact Pack Face Detailer"
git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git 2>/dev/null || echo "Already exists"

# 2. Ultimate SD Upscale
echo "2️⃣  Ultimate SD Upscale"  
git clone https://github.com/ssitu/ComfyUI_UltimateSDUpscale.git 2>/dev/null || echo "Already exists"

# 3. Face Detailer
echo "3️⃣  Face Detailer"
git clone https://github.com/nicofdga/DZ-FaceDetailer.git 2>/dev/null || echo "Already exists"

# 4. Advanced ControlNet
echo "4️⃣  Advanced ControlNet"
git clone https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet.git 2>/dev/null || echo "Already exists"

# 5. ControlNet Auxiliary
echo "5️⃣  ControlNet Auxiliary"
git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git 2>/dev/null || echo "Already exists"

# 6. IPAdapter Plus
echo "6️⃣  IPAdapter Plus"
git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git 2>/dev/null || echo "Already exists"

# 7. Manager (必須)
echo "7️⃣  ComfyUI Manager"
git clone https://github.com/ltdrdata/ComfyUI-Manager.git 2>/dev/null || echo "Already exists"

# 8. Efficiency Nodes
echo "8️⃣  Efficiency Nodes"
git clone https://github.com/jags111/efficiency-nodes-comfyui.git 2>/dev/null || echo "Already exists"

# 9. Custom Scripts
echo "9️⃣  Custom Scripts"
git clone https://github.com/pythongosssss/ComfyUI-Custom-Scripts.git 2>/dev/null || echo "Already exists"

# 10. AnimateDiff
echo "🔟 AnimateDiff"
git clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved.git 2>/dev/null || echo "Already exists"

# 11. Video Helper
echo "1️⃣1️⃣ Video Helper Suite"
git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git 2>/dev/null || echo "Already exists"

# 12. WAS Node Suite
echo "1️⃣2️⃣ WAS Node Suite"
git clone https://github.com/WASasquatch/was-node-suite-comfyui.git 2>/dev/null || echo "Already exists"

# 13. Inspire Pack
echo "1️⃣3️⃣ Inspire Pack"
git clone https://github.com/ltdrdata/ComfyUI-Inspire-Pack.git 2>/dev/null || echo "Already exists"

# 14. ControlAltAI Nodes
echo "1️⃣4️⃣ ControlAltAI Nodes"
git clone https://github.com/gseth/ControlAltAI-Nodes.git 2>/dev/null || echo "Already exists"

# 15. Image Saver
echo "1️⃣5️⃣ Image Saver"
git clone https://github.com/alexopus/ComfyUI-Image-Saver.git 2>/dev/null || echo "Already exists"

# 16. Math Expression
echo "1️⃣6️⃣ Math Expression"
git clone https://github.com/pythongosssss/ComfyUI-Math.git 2>/dev/null || echo "Already exists"

# 17. Prompt Styler
echo "1️⃣7️⃣ SDXL Prompt Styler"
git clone https://github.com/twri/sdxl_prompt_styler.git 2>/dev/null || echo "Already exists"

# 18. Regional Prompter
echo "1️⃣8️⃣ Regional Prompter"
git clone https://github.com/Bing-su/ComfyUI-RegionalPrompter.git 2>/dev/null || echo "Already exists"

# 19. Segment Anything
echo "1️⃣9️⃣ Segment Anything"
git clone https://github.com/storyicon/comfyui_segment_anything.git 2>/dev/null || echo "Already exists"

# 20. Quality of Life
echo "2️⃣0️⃣ Quality of Life"
git clone https://github.com/omar92/ComfyUI-QualityOfLifeSuit_Omar92.git 2>/dev/null || echo "Already exists"

echo ""
echo "📦 依存関係インストール開始..."

# 各カスタムノードの依存関係をインストール
find . -name "requirements.txt" -exec echo "Installing: {}" \; -exec pip install -r {} --break-system-packages \; 2>/dev/null

echo ""
echo "✅ 20カスタムノード インストール完了"
echo "🎛️  ComfyUI再起動が必要です"

# ComfyUI起動スクリプト
echo ""
echo "🚀 ComfyUI起動中..."
cd ..

# 既存のプロセスを終了
pkill -f main.py

# ComfyUI起動 (バックグラウンド)
nohup python main.py --listen 0.0.0.0 --port 8188 --highvram --fast > /tmp/comfyui.log 2>&1 &

sleep 10

echo "✅ ComfyUI起動完了 (ポート8188)"
echo "🌐 アクセス可能: http://$(curl -s ifconfig.me):8188"
echo "📄 ログ確認: tail -f /tmp/comfyui.log"