# --- Baseline Tools for MVP ---

# 1. Internal Document/Spec Search (for docs, specs, BOM, compliance, etc.)
from langchain_community.tools.file_management import ReadFileTool

# 2. GitHub Pull Request Tool (best practice: agent submits doc/plan changes as PRs for review)
from my_agent.tools.github_tools import GitHubPRTool

# --- Tool List ---
tools = [
    # For project source of truth/doc retrieval
    ReadFileTool(root_dir="./docs"),
    # For agent-generated PRs to your GitHub repo (safe workflow, no direct pushes)
    GitHubPRTool(repo_name="Librascale83/project-taile", base_branch="main"),
]

# --- Expansion Instructions for PMs (comment for maintainers) ---
# To add new tools:
# - Import the tool at the top (see template lines below)
# - Add to the `tools` list above
#
# Examples for future expansion:
# from my_agent.tools.code_search import CodeSearchTool
# from my_agent.tools.bom_lookup import BOMLookupTool
# from my_agent.tools.task_manager import TaskManagerTool
# from my_agent.tools.compliance_reference import ComplianceReferenceTool
# from my_agent.tools.notify import NotifyTool
#
# tools.append(CodeSearchTool(repo_path="./src"))
# tools.append(BOMLookupTool(database_path="./bom.db"))
# tools.append(TaskManagerTool(api_key="..."))
# tools.append(ComplianceReferenceTool(data_path="./compliance"))
# tools.append(NotifyTool(slack_webhook_url="..."))
