#!/bin/bash

# Restart ComfyUI with ControlNet on V100
echo "🔄 Restarting ComfyUI with ControlNet..."
echo "======================================="

INSTANCE_NAME="instance-20250807-125905"
ZONE="us-central1-c"

cat << 'EOF' > /tmp/restart_comfyui.sh
#!/bin/bash

echo "🛑 Stopping any existing ComfyUI processes..."
pkill -f "python.*main.py" || true
sleep 5

echo "🧹 Cleaning up processes..."
ps aux | grep python | grep -v grep

# Navigate to ComfyUI directory
if [ -d "/home/fujinoyuki/ComfyUI" ]; then
    cd /home/fujinoyuki/ComfyUI
else
    echo "❌ ComfyUI directory not found!"
    exit 1
fi

echo "📍 Current directory: $(pwd)"
echo "🔍 Available models:"
echo "Checkpoints:"
ls -la models/checkpoints/ | head -5
echo "ControlNet:"
ls -la models/controlnet/ | head -5

echo "💾 Disk space:"
df -h / | tail -1

echo "🚀 Starting ComfyUI with ControlNet support..."
nohup python main.py --listen 0.0.0.0 --port 8188 --highvram --fast > comfyui_restart.log 2>&1 &

echo "⏳ Waiting for startup..."
sleep 15

if pgrep -f "python.*main.py" > /dev/null; then
    echo "✅ ComfyUI with ControlNet is running!"
    echo "🎛️  Available features:"
    echo "   • Juggernaut XL v10 (latest 2025 model)"
    echo "   • SDXL ControlNet Canny (edge control)"
    echo "   • GPU acceleration enabled"
    echo "🌐 Access: http://$(curl -s ifconfig.me):8188"
else
    echo "❌ ComfyUI failed to start"
    echo "📋 Recent log:"
    tail -20 comfyui_restart.log
fi
EOF

echo "🚀 Executing restart on V100..."
gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command="bash" < /tmp/restart_comfyui.sh

if [ $? -eq 0 ]; then
    echo "✅ ComfyUI restart completed!"
    echo "🌐 ComfyUI URL: http://34.70.230.62:8188"
    echo "🎛️  Ready for ControlNet + Juggernaut XL v10 generation"
else
    echo "❌ Restart failed"
fi

rm /tmp/restart_comfyui.sh