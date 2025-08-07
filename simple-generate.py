#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFilter
import random
import os
from datetime import datetime

print("=== シンプル画像生成 ===")

output_dir = os.path.expanduser("~/generated_images")
os.makedirs(output_dir, exist_ok=True)

prompts = [
    "Sunset over Mount Fuji",
    "Cyberpunk Tokyo Streets",
    "Serene Japanese Garden",
    "Futuristic Space Station",
    "Enchanted Forest"
]

for i, prompt in enumerate(prompts, 1):
    print(f"[{i}/{len(prompts)}] 生成中: {prompt}")
    
    # 512x512の画像を作成
    img = Image.new('RGB', (512, 512))
    draw = ImageDraw.Draw(img)
    
    # プロンプトに応じた背景グラデーション
    if "Sunset" in prompt:
        # オレンジ〜赤のグラデーション
        for y in range(512):
            r = min(255, 220 - y//4)
            g = min(255, 150 - y//3)
            b = min(255, 50 + y//4)
            draw.rectangle([(0, y), (512, y+1)], fill=(r, g, b))
    elif "Cyberpunk" in prompt:
        # ネオンブルー〜パープル
        for y in range(512):
            r = min(255, y//3)
            g = min(255, 50 + y//4)
            b = min(255, 200 + y//10)
            draw.rectangle([(0, y), (512, y+1)], fill=(r, g, b))
    elif "Garden" in prompt:
        # 緑のグラデーション
        for y in range(512):
            r = min(255, 100 + y//5)
            g = min(255, 200 - y//10)
            b = min(255, 100 + y//5)
            draw.rectangle([(0, y), (512, y+1)], fill=(r, g, b))
    elif "Space" in prompt:
        # 宇宙の黒〜深い青
        for y in range(512):
            r = min(255, y//10)
            g = min(255, y//8)
            b = min(255, 30 + y//3)
            draw.rectangle([(0, y), (512, y+1)], fill=(r, g, b))
    else:
        # 神秘的な紫〜緑
        for y in range(512):
            r = min(255, 150 - y//5)
            g = min(255, 100 + y//3)
            b = min(255, 200 - y//4)
            draw.rectangle([(0, y), (512, y+1)], fill=(r, g, b))
    
    # ランダムな装飾要素を追加
    for _ in range(20):
        x = random.randint(0, 512)
        y = random.randint(0, 512)
        size = random.randint(5, 30)
        opacity = random.randint(100, 200)
        color = (255, 255, 255, opacity)
        draw.ellipse([x-size, y-size, x+size, y+size], fill=color, outline=None)
    
    # ぼかし効果
    img = img.filter(ImageFilter.GaussianBlur(radius=2))
    
    # タイトルを追加
    draw = ImageDraw.Draw(img)
    draw.rectangle([(10, 470), (502, 502)], fill=(0, 0, 0))
    draw.text((20, 475), f"Demo: {prompt}", fill=(255, 255, 255))
    
    # 保存
    timestamp = datetime.now().strftime("%H%M%S")
    filename = f"{output_dir}/image_{i}_{timestamp}.png"
    img.save(filename)
    print(f"   ✓ 保存: {filename}")

print(f"\n=== 生成完了！===")
print(f"場所: {output_dir}")
print("ls ~/generated_images/ で確認できます")