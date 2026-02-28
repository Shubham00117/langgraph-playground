import asyncio
import threading
from typing import Annotated, TypedDict
import os

from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

# MCP Integrations
try:
    from langchain_mcp_adapters.client import MultiServerMCPClient
    from langchain_core.tools import BaseTool
except ImportError:
    print("langchain_mcp_adapters package required. Install it via pip.")

# 1. Background Event Loop Setup (for Sync bridging)
_ASYNC_LOOP = asyncio.new_event_loop()
_ASYNC_THREAD = threading.Thread(target=_ASYNC_LOOP.run_forever, daemon=True)
_ASYNC_THREAD.start()

def run_async(coro):
    """Bridge async code into sync application scope."""
    future = asyncio.run_coroutine_threadsafe(coro, _ASYNC_LOOP)
    return future.result()

# 2. Architect MCP Client connections to servers
client = MultiServerMCPClient({
    "arith": { 
        # Connect to our local server process
        "transport": "stdio",
        "command": "python3",
        "args": ["arith_server.py"], # Assuming script runs in the directory
    }
    # Example for remote FastMCP Cloud:
    # "expense": { "transport": "streamable_http", "url": "https://<cloud_url>.fastmcp.app/mcp" }
})

# 3. Request Tools from the Server dynamically
def load_mcp_tools() -> list[BaseTool]:
    try:
        return run_async(client.get_tools())
    except Exception as e:
        print(f"Error connecting to MCP servers: {e}")
        return []

mcp_tools = load_mcp_tools()
print(f"Discovered MCP Tools: {[t.name for t in mcp_tools]}")

# 4. Integrate into LangGraph
llm = ChatGroq(model="llama-3.3-70b-versatile")
llm_with_tools = llm.bind_tools(mcp_tools) if mcp_tools else llm
tool_node = ToolNode(mcp_tools) if mcp_tools else None

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# IMPORTANT: Node must be async when dealing with MCP adapters
async def chat_node(state: ChatState):
    response = await llm_with_tools.ainvoke(state['messages'])
    return {"messages": [response]}

# Architecture Graph
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")

if tool_node:
    graph.add_node("tools", tool_node)
    graph.add_conditional_edges("chat_node", tools_condition)
    graph.add_edge("tools", "chat_node")
else:
    graph.add_edge("chat_node", END)

# Skip sqlite here due to missing dependencies/complexities out of demo scope, just run pure compile
chatbot = graph.compile()

# Example Invocation via run_async
async def main():
    print("\n--- Running AI Flow asking Math Query via MCP ---")
    inputs = {"messages": [HumanMessage(content="Can you add 400 and 80. Then divide the result by 2 using your tools?")]}
    result = await chatbot.ainvoke(inputs)
    print("Final Agent Response:", result['messages'][-1].content)

if __name__ == "__main__":
    if mcp_tools:
        # Run test explicitly
        asyncio.run(main())
    else:
        print("MCP Tools omitted due to missing packages or server connection.")
