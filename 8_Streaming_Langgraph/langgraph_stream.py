import streamlit as st
import time
from typing import TypedDict
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage

load_dotenv('/Users/shubham_infinity/Desktop/Projects/LangGraph_Projects/.env')

st.title("Topic 87-92: Streaming in LangGraph")

# --- Topic 89: Python Generator (Foundation) ---
def simple_generator():
    yield "Hello "
    time.sleep(0.5)
    yield "World"

st.subheader("1. Simple Python Generator")
if st.button("Run Generator"):
    st.write_stream(simple_generator())


# --- Topic 90 & 91: LangGraph Backend Streaming & Streamlit Frontend ---
class State(TypedDict):
    messages: list

def call_model(state: State):
    llm = ChatGroq(model="llama-3.3-70b-versatile")
    response = llm.invoke(state['messages'])
    return {"messages": [response]}

workflow = StateGraph(State)
workflow.add_node("agent", call_model)
workflow.add_edge(START, "agent")
workflow.add_edge("agent", END)
app = workflow.compile()

st.subheader("2. LangGraph Token Streaming")

# Provide an input field
user_input = st.text_input("Ask the LLM something:")

if st.button("Stream Response") and user_input:
    # We display the chat message bubble
    with st.chat_message('assistant'):
        # Topic 91: st.write_stream consumes a generator yielding tokens
        # Topic 90: using stream_mode='messages' to get token fragments
        
        # Generator expression that streams tokens
        def langgraph_token_generator():
            # Streams chunks as generated
            for message_chunk, metadata in app.stream(
                {'messages': [HumanMessage(content=user_input)]},
                stream_mode='messages'
            ):
                if message_chunk.content:
                    yield message_chunk.content

        # Renders the tokens live on UI
        full_response = st.write_stream(langgraph_token_generator())
        
        # In a real app, you would append full_response to session_state message history here. 
