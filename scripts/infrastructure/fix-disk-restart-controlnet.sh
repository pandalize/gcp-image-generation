#!/bin/bash

# Fix disk space and restart ComfyUI with ControlNet
echo "🛠️  Fixing disk space and restarting ControlNet..."
echo "================================================"

INSTANCE_NAME="instance-20250807-125905"
ZONE="us-central1-c"

cat << 'EOF' > /tmp/fix_disk_restart.sh
#!/bin/bash

echo "🧹 Cleaning up disk space..."
cd /home/fujinoyuki/ComfyUI

# Remove incomplete downloads
rm -f models/controlnet/diffusers_xl_openpose_full.safetensors
rm -f models/controlnet/diffusers_xl_depth_full.safetensors

# Clean up any temporary files
rm -f *.tmp
rm -f /tmp/*
find . -name "*.log" -size +10M -delete
find . -name "*.pyc" -delete

echo "💾 Disk space after cleanup:"
df -h

# Kill any existing ComfyUI processes
pkill -f "python.*main.py" || true
sleep 5

echo "🚀 Starting ComfyUI with ControlNet Canny support..."
cd /home/fujinoyuki/ComfyUI
nohup python main.py --listen 0.0.0.0 --port 8188 --highvram --fast > comfyui_controlnet.log 2>&1 &

sleep 10

if pgrep -f "python.*main.py" > /dev/null; then
    echo "✅ ComfyUI with ControlNet is running!"
    echo "🎛️  Available models:"
    echo "   • Juggernaut XL v10 (checkpoint)"
    echo "   • SDXL ControlNet Canny (edge detection)"
    echo "🌐 URL: http://$(curl -s ifconfig.me):8188"
else
    echo "❌ Failed to start ComfyUI"
    echo "📋 Recent log:"
    tail -10 comfyui_controlnet.log
fi
EOF

echo "🚀 Executing disk cleanup and restart..."
gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command="chmod +x && bash" < /tmp/fix_disk_restart.sh

rm /tmp/fix_disk_restart.sh

echo "✅ ControlNet setup with disk cleanup complete!"