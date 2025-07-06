from github import Github, GithubException
import os
import datetime

class GitHubPRTool:
    """
    Agent tool for safely creating PRs to a GitHub repo (best practice: no direct pushes to main).
    """
    def __init__(self, repo_name="Librascale83/project-taile", base_branch="main"):
        self.repo_name = repo_name
        self.base_branch = base_branch
        self.token = os.environ.get("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GITHUB_TOKEN environment variable not set. Please add it as a workspace secret.")
        self.client = Github(self.token)
        self.repo = self.client.get_repo(self.repo_name)

    def create_or_update_file_and_pr(self, file_path, content, pr_title, pr_body):
        branch_name = f"agent-{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        base = self.repo.get_branch(self.base_branch)
        self.repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base.commit.sha)
        print(f"[GitHubPRTool] Creating/Updating {file_path} on branch {branch_name}")

        try:
            contents = self.repo.get_contents(file_path, ref=branch_name)
            self.repo.update_file(
                file_path, pr_title, content, contents.sha, branch=branch_name
            )
        except GithubException as e:
            if e.status == 404:
                self.repo.create_file(
                    file_path, pr_title, content, branch=branch_name
                )
            else:
                raise

        pr = self.repo.create_pull(
            title=pr_title,
            body=pr_body,
            head=branch_name,
            base=self.base_branch,
        )
        print(f"[GitHubPRTool] Pull Request created: {pr.html_url}")
        return pr.html_url
