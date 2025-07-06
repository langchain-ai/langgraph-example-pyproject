# --- Baseline Tools for MVP ---

# 1. Internal Document/Spec Search (for docs, specs, BOM, compliance, etc.)
from langchain_community.tools.file_management import ReadFileTool
from langchain_community.tools import tool

# 2. GitHub Pull Request Tool (expose as function, not class)
@tool
def create_github_pr(file_path: str, content: str, pr_title: str, pr_body: str) -> str:
    """
    Create or update a file and open a PR in the project-taile GitHub repo.
    """
    from my_agent.tools.github_tools import GitHubPRTool
    pr_tool = GitHubPRTool(repo_name="Librascale83/project-taile", base_branch="main")
    return pr_tool.create_or_update_file_and_pr(file_path, content, pr_title, pr_body)

# --- Tool List ---
tools = [
    # For project source of truth/doc retrieval
    ReadFileTool(root_dir="./docs"),
    # For agent-generated PRs to your GitHub repo (safe workflow, no direct pushes)
    create_github_pr,
]

# --- Expansion Instructions for PMs (comment for maintainers) ---
# To add new tools:
# - Import or define a function above
# - Add it to the `tools` list above
#
# Examples for future expansion:
# from my_agent.utils.tools.code_search import CodeSearchTool
# from my_agent.utils.tools.bom_lookup import BOMLookupTool
# from my_agent.utils.tools.task_manager import TaskManagerTool
# from my_agent.utils.tools.compliance_reference import ComplianceReferenceTool
# from my_agent.utils.tools.notify import NotifyTool
#
# tools.append(CodeSearchTool(repo_path="./src"))
# tools.append(BOMLookupTool(database_path="./bom.db"))
# tools.append(TaskManagerTool(api_key="..."))
# tools.append(ComplianceReferenceTool(data_path="./compliance"))
# tools.append(NotifyTool(slack_webhook_url="..."))
