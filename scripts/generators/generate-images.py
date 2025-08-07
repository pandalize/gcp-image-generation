#!/usr/bin/env python3

import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
import time
import os
from datetime import datetime
import argparse

def setup_pipeline(model_id="stabilityai/stable-diffusion-xl-base-1.0"):
    """Stable Diffusion XLパイプラインのセットアップ"""
    print(f"モデルをロード中: {model_id}")
    
    pipe = StableDiffusionXLPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        use_safetensors=True,
        variant="fp16"
    )
    
    # DPMソルバーで高速化
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
    
    # GPUに移動
    pipe = pipe.to("cuda")
    
    # メモリ最適化
    pipe.enable_xformers_memory_efficient_attention()
    pipe.enable_model_cpu_offload()
    
    return pipe

def generate_batch(pipe, prompt, num_images=100, batch_size=4, output_dir="outputs"):
    """バッチで大量の画像を生成"""
    os.makedirs(output_dir, exist_ok=True)
    
    total_start = time.time()
    generated = 0
    
    print(f"\n生成開始: {num_images}枚の画像を生成します")
    print(f"プロンプト: {prompt}")
    print(f"バッチサイズ: {batch_size}")
    print("-" * 50)
    
    while generated < num_images:
        batch_start = time.time()
        current_batch = min(batch_size, num_images - generated)
        
        # 画像生成
        with torch.autocast("cuda"):
            images = pipe(
                prompt=[prompt] * current_batch,
                num_inference_steps=25,  # 速度重視で少なめ
                guidance_scale=7.5,
                height=1024,
                width=1024
            ).images
        
        # 保存
        for i, image in enumerate(images):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{output_dir}/image_{timestamp}_{generated + i:04d}.png"
            image.save(filename)
        
        generated += current_batch
        batch_time = time.time() - batch_start
        
        print(f"進捗: {generated}/{num_images} | "
              f"バッチ時間: {batch_time:.2f}秒 | "
              f"速度: {current_batch/batch_time:.2f}枚/秒")
    
    total_time = time.time() - total_start
    print("-" * 50)
    print(f"\n完了! 総生成時間: {total_time:.2f}秒")
    print(f"平均速度: {num_images/total_time:.2f}枚/秒")
    print(f"推定時間コスト: {total_time/3600 * 3000:.0f}円")

def main():
    parser = argparse.ArgumentParser(description="高速画像生成スクリプト")
    parser.add_argument("--prompt", type=str, 
                       default="beautiful landscape, highly detailed, 8k, photorealistic",
                       help="生成プロンプト")
    parser.add_argument("--num-images", type=int, default=1000,
                       help="生成する画像数")
    parser.add_argument("--batch-size", type=int, default=4,
                       help="バッチサイズ")
    parser.add_argument("--output-dir", type=str, default="outputs",
                       help="出力ディレクトリ")
    
    args = parser.parse_args()
    
    # パイプラインセットアップ
    pipe = setup_pipeline()
    
    # 画像生成
    generate_batch(
        pipe,
        prompt=args.prompt,
        num_images=args.num_images,
        batch_size=args.batch_size,
        output_dir=args.output_dir
    )

if __name__ == "__main__":
    main()