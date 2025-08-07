#!/bin/bash

# Final ControlNet startup with correct Python path
echo "🎛️ Final ControlNet startup..."
echo "==============================="

INSTANCE_NAME="instance-20250807-125905"
ZONE="us-central1-c"

cat << 'EOF' > /tmp/final_start.sh
#!/bin/bash

echo "🔍 Finding Python and starting ComfyUI..."

# Go to ComfyUI directory
cd /home/fujinoyuki/ComfyUI || exit 1

echo "📍 Current directory: $(pwd)"

# Find Python executable
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python not found!"
    exit 1
fi

echo "🐍 Using Python: $PYTHON_CMD"
echo "📋 Python version: $($PYTHON_CMD --version)"

# Check if virtual environment exists
if [ -d "comfyui_env" ]; then
    echo "🔄 Activating virtual environment..."
    source comfyui_env/bin/activate
    PYTHON_CMD="python"
fi

echo "💾 Current disk space:"
df -h / | tail -1

echo "📦 Available models:"
echo "  • $(ls models/checkpoints/*.safetensors | wc -l) checkpoint(s)"
echo "  • $(ls models/controlnet/*.safetensors | wc -l) ControlNet model(s)"

# Kill any existing processes
pkill -f "python.*main.py" || true
sleep 3

echo "🚀 Starting ComfyUI with ControlNet..."
nohup $PYTHON_CMD main.py --listen 0.0.0.0 --port 8188 --highvram --fast > comfyui_final.log 2>&1 &

echo "⏳ Waiting for ComfyUI to start..."
for i in {1..20}; do
    sleep 3
    if pgrep -f "python.*main.py" > /dev/null; then
        echo "✅ ComfyUI process detected!"
        break
    fi
    echo "Waiting... ($i/20)"
done

# Test connection
echo "🔗 Testing connection..."
if curl -s http://localhost:8188 > /dev/null 2>&1; then
    echo "✅ ComfyUI is responding!"
    echo "🎛️ ControlNet + Juggernaut XL v10 ready!"
    echo "🌐 URL: http://$(curl -s ifconfig.me):8188"
else
    echo "❌ ComfyUI not responding"
    echo "📋 Recent log:"
    tail -20 comfyui_final.log
fi
EOF

echo "🚀 Executing final startup..."
gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command="bash" < /tmp/final_start.sh

rm /tmp/final_start.sh

echo "🎉 ControlNet startup sequence complete!"