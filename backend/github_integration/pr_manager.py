import os
import requests
import subprocess
from typing import Dict, Any, Optional
from backend.config import GITHUB_TOKEN, GITHUB_REPO, ROOT_DIR

class GitHubPRManager:
    def __init__(self):
        self.token = GITHUB_TOKEN
        self.repo = GITHUB_REPO

    def is_configured(self) -> bool:
        return bool(self.token and self.repo)

    def create_pull_request(
        self,
        branch_name: str,
        title: str,
        body: str,
        file_path: str,
        repaired_content: str
    ) -> Dict[str, Any]:
        """
        Creates a Git branch and opens a Pull Request on GitHub.
        Falls back to safe simulation mode if GITHUB_TOKEN is not configured.
        """
        if not self.is_configured():
            # Simulated PR creation for local testing and presentation
            pr_number = 42
            mock_url = f"https://github.com/infotact-staging/omnisight-store/pull/{pr_number}"
            return {
                "success": True,
                "mode": "simulated",
                "pr_number": pr_number,
                "pr_url": mock_url,
                "branch": branch_name,
                "title": title,
                "message": "Simulated Pull Request prepared successfully. To push to real GitHub, configure GITHUB_TOKEN and GITHUB_REPO in .env."
            }

        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        api_base = f"https://api.github.com/repos/{self.repo}"

        try:
            # 1. Get default branch ref (main)
            repo_res = requests.get(f"{api_base}", headers=headers, timeout=10)
            default_branch = repo_res.json().get("default_branch", "main")
            
            ref_res = requests.get(f"{api_base}/git/ref/heads/{default_branch}", headers=headers, timeout=10)
            latest_commit_sha = ref_res.json()["object"]["sha"]

            # 2. Create new branch
            create_branch_res = requests.post(
                f"{api_base}/git/refs",
                headers=headers,
                json={"ref": f"refs/heads/{branch_name}", "sha": latest_commit_sha},
                timeout=10
            )

            # 3. Create or update file on the new branch
            file_res = requests.get(
                f"{api_base}/contents/{file_path}?ref={branch_name}",
                headers=headers,
                timeout=10
            )
            sha = file_res.json().get("sha") if file_res.status_code == 200 else None

            import base64
            b64_content = base64.b64encode(repaired_content.encode("utf-8")).decode("utf-8")

            commit_payload = {
                "message": f"🤖 OmniSight: Self-heal {file_path}",
                "content": b64_content,
                "branch": branch_name
            }
            if sha:
                commit_payload["sha"] = sha

            requests.put(
                f"{api_base}/contents/{file_path}",
                headers=headers,
                json=commit_payload,
                timeout=10
            )

            # 4. Open PR
            pr_res = requests.post(
                f"{api_base}/pulls",
                headers=headers,
                json={
                    "title": title,
                    "head": branch_name,
                    "base": default_branch,
                    "body": body
                },
                timeout=10
            )
            pr_data = pr_res.json()

            return {
                "success": True,
                "mode": "live_github",
                "pr_number": pr_data.get("number"),
                "pr_url": pr_data.get("html_url"),
                "branch": branch_name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "mode": "live_github"
            }
