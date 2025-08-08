#!/usr/bin/env python3
"""
最後の2枚を生成するスクリプト
"""

import requests
import json
import time
import random

def generate_final_two():
    base_url = 'http://localhost:8188'
    
    # バリエーション1: エメラルドグリーンの瞳の美女
    positive1 = """RAW photo, (photorealistic:1.4), (hyperrealistic:1.3), professional portrait photography, 
stunning beautiful woman, 26 years old, ethereal natural beauty, mesmerizing emerald green eyes with golden flecks,
silky auburn hair cascading over shoulders, perfect bone structure, porcelain skin with natural freckles,
(highly detailed skin:1.3), visible skin texture, subsurface scattering,

luxury fashion model, graceful pose, serene expression with enigmatic smile,
wearing haute couture evening gown, jewelry by Cartier,

shot on Phase One XF IQ4, 110mm lens, f/2.8, medium format sensor,
butterfly lighting setup, beauty dish key light, silver reflector fill,
studio strobe lighting, perfect catchlights in eyes,

(8K resolution:1.2), ultra sharp details, medium format quality,
professional retouching, fashion magazine cover quality,
Harper's Bazaar aesthetic, Irving Penn inspired minimalism,

award-winning beauty portrait, gallery exhibition quality,
masterpiece, best quality, flawless execution,
creamy bokeh, tack sharp focus on eyes"""
    
    # バリエーション2: 北欧系プラチナブロンドの美女
    positive2 = """RAW photo, (photorealistic:1.4), (hyperrealistic:1.3), professional portrait photography,
breathtaking Scandinavian beauty, 24 years old, ethereal Nordic features, crystal blue eyes like arctic ice,
natural platinum blonde hair in elegant updo, high cheekbones, alabaster skin with rosy undertones,
(highly detailed skin:1.3), natural skin texture visible, subsurface scattering,

high fashion supermodel, confident power pose, captivating direct gaze,
wearing minimalist designer outfit by Jil Sander, statement earrings,

shot on Leica S3, 90mm Summicron lens, f/2.0, exceptional sharpness,
classic Rembrandt lighting, north-facing window light, white v-flat reflector,
natural daylight studio, subtle rim lighting on hair,

(8K resolution:1.2), medium format quality, exceptional detail,
minimal retouching preserving natural beauty,
Scandinavian minimalist aesthetic, Peter Lindbergh inspired naturalism,

museum-quality fine art portrait, timeless elegance,
masterpiece, best quality, authentic beauty,
shallow depth of field, crystalline sharpness on facial features"""
    
    negative = """worst quality, low quality, normal quality, lowres, bad anatomy, bad hands,
monochrome, grayscale, cropped, oversaturated, extra limbs, missing limbs,
deformed hands, long neck, mutation, deformed, ugly, blurry,
bad art, bad anatomy, 3d render, anime, cartoon, animated,
amateur photography, harsh lighting, instagram filter, plastic skin,
over-processed, artificial looking, uncanny valley, doll-like"""
    
    prompts = [positive1, positive2]
    
    for i, positive in enumerate(prompts):
        seed = int(time.time() * 1000000 + i * 10000) % (2**32)
        
        workflow = {
            '1': {'inputs': {'ckpt_name': 'juggernaut_v10.safetensors'}, 'class_type': 'CheckpointLoaderSimple'},
            '2': {'inputs': {'text': positive, 'clip': ['1', 1]}, 'class_type': 'CLIPTextEncode'},
            '3': {'inputs': {'text': negative, 'clip': ['1', 1]}, 'class_type': 'CLIPTextEncode'},
            '4': {'inputs': {'width': 896, 'height': 1152, 'batch_size': 1}, 'class_type': 'EmptyLatentImage'},
            '5': {'inputs': {
                'seed': seed,
                'steps': 110,
                'cfg': 9.8,
                'sampler_name': 'dpmpp_2m',
                'scheduler': 'karras',
                'denoise': 1.0,
                'model': ['1', 0],
                'positive': ['2', 0],
                'negative': ['3', 0],
                'latent_image': ['4', 0]
            }, 'class_type': 'KSampler'},
            '6': {'inputs': {'samples': ['5', 0], 'vae': ['1', 2]}, 'class_type': 'VAEDecode'},
            '7': {'inputs': {'filename_prefix': f'ULTIMATE_BEAUTY', 'images': ['6', 0]}, 'class_type': 'SaveImage'}
        }
        
        try:
            response = requests.post(f'{base_url}/prompt', json={'prompt': workflow}, timeout=30)
            if response.status_code == 200:
                result = response.json()
                prompt_id = result.get('prompt_id')
                print(f'✅ Queued image {9+i}/10: {prompt_id}')
                print(f'   Style: {"Emerald Beauty" if i == 0 else "Nordic Beauty"}')
                print(f'   Seed: {seed}')
                
                # 生成完了まで待機
                print(f'⏳ Waiting for generation to complete...')
                time.sleep(90)  # 90秒待機
                
            else:
                print(f'❌ Failed to queue image {9+i}')
        except Exception as e:
            print(f'❌ Error: {e}')
    
    print('\n🎉 Final 2 images generation completed!')
    print('📁 Images saved to: /home/fujinoyuki/ComfyUI/output/')

if __name__ == "__main__":
    generate_final_two()