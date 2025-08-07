#!/usr/bin/env python3
"""
ComfyUI画像保存診断ツール
SaveImageノードの実際の動作とファイル保存場所を調査
"""
import subprocess
import json
from pathlib import Path

class ComfyUIStorageDiagnostic:
    def __init__(self):
        self.instance_name = "instance-20250807-125905"
        self.zone = "us-central1-c"
        
    def run_command(self, command):
        """SSH経由でコマンド実行"""
        try:
            result = subprocess.run([
                "gcloud", "compute", "ssh", 
                f"{self.instance_name}",
                f"--zone={self.zone}",
                "--command", command,
                "--quiet"
            ], capture_output=True, text=True, timeout=60)
            
            return result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return "", str(e)
    
    def diagnose_comfyui_storage(self):
        """ComfyUI画像保存の詳細診断"""
        print("🔍 ComfyUI画像保存詳細診断")
        print("=" * 60)
        
        # 1. ComfyUI プロセスとディレクトリ確認
        print("\n📊 ComfyUIプロセスとディレクトリ")
        print("-" * 40)
        stdout, stderr = self.run_command("ps aux | grep python | grep -v grep")
        if stdout:
            print("プロセス情報:")
            print(stdout)
        
        # 2. ComfyUIの設定とSaveImageノード検索
        print("\n🎯 SaveImageノード設定調査")
        print("-" * 40)
        
        diagnostic_commands = [
            ("SaveImageノード検索", "find ~/ComfyUI -name '*.py' -exec grep -l 'SaveImage' {} \\; | head -5"),
            ("outputディレクトリ確認", "ls -la ~/ComfyUI/output/ 2>/dev/null || echo 'output dir not found'"),
            ("tempディレクトリ確認", "ls -la ~/ComfyUI/temp/ 2>/dev/null || echo 'temp dir not found'"),
            ("最近作成ファイル", "find ~/ComfyUI -type f -mmin -180 -not -path '*/.*' | head -20"),
            ("ComfyUI設定ファイル", "find ~/ComfyUI -name '*.json' -o -name '*.yaml' | grep -v env | head -5"),
        ]
        
        for title, cmd in diagnostic_commands:
            print(f"\n{title}:")
            stdout, stderr = self.run_command(cmd)
            if stdout:
                print(stdout)
            if stderr and "not found" not in stderr.lower():
                print(f"⚠️ {stderr}")
        
        # 3. ComfyUI APIの実際の出力構造を確認
        print(f"\n🌐 ComfyUI API出力構造詳細確認")
        print("-" * 40)
        
        # 履歴の最初のエントリを詳しく見る
        api_cmd = """
        curl -s http://localhost:8188/history | jq 'to_entries[0] | {
            key: .key,
            status: .value.status,
            outputs: .value.outputs,
            meta: .value.meta
        }'
        """
        
        stdout, stderr = self.run_command(api_cmd)
        if stdout:
            print("履歴エントリサンプル:")
            print(stdout)
        else:
            print("API応答取得失敗")
        
        # 4. 手動でSaveImageノードの動作確認
        print(f"\n🔧 SaveImageノード実行テスト")
        print("-" * 40)
        
        # テスト用の簡単なワークフローを作成してテスト
        test_workflow = {
            "1": {
                "inputs": {"image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="},
                "class_type": "LoadImage"
            },
            "2": {
                "inputs": {
                    "filename_prefix": "TEST_DIAGNOSTIC_", 
                    "images": ["1", 0]
                },
                "class_type": "SaveImage"
            }
        }
        
        # JSON文字列として作成
        workflow_json = json.dumps(test_workflow).replace('"', '\\"')
        test_cmd = 'curl -s -X POST http://localhost:8188/prompt -H "Content-Type: application/json" -d "{\\"prompt\\": ' + workflow_json + '}"'
        
        stdout, stderr = self.run_command(test_cmd)
        if stdout:
            print("テストワークフロー送信結果:")
            print(stdout)
        
        # 5. 実際のファイル保存場所を徹底調査
        print(f"\n📁 ファイル保存場所徹底調査")
        print("-" * 40)
        
        search_commands = [
            "find ~ -name '*TEST_DIAGNOSTIC*' 2>/dev/null",
            "find /tmp -name '*TEST_DIAGNOSTIC*' 2>/dev/null", 
            "find /var/tmp -name '*TEST_DIAGNOSTIC*' 2>/dev/null",
            "find ~ -name '*.png' -mmin -5 2>/dev/null",
            "find ~ -type f -mmin -5 -not -path '*/.*' 2>/dev/null | grep -E '\\.(png|jpg|jpeg)$'"
        ]
        
        for cmd in search_commands:
            print(f"\n検索: {cmd.split('find')[1] if 'find' in cmd else cmd}")
            stdout, stderr = self.run_command(cmd)
            if stdout:
                print(stdout)
        
        # 6. ComfyUIのデフォルト設定確認
        print(f"\n⚙️ ComfyUI SaveImage デフォルト設定確認")
        print("-" * 40)
        
        config_commands = [
            "python3 -c \"import sys; sys.path.append('/home/fujinoyuki/ComfyUI'); from nodes import SaveImage; print(f'SaveImage found'); import inspect; print(inspect.getsource(SaveImage))\" 2>/dev/null | head -30",
            "grep -r 'output_directory\\|output_dir' ~/ComfyUI/ --include='*.py' | head -10",
            "find ~/ComfyUI -name '*.py' -exec grep -l 'OUTPUT_DIRECTORY\\|output_dir' {} \\; | head -5"
        ]
        
        for cmd in config_commands:
            stdout, stderr = self.run_command(cmd)
            if stdout:
                print(stdout[:500])  # 最初の500文字のみ表示
                print("..." if len(stdout) > 500 else "")

def main():
    diagnostic = ComfyUIStorageDiagnostic()
    diagnostic.diagnose_comfyui_storage()

if __name__ == "__main__":
    main()