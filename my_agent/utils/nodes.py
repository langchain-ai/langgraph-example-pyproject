from functools import lru_cache
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from my_agent.utils.tools import tools
from langgraph.prebuilt import ToolNode
from typing import Dict, Any
import re

@lru_cache(maxsize=4)
def _get_model(model_name: str):
    if model_name == "openai":
        model = ChatOpenAI(temperature=0, model_name="gpt-4o")
    elif model_name == "anthropic":
        # Claude Sonnet 4 (latest)
        model = ChatAnthropic(temperature=0, model_name="claude-sonnet-4-20250514")
    elif model_name == "anthropic-opus":
        # Claude Opus 4 (premium)
        model = ChatAnthropic(temperature=0, model_name="claude-opus-4-20250514")
    else:
        raise ValueError(f"Unsupported model type: {model_name}")
    model = model.bind_tools(tools)
    return model

# --- Content Generation Functions ---
def generate_pr_title(doc_type: str, changes_summary: str, project_name: str = None) -> str:
    """Generate PR title based on documentation type and changes"""
    
    project_prefix = f"{project_name}: " if project_name else ""
    
    title_templates = {
        "technical_spec": f"feat: {project_prefix}Add {{topic}} Technical Specification",
        "user_guide": f"docs: {project_prefix}Add {{topic}} User Guide",
        "architecture": f"feat: {project_prefix}Add {{topic}} Architecture Documentation",
        "api_docs": f"docs: {project_prefix}Add {{topic}} API Documentation",
        "deployment": f"feat: {project_prefix}Add {{topic}} Deployment Guide",
        "troubleshooting": f"docs: {project_prefix}Add {{topic}} Troubleshooting Guide",
        "master_brain_dump": f"feat: {project_prefix}Add {{topic}} Master Documentation",
        "context_engineering": f"feat: {project_prefix}Add {{topic}} Context Engineering Framework"
    }
    
    template = title_templates.get(doc_type, f"feat: {project_prefix}Add {{topic}} Documentation")
    return template.format(topic=changes_summary)

def generate_pr_body(doc_type: str, changes_summary: str, business_impact: str, project_name: str = None) -> str:
    """Generate PR body based on context"""
    
    project_section = f"**Project**: {project_name}\n" if project_name else ""
    
    return f"""## Summary
This PR adds {doc_type.replace('_', ' ')} documentation for {changes_summary}.

{project_section}## Key Changes
- **Documentation Type**: {doc_type.title().replace('_', ' ')}
- **Content Added**: {changes_summary}
- **Target Audience**: Development team and stakeholders

## Business Impact
{business_impact}

## Technical Details
- Addresses specific documentation gap in the codebase
- Improves developer onboarding and system understanding
- Enhances maintainability and knowledge transfer

## Next Actions
- [ ] Review documentation for accuracy and completeness
- [ ] Update related documentation links and references
- [ ] Notify relevant team members and stakeholders
- [ ] Schedule documentation walkthrough if needed
- [ ] Update project documentation index

## Quality Assurance
- [ ] Documentation follows established style guide
- [ ] All code examples are tested and working
- [ ] Links and references are valid
- [ ] Content is accessible to target audience
"""

def generate_file_content(doc_type: str, topic: str, details: str, project_name: str = None) -> str:
    """Generate actual file content based on documentation type"""
    
    project_header = f"**Project**: {project_name}\n" if project_name else ""
    
    content_templates = {
        "technical_spec": f"""# {topic} Technical Specification

{project_header}**Document Purpose**: Technical specification for {topic}
**Last Updated**: {get_current_date()}
**Status**: In Development

## Overview
{details}

## Architecture Overview
This section describes the high-level architecture and design decisions.

## System Components
Detail the main components and their interactions.

## Implementation Details
Specific implementation guidelines and requirements.

## API Reference
API endpoints, parameters, and response formats.

## Configuration
Configuration options and environment setup.

## Performance Considerations
Performance requirements and optimization strategies.

## Security Considerations
Security requirements and best practices.

## Testing Strategy
Testing approach and requirements.

## Deployment
Deployment procedures and requirements.

## Monitoring & Logging
Monitoring and logging specifications.

## Troubleshooting
Common issues and solutions.

## References
Links to related documentation and resources.
""",
        "user_guide": f"""# {topic} User Guide

{project_header}**Document Purpose**: User guide for {topic}
**Last Updated**: {get_current_date()}
**Target Audience**: End users and operators

## Getting Started
{details}

## Prerequisites
What users need before starting.

## Step-by-Step Instructions
Detailed walkthrough of common tasks.

## Common Use Cases
Real-world scenarios and examples.

## Advanced Features
Advanced functionality and configuration options.

## Best Practices
Recommended approaches and patterns.

## Troubleshooting
Common issues and solutions.

## FAQ
Frequently asked questions and answers.

## Support
How to get help and additional resources.

## Glossary
Definition of terms and concepts.
""",
        "architecture": f"""# {topic} Architecture

{project_header}**Document Purpose**: Architecture documentation for {topic}
**Last Updated**: {get_current_date()}
**Status**: Current

## System Overview
{details}

## Architecture Principles
Core principles guiding the architecture.

## System Context
External systems and interfaces.

## Component Architecture
Detailed component breakdown and relationships.

## Data Architecture
Data flow, storage, and management.

## Security Architecture
Security design and implementation.

## Deployment Architecture
Deployment topology and infrastructure.

## Integration Points
External integrations and APIs.

## Scalability Considerations
Scalability design and limitations.

## Performance Characteristics
Performance requirements and benchmarks.

## Reliability & Availability
Reliability design and SLA considerations.

## Monitoring & Observability
Monitoring and observability strategy.

## Future Considerations
Planned improvements and evolution.
""",
        "master_brain_dump": f"""# {topic} Master Documentation

{project_header}**Document Purpose**: Complete reference and source of truth for {topic}
**Last Updated**: {get_current_date()}
**Status**: Living Document

## Executive Summary
{details}

## Project Vision
Long-term vision and goals.

## Technical Architecture
High-level technical design and components.

## Implementation Roadmap
Development timeline and milestones.

## Team Structure
Team organization and responsibilities.

## Resource Requirements
Required resources and budget considerations.

## Risk Assessment
Identified risks and mitigation strategies.

## Success Metrics
Key performance indicators and success criteria.

## Documentation Matrix
Complete documentation structure and ownership.

## Context Engineering
Context management and coordination strategies.

## Quality Assurance
Quality gates and validation procedures.

## Deployment Strategy
Deployment approach and rollout plan.

## Operational Procedures
Day-to-day operational guidelines.

## Continuous Improvement
Feedback loops and improvement processes.
"""
    }
    
    return content_templates.get(doc_type, f"# {topic}\n\n{project_header}## Overview\n{details}\n\n## Implementation\n\n## Usage\n\n## Configuration\n\n## Troubleshooting\n")

