#!/usr/bin/env python3
"""
インタラクティブComfyUI画像生成システム
ユーザーが直接プロンプトを入力して画像生成
"""
import requests
import json
import time
import uuid
import os
from datetime import datetime

class InteractiveComfyUIGenerator:
    def __init__(self, server_ip="35.225.113.119", port=8188):
        self.server_ip = server_ip
        self.port = port
        self.base_url = f"http://{server_ip}:{port}"
        
    def check_server(self):
        """サーバー接続チェック"""
        try:
            response = requests.get(f"{self.base_url}/system_stats", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def create_workflow(self, prompt, negative_prompt="low quality, blurry, worst quality", steps=25, cfg=7.0):
        """ワークフロー作成"""
        workflow = {
            "3": {
                "inputs": {
                    "seed": int(time.time() * 1000000) % 1000000,
                    "steps": steps,
                    "cfg": cfg,
                    "sampler_name": "euler",
                    "scheduler": "normal", 
                    "denoise": 1.0,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                },
                "class_type": "KSampler",
                "_meta": {"title": "KSampler"}
            },
            "4": {
                "inputs": {
                    "ckpt_name": "sdxl_base_1.0.safetensors"
                },
                "class_type": "CheckpointLoaderSimple",
                "_meta": {"title": "Load Checkpoint"}
            },
            "5": {
                "inputs": {
                    "width": 1024,
                    "height": 1024,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage",
                "_meta": {"title": "Empty Latent Image"}
            },
            "6": {
                "inputs": {
                    "text": prompt,
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "CLIP Text Encode (Prompt)"}
            },
            "7": {
                "inputs": {
                    "text": negative_prompt,
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "CLIP Text Encode (Negative)"}
            },
            "8": {
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["4", 2]
                },
                "class_type": "VAEDecode",
                "_meta": {"title": "VAE Decode"}
            },
            "9": {
                "inputs": {
                    "filename_prefix": "Custom_Gen_",
                    "images": ["8", 0]
                },
                "class_type": "SaveImage",
                "_meta": {"title": "Save Image"}
            }
        }
        return workflow
    
    def queue_prompt(self, workflow):
        """プロンプトをキューに追加"""
        try:
            response = requests.post(f"{self.base_url}/prompt", json={"prompt": workflow}, timeout=30)
            if response.status_code == 200:
                return response.json()["prompt_id"]
            return None
        except Exception as e:
            print(f"Error queuing prompt: {e}")
            return None
    
    def check_queue_status(self):
        """キュー状況確認"""
        try:
            response = requests.get(f"{self.base_url}/queue", timeout=10)
            if response.status_code == 200:
                data = response.json()
                running = len(data.get("queue_running", []))
                pending = len(data.get("queue_pending", []))
                return running, pending
            return 0, 0
        except:
            return 0, 0
    
    def generate_image(self, prompt, negative_prompt="", steps=25, cfg=7.0):
        """単一画像生成"""
        if not self.check_server():
            print("❌ ComfyUIサーバーに接続できません")
            return False
            
        print(f"🎨 生成開始: {prompt[:50]}...")
        
        workflow = self.create_workflow(prompt, negative_prompt, steps, cfg)
        prompt_id = self.queue_prompt(workflow)
        
        if prompt_id:
            print(f"✅ キューに追加: ID {prompt_id}")
            print("⏳ 生成中...")
            
            # 完了待機
            while True:
                running, pending = self.check_queue_status()
                if running == 0 and pending == 0:
                    break
                time.sleep(2)
            
            print("🎉 生成完了!")
            return True
        else:
            print("❌ 生成失敗")
            return False
    
    def interactive_mode(self):
        """インタラクティブモード"""
        print("🎨 ComfyUI インタラクティブ画像生成システム")
        print("=" * 50)
        print(f"🎯 接続先: {self.base_url}")
        
        if not self.check_server():
            print("❌ ComfyUIサーバーに接続できません")
            print("L4 VMが起動しているか確認してください")
            return
        
        print("✅ サーバー接続確認完了")
        print("\n📝 使用方法:")
        print("- プロンプトを入力してEnter")
        print("- 'quit' で終了")
        print("- 'status' でキュー状況確認")
        print()
        
        while True:
            try:
                user_input = input("🎨 プロンプト入力 > ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 終了します")
                    break
                
                if user_input.lower() == 'status':
                    running, pending = self.check_queue_status()
                    print(f"📊 キュー状況 - 実行中: {running}, 待機中: {pending}")
                    continue
                
                if user_input:
                    # オプション設定
                    negative = input("🚫 ネガティブプロンプト (空白でデフォルト) > ").strip()
                    if not negative:
                        negative = "low quality, blurry, worst quality, bad anatomy"
                    
                    steps_input = input("🔧 ステップ数 (デフォルト25) > ").strip()
                    steps = int(steps_input) if steps_input.isdigit() else 25
                    
                    cfg_input = input("⚙️ CFG Scale (デフォルト7.0) > ").strip()
                    cfg = float(cfg_input) if cfg_input.replace('.','').isdigit() else 7.0
                    
                    self.generate_image(user_input, negative, steps, cfg)
                    print()
                    
            except KeyboardInterrupt:
                print("\n👋 終了します")
                break
            except Exception as e:
                print(f"❌ エラー: {e}")

def main():
    generator = InteractiveComfyUIGenerator()
    generator.interactive_mode()

if __name__ == "__main__":
    main()