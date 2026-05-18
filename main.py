from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Any
import uvicorn
import os
import shutil
import subprocess
from langchain_core.messages import HumanMessage
from agent_workflow_v3 import app as agent_app

app = FastAPI(title="AI Research Assistant API")

@app.get("/")
async def root():
    return {"status": "online", "message": "AI Research Assistant API is active"}

class ChatRequest(BaseModel):
    message: str
    k: int = 5
    thread_id: str = "default_thread" # New: for persistent memory

class ChatResponse(BaseModel):
    response: str
    retrieval_data: Optional[List[Any]] = None
    trace: Optional[List[str]] = None

@app.post("/chat/agent", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    try:
        config = {"configurable": {"thread_id": request.thread_id}}
        
        initial_state = {
            "messages": [HumanMessage(content=request.message)], 
            "k": request.k,
            "retrieval_data": [],
            "research_notes": [],
            "route": "",
            "relevance": "",
            "errors": [],
            "final_answer": ""
        }
        
        trace = []
        last_retrieval_data = []
        
        print(f"\n--- NEW PLAN-AND-EXECUTE SESSION: '{request.message}' (Thread: {request.thread_id}) ---")
        
        # Stream the graph with the thread configuration
        for output in agent_app.stream(initial_state, config=config):
            for node_name, state_update in output.items():
                trace.append(node_name)
                print(f"[Node: {node_name}] Running... Output keys: {list(state_update.keys())}")
                
                if "retrieval_data" in state_update:
                    last_retrieval_data = state_update["retrieval_data"]

        print("--- STREAM FINISHED ---")
        # Fetch the FINAL STATE from the memory checkpointer
        state_snapshot = agent_app.get_state(config)
        print(f"--- STATE SNAPSHOT FETCHED. Keys: {list(state_snapshot.values.keys()) if state_snapshot.values else 'None'}")
        
        response_text = state_snapshot.values.get("final_answer", "") if state_snapshot.values else ""
        print(f"--- RESPONSE TEXT FROM final_answer: {response_text[:50]}... ---")

        # Fallback to message history if final_answer is not set
        if not response_text:
            print("--- FALLBACK: Searching messages ---")
            full_history = state_snapshot.values.get("messages", []) if state_snapshot.values else []
            for m in reversed(full_history):
                is_tool_call = hasattr(m, "tool_calls") and m.tool_calls
                if m.content and not is_tool_call:
                    content_str = str(m.content)
                    if content_str.strip() and not (content_str.strip().startswith("{") and "name" in content_str):
                        response_text = content_str
                        break

        print(f"--- FINAL ANSWER READY: {response_text[:50]}... ---\n")

        return ChatResponse(
            response=response_text,
            retrieval_data=last_retrieval_data,
            trace=trace
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear_db")
async def clear_db():
    """Deletes the ChromaDB directory to start fresh."""
    try:
        if os.path.exists("chroma_db"):
            shutil.rmtree("chroma_db")
            return {"status": "success", "message": "Database cleared successfully."}
        return {"status": "info", "message": "Database directory does not exist."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest")
async def ingest_docs():
    """Triggers the ingestion script to process documents."""
    try:
        # Run ingest.py as a subprocess
        result = subprocess.run(["python3", "ingest.py"], capture_output=True, text=True)
        if result.returncode == 0:
            return {"status": "success", "message": "Ingestion completed.", "output": result.stdout}
        else:
            raise Exception(result.stderr)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
