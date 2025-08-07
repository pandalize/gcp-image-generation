#!/usr/bin/env python3
# 簡単なテスト画像生成（GPUなしでも動作）
from PIL import Image, ImageDraw, ImageFont
import random
import os

# 出力ディレクトリ作成
os.makedirs("test_images", exist_ok=True)

# テスト画像を生成
for i in range(3):
    # ランダムな色でグラデーション画像を作成
    img = Image.new('RGB', (512, 512))
    draw = ImageDraw.Draw(img)
    
    # グラデーション描画
    for y in range(512):
        r = int(255 * (y / 512))
        g = random.randint(100, 200)
        b = random.randint(150, 255)
        draw.rectangle([(0, y), (512, y+1)], fill=(r, g, b))
    
    # テキスト追加
    text = f"GPU Test Image {i+1}"
    draw.text((150, 240), text, fill=(255, 255, 255))
    
    # 保存
    filename = f"test_images/test_{i+1}.png"
    img.save(filename)
    print(f"Created: {filename}")

print("\nTest images created successfully!")
print("Waiting for GPU setup to complete for real AI image generation...")