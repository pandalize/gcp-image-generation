#!/usr/bin/env python3

import torch
import numpy as np
from PIL import Image
import cv2
from diffusers import StableDiffusionXLPipeline, AnimateDiffPipeline, ControlNetModel
from transformers import pipeline as hf_pipeline
import moviepy.editor as mpe
from moviepy.video.fx import resize, fadein, fadeout
import os
from tqdm import tqdm
import argparse

class AdvancedVideoEffects:
    """高度な動画エフェクトと処理"""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def create_animated_sequence(self, base_prompt, num_frames=120, fps=30):
        """AnimateDiffを使用したアニメーション生成"""
        print("AnimateDiffでアニメーション生成中...")
        
        # AnimateDiffパイプライン
        pipe = AnimateDiffPipeline.from_pretrained(
            "guoyww/animatediff-motion-adapter-v1-5-2",
            torch_dtype=torch.float16
        ).to(self.device)
        
        # 時間経過に応じたプロンプト変化
        prompts = []
        for i in range(num_frames // 16):  # 16フレームごと
            time_modifier = [
                "sunrise", "morning", "noon", "afternoon", 
                "sunset", "evening", "night", "midnight"
            ][i % 8]
            prompts.append(f"{base_prompt}, {time_modifier} lighting")
        
        frames = []
        for prompt in tqdm(prompts, desc="アニメーション生成"):
            with torch.autocast("cuda"):
                output = pipe(
                    prompt=prompt,
                    num_frames=16,
                    guidance_scale=7.5,
                    num_inference_steps=25
                )
                frames.extend(output.frames[0])
        
        return frames
    
    def apply_style_transfer(self, video_frames, style="anime"):
        """スタイル変換を適用"""
        print(f"スタイル変換を適用中: {style}")
        
        style_prompts = {
            "anime": "anime style, studio ghibli, colorful",
            "oil_painting": "oil painting, van gogh style, textured",
            "watercolor": "watercolor painting, soft edges, artistic",
            "cyberpunk": "cyberpunk style, neon, futuristic",
            "photorealistic": "photorealistic, 8k, highly detailed"
        }
        
        styled_frames = []
        for frame in tqdm(video_frames, desc="スタイル変換"):
            # ここでimg2imgを使用してスタイル変換
            styled_frame = self.apply_img2img(frame, style_prompts.get(style, style))
            styled_frames.append(styled_frame)
        
        return styled_frames
    
    def apply_img2img(self, image, prompt, strength=0.75):
        """img2imgでフレームを変換"""
        pipe = StableDiffusionXLPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0",
            torch_dtype=torch.float16
        ).to(self.device)
        
        with torch.autocast("cuda"):
            result = pipe(
                prompt=prompt,
                image=image,
                strength=strength,
                guidance_scale=7.5
            ).images[0]
        
        return result
    
    def create_morphing_video(self, start_image, end_image, duration=5, fps=30):
        """画像間のモーフィング動画を作成"""
        print("モーフィング動画を生成中...")
        
        num_frames = duration * fps
        frames = []
        
        start_array = np.array(start_image)
        end_array = np.array(end_image)
        
        for i in range(num_frames):
            alpha = i / (num_frames - 1)
            # 非線形補間でよりスムーズな遷移
            alpha = self.ease_in_out(alpha)
            
            morphed = (1 - alpha) * start_array + alpha * end_array
            
            # ノイズを追加して自然な遷移に
            noise = np.random.normal(0, 5, morphed.shape)
            morphed = np.clip(morphed + noise * (1 - abs(2 * alpha - 1)), 0, 255)
            
            frames.append(Image.fromarray(morphed.astype(np.uint8)))
        
        return frames
    
    def ease_in_out(self, t):
        """イージング関数"""
        return t * t * (3.0 - 2.0 * t)
    
    def add_cinematic_effects(self, video_path, output_path):
        """映画的エフェクトを追加"""
        print("映画的エフェクトを追加中...")
        
        clip = mpe.VideoFileClip(video_path)
        
        # エフェクトチェーン
        clip = clip.fx(resize, width=1920)  # Full HD
        clip = clip.fx(fadein, duration=1)  # フェードイン
        clip = clip.fx(fadeout, duration=1)  # フェードアウト
        
        # レターボックス（映画的黒帯）
        clip = self.add_letterbox(clip)
        
        # カラーグレーディング
        clip = self.apply_color_grading(clip)
        
        # 音楽を追加（オプション）
        # audio = mpe.AudioFileClip("background_music.mp3")
        # clip = clip.set_audio(audio)
        
        clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
        
        return output_path
    
    def add_letterbox(self, clip, aspect_ratio=2.35):
        """レターボックス（黒帯）を追加"""
        w, h = clip.size
        target_h = int(w / aspect_ratio)
        
        if target_h < h:
            bar_height = (h - target_h) // 2
            clip = clip.crop(y1=bar_height, y2=h-bar_height)
        
        return clip
    
    def apply_color_grading(self, clip):
        """カラーグレーディング"""
        def process_frame(frame):
            # 暖色系のトーンを追加
            frame = frame.astype(float)
            frame[:, :, 0] *= 1.1  # 赤を強調
            frame[:, :, 2] *= 0.9  # 青を抑制
            
            # コントラスト調整
            frame = np.clip(frame * 1.2 - 30, 0, 255)
            
            return frame.astype('uint8')
        
        return clip.fl_image(process_frame)
    
    def create_timelapse(self, frames, speedup_factor=10):
        """タイムラプス動画を作成"""
        print(f"タイムラプス作成中（{speedup_factor}倍速）...")
        
        # フレームを間引き
        selected_frames = frames[::speedup_factor]
        
        # モーションブラーを追加
        blurred_frames = []
        for i in range(len(selected_frames)):
            if i > 0:
                # 前フレームとブレンド
                prev = np.array(selected_frames[i-1])
                curr = np.array(selected_frames[i])
                blended = cv2.addWeighted(prev, 0.3, curr, 0.7, 0)
                blurred_frames.append(Image.fromarray(blended))
            else:
                blurred_frames.append(selected_frames[i])
        
        return blurred_frames
    
    def create_slow_motion(self, frames, slowdown_factor=4):
        """スローモーション動画を作成"""
        print(f"スローモーション作成中（{slowdown_factor}倍スロー）...")
        
        interpolated_frames = []
        
        for i in range(len(frames) - 1):
            interpolated_frames.append(frames[i])
            
            # フレーム間を補間
            for j in range(1, slowdown_factor):
                alpha = j / slowdown_factor
                frame1 = np.array(frames[i])
                frame2 = np.array(frames[i + 1])
                
                # オプティカルフロー計算（簡易版）
                interpolated = (1 - alpha) * frame1 + alpha * frame2
                interpolated_frames.append(Image.fromarray(interpolated.astype(np.uint8)))
        
        interpolated_frames.append(frames[-1])
        
        return interpolated_frames

