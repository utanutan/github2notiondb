# GitHub Repository Data Exporter

GitHubのリポジトリ情報をCSVファイルとして出力し、Notionデータベースに同期するツールです。

## セットアップ

1. 必要なパッケージをインストール:
```bash
pip install -r requirements.txt
```

2. GitHub Personal Access Tokenの設定:
- GitHubの設定ページから Personal Access Token を生成
- `.env.example` を `.env` にコピーし、トークンを設定
```bash
cp .env.example .env
```
- `.env`ファイルを編集し、`your_github_token_here`を実際のトークンに置き換え

3. `.gitignore`の設定:
- `.gitignore`ファイルが用意されており、以下のファイルが無視されます:
  - Python関連ファイル（`__pycache__`, `.pyc`など）
  - 仮想環境ディレクトリ
  - `.env`ファイル（機密情報保護のため）
  - CSVファイル
  - IDE関連ファイル

## 使用方法

1. GitHubデータをCSVに出力:
```bash
python github_to_csv.py
```

2. CSVデータをNotionに同期:
```bash
python csv_to_notion.py
```

## 出力データ項目

- リポジトリ名: リポジトリの名前
- 説明: リポジトリの概要
- URL: GitHubリポジトリのURL
- ステータス: 開発中/メンテナンス中/アーカイブ
- 更新日: 最終更新日
- オーナー/担当者: リポジトリオーナー
- 技術スタック: 使用されている技術一覧
- プライバシー設定: 公開/プライベート
- タグ: カテゴリタグ（必要に応じて追加）
