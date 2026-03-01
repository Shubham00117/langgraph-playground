from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

# Shared state used by both parent and subgraph
class ParentState(TypedDict):
    question: str
    answer_eng: str
    answer_hin: str      # written by subgraph

parent_llm  = ChatOpenAI(model='gpt-4o-mini')
subgraph_llm = ChatOpenAI(model='gpt-4o-mini')

# Subgraph node reads from & writes to ParentState directly
def translate_text(state: ParentState):   # uses ParentState, not SubState
    print("--- Translating inside Shared Subgraph Node ---")
    prompt = f"""Translate the following text to Hindi.
Keep it natural and clear. Do not add extra content.

Text:
{state["answer_eng"]}""".strip()

    translated_text = subgraph_llm.invoke(prompt).content
    return {'answer_hin': translated_text}  # directly updates parent state

# Build subgraph on ParentState
subgraph_builder = StateGraph(ParentState)
subgraph_builder.add_node('translate_text', translate_text)
subgraph_builder.add_edge(START, 'translate_text')
subgraph_builder.add_edge('translate_text', END)
subgraph = subgraph_builder.compile()

# Parent graph — pass compiled subgraph directly as a node
def generate_answer(state: ParentState):
    print("--- Generating Answer in Parent Node ---")
    answer = parent_llm.invoke(
        f"You are a helpful assistant. Answer clearly.\n\nQuestion: {state['question']}"
    ).content
    return {'answer_eng': answer}

parent_builder = StateGraph(ParentState)
parent_builder.add_node("answer", generate_answer)
parent_builder.add_node("translate", subgraph)   # <-- subgraph passed directly

parent_builder.add_edge(START, 'answer')
parent_builder.add_edge('answer', 'translate')
parent_builder.add_edge('translate', END)

graph = parent_builder.compile()

if __name__ == "__main__":
    question = 'What is quantum physics?'
    print(f"Question: {question}")
    result = graph.invoke({'question': question})

    print("\n--- Final Results ---")
    print(f"English Answer: {result['answer_eng'][:100]}...")
    print(f"Hindi Answer: {result['answer_hin'][:100]}...")
