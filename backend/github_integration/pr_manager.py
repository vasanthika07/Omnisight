import os
import re
import time
import requests
import subprocess
from typing import Dict, Any, Optional
from backend.config import GITHUB_TOKEN, GITHUB_REPO, ROOT_DIR

class GitHubPRManager:
    def __init__(self):
        self.token = GITHUB_TOKEN
        self.repo = GITHUB_REPO or self._detect_repo()

    def _detect_repo(self) -> Optional[str]:
        """
        Attempts to auto-detect GitHub repository name from local git remote.
        """
        try:
            res = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                cwd=str(ROOT_DIR),
                capture_output=True,
                text=True,
                timeout=4
            )
            raw = res.stdout.strip()
            match = re.search(r"github\.com[:/]([^/]+/[^/.]+?)(?:\.git)?$", raw)
            if match:
                return match.group(1)
        except Exception:
            pass
        return None

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
        Falls back to local branch creation and safe simulation mode if GITHUB_TOKEN is not configured.
        """
        target_repo = self.repo or "vasanthika07/Omnisight"

        # Try to ensure a local Git branch exists for developer auditability
        try:
            subprocess.run(["git", "branch", branch_name], cwd=str(ROOT_DIR), capture_output=True, timeout=5)
        except Exception:
            pass

        if not self.is_configured():
            # Simulated PR creation for local testing and presentation
            pr_number = (int(time.time()) % 900) + 100
            mock_url = f"https://github.com/{target_repo}/pull/{pr_number}"
            compare_url = f"https://github.com/{target_repo}/compare/main...{branch_name}?expand=1"
            
            return {
                "success": True,
                "mode": "simulated",
                "pr_number": pr_number,
                "pr_url": mock_url,
                "compare_url": compare_url,
                "branch": branch_name,
                "repo": target_repo,
                "title": title,
                "message": (
                    f"Automated Pull Request prepared for branch '{branch_name}'. "
                    f"Local branch registered. Set GITHUB_TOKEN in .env to auto-push directly to GitHub."
                )
            }

        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        api_base = f"https://api.github.com/repos/{target_repo}"

        try:
            # 1. Get default branch ref (main)
            repo_res = requests.get(f"{api_base}", headers=headers, timeout=10)
            if repo_res.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to access GitHub repository '{target_repo}': {repo_res.text}",
                    "mode": "live_github"
                }
            default_branch = repo_res.json().get("default_branch", "main")
            
            ref_res = requests.get(f"{api_base}/git/ref/heads/{default_branch}", headers=headers, timeout=10)
            latest_commit_sha = ref_res.json()["object"]["sha"]

            # 2. Create new branch (or continue if already exists)
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

            if pr_res.status_code not in [200, 201]:
                err_msg = pr_data.get("message") or str(pr_data)
                return {
                    "success": False,
                    "error": f"GitHub PR dispatch rejected: {err_msg}",
                    "mode": "live_github"
                }

            return {
                "success": True,
                "mode": "live_github",
                "pr_number": pr_data.get("number"),
                "pr_url": pr_data.get("html_url"),
                "branch": branch_name,
                "repo": target_repo
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "mode": "live_github"
            }
