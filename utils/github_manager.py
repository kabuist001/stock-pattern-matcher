"""
GitHub連携モジュール
Issue作成、HTMLレポートのアップロード機能
"""

import requests
from typing import Optional, Dict
from datetime import datetime
import base64
import traceback


class GitHubManager:
    """GitHub連携クラス"""
    
    def __init__(self, token: str, config):
        self.token = token
        self.config = config
        self.owner = config.get('github.owner', '')
        self.repo = config.get('github.repo', '')
        self.reports_folder = config.get('github.reports_folder', 'reports')
        self.auto_create_issue = config.get('github.auto_create_issue_on_error', True)
        self.base_url = "https://api.github.com"
        self.headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    
    def create_issue(self, title: str, body: str, labels: list = None) -> Optional[str]:
        """GitHub Issueを作成"""
        if not self.token:
            print("⚠️  GITHUB_TOKEN not set, skipping issue creation")
            return None
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues"
        data = {"title": title, "body": body, "labels": labels or ["bug", "auto-generated"]}
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            issue_url = response.json().get('html_url')
            print(f"✅ GitHub Issue created: {issue_url}")
            return issue_url
        except Exception as e:
            print(f"❌ Failed to create GitHub Issue: {e}")
            return None
    
    def upload_report(self, html_content: str, filename: str = None) -> Optional[str]:
        """HTMLレポートをGitHubにアップロード"""
        if not self.token:
            print("⚠️  GITHUB_TOKEN not set, skipping report upload")
            return None
        if filename is None:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = f"{timestamp}_analysis_report.html"
        file_path = f"{self.reports_folder}/{filename}"
        content_bytes = html_content.encode('utf-8')
        content_base64 = base64.b64encode(content_bytes).decode('utf-8')
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/contents/{file_path}"
        data = {"message": f"add: Analysis report {filename}", "content": content_base64, "branch": "main"}
        try:
            response = requests.put(url, headers=self.headers, json=data)
            response.raise_for_status()
            file_url = response.json()['content']['html_url']
            print(f"✅ Report uploaded: {file_url}")
            return file_url
        except Exception as e:
            print(f"❌ Failed to upload report: {e}")
            if hasattr(response, 'status_code') and response.status_code == 422:
                print("   File already exists, trying to update...")
                return self._update_existing_report(file_path, html_content)
            return None
    
    def _update_existing_report(self, file_path: str, html_content: str) -> Optional[str]:
        """既存のレポートを更新"""
        try:
            url = f"{self.base_url}/repos/{self.owner}/{self.repo}/contents/{file_path}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            sha = response.json()['sha']
            content_bytes = html_content.encode('utf-8')
            content_base64 = base64.b64encode(content_bytes).decode('utf-8')
            data = {"message": f"update: Analysis report {file_path}", "content": content_base64, "sha": sha, "branch": "main"}
            response = requests.put(url, headers=self.headers, json=data)
            response.raise_for_status()
            file_url = response.json()['content']['html_url']
            print(f"✅ Report updated: {file_url}")
            return file_url
        except Exception as e:
            print(f"❌ Failed to update report: {e}")
            return None
    
    def create_error_issue(self, error: Exception, context: Dict = None) -> Optional[str]:
        """エラー発生時にIssueを自動作成"""
        if not self.auto_create_issue:
            return None
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        title = f"[Auto] Error - {type(error).__name__} - {timestamp}"
        error_trace = traceback.format_exc()
        body = f"""## 🚨 エラーが発生しました

**発生日時**: {timestamp}

### エラー情報
**エラータイプ**: `{type(error).__name__}`
**エラーメッセージ**: ```{str(error)}```

### トレースバック
```python
{error_trace}
```

### 実行環境
"""
        if context:
            body += "**コンテキスト情報**:\n"
            for key, value in context.items():
                body += f"- {key}: `{value}`\n"
        body += """
### 対応方法
1. エラーメッセージとトレースバックを確認
2. 入力データの形式を確認
3. 設定ファイル（`config/settings.yaml`）を確認
4. 必要に応じてコードを修正

### 自動修正
ClaudeがこのエラーをGitHub MCPで分析し、修正PRを作成します。

---
*このIssueは自動的に作成されました*
"""
        return self.create_issue(title=title, body=body, labels=["bug", "auto-generated", "error"])
    
    def check_repository_access(self) -> bool:
        """リポジトリへのアクセス権限を確認"""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            print(f"✅ Repository access confirmed: {self.owner}/{self.repo}")
            return True
        except Exception as e:
            print(f"❌ Cannot access repository: {e}")
            return False
    
    def list_reports(self, limit: int = 10) -> list:
        """アップロード済みレポートのリストを取得"""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/contents/{self.reports_folder}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            files = response.json()
            html_files = [f for f in files if f['name'].endswith('.html')]
            html_files.sort(key=lambda x: x['name'], reverse=True)
            return html_files[:limit]
        except Exception as e:
            print(f"❌ Failed to list reports: {e}")
            return []
