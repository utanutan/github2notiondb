# GitHub Repository Data Exporter

GitHubのリポジトリ情報をNotionデータベースに同期するツールです。
GitHub Actionsにより毎日自動的に同期が実行されます。

## セットアップ

1. 必要なパッケージをインストール:
```bash
pip install -r requirements.txt
```

2. GitHub Personal Access Token (PAT)の設定:
- GitHubの設定ページ（Settings > Developer settings > Personal access tokens > Tokens (classic)）からPATを生成
  - 必要な権限: `repo` と `read:user`
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
  - IDE関連ファイル

4. GitHub Actionsの設定:
- リポジトリの"Settings" > "Secrets and variables" > "Actions"で以下のシークレットを設定:
  - `GH_PAT`: GitHub Personal Access Token（上記で生成したもの）
  - `NOTION_TOKEN`: NotionのAPIトークン
  - `NOTION_DATABASE_ID`: NotionのデータベースID

## 使用方法

### 自動実行
GitHub Actionsにより毎日UTC 00:00（JST 09:00）に自動的に同期が実行されます。
また、GitHubのActionsタブから手動で実行することも可能です。

### 手動実行

GitHubのリポジトリ情報をNotionデータベースに同期:
```bash
python github_to_notion.py
```

## 同期データ項目

- リポジトリ名: リポジトリの名前
- 説明: リポジトリの概要
- URL: GitHubリポジトリのURL
- ステータス: Active/Archived
- 更新日: 最終更新日
- オーナー/担当者: リポジトリオーナー
- 技術スタック: 使用されている技術一覧
- プライバシー設定: 公開/プライベート
