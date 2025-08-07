#!/usr/bin/env python3
"""
L4 GPU完全版 - 本格AI美女画像生成システム
目標: 最高品質の商用AI美女画像を大量生成
"""
import subprocess
import sys
import os

print("=== L4 GPU完全版AI美女画像生成システム ===")
print("GPU: NVIDIA L4 (23.6GB)")
print("目標: 商用品質AI美女画像 200枚生成")

# 必要パッケージのインストール
def install_ai_packages():
    packages = [
        "diffusers==0.25.0",
        "transformers==4.36.0", 
        "accelerate==0.25.0",
        "safetensors==0.4.1",
        "xformers",  # L4メモリ効率化
        "opencv-python-headless",
        "compel",  # プロンプト強化
    ]
    
    for pkg in packages:
        print(f"Installing: {pkg}")
        subprocess.run([sys.executable, "-m", "pip", "install", pkg], check=True)

print("Step 1: AI画像生成ライブラリをインストール中...")
try:
    install_ai_packages()
    print("✓ 全パッケージインストール完了")
except Exception as e:
    print(f"パッケージインストールエラー: {e}")
    sys.exit(1)

print("\nStep 2: L4 GPU最適化AI画像生成開始...")

try:
    import torch
    from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
    from PIL import Image
    import random
    import time
    from datetime import datetime
    import gc
    
    # GPU設定確認
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"デバイス: {device}")
    print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A'}")
    
    if device == "cpu":
        print("❌ GPU利用不可 - 終了")
        sys.exit(1)
    
    # 出力ディレクトリ
    output_dir = "l4_ai_beauty_collection"
    os.makedirs(output_dir, exist_ok=True)
    
    print("\nStep 3: 最高品質AI美女モデルをロード中...")
    
    # 最高品質商用モデル
    model_id = "SG161222/RealVisXL_V4.0"  # 最高品質リアル美女モデル
    
    try:
        # パイプライン設定（L4最適化）
        pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16,  # メモリ効率
            safety_checker=None,
            requires_safety_checker=False,
            use_safetensors=True
        )
        
        # L4 GPU最適化
        pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
        pipe = pipe.to(device)
        
        # メモリ最適化（L4用）
        pipe.enable_attention_slicing()
        pipe.enable_vae_slicing() 
        if hasattr(pipe, 'enable_xformers_memory_efficient_attention'):
            pipe.enable_xformers_memory_efficient_attention()
        
        print("✓ AI美女モデル完全ロード完了")
        
    except Exception as e:
        print(f"モデルロードエラー: {e}")
        print("フォールバック: Stable Diffusion v1.5を使用...")
        
        # フォールバック：確実に動作するモデル
        model_id = "runwayml/stable-diffusion-v1-5"
        pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            safety_checker=None,
            requires_safety_checker=False
        )
        pipe = pipe.to(device)
        pipe.enable_attention_slicing()
    
    print("\nStep 4: 最高品質美女プロンプト準備...")
    
    # 超高品質美女プロンプト（商用向け）
    premium_beauty_prompts = [
        "(masterpiece, best quality, ultra detailed, 8k), beautiful elegant woman, professional studio portrait, perfect face, symmetrical features, natural soft lighting, high fashion model, commercial photography style, photorealistic",
        
        "(photorealistic, ultra high quality), stunning asian businesswoman, confident smile, modern office background, natural beauty, perfect skin, executive portrait, commercial headshot style",
        
        "(masterpiece, professional photography), gorgeous european model, haute couture fashion, studio lighting, elegant pose, natural expression, commercial beauty photography, ultra detailed, 8k quality",
        
        "(best quality, ultra realistic), beautiful woman in casual elegant style, natural daylight, genuine smile, lifestyle photography, modern fashion, commercial quality portrait",
        
        "(8k, photorealistic, professional), elegant business executive, confident pose, corporate portrait, natural beauty, high-end commercial photography style",
        
        "(masterpiece, commercial photography), stunning fashion model, professional lighting, elegant styling, natural beauty, high fashion portrait, ultra detailed",
        
        "(ultra high quality, photorealistic), beautiful woman summer portrait, golden hour lighting, natural beauty, outdoor lifestyle photography, commercial grade",
        
        "(professional photography, 8k), gorgeous woman in evening attire, sophisticated pose, elegant lighting, formal portrait, commercial beauty photography",
        
        "(masterpiece, best quality), beautiful casual portrait, natural lighting, genuine expression, lifestyle fashion, commercial photography quality, ultra realistic",
        
        "(photorealistic, commercial grade), elegant woman portrait, business professional, natural lighting, confident expression, executive photography style"
    ]
    
    # 高品質ネガティブプロンプト
    negative_prompt = """
    (low quality, worst quality, bad quality), lowres, bad anatomy, bad hands, text, error, 
    missing fingers, extra digit, fewer digits, cropped, jpeg artifacts, signature, watermark, 
    username, blurry, artist name, deformed, disfigured, ugly, duplicate, extra limbs, 
    malformed limbs, poorly drawn hands, poorly drawn face, mutation, bad proportions, 
    gross proportions, long neck, extra arms, extra legs, extra fingers, missing arms, 
    missing legs, fused fingers, too many fingers, unclear eyes
    """
    
    print("✓ プレミアム美女プロンプト準備完了")
    
    print("\nStep 5: L4 GPU大量生成開始...")
    
    # 生成設定
    total_images = 200  # 200枚の最高品質美女画像
    batch_size = 10
    num_batches = total_images // batch_size
    
    generated_count = 0
    start_time = time.time()
    
    for batch in range(num_batches):
        batch_start_time = time.time()
        print(f"\n=== Batch {batch + 1}/{num_batches} ===")
        
        for i in range(batch_size):
            try:
                # ランダム設定
                prompt = random.choice(premium_beauty_prompts)
                width = random.choice([768, 832, 896])
                height = random.choice([768, 832, 896]) 
                steps = random.choice([25, 30, 35])
                guidance = random.uniform(7.0, 9.5)
                seed = random.randint(0, 2**32-1)
                
                print(f"生成中 {generated_count + 1}/{total_images}: {width}x{height}, {steps}steps, seed={seed}")
                
                # AI美女画像生成
                with torch.cuda.amp.autocast():  # 混合精度で高速化
                    image = pipe(
                        prompt=prompt,
                        negative_prompt=negative_prompt,
                        width=width,
                        height=height,
                        num_inference_steps=steps,
                        guidance_scale=guidance,
                        generator=torch.manual_seed(seed)
                    ).images[0]
                
                # 高品質保存
                timestamp = datetime.now().strftime("%H%M%S_%f")[:-3]
                filename = f"{output_dir}/l4_beauty_{batch+1:02d}_{i+1:02d}_{timestamp}.png"
                image.save(filename, quality=95, optimize=True, dpi=(300, 300))
                
                generated_count += 1
                
                # 進捗表示
                elapsed = time.time() - start_time
                avg_time = elapsed / generated_count if generated_count > 0 else 0
                eta = avg_time * (total_images - generated_count)
                
                print(f"   ✓ 保存: {filename}")
                print(f"   進捗: {generated_count}/{total_images} ({generated_count/total_images*100:.1f}%)")
                print(f"   ETA: {eta/60:.1f}分")
                
                # メモリ管理
                del image
                torch.cuda.empty_cache()
                gc.collect()
                
            except Exception as e:
                print(f"   ✗ 生成エラー: {e}")
                continue
        
        batch_time = time.time() - batch_start_time
        print(f"Batch {batch + 1} 完了: {batch_time/60:.1f}分")
        print(f"GPU温度チェック...")
        
        # GPU状態確認
        if generated_count % 20 == 0:
            gpu_memory = torch.cuda.memory_allocated() / 1e9
            print(f"GPU Memory使用: {gpu_memory:.2f} GB")
        
        # GPU休憩
        time.sleep(1)
    
    total_time = time.time() - start_time
    
    print(f"\n=== L4 GPU AI美女画像生成完了！ ===")
    print(f"生成画像数: {generated_count}")
    print(f"総生成時間: {total_time/60:.1f}分")
    print(f"平均生成時間: {total_time/generated_count:.2f}秒/枚")
    print(f"出力ディレクトリ: {output_dir}/")
    print(f"推定GPU使用コスト: ${generated_count * 0.01:.2f}")
    
    # 最終GPU統計
    if torch.cuda.is_available():
        max_memory = torch.cuda.max_memory_allocated() / 1e9
        print(f"最大GPU Memory使用: {max_memory:.2f} GB")
    
    print("\n🎉 商用品質AI美女画像コレクション完成！")

except ImportError as e:
    print(f"インポートエラー: {e}")
    print("必要なライブラリがインストールされていません")
    
except Exception as e:
    print(f"実行エラー: {e}")
    import traceback
    traceback.print_exc()

print("\n=== L4 GPU AI美女生成システム終了 ===")