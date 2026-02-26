# QIIME 2 Assistant

ローカル LLM（Ollama）を使った QIIME 2 対話式 AI アシスタント。
[qiime2-manual](https://github.com/qiime-lab/qiime2-manual) の全ドキュメントをナレッジベースとして読み込み、QIIME 2 解析に関する質問にチャット形式で回答します。

## 特徴

- **完全ローカル動作** — API キー不要、データが外部に送信されない
- **マニュアル準拠** — qiime2-manual の内容に基づいた正確な回答
- **ストリーミング応答** — トークン単位でリアルタイム表示
- **日本語対応** — 日本語で質問・回答

## 必要なもの

- Python 3.10+
- [Ollama](https://ollama.com/)
- [qiime2-manual](https://github.com/qiime-lab/qiime2-manual)（同じ親ディレクトリに配置）

```
parent/
├── qiime2-assistant/   # このリポジトリ
└── qiime2-manual/      # マニュアルリポジトリ
```

## セットアップ

### 1. Ollama のインストールとモデル取得

```bash
# macOS
brew install ollama

# モデルをダウンロード（日本語対応の qwen2.5 推奨）
ollama pull qwen2.5:7b
```

### 2. アプリのセットアップ

```bash
git clone https://github.com/qiime-lab/qiime2-assistant.git
cd qiime2-assistant

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. マニュアルの配置

```bash
# qiime2-assistant と同じ階層にクローン
cd ..
git clone https://github.com/qiime-lab/qiime2-manual.git
```

## 使い方

```bash
# Ollama を起動（別ターミナル or バックグラウンド）
ollama serve

# アプリを起動
cd qiime2-assistant
source .venv/bin/activate
streamlit run app.py
```

ブラウザが自動で開きます。チャット欄に質問を入力するか、初期画面の質問例をクリックしてください。

## 対応トピック

qiime2-manual に含まれる全章をカバーしています：

- インストール・環境構築
- データインポート（FASTQ）
- DADA2 による品質管理・ノイズ除去
- 系統樹構築
- 多様性解析（α / β）
- 分類器作成・細菌同定
- 内部標準（IS）除去・絶対定量
- ネガティブコントロール除去
- 統計検定（PERMANOVA 等）
- R / phyloseq 連携
- トラブルシューティング

## ライセンス

MIT