def get_current_date() -> str:
    """Get current date in readable format"""
    from datetime import datetime
    return datetime.now().strftime("%B %Y")

def extract_pr_context(user_request: str) -> Dict[str, Any]:
    """Extract PR context from user request"""
    
    context = {}
    user_request_lower = user_request.lower()
    
    # Determine documentation type
    if "technical" in user_request_lower or "spec" in user_request_lower:
        context["doc_type"] = "technical_spec"
    elif "user guide" in user_request_lower or "guide" in user_request_lower:
        context["doc_type"] = "user_guide"
    elif "architecture" in user_request_lower or "system design" in user_request_lower:
        context["doc_type"] = "architecture"
    elif "api" in user_request_lower:
        context["doc_type"] = "api_docs"
    elif "deployment" in user_request_lower or "deploy" in user_request_lower:
        context["doc_type"] = "deployment"
    elif "troubleshooting" in user_request_lower or "troubleshoot" in user_request_lower:
        context["doc_type"] = "troubleshooting"
    elif "master" in user_request_lower or "brain dump" in user_request_lower:
        context["doc_type"] = "master_brain_dump"
    elif "context engineering" in user_request_lower:
        context["doc_type"] = "context_engineering"
    else:
        context["doc_type"] = "technical_spec"
    
    # Extract project name
    project_matches = re.findall(r'(?:project|for)\s+([a-zA-Z0-9-_]+)', user_request_lower)
    if project_matches:
        context["project_name"] = project_matches[0].title()
    
    # Extract topic/feature name
    topic_patterns = [
        r'(?:for|about|regarding)\s+([a-zA-Z0-9\s-_]+?)(?:\s+(?:documentation|docs|guide|spec))',
        r'(?:add|create|document)\s+([a-zA-Z0-9\s-_]+?)(?:\s+(?:documentation|docs|guide|spec))',
        r'(?:documentation|docs|guide|spec)\s+(?:for|about)\s+([a-zA-Z0-9\s-_]+)'
    ]
    
    topic = "New Feature"
    for pattern in topic_patterns:
        match = re.search(pattern, user_request_lower)
        if match:
            topic = match.group(1).strip().title()
            break
    
    context["topic"] = topic
    context["feature_name"] = topic
    
    # Set file path based on doc type and topic
    doc_type = context["doc_type"]
    topic_clean = topic.lower().replace(" ", "_").replace("-", "_")
    project_clean = context.get("project_name", "").lower().replace(" ", "_").replace("-", "_")
    
    path_map = {
        "technical_spec": f"docs/technical/{topic_clean}_spec.md",
        "user_guide": f"docs/guides/{topic_clean}_guide.md",
        "architecture": f"docs/architecture/{topic_clean}_architecture.md",
        "api_docs": f"docs/api/{topic_clean}_api.md",
        "deployment": f"docs/deployment/{topic_clean}_deployment.md",
        "troubleshooting": f"docs/troubleshooting/{topic_clean}_troubleshooting.md",
        "master_brain_dump": f"docs/{project_clean}_master_brain_dump.md" if project_clean else f"docs/{topic_clean}_master.md",
        "context_engineering": f"docs/context_engineering/{topic_clean}_context.md"
    }
    
    context["file_path"] = path_map.get(doc_type, f"docs/{topic_clean}.md")
    context["business_impact"] = f"Improves documentation and knowledge management for {topic}"
    context["target_audience"] = "developers"
    context["priority_level"] = "medium"
    
    return context

