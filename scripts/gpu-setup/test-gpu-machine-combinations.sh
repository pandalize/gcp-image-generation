#!/bin/bash

# GPU + マシンタイプ組み合わせテストスクリプト

echo "======================================================"
echo "🔍 GPU + マシンタイプ組み合わせテスト"
echo "======================================================"
echo ""
echo "各GPUがどのマシンタイプと組み合わせ可能かテストします"
echo "dry-runでテストするため、実際のVMは作成されません"
echo ""

# テスト関数
test_combination() {
    local gpu_type=$1
    local machine_type=$2
    local test_name="test-$gpu_type-$machine_type-$(date +%s)"
    
    echo "テスト: $gpu_type + $machine_type"
    
    if gcloud compute instances create $test_name \
        --zone=us-central1-a \
        --machine-type=$machine_type \
        --accelerator="type=$gpu_type,count=1" \
        --image-family=ubuntu-2004-lts \
        --image-project=ubuntu-os-cloud \
        --dry-run > /dev/null 2>&1; then
        echo "  ✅ 有効な組み合わせ"
        return 0
    else
        echo "  ❌ 無効な組み合わせ"
        return 1
    fi
}

# T4 GPU テスト
echo "=== T4 GPU テスト ==="
test_combination "nvidia-tesla-t4" "n1-standard-4"
test_combination "nvidia-tesla-t4" "n1-standard-8"
test_combination "nvidia-tesla-t4" "n2-standard-4"
test_combination "nvidia-tesla-t4" "n2-standard-8"
test_combination "nvidia-tesla-t4" "e2-standard-4"
test_combination "nvidia-tesla-t4" "e2-standard-8"
test_combination "nvidia-tesla-t4" "g2-standard-4"
echo ""

# L4 GPU テスト
echo "=== L4 GPU テスト ==="
test_combination "nvidia-l4" "g2-standard-4"
test_combination "nvidia-l4" "g2-standard-8"
test_combination "nvidia-l4" "n1-standard-4"
test_combination "nvidia-l4" "n1-standard-8"
test_combination "nvidia-l4" "n2-standard-4"
test_combination "nvidia-l4" "n2-standard-8"
echo ""

# V100 GPU テスト
echo "=== V100 GPU テスト ==="
test_combination "nvidia-tesla-v100" "n1-standard-4"
test_combination "nvidia-tesla-v100" "n1-standard-8"
test_combination "nvidia-tesla-v100" "n1-standard-16"
test_combination "nvidia-tesla-v100" "n2-standard-4"
test_combination "nvidia-tesla-v100" "n2-standard-8"
echo ""

# P100 GPU テスト
echo "=== P100 GPU テスト ==="
test_combination "nvidia-tesla-p100" "n1-standard-4"
test_combination "nvidia-tesla-p100" "n1-standard-8"
test_combination "nvidia-tesla-p100" "n2-standard-4"
test_combination "nvidia-tesla-p100" "n2-standard-8"
echo ""

# P4 GPU テスト
echo "=== P4 GPU テスト ==="
test_combination "nvidia-tesla-p4" "n1-standard-4"
test_combination "nvidia-tesla-p4" "n1-standard-8"
test_combination "nvidia-tesla-p4" "n2-standard-4"
echo ""

# K80 GPU テスト
echo "=== K80 GPU テスト ==="
test_combination "nvidia-tesla-k80" "n1-standard-4"
test_combination "nvidia-tesla-k80" "n1-standard-8"
test_combination "nvidia-tesla-k80" "n2-standard-4"
echo ""

echo "======================================================"
echo "✅ テスト完了"
echo "======================================================"
echo ""
echo "💡 上記の結果をもとに、有効な組み合わせのみを使用した"
echo "   最適化されたGPU検索スクリプトを作成します。"