def generate_creative_videos():
    """クリエイティブな動画を大量生成"""
    
    effects = AdvancedVideoEffects()
    
    creative_prompts = [
        "time-lapse of flower blooming, macro photography",
        "city transforming from day to night, urban landscape",
        "seasons changing in forest, nature documentary",
        "abstract colors morphing, psychedelic art",
        "underwater coral reef coming to life, nature documentary",
        "futuristic city being built, sci-fi visualization",
        "paint spreading on canvas, artistic process",
        "clouds forming and dissipating, weather time-lapse",
        "galaxy formation, space documentary",
        "metamorphosis of butterfly, nature macro"
    ]
    
    for i, prompt in enumerate(creative_prompts):
        print(f"\n生成中 ({i+1}/{len(creative_prompts)}): {prompt}")
        
        # アニメーション生成
        frames = effects.create_animated_sequence(prompt, num_frames=120)
        
        # エフェクト適用（ランダムに選択）
        import random
        effect_type = random.choice(["anime", "oil_painting", "cyberpunk"])
        frames = effects.apply_style_transfer(frames, style=effect_type)
        
        # タイムラプスまたはスローモーション
        if "time-lapse" in prompt:
            frames = effects.create_timelapse(frames, speedup_factor=5)
        elif "slow" in prompt or "macro" in prompt:
            frames = effects.create_slow_motion(frames, slowdown_factor=3)
        
        # 動画として保存
        output_path = f"outputs/creative/video_{i:03d}_{effect_type}.mp4"
        save_frames_as_video(frames, output_path)
        
        print(f"保存完了: {output_path}")

def save_frames_as_video(frames, output_path, fps=30):
    """フレームリストを動画として保存"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 一時的に画像として保存
    temp_dir = "temp_frames"
    os.makedirs(temp_dir, exist_ok=True)
    
    for i, frame in enumerate(frames):
        frame.save(f"{temp_dir}/frame_{i:05d}.png")
    
    # FFmpegで動画化
    os.system(f"ffmpeg -r {fps} -i {temp_dir}/frame_%05d.png -c:v libx264 -pix_fmt yuv420p {output_path}")
    
    # 一時ファイル削除
    os.system(f"rm -rf {temp_dir}")

def main():
    parser = argparse.ArgumentParser(description="高度な動画エフェクト生成")
    parser.add_argument("--mode", choices=["creative", "morphing", "timelapse"], 
                       default="creative", help="生成モード")
    parser.add_argument("--prompt", type=str, 
                       default="beautiful landscape transforming through seasons",
                       help="ベースプロンプト")
    
    args = parser.parse_args()
    
    if args.mode == "creative":
        generate_creative_videos()
    else:
        effects = AdvancedVideoEffects()
        frames = effects.create_animated_sequence(args.prompt)
        save_frames_as_video(frames, "output_advanced.mp4")

if __name__ == "__main__":
    main()