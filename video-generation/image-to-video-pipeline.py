#!/usr/bin/env python3

import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from diffusers import StableVideoDiffusionPipeline
from diffusers.utils import load_image, export_to_video
import numpy as np
from PIL import Image
import cv2
import os
import time
from datetime import datetime
import argparse
from tqdm import tqdm

class ImageToVideoPipeline:
    """画像生成→動画変換の統合パイプライン"""
    
    def __init__(self, device="cuda"):
        self.device = device
        self.image_pipe = None
        self.video_pipe = None
        
    def setup_image_pipeline(self, model_id="stabilityai/stable-diffusion-xl-base-1.0"):
        """Stable Diffusion XL画像生成パイプライン"""
        print(f"画像生成モデルをロード中: {model_id}")
        
        self.image_pipe = StableDiffusionXLPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            use_safetensors=True,
            variant="fp16"
        )
        
        self.image_pipe.scheduler = DPMSolverMultistepScheduler.from_config(
            self.image_pipe.scheduler.config
        )
        
        self.image_pipe = self.image_pipe.to(self.device)
        self.image_pipe.enable_xformers_memory_efficient_attention()
        
        return self.image_pipe
    
    def setup_video_pipeline(self, model_id="stabilityai/stable-video-diffusion-img2vid-xt"):
        """Stable Video Diffusion動画生成パイプライン"""
        print(f"動画生成モデルをロード中: {model_id}")
        
        self.video_pipe = StableVideoDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            variant="fp16"
        )
        
        self.video_pipe = self.video_pipe.to(self.device)
        self.video_pipe.enable_xformers_memory_efficient_attention()
        
        return self.video_pipe
    
    def generate_keyframes(self, prompts, output_dir="outputs/images", batch_size=4):
        """複数のキーフレーム画像を生成"""
        os.makedirs(output_dir, exist_ok=True)
        generated_images = []
        
        print(f"\n{len(prompts)}枚のキーフレームを生成中...")
        
        for i, prompt in enumerate(tqdm(prompts, desc="キーフレーム生成")):
            with torch.autocast("cuda"):
                image = self.image_pipe(
                    prompt=prompt,
                    num_inference_steps=25,
                    guidance_scale=7.5,
                    height=768,  # SVDに適したサイズ
                    width=768
                ).images[0]
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{output_dir}/keyframe_{i:03d}_{timestamp}.png"
            image.save(filename)
            generated_images.append(image)
            
        return generated_images
    
    def interpolate_frames(self, image1, image2, num_frames=8):
        """2つの画像間を補間してトランジションフレームを生成"""
        frames = []
        img1_array = np.array(image1)
        img2_array = np.array(image2)
        
        for i in range(num_frames):
            alpha = i / (num_frames - 1)
            interpolated = (1 - alpha) * img1_array + alpha * img2_array
            frames.append(Image.fromarray(interpolated.astype(np.uint8)))
            
        return frames
    
    def generate_video_from_image(self, image, num_frames=25, motion_bucket_id=127):
        """単一画像から動画を生成（Stable Video Diffusion）"""
        
        # 画像を正しいサイズにリサイズ
        image = image.resize((768, 768))
        
        with torch.autocast("cuda"):
            frames = self.video_pipe(
                image,
                decode_chunk_size=8,
                num_frames=num_frames,
                motion_bucket_id=motion_bucket_id,  # モーション強度（0-255）
                noise_aug_strength=0.02
            ).frames[0]
        
        return frames
    
    def create_video_sequence(self, keyframe_prompts, output_path="output_video.mp4", fps=30):
        """完全な動画シーケンスを作成"""
        
        # 1. キーフレーム生成
        keyframes = self.generate_keyframes(keyframe_prompts)
        
        all_frames = []
        
        # 2. 各キーフレームから動画セグメントを生成
        print("\n動画セグメントを生成中...")
        for i, keyframe in enumerate(tqdm(keyframes, desc="動画化")):
            video_frames = self.generate_video_from_image(
                keyframe,
                num_frames=25,
                motion_bucket_id=180  # 高めのモーション
            )
            all_frames.extend(video_frames)
            
            # キーフレーム間のトランジション
            if i < len(keyframes) - 1:
                transition_frames = self.interpolate_frames(
                    keyframe, keyframes[i + 1], num_frames=10
                )
                all_frames.extend(transition_frames)
        
        # 3. 動画として出力
        export_to_video(all_frames, output_path, fps=fps)
        print(f"\n動画を保存しました: {output_path}")
        
        return output_path

