import os
from datetime import datetime
from github import Github
import pandas as pd
from dotenv import load_dotenv

def get_tech_stack(repo):
    """リポジトリの技術スタックを推測する"""
    tech_stack = set()
    
    # 言語情報から技術スタックを取得
    languages = repo.get_languages()
    tech_stack.update(languages.keys())
    
    # README.mdからキーワードを抽出することも可能
    # ここでは基本的な言語情報のみを使用
    
    return list(tech_stack)

def get_repository_data(github_token):
    """GitHubからリポジトリ情報を取得する"""
    g = Github(github_token)
    user = g.get_user()
    
    repositories = []
    
    for repo in user.get_repos():
        repo_data = {
            "リポジトリ名": repo.name,
            "説明": repo.description or "",
            "URL": repo.html_url,
            "ステータス": "アーカイブ" if repo.archived else "メンテナンス中" if repo.pushed_at else "開発中",
            "更新日": repo.pushed_at.strftime("%Y-%m-%d") if repo.pushed_at else "",
            "オーナー/担当者": repo.owner.login,
            "技術スタック": ", ".join(get_tech_stack(repo)),
            "プライバシー設定": "プライベート" if repo.private else "公開",
            "タグ": ""  # タグは必要に応じて追加
        }
        repositories.append(repo_data)
    
    return repositories

def main():
    load_dotenv()
    github_token = os.getenv("GITHUB_TOKEN")
    
    if not github_token:
        print("Error: GitHub token not found. Please set GITHUB_TOKEN in .env file")
        return
    
    try:
        repositories = get_repository_data(github_token)
        df = pd.DataFrame(repositories)
        
        # CSVファイルとして保存
        output_file = "github_repositories.csv"
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"Repository data has been saved to {output_file}")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    main()
