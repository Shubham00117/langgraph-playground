from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver
from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini")

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    decision = interrupt({
        "type": "approval",
        "reason": "Model is about to answer a user question.",
        "question": state["messages"][-1].content,
        "instruction": "Approve this question? yes/no"
    })

    if decision["approved"] == 'no':
        return {"messages": [AIMessage(content="Not approved.")]}
    else:
        response = llm.invoke(state["messages"])
        return {"messages": [response]}

# Build the graph: START -> chat -> END
builder = StateGraph(ChatState)
builder.add_node("chat", chat_node)
builder.add_edge(START, "chat")
builder.add_edge("chat", END)

# Checkpointer is required for interrupts
checkpointer = MemorySaver()
app = builder.compile(checkpointer=checkpointer)

if __name__ == "__main__":
    # Running — First invoke (triggers interrupt)
    config = {"configurable": {"thread_id": "thread-1"}}

    print("--- First Invoke ---")
    result = app.invoke(
        {"messages": [HumanMessage(content="Explain gradient descent in very simple terms.")]},
        config=config
    )

    # result contains __interrupt__ key with payload
    if "__interrupt__" in result:
        message = result['__interrupt__'][0].value
        # Shows the interrupt payload to the human
        print(f"\nBackend message: {message}")
        user_input = input("Approve this question? (yes/no): ").strip().lower()
        
        # Resume the graph with the approval decision
        print("\n--- Resuming with decision ---")
        final_result = app.invoke(
            Command(resume={"approved": user_input}),
            config=config,
        )
        print(f"Final Message: {final_result['messages'][-1].content}")
    else:
        print(result)
