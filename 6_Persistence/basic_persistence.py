import os
import time
from typing import TypedDict
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# Load API keys
load_dotenv('/Users/shubham_infinity/Desktop/Projects/LangGraph_Projects/.env')

# Define State
class State(TypedDict):
    messages: list
    topic: str

# Define Nodes
def generate_joke(state: State):
    llm = ChatGroq(model="llama-3.3-70b-versatile")
    prompt = f"Tell me a short joke about {state.get('topic', 'AI')}."
    response = llm.invoke(prompt)
    return {"messages": state.get('messages', []) + [response]}

def human_review(state: State):
    # This node is just a placeholder for the human interrupt point
    return {"messages": state.get('messages', [])}

def publish_joke(state: State):
    return {"messages": state.get('messages', []) + ["Joke Published!"]}

# Build Graph with Persistence
workflow = StateGraph(State)
workflow.add_node("generate", generate_joke)
workflow.add_node("review", human_review)
workflow.add_node("publish", publish_joke)

workflow.add_edge(START, "generate")
workflow.add_edge("generate", "review")
workflow.add_edge("review", "publish")
workflow.add_edge("publish", END)

checkpointer = MemorySaver()

# Compile with Human-In-The-Loop interrupt before 'publish'
app = workflow.compile(checkpointer=checkpointer, interrupt_before=["publish"])

config = {"configurable": {"thread_id": "demo-thread-1"}}

print("=== 1. Basic Persistence & Execution ===")
response = app.invoke({"topic": "pizza", "messages": []}, config=config)
print("Agent Generated Joke:", response['messages'][-1].content)

print("\n=== 2. Human-In-The-Loop (HITL) ===")
# At this point, the graph hit 'interrupt_before=["publish"]'
current_state = app.get_state(config)
print(f"Current Next Step: {current_state.next}") # Will show ('publish',)

# Simulate Human Reviewing and Approving -> Resume by passing None
print("Human approved! Resuming...")
final_response = app.invoke(None, config=config)
print("Final State:", final_response['messages'][-1])

print("\n=== 3. Fault Tolerance (Resume) ===")
# If the app crashed mid-way (e.g. before publish), invoking with `None` resumes from the last checkpoint automatically.
print("Passing None resumes from the exact last state if interrupted!")

print("\n=== 4. Time Travel ===")
# View history
history = list(app.get_state_history(config))
print(f"Total checkpoints saved: {len(history)}")

# Pick an old checkpoint (the one right after 'generate')
past_checkpoint = history[-2] 
print(f"Going back in time to checkpoint: {past_checkpoint.config['configurable']['checkpoint_id']}")

# Re-run from the past state
print("Replaying from past state...")
replay_response = app.invoke(None, past_checkpoint.config)
print("Replay Output:", replay_response['messages'][-1])

print("\n=== 5. Updating State (Branching) ===")
# Modify the past state
new_config = app.update_state(
    past_checkpoint.config,
    {"topic": "samosa"} # Changing the topic retroactively
)
print("Updated state topic to 'samosa'. Re-running from this new branch...")
branch_response = app.invoke(None, new_config)
print("Branched Output:", app.get_state(new_config).values['messages'][-1])
