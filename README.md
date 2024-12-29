# GitHub Repository Data Exporter

GitHubのリポジトリ情報をNotionデータベースに同期するツールです。
GitHub Actionsにより毎日自動的に同期が実行されます。

## セットアップ

1. 依存パッケージのインストール:
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

3. Notionのセットアップ:

a. Notionインテグレーションの作成:
- [Notion Integrations](https://www.notion.so/my-integrations)ページにアクセス
- 「New integration」をクリック
- インテグレーション名を入力（例：「GitHub Sync」）
- 「Submit」をクリックしてトークンを取得

b. データベースの作成:
- **重要**: データベースは必ず**フルページ**として作成してください（インラインデータベースでは動作しません）
- 新しいページを作成し、`/database`と入力してフルページデータベースを作成
- 以下のプロパティを設定（プロパティ名は正確に入力してください）：
  - `Name` (タイトル): リポジトリ名
  - `Description` (テキスト): リポジトリの説明
  - `URL` (URL): リポジトリのURL
  - `Status` (ステータス): リポジトリの状態（進行中/完了）
  - `Last Updated` (日付): 最終更新日
  - `Tech Stack` (マルチセレクト): 使用技術
  - `Privacy` (セレクト): プライバシー設定（Public/Private）
  - `Tags` (マルチセレクト): カテゴリタグ

c. インテグレーションの接続:
- 作成したデータベースを開く
- 右上の「...」をクリック
- 「Add connections」を選択
- 作成したインテグレーションを選択して接続

d. データベースIDの取得:
- データベースのURLから取得: `https://notion.so/your-workspace/{DATABASE_ID}?v=...`
- `DATABASE_ID`の部分（32文字のID）をコピー

4. `.gitignore`の設定:
以下のファイルが無視されます：
  - Python関連ファイル（`__pycache__`, `.pyc`など）
  - 仮想環境ディレクトリ
  - `.env`ファイル（機密情報保護のため）
  - IDE関連ファイル

5. GitHub Actionsの設定:
リポジトリの Settings > Secrets and variables > Actions で以下のシークレットを設定:
  - `GH_PAT`: GitHub Personal Access Token（上記で生成したもの）
  - `NOTION_TOKEN`: NotionのAPIトークン
  - `NOTION_DATABASE_ID`: NotionのデータベースID

## 使用方法

### 手動実行

GitHubのリポジトリ情報をNotionデータベースに同期:
```bash
python github_to_notion.py
```

## 同期データ項目

- リポジトリ名: リポジトリの名前
- 説明: リポジトリの概要
- URL: リポジトリのURL
- ステータス: Active/Archived
- 更新日: 最終更新日
- 技術スタック: 使用されている技術一覧
- プライバシー設定: Public/Private
- タグ: カテゴリタグ（必要に応じて追加）

## トラブルシューティング

1. Notionデータベースの問題:
- データベースが正しく同期されない場合は、以下を確認してください：
  - データベースがフルページとして作成されているか
  - プロパティ名が正確に一致しているか
  - インテグレーションがデータベースに接続されているか

2. 権限の問題:
- GitHub PATに必要な権限（`repo`と`read:user`）が付与されているか
- Notionインテグレーションがデータベースに接続されているか
