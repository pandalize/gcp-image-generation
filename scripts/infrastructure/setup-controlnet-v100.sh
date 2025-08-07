#!/bin/bash

# V100 ControlNet Setup Script
# Install ControlNet models and custom nodes for ComfyUI

echo "🎛️  Setting up ControlNet on V100..."
echo "==========================================="

# Connect to V100 instance
SERVER_IP="34.70.230.62"

# Create the setup commands
cat << 'REMOTE_EOF' > /tmp/controlnet_setup.sh
#!/bin/bash

echo "📦 Installing ControlNet Custom Nodes..."

# Go to ComfyUI directory
cd /home/claude_user/ComfyUI

# Install ComfyUI-Manager (for easy custom node management)
if [ ! -d "custom_nodes/ComfyUI-Manager" ]; then
    echo "Installing ComfyUI Manager..."
    cd custom_nodes
    git clone https://github.com/ltdrdata/ComfyUI-Manager.git
    cd ComfyUI-Manager
    pip install -r requirements.txt
    cd ../..
fi

# Install ControlNet nodes
if [ ! -d "custom_nodes/ComfyUI_Comfyroll_CustomNodes" ]; then
    echo "Installing Comfyroll Custom Nodes..."
    cd custom_nodes
    git clone https://github.com/RockOfFire/ComfyUI_Comfyroll_CustomNodes.git
    cd ComfyUI_Comfyroll_CustomNodes
    pip install -r requirements.txt
    cd ../..
fi

# Install ControlNet preprocessor nodes
if [ ! -d "custom_nodes/comfyui_controlnet_aux" ]; then
    echo "Installing ControlNet Auxiliary Preprocessors..."
    cd custom_nodes
    git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git
    cd comfyui_controlnet_aux
    pip install -r requirements.txt
    cd ../..
fi

# Create controlnet models directory
mkdir -p models/controlnet

# Download essential ControlNet models
echo "📥 Downloading ControlNet models..."

# SDXL ControlNet Canny
if [ ! -f "models/controlnet/diffusers_xl_canny_full.safetensors" ]; then
    echo "Downloading SDXL ControlNet Canny..."
    wget -O models/controlnet/diffusers_xl_canny_full.safetensors \
        "https://huggingface.co/diffusers/controlnet-canny-sdxl-1.0/resolve/main/diffusion_pytorch_model.safetensors"
fi

# SDXL ControlNet OpenPose
if [ ! -f "models/controlnet/diffusers_xl_openpose_full.safetensors" ]; then
    echo "Downloading SDXL ControlNet OpenPose..."
    wget -O models/controlnet/diffusers_xl_openpose_full.safetensors \
        "https://huggingface.co/thibaud/controlnet-openpose-sdxl-1.0/resolve/main/diffusion_pytorch_model.safetensors"
fi

# SDXL ControlNet Depth
if [ ! -f "models/controlnet/diffusers_xl_depth_full.safetensors" ]; then
    echo "Downloading SDXL ControlNet Depth..."
    wget -O models/controlnet/diffusers_xl_depth_full.safetensors \
        "https://huggingface.co/diffusers/controlnet-depth-sdxl-1.0/resolve/main/diffusion_pytorch_model.safetensors"
fi

echo "✅ ControlNet setup completed!"
echo "Available ControlNet models:"
ls -la models/controlnet/

# Check disk space
echo "💾 Disk space after ControlNet installation:"
df -h /

echo "🔄 Restarting ComfyUI with ControlNet support..."
# Kill existing ComfyUI process
pkill -f "python main.py"
sleep 5

# Start ComfyUI with ControlNet support
cd /home/claude_user/ComfyUI
nohup python main.py --listen 0.0.0.0 --port 8188 --highvram --fast > comfyui.log 2>&1 &

# Wait for startup
sleep 10

echo "🎛️  ControlNet setup complete!"
echo "ComfyUI with ControlNet is now running on port 8188"
REMOTE_EOF

# Copy and execute the script on V100
echo "📤 Uploading setup script to V100..."
scp -o StrictHostKeyChecking=no /tmp/controlnet_setup.sh claude_user@${SERVER_IP}:/tmp/

echo "🚀 Executing ControlNet setup on V100..."
ssh -o StrictHostKeyChecking=no claude_user@${SERVER_IP} 'chmod +x /tmp/controlnet_setup.sh && /tmp/controlnet_setup.sh'

echo "✅ ControlNet setup completed on V100!"
echo "Server: http://${SERVER_IP}:8188"

# Clean up
rm /tmp/controlnet_setup.sh