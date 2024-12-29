import os
from datetime import datetime
from github import Github
from notion_client import Client
import pytz

def get_repository_data():
    """GitHubからリポジトリ情報を取得"""
    github_token = os.getenv('GH_PAT')
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
    return {'select': {'name': 'Private' if is_private else 'Public'}}

def convert_status_to_select(status):
    """ステータスをNotionのセレクトオプションに変換"""
    return {'select': {'name': status}}

def convert_language_to_multi_select(language):
    """言語をNotionのマルチセレクトオプションに変換"""
    languages = [lang.strip() for lang in language.split(',') if lang.strip()] if language else []
    if not languages and language:
        languages = [language]
    return {'multi_select': [{'name': lang} for lang in languages]}

def create_page_properties(repo_data):
    """NotionのページプロパティをGitHubのデータから作成"""
    jst = pytz.timezone('Asia/Tokyo')
    updated_at_jst = repo_data['updated_at'].astimezone(jst)
    
    return {
        'Name': {'title': [{'text': {'content': repo_data['name']}}]},
        'Description': {'rich_text': [{'text': {'content': repo_data['description'][:2000]}}]},
        'URL': {'url': repo_data['url']},
        'Status': convert_status_to_select(repo_data['status']),
        'Updated': {'date': {'start': updated_at_jst.isoformat()}},
        'Owner': {'rich_text': [{'text': {'content': repo_data['owner']}}]},
        'Tech Stack': convert_language_to_multi_select(repo_data['language']),
        'Privacy': convert_privacy_to_select(repo_data['private']),
    }

def sync_to_notion(repositories):
    """NotionデータベースにGitHubのリポジトリ情報を同期"""
    notion_token = os.getenv('NOTION_TOKEN')
    database_id = os.getenv('NOTION_DATABASE_ID')
    notion = Client(auth=notion_token)
    
    # 既存のページを取得
    existing_pages = {}
    for page in notion.databases.query(database_id)['results']:
        repo_name = page['properties']['Name']['title'][0]['text']['content'] if page['properties']['Name']['title'] else ''
        existing_pages[repo_name] = page['id']
    
    # リポジトリごとにNotionを更新
    for repo in repositories:
        properties = create_page_properties(repo)
        
        if repo['name'] in existing_pages:
            # 既存のページを更新
            notion.pages.update(page_id=existing_pages[repo['name']], properties=properties)
            print(f"Updated: {repo['name']}")
        else:
            # 新しいページを作成
            notion.pages.create(parent={'database_id': database_id}, properties=properties)
            print(f"Created: {repo['name']}")

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
