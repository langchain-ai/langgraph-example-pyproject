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
        model = ChatAnthropic(temperature=0, model_name="claude-sonnet-4-20250514")
    elif model_name == "anthropic-opus":
        model = ChatAnthropic(temperature=0, model_name="claude-opus-4-20250514")
    else:
        raise ValueError(f"Unsupported model type: {model_name}")
    model = model.bind_tools(tools)
    return model

def should_continue(state):
    messages = state["messages"]
    last_message = messages[-1]
    # Works for dict or object; avoids NoneType errors
    if isinstance(last_message, dict):
        tool_calls = last_message.get("tool_calls", None)
    else:
        tool_calls = getattr(last_message, "tool_calls", None)
    if not tool_calls:
        return "end"
    else:
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
