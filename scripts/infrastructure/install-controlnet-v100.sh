#!/bin/bash

# V100 ControlNet Complete Setup Script
# Install ControlNet models and custom nodes for ComfyUI

echo "🎛️  Installing ControlNet + Juggernaut XL v10..."
echo "================================================"

# Define instance details
INSTANCE_NAME="instance-20250807-125905"
ZONE="us-central1-c"

echo "📝 Creating comprehensive ControlNet setup script..."

# Create the complete setup script
cat << 'EOF' > /tmp/controlnet_complete_setup.sh
#!/bin/bash

echo "🚀 Starting ControlNet installation on V100..."

# Check current directory and navigate to ComfyUI
if [ -d "/home/claude_user/ComfyUI" ]; then
    cd /home/claude_user/ComfyUI
elif [ -d "ComfyUI" ]; then
    cd ComfyUI
else
    echo "❌ ComfyUI directory not found!"
    exit 1
fi

echo "📍 Current directory: $(pwd)"

# Stop existing ComfyUI process
echo "🛑 Stopping existing ComfyUI process..."
pkill -f "python.*main.py" || true
sleep 3

# Create necessary directories
echo "📁 Creating model directories..."
mkdir -p models/controlnet
mkdir -p custom_nodes

# Install ControlNet custom nodes
echo "📦 Installing ControlNet custom nodes..."

# Install ComfyUI ControlNet Auxiliary Preprocessors
if [ ! -d "custom_nodes/comfyui_controlnet_aux" ]; then
    echo "Installing ControlNet Auxiliary Preprocessors..."
    cd custom_nodes
    git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git
    cd comfyui_controlnet_aux
    pip install -r requirements.txt
    cd ../..
fi

# Download SDXL ControlNet models (essential ones)
echo "📥 Downloading SDXL ControlNet models..."

# SDXL ControlNet Canny (edge detection)
if [ ! -f "models/controlnet/diffusers_xl_canny_full.safetensors" ]; then
    echo "📥 Downloading SDXL ControlNet Canny..."
    wget -q --show-progress --timeout=600 \
        -O models/controlnet/diffusers_xl_canny_full.safetensors \
        "https://huggingface.co/diffusers/controlnet-canny-sdxl-1.0/resolve/main/diffusion_pytorch_model.safetensors"
    
    if [ $? -eq 0 ]; then
        echo "✅ ControlNet Canny downloaded successfully"
    else
        echo "❌ Failed to download ControlNet Canny"
    fi
fi

# SDXL ControlNet OpenPose (pose control)
if [ ! -f "models/controlnet/diffusers_xl_openpose_full.safetensors" ]; then
    echo "📥 Downloading SDXL ControlNet OpenPose..."
    wget -q --show-progress --timeout=600 \
        -O models/controlnet/diffusers_xl_openpose_full.safetensors \
        "https://huggingface.co/thibaud/controlnet-openpose-sdxl-1.0/resolve/main/diffusion_pytorch_model.safetensors"
    
    if [ $? -eq 0 ]; then
        echo "✅ ControlNet OpenPose downloaded successfully"
    else
        echo "❌ Failed to download ControlNet OpenPose"
    fi
fi

# SDXL ControlNet Depth (depth control)
if [ ! -f "models/controlnet/diffusers_xl_depth_full.safetensors" ]; then
    echo "📥 Downloading SDXL ControlNet Depth..."
    wget -q --show-progress --timeout=600 \
        -O models/controlnet/diffusers_xl_depth_full.safetensors \
        "https://huggingface.co/diffusers/controlnet-depth-sdxl-1.0/resolve/main/diffusion_pytorch_model.safetensors"
    
    if [ $? -eq 0 ]; then
        echo "✅ ControlNet Depth downloaded successfully"
    else
        echo "❌ Failed to download ControlNet Depth"
    fi
fi

# Verify Juggernaut XL v10 model exists
echo "🔍 Checking for Juggernaut XL v10 model..."
if [ -f "models/checkpoints/juggernaut_xl_v10.safetensors" ]; then
    echo "✅ Juggernaut XL v10 found"
else
    echo "❌ Juggernaut XL v10 not found - please ensure it's installed"
fi

# Show installed models
echo "📋 Installed ControlNet models:"
ls -la models/controlnet/ || echo "No ControlNet models found"

echo "📋 Available checkpoint models:"
ls -la models/checkpoints/ || echo "No checkpoint models found"

# Check disk space
echo "💾 Current disk usage:"
df -h

# Restart ComfyUI with ControlNet support
echo "🚀 Starting ComfyUI with ControlNet support..."
cd /home/claude_user/ComfyUI || cd ComfyUI
nohup python main.py --listen 0.0.0.0 --port 8188 --highvram --fast > comfyui_controlnet.log 2>&1 &

# Wait for startup
sleep 10

# Check if ComfyUI is running
if pgrep -f "python.*main.py" > /dev/null; then
    echo "✅ ComfyUI with ControlNet is running!"
    echo "🌐 Access at: http://$(curl -s ifconfig.me):8188"
else
    echo "❌ Failed to start ComfyUI"
    echo "📋 Log output:"
    tail -20 comfyui_controlnet.log
fi

echo "🎛️  ControlNet setup completed!"
echo "================================================"
echo "✅ Components installed:"
echo "   • ControlNet Auxiliary Preprocessors"
echo "   • SDXL ControlNet Canny"
echo "   • SDXL ControlNet OpenPose"  
echo "   • SDXL ControlNet Depth"
echo "   • Juggernaut XL v10 (base model)"
echo ""
echo "🎨 Ready for advanced image generation with:"
echo "   • Anatomical accuracy (OpenPose)"
echo "   • Edge-guided generation (Canny)"
echo "   • Depth-controlled composition"
EOF

echo "📤 Uploading setup script to V100..."

# Copy the script to the instance via gcloud
gcloud compute scp --zone=$ZONE /tmp/controlnet_complete_setup.sh $INSTANCE_NAME:~/

echo "🚀 Executing ControlNet setup on V100..."

# Execute the script on the instance
gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command="chmod +x ~/controlnet_complete_setup.sh && ~/controlnet_complete_setup.sh"

if [ $? -eq 0 ]; then
    echo "✅ ControlNet setup completed successfully!"
    echo "🎛️  V100 now has ControlNet + Juggernaut XL v10"
    echo "🌐 ComfyUI URL: http://34.70.230.62:8188"
else
    echo "❌ Setup failed. Check the logs above."
fi

# Clean up
rm -f /tmp/controlnet_complete_setup.sh

echo "🎉 ControlNet installation complete!"