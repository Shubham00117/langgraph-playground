import os
import sqlite3
import streamlit as st
import uuid
from typing import TypedDict
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

load_dotenv('/Users/shubham_infinity/Desktop/Projects/LangGraph_Projects/.env')

# --- Backend SQLite Checkpointer Setup (Topic 101/102) ---
db_path = "chatbot.db"
# check_same_thread=False allows Streamlit's multiple threads to interact with DB
conn = sqlite3.connect(db_path, check_same_thread=False)
checkpointer = SqliteSaver(conn)

class State(TypedDict):
    messages: list

def call_model(state: State):
    llm = ChatGroq(model="llama-3.3-70b-versatile")
    response = llm.invoke(state['messages'])
    return {"messages": state['messages'] + [response]}

workflow = StateGraph(State)
workflow.add_node("agent", call_model)
workflow.add_edge(START, "agent")
workflow.add_edge("agent", END)

# Compile using sqlite checkpointer
app = workflow.compile(checkpointer=checkpointer)

# --- Topic 103: Retrieve All Saved Threads from DB ---
def retrieve_all_threads():
    all_threads = set() # Prevent duplicates handling many checkpoints per thread
    for checkpoint in checkpointer.list(None):
        thread_id = checkpoint.config['configurable']['thread_id']
        all_threads.add(thread_id)
    return list(all_threads)

# --- Frontend Integration (Topic 104) ---
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = str(uuid.uuid4())

if 'chat_threads' not in st.session_state:
    # Instead of starting with empty list [], load past ones from SQLite
    saved_threads = retrieve_all_threads()
    st.session_state['chat_threads'] = saved_threads

# Register current thread
if st.session_state['thread_id'] not in st.session_state['chat_threads']:
    st.session_state['chat_threads'].append(st.session_state['thread_id'])

# UI Build
st.title("Topic 100-105: SQLite Persistence")
st.write("Current Threads pulled from DB:", st.session_state['chat_threads'])

config = {'configurable': {'thread_id': st.session_state['thread_id']}}

if st.button("Send Test Message"):
    resp = app.invoke({"messages": [HumanMessage(content="Hello SQLite!")]}, config=config)
    st.success(f"Agent Replied: {resp['messages'][-1].content}")
    st.info("Check `chatbot.db` file. If you rerun the script, the past thread IDs will remain in UI.")

# Clean up db connection on app close in production
