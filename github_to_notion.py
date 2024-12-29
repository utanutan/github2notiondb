import os
from datetime import datetime
from github import Github
from notion_client import Client
from notion_client.errors import APIResponseError
import pytz
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

def get_repository_data():
    """GitHubからリポジトリ情報を取得"""
    github_token = os.getenv('GH_PAT')
    if not github_token:
        raise ValueError("GH_PAT environment variable is not set")
    
    g = Github(github_token)
    user = g.get_user()
    
    repositories = []
    for repo in user.get_repos():
        # リポジトリの情報を取得
        repo_data = {
            'name': repo.name,
            'description': repo.description or '',
            'url': repo.html_url,
            'status': 'Archived' if repo.archived else 'Active',
            'updated_at': repo.updated_at,
            'owner': repo.owner.login,
            'language': repo.language or '',
            'private': repo.private,
        }
        repositories.append(repo_data)
    
    return repositories

def convert_privacy_to_select(is_private):
    """プライバシー設定をNotionのセレクトオプションに変換"""
    status = "Private" if is_private else "Public"
    return {"name": status}

def convert_status_to_select(status):
    """ステータスをNotionのセレクトオプションに変換"""
    status_mapping = {
        "Active": "進行中",
        "Archived": "完了"
    }
    return {"name": status_mapping.get(status, "進行中")}

def convert_language_to_multi_select(language):
    """言語をNotionのマルチセレクトオプションに変換"""
    if not language:
        return []
    languages = [lang.strip() for lang in language.split(',') if lang.strip()]
    if not languages and language:
        languages = [language]
    return [{"name": lang} for lang in languages]

def create_page_properties(repo_data):
    """NotionのページプロパティをGitHubのデータから作成"""
    jst = pytz.timezone('Asia/Tokyo')
    updated_at_jst = repo_data['updated_at'].astimezone(jst)
    
    # 説明文が長すぎる場合は切り詰める
    description = repo_data['description'][:2000] if repo_data['description'] else ""
    
    properties = {
        "Name": {"title": [{"text": {"content": repo_data['name']}}]},
        "Description": {"rich_text": [{"text": {"content": description}}]},
        "URL": {"url": repo_data['url']},
        "Status": {"status": convert_status_to_select(repo_data['status'])},
        "Last Updated": {"date": {"start": updated_at_jst.isoformat()}},
        "Tech Stack": {"multi_select": convert_language_to_multi_select(repo_data['language'])},
        "Privacy": {"select": convert_privacy_to_select(repo_data['private'])},
        "Tags": {"multi_select": []}  # デフォルトは空のタグリスト
    }
    
    return properties

def sync_to_notion(repositories):
    """NotionデータベースにGitHubのリポジトリ情報を同期"""
    notion_token = os.getenv('NOTION_TOKEN')
    database_id = os.getenv('NOTION_DATABASE_ID')

    if not notion_token:
        raise ValueError("NOTION_TOKEN environment variable is not set")
    if not database_id:
        raise ValueError("NOTION_DATABASE_ID environment variable is not set")

    notion = Client(auth=notion_token)
    
    # 既存のページを取得
    existing_pages = {}
    try:
        pages = notion.databases.query(database_id)['results']
        for page in pages:
            if page['properties']['Name']['title']:
                repo_name = page['properties']['Name']['title'][0]['text']['content']
                existing_pages[repo_name] = page['id']
        print(f"Found {len(existing_pages)} existing pages in Notion")
    except APIResponseError as e:
        print(f"Error querying Notion database: {e}")
        raise
    
    # リポジトリごとにNotionを更新
    updated_count = 0
    created_count = 0
    for repo in repositories:
        try:
            properties = create_page_properties(repo)
            
            if repo['name'] in existing_pages:
                # 既存のページを更新
                try:
                    notion.pages.update(page_id=existing_pages[repo['name']], properties=properties)
                    print(f"Updated: {repo['name']}")
                    updated_count += 1
                except APIResponseError as e:
                    print(f"Error updating {repo['name']}: {e}")
                    print(f"Properties being sent: {properties}")
                    continue
            else:
                # 新しいページを作成
                try:
                    notion.pages.create(parent={'database_id': database_id}, properties=properties)
                    print(f"Created: {repo['name']}")
                    created_count += 1
                except APIResponseError as e:
                    print(f"Error creating {repo['name']}: {e}")
                    continue
        except Exception as e:
            print(f"Error processing {repo['name']}: {e}")
            continue
    
    print(f"Sync completed. Updated: {updated_count}, Created: {created_count} pages")

def main():
    """メイン処理"""
    try:
        repositories = get_repository_data()
        sync_to_notion(repositories)
        print("Successfully synced data to Notion database")
    except Exception as e:
        print(f"Error: {str(e)}")
        raise

if __name__ == '__main__':
    main()
