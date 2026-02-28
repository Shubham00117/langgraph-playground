import streamlit as st
import uuid
from typing import TypedDict
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# --- SETUP LANGGRAPH BACKEND ---
load_dotenv('/Users/shubham_infinity/Desktop/Projects/LangGraph_Projects/.env')

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

# Checkpointer must be persistent across script reruns
if "checkpointer" not in st.session_state:
    st.session_state.checkpointer = MemorySaver()
    
# In a real app we compile using st.session_state.checkpointer OR use a database
app = workflow.compile(checkpointer=st.session_state.checkpointer)

# --- UTILITY FUNCTIONS (Topic 95) ---
def generate_thread_id():
    return str(uuid.uuid4())

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(thread_id)
    st.session_state['message_history'] = []

def load_conversation(thread_id):
    # Topic 97: Load from LangGraph Memory
    config = {'configurable': {'thread_id': thread_id}}
    state = app.get_state(config)
    messages = state.values.get('messages', [])
    
    temp_messages = []
    for msg in messages:
        role = 'user' if isinstance(msg, HumanMessage) else 'assistant'
        temp_messages.append({'role': role, 'content': msg.content})
    return temp_messages

# --- SESSION SETUP (Topic 94) ---
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []

add_thread(st.session_state['thread_id'])

# --- SIDEBAR UI (Topic 96) ---
st.sidebar.title('LangGraph Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header('My Conversations')
for thread_id in st.session_state['chat_threads']:
    # Display each thread as a clickable button
    if st.sidebar.button(f"Chat: {str(thread_id)[:8]}"):
        st.session_state['thread_id'] = thread_id
        st.session_state['message_history'] = load_conversation(thread_id)

# --- MAIN UI & DYNAMIC CONFIG (Topic 98) ---
st.title("Topic 93-99: Resume Chat UI")
st.write(f"Active Thread ID: `{st.session_state['thread_id']}`")

for msg in st.session_state['message_history']:
    with st.chat_message(msg['role']):
        st.write(msg['content'])

user_input = st.chat_input("Type your message...")

if user_input:
    # 1. Update UI history immediately
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.write(user_input)
        
    # 2. Dynamic Config using active thread
    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}
    
    # 3. Stream from Agent
    with st.chat_message('assistant'):
        def token_stream():
            for chunk, _ in app.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            ):
                if chunk.content:
                    yield chunk.content
                    
        ai_message = st.write_stream(token_stream())
        
    # 4. Save Final AI message to UI history
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
