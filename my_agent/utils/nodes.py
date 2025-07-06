from functools import lru_cache
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from my_agent.utils.tools import tools
from langgraph.prebuilt import ToolNode

@lru_cache(maxsize=4)
def _get_model(model_name: str):
    if model_name == "openai":
        model = ChatOpenAI(temperature=0, model_name="gpt-4o")
    elif model_name == "anthropic":
        # Claude Sonnet 4 (latest, July 2025)
        model = ChatAnthropic(temperature=0, model_name="claude-sonnet-4-20250514")
    elif model_name == "anthropic-opus":
        # Claude Opus 4 (premium)
        model = ChatAnthropic(temperature=0, model_name="claude-opus-4-20250514")
    else:
        raise ValueError(f"Unsupported model type: {model_name}")
    model = model.bind_tools(tools)
    return model

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

system_prompt = """Be a helpful assistant"""

def call_model(state, config):
    messages = state["messages"]
    messages = [{"role": "system", "content": system_prompt}] + messages
    model_name = config.get('configurable', {}).get("model_name", "anthropic")
    model = _get_model(model_name)
    response = model.invoke(messages)
    return {"messages": [response]}

tool_node = ToolNode(tools)
