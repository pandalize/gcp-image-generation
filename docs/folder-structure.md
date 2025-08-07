# 📁 GCP画像生成プロジェクト - フォルダ構成

## 🗂️ 整理済みディレクトリ構造

```
gcp/
├── 📋 docs/                          # ドキュメント
│   ├── CLAUDE.md                     # メイン作業ログ
│   ├── GPU-QUOTA-REQUEST-GUIDE.md    # GPUクォータ申請ガイド
│   ├── README.md                     # プロジェクト概要
│   └── folder-structure.md           # このファイル
│
├── 🛠️ scripts/                       # 実行スクリプト
│   ├── infrastructure/               # インフラ構築
│   │   ├── setup-gcp-project.sh     # GCPプロジェクト初期設定
│   │   ├── create-*.sh              # VM作成スクリプト群
│   │   └── find-*.sh                # リソース検索スクリプト
│   │
│   ├── gpu-setup/                   # GPU環境構築
│   │   ├── fix-nvidia-*.sh          # NVIDIA driver修復
│   │   ├── gpu-complete-fix.sh      # GPU完全修復
│   │   └── nvidia-535-install.sh    # ドライバー手動インストール
│   │
│   └── generators/                  # 画像生成スクリプト
│       ├── comfyui_batch_generator.py # ComfyUI バッチ生成 ⭐
│       ├── *beauty*.py              # 美女画像生成各種
│       └── real-ai-beauty-generator.py # リアルAI美女生成
│
├── 🎨 outputs/                      # 生成画像出力
│   ├── comfyui/                     # ComfyUI出力 (9枚)
│   ├── commercial/                  # 商用品質出力 (50枚)
│   ├── artistic/                    # アーティスティック (50枚)
│   └── l4_final/                    # L4 GPU最終出力 (30枚)
│
├── 📹 video-generation/             # 動画生成 (未実装)
│   ├── setup-video-env.sh
│   ├── image-to-video-pipeline.py
│   └── parallel-video-generation.sh
│
└── 🔧 utility/                     # ユーティリティ
    ├── check-gpu-quotas.sh          # GPUクォータ確認
    ├── monitor-costs.sh             # コスト監視
    └── run-parallel-generation.sh   # 並列生成実行
```

## 📊 生成実績サマリー

### ✅ 完了した出力
- **ComfyUI + SDXL**: 9枚 (1024×1024, プロ品質)
- **商用美女ポートレート**: 50枚 (高品質)
- **アーティスティック**: 50枚 (芸術的)
- **L4 Final**: 30枚 (最高品質)

**総生成数**: 139枚の高品質AI画像

## 🚀 次のステップ

1. **フォルダ構成をGitに反映**
2. **GPU性能向上の検討**
3. **大量並列生成の実装**