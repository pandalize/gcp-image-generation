# ComfyUI WebUI アクセスガイド

## 🎯 概要
GCP V100 VM上のComfyUIに直接WebUIでアクセスする方法

## 🔧 必要な設定

### 1. プロジェクト設定
```bash
gcloud config set project gen-lang-client-0106774703
```

### 2. ポートフォワーディング設定
```bash
gcloud compute ssh v100-i2 --zone=asia-east1-c -- -L 8188:localhost:8188
```

## 🌐 WebUIアクセス

### URL
```
http://localhost:8188
```

## 🎛️ WebUI画面構成

### メイン機能
- **ノードグラフ**: 中央のワークフロー表示エリア
- **Queue Prompt**: 右上の生成実行ボタン
- **History**: 右側タブで過去の生成履歴
- **Queue**: 現在のキュー状況表示

### 基本操作
- **右クリック**: ノード追加メニュー
- **ドラッグ**: ノード移動・接続
- **パラメータ編集**: ノード内で直接数値変更
- **Save/Load**: ワークフローの保存・読み込み

## 📊 現在利用可能なワークフロー

### 最終設定 (Ultimate Quality)
- **Resolution**: 1024x1344
- **Steps**: 150
- **CFG**: 11.0  
- **Sampler**: dpmpp_3m_sde
- **Model**: juggernaut_v10.safetensors

### 生成履歴
- Ultimate Prototype Generator (3種類のマスターピース)
- Sampler Comparison Tests
- Ultra High Quality Tests

## 💡 利点
- **視覚的操作**: ドラッグ&ドロップでワークフロー構築
- **リアルタイム調整**: パラメータを即座に変更可能
- **履歴管理**: 過去の生成結果を簡単に参照
- **直感的**: ノードベースの分かりやすいインターフェース

## 🚨 トラブルシューティング

### 接続できない場合
1. ポートフォワーディングを再実行
2. ブラウザの再読み込み
3. VM上でComfyUI稼働確認: `curl http://localhost:8188/system_stats`

### 認証エラーの場合
```bash
gcloud auth login
gcloud config set project gen-lang-client-0106774703
```

---
**結論**: WebUIを使うことで、より直感的で柔軟なComfyUI操作が可能になります！