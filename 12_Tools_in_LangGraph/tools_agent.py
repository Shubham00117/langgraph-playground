import os
import requests
from typing import Annotated, TypedDict
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import BaseMessage, HumanMessage

from langgraph.graph import START, END, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages

# Load API keys
load_dotenv('/Users/shubham_infinity/Desktop/Projects/LangGraph_Projects/.env')

# --- 1. Tool Definitions ---
# Prebuilt tool
search_tool = DuckDuckGoSearchRun(region="us-en")

# Custom tool 1
@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """Perform add, sub, mul, div."""
    if operation == 'add': return {'result': first_num + second_num}
    elif operation == 'sub': return {'result': first_num - second_num}
    elif operation == 'mul': return {'result': first_num * second_num}
    elif operation == 'div': return {'result': first_num / second_num}
    return {'result': 'invalid operation'}

# Custom tool 2
@tool
def get_stock_price(symbol: str) -> dict:
    """Fetch latest price for e.g. AAPL."""
    # Dummy mock response since alphavantage requires API key
    return {"symbol": symbol, "price": 150.0}

# Collect all tools
tools = [get_stock_price, search_tool, calculator]

# --- 2. Bind Tools & State ---
llm = ChatGroq(model="llama-3.3-70b-versatile")
llm_with_tools = llm.bind_tools(tools)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# --- 3. Graph Logic ---
def chat_node(state: ChatState):
    # Sends messages to LLM -> LLM returns AIMessage or tool_calls
    response = llm_with_tools.invoke(state['messages'])
    return {"messages": [response]}

# ToolNode executes the requested Python functions
tool_node = ToolNode(tools)

# --- 4. Architect the Graph Loop ---
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")
# Conditionally route: If LLM asks for tool -> tools, else -> END
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge("tools", "chat_node") # Loop back so LLM sees the tool output
chatbot = graph.compile()

print("\n=== Invoking Agent with Tools Built Into Graph ===\n")

print("User: Calculate 45 mul 2. Then check the mock stock price for GOOGL.")
inputs = {"messages": [HumanMessage(content="Calculate 45 mul 2. Then check the mock stock price for GOOGL.")]}

for event in chatbot.stream(inputs, stream_mode="values"):
    message = event["messages"][-1]
    msg_type = message.type
    content = message.content or str(getattr(message, 'tool_calls', ''))
    print(f"\n[Node -> {msg_type.upper()}] {content}")