# --- Robust should_continue that can't crash from NoneType, empty, or dict/object differences ---
def should_continue(state):
    messages = state.get("messages", [])
    if not messages:
        return "end"
    last_message = messages[-1]
    # Accept both dict (API msg) and object (LC msg)
    if isinstance(last_message, dict):
        tool_calls = last_message.get("tool_calls")
    else:
        tool_calls = getattr(last_message, "tool_calls", None)
    if not tool_calls:
        return "end"
    return "continue"

# --- Enhanced system prompt for dynamic PR creation ---
system_prompt = """You are a PM Orchestrator that creates GitHub PRs for various types of documentation.

When a user requests PR creation, analyze their request to determine:
1. Documentation type (technical_spec, user_guide, architecture, api_docs, deployment, troubleshooting, master_brain_dump, context_engineering)
2. Topic/feature they want documented
3. Project context and business impact
4. Target audience and priority level

Generate appropriate file paths, titles, and content based on the specific context.

You can handle requests like:
- "Create technical documentation for [feature]"
- "Add user guide for [feature]"
- "Create architecture docs for [system]"
- "Add API documentation for [endpoint]"
- "Create master brain dump for [project]"
- "Add context engineering framework for [project]"

Always customize the PR title, content, and description based on the specific request.
Use clear, professional language and follow documentation best practices."""

def call_model(state, config):
    messages = state["messages"]
    
    # Analyze user request to determine PR context
    user_request = " ".join([str(msg.content) if hasattr(msg, 'content') else str(msg) for msg in messages[-3:]])
    
    # Check if this is a PR creation request
    pr_keywords = ["create pr", "pull request", "add documentation", "create documentation", 
                   "add docs", "create docs", "document", "add guide", "create guide"]
    is_pr_request = any(keyword in user_request.lower() for keyword in pr_keywords)
    
    if is_pr_request:
        # Extract context from user request
        context = extract_pr_context(user_request)
        
        # Generate dynamic PR parameters
        pr_state_update = {
            "file_path": context.get("file_path"),
            "file_content": generate_file_content(
                context.get("doc_type", "technical_spec"),
                context.get("topic", "New Feature"),
                context.get("business_impact", "Documentation for new feature"),
                context.get("project_name")
            ),
            "pr_title": generate_pr_title(
                context.get("doc_type", "technical_spec"),
                context.get("topic", "New Feature"),
                context.get("project_name")
            ),
            "pr_body": generate_pr_body(
                context.get("doc_type", "technical_spec"),
                context.get("topic", "New Feature"),
                context.get("business_impact", "Improves system documentation"),
                context.get("project_name")
            ),
            "documentation_type": context.get("doc_type"),
            "target_audience": context.get("target_audience", "developers"),
            "changes_summary": context.get("topic"),
            "business_impact": context.get("business_impact"),
            "project_name": context.get("project_name"),
            "feature_name": context.get("feature_name"),
            "priority_level": context.get("priority_level", "medium")
        }
        
        # Update state with dynamic PR data
        state.update(pr_state_update)
    
    # Continue with model call
    messages = [{"role": "system", "content": system_prompt}] + messages
    # Default to Opus 4 for PM unless overridden
    model_name = config.get('configurable', {}).get("model_name", "anthropic-opus")
    model = _get_model(model_name)
    response = model.invoke(messages)
    
    return {"messages": [response]}

# --- Custom tool node for complete PR parameter handling ---
def tool_node(state):
    """Custom tool node that ensures complete PR parameters"""
    
    messages = state["messages"]
    last_message = messages[-1]
    
    # Handle tool calls with proper parameter validation
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        tool_call = last_message.tool_calls[0]
        
        # Special handling for create_github_pr
        if tool_call.get('name') == 'create_github_pr':
            # Use state data instead of incomplete model parameters
            pr_params = {
                'file_path': state.get('file_path', 'docs/new_documentation.md'),
                'content': state.get('file_content', '# New Documentation\n\nThis is new documentation.'),
                'pr_title': state.get('pr_title', 'feat: Add new documentation'),
                'pr_body': state.get('pr_body', 'This PR adds new documentation to the repository.')
            }
            
            # Debug logging
            print(f"PR Parameters: {list(pr_params.keys())}")
            print(f"All required fields present: {all(pr_params.values())}")
            
            # Import and call the tool with complete parameters
            from my_agent.utils.tools import create_github_pr
            try:
                result = create_github_pr.invoke(pr_params)
                return {"messages": [result]}
            except Exception as e:
                error_msg = f"Error creating PR: {str(e)}"
                print(error_msg)
                return {"messages": [{"role": "assistant", "content": error_msg}]}
    
    # For other tools, use standard ToolNode behavior
    tool_node_standard = ToolNode(tools)
    return tool_node_standard.invoke(state)

# Export the custom tool_node instead of the standard one
# tool_node = ToolNode(tools)  # Remove this line
# Use the custom tool_node function instead
