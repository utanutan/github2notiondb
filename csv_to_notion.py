import os
import pandas as pd
from notion_client import Client
from dotenv import load_dotenv
from datetime import datetime

def init_notion():
    """Notionクライアントを初期化する"""
    load_dotenv()
    notion_token = os.getenv('NOTION_TOKEN')
    if not notion_token:
        raise ValueError("Notion token not found in .env file")
    return Client(auth=notion_token)

def get_database_id():
    """NotionデータベースIDを取得する"""
    database_id = os.getenv('NOTION_DATABASE_ID')
    if not database_id:
        raise ValueError("Notion database ID not found in .env file")
    return database_id

def convert_tech_stack_to_multi_select(tech_stack):
    """技術スタックの文字列をマルチセレクト用の形式に変換する"""
    if pd.isna(tech_stack):
        return []
    techs = [tech.strip() for tech in tech_stack.split(',')]
    return [{"name": tech} for tech in techs if tech]

def convert_status_to_select(status):
    """ステータスを選択用の形式に変換する"""
    status_mapping = {
        "メンテナンス中": "進行中",
        "完了": "完了",
        "未着手": "未着手",
        "開発中": "進行中",
        "アーカイブ": "完了"
    }
    
    if pd.isna(status):
        return {"name": "未着手"}
    
    return {"name": status_mapping.get(status, "未着手")}

def convert_privacy_to_select(privacy):
    """プライバシー設定を選択用の形式に変換する"""
    privacy_mapping = {
        "公開": "Public",
        "非公開": "Private",
        "アーカイブ": "Archived"
    }
    
    if pd.isna(privacy):
        return {"name": "Private"}
    
    return {"name": privacy_mapping.get(privacy, "Private")}

def convert_tags_to_multi_select(tags):
    """タグをマルチセレクト用の形式に変換する"""
    if pd.isna(tags):
        return []
    tag_list = [tag.strip() for tag in tags.split(',')]
    return [{"name": tag} for tag in tag_list if tag]

def create_page_properties(row):
    """NotionページのプロパティをCSVデータから作成する"""
    properties = {
        "Name": {"title": [{"text": {"content": row['リポジトリ名']}}]},
        "Description": {"rich_text": [{"text": {"content": str(row['説明']) if not pd.isna(row['説明']) else ""}}]},
        "URL": {"url": row['URL'] if not pd.isna(row['URL']) else ""},
        "Status": {"status": convert_status_to_select(row['ステータス'])},
        "Tech Stack": {"multi_select": convert_tech_stack_to_multi_select(row['技術スタック'])},
        "Privacy": {"select": convert_privacy_to_select(row['プライバシー設定'])},
        "Tags": {"multi_select": convert_tags_to_multi_select(row['タグ'])},
    }

    # 更新日の処理
    if not pd.isna(row['更新日']):
        properties["Last Updated"] = {"date": {"start": row['更新日']}}

    return properties

def sync_to_notion(csv_file='github_repositories.csv'):
    """CSVファイルのデータをNotionデータベースに同期する"""
    notion = init_notion()
    database_id = get_database_id()
    
    # CSVファイルを読み込む
    df = pd.read_csv(csv_file)
    
    # 既存のデータベースページを取得
    existing_pages = notion.databases.query(database_id=database_id)
    existing_titles = {
        page['properties']['Name']['title'][0]['text']['content']: page['id']
        for page in existing_pages['results']
        if page['properties']['Name']['title']
    }
    
    # 各リポジトリをNotionに追加または更新
    for _, row in df.iterrows():
        repo_name = row['リポジトリ名']
        properties = create_page_properties(row)
        
        try:
            if repo_name in existing_titles:
                # 既存ページを更新
                notion.pages.update(page_id=existing_titles[repo_name], properties=properties)
                print(f"Updated: {repo_name}")
            else:
                # 新規ページを作成
                notion.pages.create(
                    parent={"database_id": database_id},
                    properties=properties
                )
                print(f"Created: {repo_name}")
        except Exception as e:
            print(f"Error processing {repo_name}: {str(e)}")

if __name__ == "__main__":
    try:
        sync_to_notion()
        print("Successfully synced data to Notion database")
    except Exception as e:
        print(f"Error: {str(e)}")
