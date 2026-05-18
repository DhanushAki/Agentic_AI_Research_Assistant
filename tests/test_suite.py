import os
import requests
from langchain_core.messages import HumanMessage
from agent_workflow_v3 import app as agent_app

# --- 1. LLM Connectivity Test ---
def test_llm():
    print("\n--- TEST: LLM Connectivity ---")
    from langchain_ollama import ChatOllama
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    llm = ChatOllama(model="qwen2.5-coder:7b", base_url=ollama_base_url)
    try:
        res = llm.invoke("Hello, are you online?")
        print(f"✅ LLM Response: {res.content[:50]}...")
    except Exception as e:
        print(f"❌ LLM Failed: {e}")

# --- 2. RAG Retrieval Test ---
def test_retrieval():
    print("\n--- TEST: RAG Retrieval ---")
    from rag_tool_function import search_documents
    try:
        context, forensics = search_documents.invoke({"query": "Dhanush", "k": 2})
        if context:
            print(f"✅ Retrieval Success! Found {len(forensics)} chunks.")
        else:
            print("⚠️ Retrieval returned no context (DB might be empty).")
    except Exception as e:
        print(f"❌ Retrieval Failed: {e}")

# --- 3. Full Agent Workflow Test ---
def test_agent():
    print("\n--- TEST: Full Agent Workflow ---")
    config = {"configurable": {"thread_id": "test_thread"}}
    initial_state = {
        "messages": [HumanMessage(content="Who is Dhanush?")],
        "k": 3,
        "retrieval_data": [],
        "research_notes": [],
        "route": "",
        "errors": [],
        "final_answer": ""
    }
    try:
        for output in agent_app.stream(initial_state, config=config):
            for node, state in output.items():
                print(f"📍 Node: {node}")
        
        final_state = agent_app.get_state(config)
        answer = final_state.values.get("final_answer")
        print(f"✅ Agent Final Answer: {answer[:100]}...")
    except Exception as e:
        print(f"❌ Agent Workflow Failed: {e}")

if __name__ == "__main__":
    test_llm()
    test_retrieval()
    test_agent()
