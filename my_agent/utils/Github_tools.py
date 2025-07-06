from github import Github
import os
import datetime

class GitHubPRTool:
    """
    Agent tool for safely creating PRs to a GitHub repo (best practice: no direct pushes to main).
    """
    def __init__(self, repo_name="Librascale83/project-taile", base_branch="main"):
        self.repo_name = repo_name
        self.base_branch = base_branch
        self.token = os.environ["GITHUB_TOKEN"]
        self.client = Github(self.token)
        self.repo = self.client.get_repo(self.repo_name)

    def create_or_update_file_and_pr(self, file_path, content, pr_title, pr_body):
        # Always use unique branch name (by timestamp)
        branch_name = f"agent-{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        base = self.repo.get_branch(self.base_branch)
        self.repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base.commit.sha)
        # Try update file (if exists), else create new
        try:
            contents = self.repo.get_contents(file_path, ref=branch_name)
            self.repo.update_file(
                file_path, pr_title, content, contents.sha, branch=branch_name
            )
        except Exception:
            self.repo.create_file(
                file_path, pr_title, content, branch=branch_name
            )
        # Open PR to main
        pr = self.repo.create_pull(
            title=pr_title,
            body=pr_body,
            head=branch_name,
            base=self.base_branch,
        )
        return pr.html_url