def generate_massive_content(pipeline, num_videos=100, videos_per_prompt=10):
    """大量の動画コンテンツを生成"""
    
    base_prompts = [
        "futuristic city with flying cars, neon lights, cyberpunk aesthetic",
        "magical forest with glowing mushrooms, fairy lights, mystical atmosphere",
        "underwater coral reef, colorful fish, sunlight rays through water",
        "space station orbiting Earth, astronauts, stars in background",
        "ancient temple ruins, overgrown with vines, mysterious atmosphere",
        "steampunk airship flying through clouds, brass gears, Victorian era",
        "northern lights over snowy mountains, aurora borealis, night sky",
        "japanese garden in autumn, red maple leaves, koi pond, zen atmosphere",
        "volcanic eruption at sunset, lava flows, dramatic sky",
        "alien landscape with multiple moons, strange plants, otherworldly"
    ]
    
    total_start = time.time()
    generated_count = 0
    
    print(f"\n=== 大量動画生成開始: {num_videos}本 ===")
    
    for i in range(0, num_videos, videos_per_prompt):
        prompt_set = base_prompts[i % len(base_prompts)]
        
        # プロンプトのバリエーション作成
        variations = [
            f"{prompt_set}, ultra detailed, 8k quality",
            f"{prompt_set}, cinematic lighting, dramatic mood",
            f"{prompt_set}, wide angle shot, epic scale",
            f"{prompt_set}, close-up detail, macro photography",
            f"{prompt_set}, golden hour lighting, warm tones"
        ]
        
        for j, prompts in enumerate([variations[:3]]):
            output_path = f"outputs/videos/video_{generated_count:04d}.mp4"
            pipeline.create_video_sequence(prompts, output_path)
            generated_count += 1
            
            elapsed = time.time() - total_start
            rate = generated_count / (elapsed / 3600)  # 動画/時間
            estimated_cost = (elapsed / 3600) * 3000  # 推定コスト
            
            print(f"進捗: {generated_count}/{num_videos} | "
                  f"速度: {rate:.2f}本/時間 | "
                  f"推定コスト: {estimated_cost:.0f}円")
    
    total_time = time.time() - total_start
    print(f"\n完了！総時間: {total_time/3600:.2f}時間")
    print(f"総コスト: {(total_time/3600) * 3000:.0f}円")

def main():
    parser = argparse.ArgumentParser(description="画像→動画生成パイプライン")
    parser.add_argument("--mode", choices=["single", "batch", "massive"], 
                       default="single", help="実行モード")
    parser.add_argument("--num-videos", type=int, default=100,
                       help="生成する動画数（massiveモード）")
    parser.add_argument("--prompts", nargs="+", 
                       default=["beautiful sunset over ocean, waves crashing, golden hour"],
                       help="キーフレームのプロンプト")
    parser.add_argument("--output", type=str, default="output_video.mp4",
                       help="出力動画ファイル名")
    
    args = parser.parse_args()
    
    # パイプライン初期化
    pipeline = ImageToVideoPipeline()
    pipeline.setup_image_pipeline()
    pipeline.setup_video_pipeline()
    
    if args.mode == "single":
        # 単一動画生成
        pipeline.create_video_sequence(args.prompts, args.output)
        
    elif args.mode == "massive":
        # 大量生成モード
        generate_massive_content(pipeline, num_videos=args.num_videos)
    
    else:
        print(f"未対応のモード: {args.mode}")

if __name__ == "__main__":
    main()