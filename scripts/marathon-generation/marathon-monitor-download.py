#!/usr/bin/env python3
"""
V100マラソン生成監視・自動ダウンロードスクリプト
30分間隔で生成画像を自動ダウンロード・バックアップ
"""

import subprocess
import time
import os
import shutil
from datetime import datetime
import glob

class MarathonMonitorDownloader:
    def __init__(self):
        self.output_base = "/Users/fujinoyuki/Desktop/gcp/outputs/marathon_generation"
        self.gcp_zone = "asia-east1-c"
        self.instance_name = "v100-i2"
        self.remote_path = "/home/fujinoyuki/ComfyUI/output"
        self.download_interval = 30 * 60  # 30分間隔
        self.last_download_time = None
        self.total_downloaded = 0
        
        # 出力ディレクトリ作成
        os.makedirs(self.output_base, exist_ok=True)
        
    def log(self, message):
        """ログ出力"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def get_marathon_images_count(self):
        """V100上のマラソン画像数を取得"""
        try:
            cmd = [
                "gcloud", "compute", "ssh", self.instance_name,
                "--zone", self.gcp_zone,
                "--command", "find /home/fujinoyuki/ComfyUI/output -name 'MARATHON_*' | wc -l"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return int(result.stdout.strip())
        except Exception as e:
            self.log(f"Error getting image count: {e}")
        return 0
    
    def check_marathon_status(self):
        """マラソンスクリプトの実行状況確認"""
        try:
            cmd = [
                "gcloud", "compute", "ssh", self.instance_name,
                "--zone", self.gcp_zone,
                "--command", "ps aux | grep marathon | grep -v grep | wc -l"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return int(result.stdout.strip()) > 0
        except Exception as e:
            self.log(f"Error checking marathon status: {e}")
        return False
    
    def get_comfyui_queue_status(self):
        """ComfyUIのキュー状況確認"""
        try:
            cmd = [
                "gcloud", "compute", "ssh", self.instance_name,
                "--zone", self.gcp_zone,
                "--command", "curl -s http://localhost:8188/queue | python3 -c \"import sys,json; data=json.load(sys.stdin); print(len(data['queue_running']), len(data['queue_pending']))\""
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                running, pending = map(int, result.stdout.strip().split())
                return running, pending
        except Exception as e:
            self.log(f"Error getting queue status: {e}")
        return 0, 0
    
    def download_marathon_images(self):
        """マラソン画像をダウンロード"""
        try:
            # タイムスタンプ付きディレクトリ作成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_dir = os.path.join(self.output_base, f"session_{timestamp}")
            os.makedirs(session_dir, exist_ok=True)
            
            # 全ての生成画像をダウンロード（MARATHON_, THEME_, EXPERIMENT_）
            patterns = ["MARATHON_*", "THEME_*", "EXPERIMENT_*"]
            all_downloaded = []
            
            for pattern in patterns:
                try:
                    cmd = [
                        "gcloud", "compute", "scp",
                        f"{self.instance_name}:{self.remote_path}/{pattern}",
                        session_dir,
                        f"--zone={self.gcp_zone}",
                        "--recurse"
                    ]
                    self.log(f"Downloading {pattern} images...")
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
                    
                    if result.returncode == 0:
                        pattern_files = glob.glob(os.path.join(session_dir, pattern))
                        all_downloaded.extend(pattern_files)
                        if pattern_files:
                            self.log(f"✅ Downloaded {len(pattern_files)} {pattern} files")
                    else:
                        self.log(f"⚠️  No {pattern} files found or download failed")
                except Exception as e:
                    self.log(f"Error downloading {pattern}: {e}")
            
            downloaded_files = all_downloaded
            new_downloads = len(downloaded_files)
            
            # 重複除去：既にダウンロード済みのファイルは除く
            if self.last_download_time:
                existing_files = set()
                for prev_session in glob.glob(os.path.join(self.output_base, "session_*")):
                    if prev_session != session_dir:
                        # 全パターンの既存ファイルをチェック
                        for pattern in ["MARATHON_*", "THEME_*", "EXPERIMENT_*"]:
                            existing_files.update([os.path.basename(f) for f in glob.glob(os.path.join(prev_session, pattern))])
                
                # 新規ファイルのみ残す
                for file_path in downloaded_files[:]:
                    filename = os.path.basename(file_path)
                    if filename in existing_files:
                        os.remove(file_path)
                        downloaded_files.remove(file_path)
                
                new_downloads = len(downloaded_files)
            
            if new_downloads > 0:
                self.total_downloaded += new_downloads
                total_size = sum(os.path.getsize(f) for f in downloaded_files) / (1024*1024)
                self.log(f"✅ Downloaded {new_downloads} new images ({total_size:.1f}MB)")
                self.log(f"📊 Total downloaded this session: {self.total_downloaded} images")
                
                # ファイル一覧をログ出力
                self.log("🖼️  New images:")
                for file_path in downloaded_files:
                    filename = os.path.basename(file_path)
                    size_mb = os.path.getsize(file_path) / (1024*1024)
                    self.log(f"   - {filename} ({size_mb:.1f}MB)")
            else:
                self.log("ℹ️  No new images to download")
                # 空のディレクトリは削除
                try:
                    os.rmdir(session_dir)
                except:
                    pass
            
            self.last_download_time = datetime.now()
            return new_downloads
                
        except Exception as e:
            self.log(f"❌ Error during download: {e}")
            return 0
    
    def create_summary_report(self):
        """進捗サマリーレポート作成"""
        try:
            # 全ダウンロード済み画像を集計
            all_images = []
            for session_dir in glob.glob(os.path.join(self.output_base, "session_*")):
                # 全パターンの画像を集計
                for pattern in ["MARATHON_*", "THEME_*", "EXPERIMENT_*"]:
                    all_images.extend(glob.glob(os.path.join(session_dir, pattern)))
            
            if not all_images:
                return
            
            # スタイル別集計
            style_stats = {}
            total_size = 0
            
            for image_path in all_images:
                filename = os.path.basename(image_path)
                # MARATHON_StyleName_... や THEME_StyleName_... から StyleName を抽出
                parts = filename.split('_')
                if len(parts) >= 2:
                    if parts[0] in ['MARATHON', 'THEME', 'EXPERIMENT']:
                        style = f"{parts[0]}_{parts[1]}" if len(parts) > 1 else parts[0]
                    else:
                        style = parts[0]
                    style_stats[style] = style_stats.get(style, 0) + 1
                
                total_size += os.path.getsize(image_path)
            
            # レポート作成
            report = [
                "=" * 80,
                f"📊 V100 Marathon Generation Progress Report",
                f"📅 Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "=" * 80,
                f"🖼️  Total Images Downloaded: {len(all_images)}",
                f"💾 Total Size: {total_size/(1024*1024*1024):.2f} GB",
                "",
                "🎨 Style Breakdown:",
                "-" * 40
            ]
            
            for style, count in sorted(style_stats.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / len(all_images)) * 100
                report.append(f"   {style}: {count} images ({percentage:.1f}%)")
            
            report.extend([
                "",
                "📁 Download Sessions:",
                "-" * 40
            ])
            
            sessions = sorted(glob.glob(os.path.join(self.output_base, "session_*")))
            for session_dir in sessions:
                session_name = os.path.basename(session_dir)
                # 各セッションの全画像数を集計
                session_images = 0
                for pattern in ["MARATHON_*", "THEME_*", "EXPERIMENT_*"]:
                    session_images += len(glob.glob(os.path.join(session_dir, pattern)))
                if session_images > 0:
                    report.append(f"   {session_name}: {session_images} images")
            
            report_text = "\n".join(report)
            
            # ファイルに保存
            report_file = os.path.join(self.output_base, "marathon_progress_report.txt")
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            
            # コンソールに出力
            print("\n" + report_text)
            
        except Exception as e:
            self.log(f"Error creating summary report: {e}")
    
    def run_monitoring(self):
        """監視・ダウンロードループ実行"""
        self.log("🚀 V100 Marathon Monitoring Started!")
        self.log(f"📁 Output Directory: {self.output_base}")
        self.log(f"⏱️  Download Interval: {self.download_interval/60} minutes")
        
        try:
            while True:
                # マラソンスクリプトの実行確認
                is_running = self.check_marathon_status()
                remote_count = self.get_marathon_images_count()
                running, pending = self.get_comfyui_queue_status()
                
                self.log(f"📊 Status Update:")
                self.log(f"   Marathon Script: {'🟢 Running' if is_running else '🔴 Stopped'}")
                self.log(f"   Remote Images: {remote_count}")
                self.log(f"   ComfyUI Queue: {running} running, {pending} pending")
                self.log(f"   Downloaded: {self.total_downloaded}")
                
                # 定期ダウンロード実行
                if self.last_download_time is None or \
                   (datetime.now() - self.last_download_time).total_seconds() >= self.download_interval:
                    
                    new_downloads = self.download_marathon_images()
                    
                    if new_downloads > 0 or self.total_downloaded % 50 == 0:
                        self.create_summary_report()
                
                # マラソンが終了していて、キューも空の場合
                if not is_running and running == 0 and pending == 0:
                    self.log("🏁 Marathon completed and queue is empty!")
                    # 最終ダウンロード
                    self.download_marathon_images()
                    self.create_summary_report()
                    self.log("✅ Final download completed!")
                    break
                
                # 5分待機
                time.sleep(5 * 60)
                
        except KeyboardInterrupt:
            self.log("🛑 Monitoring interrupted by user")
        except Exception as e:
            self.log(f"❌ Error in monitoring loop: {e}")
        
        self.log("🏁 Marathon monitoring completed!")

def main():
    print("V100 Marathon Generation Monitoring & Auto-Download")
    
    monitor = MarathonMonitorDownloader()
    monitor.run_monitoring()

if __name__ == "__main__":
    main()