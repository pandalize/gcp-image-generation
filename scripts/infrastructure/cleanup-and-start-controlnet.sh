#!/bin/bash

# Clean disk space and start ControlNet
echo "🧹 Cleaning disk space and starting ControlNet..."
echo "=============================================="

INSTANCE_NAME="instance-20250807-125905"
ZONE="us-central1-c"

cat << 'EOF' > /tmp/cleanup_and_start.sh
#!/bin/bash

echo "🧹 Aggressive disk cleanup..."

# Go to ComfyUI directory
cd /home/fujinoyuki/ComfyUI || exit 1

# Remove old/broken ControlNet models
echo "Removing broken ControlNet models..."
rm -f models/controlnet/diffusers_xl_openpose_full.safetensors
rm -f models/controlnet/diffusers_xl_depth_full.safetensors

# Clean up logs and temporary files
echo "Cleaning logs and temp files..."
rm -f *.log
rm -f /tmp/*
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Remove one of the duplicate models to free space
echo "Removing duplicate model..."
if [ -f "models/checkpoints/devilish_photo_realism_sdxl.safetensors" ] && [ -f "models/checkpoints/juggernaut_xl_v10.safetensors" ]; then
    echo "Removing DevilishPhotoRealism to keep Juggernaut XL v10..."
    rm -f "models/checkpoints/devilish_photo_realism_sdxl.safetensors"
fi

# Also remove RealisticVision if it exists
rm -f models/checkpoints/realistic_vision_v6_b1.safetensors

echo "💾 Disk space after cleanup:"
df -h

echo "📋 Remaining models:"
echo "Checkpoints:"
ls -la models/checkpoints/
echo "ControlNet:"
ls -la models/controlnet/

# Kill any existing processes
pkill -f "python.*main.py" || true
sleep 5

echo "🚀 Starting ComfyUI with ControlNet Canny..."
nohup python main.py --listen 0.0.0.0 --port 8188 --highvram --fast --disable-smart-memory > comfyui_clean.log 2>&1 &

sleep 15

if pgrep -f "python.*main.py" > /dev/null; then
    echo "✅ ComfyUI started successfully!"
    echo "🎛️  Active configuration:"
    echo "   • Juggernaut XL v10 (7.1GB)"
    echo "   • ControlNet Canny (5GB)"
    echo "   • GPU V100 acceleration"
    echo "🌐 URL: http://$(curl -s ifconfig.me):8188"
else
    echo "❌ ComfyUI failed to start"
    echo "📋 Error log:"
    tail -30 comfyui_clean.log
fi
EOF

echo "🚀 Executing cleanup and restart..."
gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command="bash" < /tmp/cleanup_and_start.sh

echo "✅ Cleanup and restart complete!"
rm /tmp/cleanup_and_start.sh