# LangGraph Playground & Tutorials 🚀

Welcome to the **LangGraph Playground**! This repository is a collection of learning materials, comprehensive notes, and implementations focused on **LangGraph** and **Agentic AI**, following the [CampusX](https://www.youtube.com/@campusx-official) Agentic AI series.

## 📚 Project Overview

This project serves as a structured learning path for mastering LangGraph, an orchestration framework for building intelligent, stateful, and multi-step LLM workflows.

### 📝 Course Modules (Notes)

The `Notes/` directory contains detailed HTML notes with a premium aesthetic, covering the following topics:

1.  **Curriculum** (`1_Circulam.html`): The roadmap for the Agentic AI course.
2.  **GenAI vs Agentic AI** (`2_GenAi_VS_AgenticAi.html`): Understanding the evolution from generative to agentic systems.
3.  **Agentic AI** (`3_AgenticAI.html`): Core principles and architectures of AI agents.
4.  **LangChain vs LangGraph** (`4_Langchain_VS_LangGraph.html`): Comparing linear chains with graph-based orchestration.
5.  **Core Concepts** (`5_CoreConcept.html`): Deep dive into Graphs, Nodes, Edges, State, and Reducers.

---

## 🛠️ Setup Instructions

To get started with the project and run the examples, follow these setup steps:

### 1. Create a Virtual Environment
It's recommended to use a virtual environment to manage dependencies.
```bash
python3 -m venv myenv
```

### 2. Activate the Virtual Environment
Depending on your operating system, use the appropriate command:

**On macOS / Linux:**
```bash
source myenv/bin/activate
```

**On Windows:**
```bash
myenv\Scripts\activate
```

### 3. Install Dependencies
Install the core libraries along with any necessary dependencies.
```bash
pip install langgraph
pip install langchain
pip install python-dotenv
pip install openai
pip install langchain-huggingface
```

---

## 🧠 Key Learnings

- **Graphs, Nodes, and Edges**: Modeling logic as a graph rather than a linear chain.
- **State Management**: Using a shared state box that nodes can read from and write to.
- **Cycles and Loops**: Enabling agents to backtrack and retry until a goal is met.
- **Human-in-the-loop**: Incorporating human verification into automated workflows.

Happy Coding! 🤖✨
