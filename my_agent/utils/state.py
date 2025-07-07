from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage
from typing import TypedDict, Annotated, Sequence, Optional

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    
    # Dynamic PR fields (populated based on context)
    file_path: Optional[str]
    file_content: Optional[str]
    pr_title: Optional[str]
    pr_body: Optional[str]
    
    # Context for dynamic generation
    documentation_type: Optional[str]  # "technical_spec", "user_guide", "architecture", etc.
    target_audience: Optional[str]      # "developers", "stakeholders", "users"
    changes_summary: Optional[str]      # What's being added/changed
    business_impact: Optional[str]      # Why this matters
    
    # Project-specific fields
    project_name: Optional[str]         # For project-specific documentation
    feature_name: Optional[str]         # For feature-specific documentation
    priority_level: Optional[str]       # "high", "medium", "low"
