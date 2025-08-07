#!/usr/bin/env python3
"""
V100性能テスト - 異なる設定で速度比較
"""
import requests
import json
import time
from pathlib import Path

class V100PerformanceTest:
    def __init__(self):
        self.server_ip = "34.70.230.62"
        self.port = 8188
        self.base_url = f"http://{self.server_ip}:{self.port}"
        
    def create_test_workflow(self, test_name, width=512, height=512, steps=10):
        """テスト用ワークフロー"""
        workflow = {
            "3": {
                "inputs": {
                    "seed": int(time.time() * 1000000) % 1000000,
                    "steps": steps,
                    "cfg": 6.0,
                    "sampler_name": "euler",
                    "scheduler": "normal", 
                    "denoise": 1.0,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                },
                "class_type": "KSampler"
            },
            "4": {
                "inputs": {
                    "ckpt_name": "sd_xl_base_1.0.safetensors"
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "5": {
                "inputs": {
                    "width": width,
                    "height": height,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "6": {
                "inputs": {
                    "text": "beautiful woman, high quality, professional photo",
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "7": {
                "inputs": {
                    "text": "low quality, blurry",
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "8": {
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["4", 2]
                },
                "class_type": "VAEDecode"
            },
            "9": {
                "inputs": {
                    "filename_prefix": f"PerfTest_{test_name}_",
                    "images": ["8", 0]
                },
                "class_type": "SaveImage"
            }
        }
        return workflow
    
    def run_performance_test(self):
        """性能テスト実行"""
        print("🚀 V100性能テスト開始")
        print("=" * 50)
        
        test_configs = [
            {"name": "Fast_512", "width": 512, "height": 512, "steps": 10},
            {"name": "Med_768", "width": 768, "height": 768, "steps": 15}, 
            {"name": "High_1024", "width": 1024, "height": 1024, "steps": 20},
        ]
        
        results = []
        
        for config in test_configs:
            print(f"\n🎯 テスト: {config['name']}")
            print(f"📐 解像度: {config['width']}x{config['height']}")
            print(f"⚙️ ステップ: {config['steps']}")
            
            # 開始時間
            start_time = time.time()
            
            # ワークフロー送信
            workflow = self.create_test_workflow(
                config['name'],
                config['width'], 
                config['height'],
                config['steps']
            )
            
            try:
                response = requests.post(
                    f"{self.base_url}/prompt", 
                    json={"prompt": workflow}, 
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    prompt_id = result.get("prompt_id")
                    print(f"✅ キューID: {prompt_id}")
                    
                    # 完了待機
                    while True:
                        try:
                            queue_response = requests.get(f"{self.base_url}/queue", timeout=10)
                            if queue_response.status_code == 200:
                                queue_data = queue_response.json()
                                running = len(queue_data.get("queue_running", []))
                                pending = len(queue_data.get("queue_pending", []))
                                
                                if running == 0 and pending == 0:
                                    end_time = time.time()
                                    duration = end_time - start_time
                                    
                                    print(f"🎉 完了時間: {duration:.1f}秒")
                                    
                                    results.append({
                                        "config": config,
                                        "duration": duration,
                                        "pixels": config['width'] * config['height'],
                                        "steps": config['steps']
                                    })
                                    break
                                    
                            time.sleep(1)
                        except:
                            time.sleep(1)
                else:
                    print(f"❌ 送信失敗: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ エラー: {e}")
        
        # 結果表示
        print(f"\n📊 V100性能テスト結果")
        print("=" * 50)
        
        for result in results:
            config = result['config']
            duration = result['duration']
            pixels = result['pixels']
            steps = result['steps']
            
            pixels_per_sec = (pixels * steps) / duration if duration > 0 else 0
            
            print(f"🎯 {config['name']}:")
            print(f"   ⏱️  時間: {duration:.1f}秒")
            print(f"   📐 ピクセル: {pixels:,}")
            print(f"   ⚙️  ステップ: {steps}")
            print(f"   🚀 性能: {pixels_per_sec:,.0f} pixels×steps/sec")
            print()
        
        # 最適解像度提案
        if results:
            best = min(results, key=lambda x: x['duration'])
            print(f"⭐ 最速設定: {best['config']['name']} ({best['duration']:.1f}秒)")
            
            efficiency = [(r['pixels'] * r['steps']) / r['duration'] for r in results]
            best_eff_idx = efficiency.index(max(efficiency))
            best_eff = results[best_eff_idx]
            print(f"🏆 最高効率: {best_eff['config']['name']}")

def main():
    tester = V100PerformanceTest()
    tester.run_performance_test()

if __name__ == "__main__":
    main()