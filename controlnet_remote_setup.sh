#!/bin/bash

echo "📦 Installing ControlNet on V100 instance..."

# Go to ComfyUI directory
cd /home/claude_user/ComfyUI || cd ComfyUI || { echo "ComfyUI directory not found"; exit 1; }

# Create controlnet models directory
mkdir -p models/controlnet

echo "📥 Downloading ControlNet models..."

# SDXL ControlNet Canny (lightweight version)
if [ ! -f "models/controlnet/control_v11p_sd15_canny.pth" ]; then
    echo "Downloading ControlNet Canny..."
    wget -q --timeout=300 -O models/controlnet/control_v11p_sd15_canny.pth \
        "https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_canny.pth" || \
        echo "Failed to download Canny model"
fi

# SDXL ControlNet OpenPose (lightweight version)
if [ ! -f "models/controlnet/control_v11p_sd15_openpose.pth" ]; then
    echo "Downloading ControlNet OpenPose..."
    wget -q --timeout=300 -O models/controlnet/control_v11p_sd15_openpose.pth \
        "https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_openpose.pth" || \
        echo "Failed to download OpenPose model"
fi

echo "✅ ControlNet models downloaded!"
echo "Available models:"
ls -la models/controlnet/ || echo "No models found"

echo "🔄 Checking ComfyUI process..."
# Check if ComfyUI is running
if pgrep -f "python.*main.py" > /dev/null; then
    echo "ComfyUI is running"
else
    echo "Starting ComfyUI..."
    cd /home/claude_user/ComfyUI || cd ComfyUI
    nohup python main.py --listen 0.0.0.0 --port 8188 --highvram --fast > comfyui.log 2>&1 &
    sleep 5
fi

echo "🎛️  ControlNet setup complete!"
df -h
