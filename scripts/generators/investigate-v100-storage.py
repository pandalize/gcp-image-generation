#!/usr/bin/env python3
"""
V100 ComfyUI画像保存場所詳細調査ツール
"""
import subprocess
import json
from pathlib import Path

class V100StorageInvestigator:
    def __init__(self):
        self.instance_name = "instance-20250807-125905"
        self.zone = "us-central1-a" 
        self.project = "steady-flag-433105-j6"
    
    def run_ssh_command(self, command, timeout=60):
        """SSH経由でコマンド実行"""
        try:
            result = subprocess.run([
                "gcloud", "compute", "ssh", 
                f"{self.instance_name}",
                f"--zone={self.zone}",
                f"--project={self.project}",
                "--command", command
            ], capture_output=True, text=True, timeout=timeout)
            
            return result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return "", str(e)
    
    def investigate_storage(self):
        """詳細なストレージ調査"""
        print("🔍 V100 ComfyUI画像保存場所詳細調査")
        print("=" * 60)
        
        investigations = [
            ("🏠 ホームディレクトリ", "ls -la ~/ | head -20"),
            ("📁 ComfyUIディレクトリ", "ls -la ~/ComfyUI/ 2>/dev/null || echo 'ComfyUI not found'"),
            ("📂 ComfyUI/output", "ls -la ~/ComfyUI/output/ 2>/dev/null || echo 'output dir not found'"),
            ("🔍 全画像ファイル検索", "find ~ -name '*.png' -o -name '*.jpg' 2>/dev/null | head -20"),
            ("⏰ 最近作成されたファイル", "find ~ -type f -mmin -60 2>/dev/null | head -20"),
            ("📊 ComfyUIプロセス", "ps aux | grep -i comfy"),
            ("🌐 ポート確認", "netstat -tlnp | grep 8188 || ss -tlnp | grep 8188"),
            ("💾 ディスク使用量", "df -h"),
            ("📋 ComfyUIログ", "tail -20 ~/comfyui_gpu_fixed.log 2>/dev/null || echo 'log not found'"),
            ("🎯 SaveImageノード設定", "grep -r 'SaveImage' ~/ComfyUI/ 2>/dev/null | head -10 || echo 'not found'"),
            ("📸 temp/一時ファイル", "find /tmp -name '*' -type f -mmin -60 2>/dev/null | head -10"),
            ("🗂️ ComfyUIサブディレクトリ", "find ~/ComfyUI -type d -name '*output*' -o -name '*temp*' -o -name '*save*' 2>/dev/null"),
            ("📄 ComfyUI設定ファイル", "find ~/ComfyUI -name '*.json' -o -name '*.yaml' -o -name '*.conf' 2>/dev/null | head -10"),
            ("🎨 最新変更ファイル", "find ~ -type f -newer ~/ComfyUI/main.py 2>/dev/null | head -20")
        ]
        
        for title, command in investigations:
            print(f"\n{title}")
            print("-" * 40)
            stdout, stderr = self.run_ssh_command(command)
            
            if stdout:
                print(stdout)
            if stderr and "not found" not in stderr.lower():
                print(f"⚠️ エラー: {stderr}")
        
        # API履歴チェック
        print(f"\n🌐 ComfyUI API履歴チェック")
        print("-" * 40)
        api_command = "curl -s http://localhost:8188/history 2>/dev/null | head -500"
        stdout, stderr = self.run_ssh_command(api_command)
        
        if stdout:
            try:
                # JSON解析してファイル名抽出
                history = json.loads(stdout)
                print(f"📊 API履歴: {len(history)}件")
                
                for prompt_id, data in list(history.items())[:5]:
                    outputs = data.get('outputs', {})
                    for node_id, node_output in outputs.items():
                        images = node_output.get('images', [])
                        for img in images:
                            filename = img.get('filename', 'N/A')
                            print(f"  🖼️ {filename}")
                            
            except json.JSONDecodeError:
                print("❌ JSON解析エラー")
                print(stdout[:200] + "..." if len(stdout) > 200 else stdout)
        
        # ComfyUI設定調査
        print(f"\n⚙️ ComfyUI設定確認")
        print("-" * 40)
        config_commands = [
            "cat ~/ComfyUI/main.py | grep -i 'output\\|save' | head -5",
            "python3 -c \"import sys; sys.path.append('/home/fujinoyuki/ComfyUI'); from nodes import SaveImage; print('SaveImage found')\" 2>/dev/null || echo 'SaveImage import failed'"
        ]
        
        for cmd in config_commands:
            stdout, stderr = self.run_ssh_command(cmd)
            if stdout:
                print(stdout)

def main():
    investigator = V100StorageInvestigator()
    investigator.investigate_storage()

if __name__ == "__main__":
    main()