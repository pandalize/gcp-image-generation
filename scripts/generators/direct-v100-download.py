#!/usr/bin/env python3
"""
V100直接ダウンロード - 正しいプロジェクトIDで実行
"""
import subprocess
import os
from pathlib import Path

class DirectV100Downloader:
    def __init__(self):
        self.instance_name = "instance-20250807-125905"
        self.zone = "us-central1-c"
        self.project = "gen-lang-client-0106774703"  # 正しいプロジェクトID
        self.local_output = Path.home() / "Desktop" / "gcp" / "outputs" / "v100_generated"
        
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
            
            return result.stdout.strip(), result.stderr.strip(), result.returncode
        except Exception as e:
            return "", str(e), 1
    
    def download_file_scp(self, remote_path):
        """SCPで個別ファイルダウンロード"""
        try:
            filename = os.path.basename(remote_path)
            local_path = self.local_output / filename
            
            result = subprocess.run([
                "gcloud", "compute", "scp",
                f"{self.instance_name}:{remote_path}",
                str(local_path),
                f"--zone={self.zone}",
                f"--project={self.project}"
            ], capture_output=True, text=True, timeout=120)
            
            return result.returncode == 0
        except:
            return False
    
    def find_and_download_images(self):
        """画像ファイル検索とダウンロード"""
        print("🚀 V100直接画像ダウンロード")
        print("=" * 50)
        print(f"🎯 インスタンス: {self.instance_name}")
        print(f"🌏 プロジェクト: {self.project}")
        
        # 出力ディレクトリ作成
        self.local_output.mkdir(parents=True, exist_ok=True)
        print(f"📁 出力先: {self.local_output}")
        
        # 基本接続テスト
        print("\n🔧 接続テスト...")
        stdout, stderr, returncode = self.run_ssh_command("whoami && pwd")
        
        if returncode != 0:
            print(f"❌ SSH接続エラー: {stderr}")
            return
            
        print(f"✅ 接続成功: {stdout}")
        
        # ComfyUIプロセス確認
        print("\n📊 ComfyUIプロセス確認...")
        stdout, stderr, _ = self.run_ssh_command("ps aux | grep python | grep -v grep")
        print(f"プロセス情報:\n{stdout}")
        
        # 画像ファイル検索
        print("\n🔍 画像ファイル検索...")
        search_commands = [
            "find ~ -name '*.png' -type f 2>/dev/null",
            "find /tmp -name '*.png' -type f 2>/dev/null", 
            "find ~/ComfyUI -name '*.png' -o -name '*.jpg' 2>/dev/null"
        ]
        
        all_files = []
        for command in search_commands:
            stdout, stderr, _ = self.run_ssh_command(command)
            if stdout:
                files = stdout.strip().split('\n')
                for file in files:
                    if file.strip():
                        all_files.append(file.strip())
        
        # 重複削除
        unique_files = list(set(all_files))
        print(f"📊 発見: {len(unique_files)}個のファイル")
        
        # ダウンロード実行
        downloaded = 0
        for remote_path in unique_files:
            print(f"📥 ダウンロード中: {os.path.basename(remote_path)}")
            if self.download_file_scp(remote_path):
                downloaded += 1
                print(f"✅ 成功")
            else:
                print(f"❌ 失敗")
        
        print(f"\n🎉 完了: {downloaded}個のファイルをダウンロード")
        
        # ComfyUI起動状況確認
        print("\n🌐 ComfyUI API確認...")
        stdout, stderr, _ = self.run_ssh_command("curl -s http://localhost:8188/system_stats | head -10")
        if stdout:
            print(f"API応答: {stdout}")
        else:
            print("❌ API応答なし")
        
        # 最後に直近のファイル確認
        print("\n⏰ 最近変更されたファイル...")
        stdout, stderr, _ = self.run_ssh_command("find ~ -type f -mmin -120 2>/dev/null | head -20")
        if stdout:
            print(stdout)

def main():
    downloader = DirectV100Downloader() 
    downloader.find_and_download_images()

if __name__ == "__main__":
    main()