#!/usr/bin/env python3
"""
YAML PromptベースComfyUI画像生成システム
YAMLファイルからプロンプトを読み込んで一括生成
"""
import requests
import json
import time
import yaml
import os
from datetime import datetime
from pathlib import Path

class YAMLPromptGenerator:
    def __init__(self, server_ip="34.70.230.62", port=8188):
        self.server_ip = server_ip
        self.port = port
        self.base_url = f"http://{server_ip}:{port}"
        self.prompts_file = Path(__file__).parent.parent.parent / "prompts.yaml"
        
    def load_prompts(self):
        """YAMLファイルからプロンプトを読み込み"""
        try:
            with open(self.prompts_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data.get('prompts', [])
        except FileNotFoundError:
            print(f"❌ プロンプトファイルが見つかりません: {self.prompts_file}")
            return []
        except yaml.YAMLError as e:
            print(f"❌ YAML解析エラー: {e}")
            return []
    
    def check_server(self):
        """サーバー接続チェック"""
        try:
            response = requests.get(f"{self.base_url}/system_stats", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def create_workflow(self, prompt_config):
        """ワークフロー作成"""
        positive = prompt_config.get('positive', '')
        negative = prompt_config.get('negative', 'low quality, blurry, worst quality')
        steps = prompt_config.get('steps', 25)
        cfg = prompt_config.get('cfg', 7.0)
        
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
                    "width": prompt_config.get('width', 1024),
                    "height": prompt_config.get('height', 1024),
                    "batch_size": prompt_config.get('batch_size', 1)
                },
                "class_type": "EmptyLatentImage",
                "_meta": {"title": "Empty Latent Image"}
            },
            "6": {
                "inputs": {
                    "text": positive,
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "CLIP Text Encode (Prompt)"}
            },
            "7": {
                "inputs": {
                    "text": negative,
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
                    "filename_prefix": "YAML_Gen_",
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
            print(f"❌ キューエラー: {e}")
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
    
    def generate_from_yaml(self):
        """YAMLファイルから一括生成"""
        print("🎨 YAML Prompt生成システム")
        print("=" * 40)
        print(f"📁 プロンプトファイル: {self.prompts_file}")
        print(f"🎯 ComfyUIサーバー: {self.base_url}")
        
        # サーバー接続確認
        if not self.check_server():
            print("❌ ComfyUIサーバーに接続できません")
            print("VM起動状況を確認してください")
            return
        
        print("✅ サーバー接続確認完了")
        
        # プロンプト読み込み
        prompts = self.load_prompts()
        if not prompts:
            print("❌ プロンプトが見つかりません")
            print(f"📝 {self.prompts_file} にプロンプトを記述してください")
            return
        
        print(f"📋 読み込まれたプロンプト数: {len(prompts)}")
        
        # 各プロンプトを生成
        successful = 0
        for i, prompt_config in enumerate(prompts, 1):
            positive = prompt_config.get('positive', '')
            print(f"\n🎨 [{i}/{len(prompts)}] 生成中: {positive[:50]}...")
            
            workflow = self.create_workflow(prompt_config)
            prompt_id = self.queue_prompt(workflow)
            
            if prompt_id:
                print(f"✅ キューに追加: {prompt_id}")
                successful += 1
            else:
                print("❌ キューの追加に失敗")
        
        if successful > 0:
            print(f"\n⏳ {successful}個のプロンプトをキューに追加完了")
            print("🎯 生成完了まで待機中...")
            
            # 全て完了まで待機
            while True:
                running, pending = self.check_queue_status()
                if running == 0 and pending == 0:
                    break
                print(f"📊 状況 - 実行中: {running}, 待機中: {pending}")
                time.sleep(5)
            
            print("🎉 全ての画像生成が完了しました！")
        else:
            print("❌ 生成できるプロンプトがありませんでした")

def main():
    generator = YAMLPromptGenerator()
    generator.generate_from_yaml()

if __name__ == "__main__":
    main()