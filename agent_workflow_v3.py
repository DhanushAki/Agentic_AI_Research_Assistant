from typing import TypedDict, Annotated, List, Any, Tuple, Union
import operator
import json
import re
import os
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from rag_tool_function import search_documents
from web_search_tool import search_web
from pymongo import MongoClient
from langgraph.checkpoint.mongodb import MongoDBSaver

# 1. State Definition
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    k: int
    retrieval_data: Annotated[List[Any], operator.add] 
    research_notes: Annotated[List[str], operator.add] 
    route: str # 'local', 'web', 'both'
    errors: List[str] 
    final_answer: str

# 2. Setup LLM
ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
llm = ChatOllama(model="qwen2.5-coder:7b", base_url=ollama_base_url)

# 3. Node: Router
def router(state: AgentState):
    print("--- NODE: ROUTER ---")
    # Use the LATEST human message
    query = state["messages"][-1].content
    prompt = f"Categorize query: '{query}'. Reply ONLY 'local' (for files/my info), 'web' (for news/general), or 'both'. Response:"
    response = llm.invoke([HumanMessage(content=prompt)])
    decision = response.content.strip().lower()
    if 'local' in decision: decision = 'local'
    elif 'web' in decision: decision = 'web'
    else: decision = 'both'
    return {"route": decision}

# 4. Node: Local Researcher
def local_researcher(state: AgentState):
    print("--- NODE: LOCAL RESEARCHER ---")
    query = state["messages"][-1].content
    try:
        context, forensics = search_documents.invoke({"query": query, "k": state.get("k", 5)})
        if not context or "No relevant documents" in context:
            return {"research_notes": ["LOCAL: Empty"]}
        return {"research_notes": [f"LOCAL_DATA: {context[:3000]}"], "retrieval_data": forensics}
    except Exception as e:
        return {"errors": [f"Local Error: {str(e)}"], "research_notes": ["LOCAL: Error"]}

# 5. Node: Web Researcher
def web_researcher(state: AgentState):
    print("--- NODE: WEB RESEARCHER ---")
    query = state["messages"][-1].content
    try:
        result = search_web.invoke({"query": query})
        return {"research_notes": [f"WEB_DATA: {result[:3000]}"]}
    except Exception as e:
        return {"errors": [f"Web Error: {str(e)}"]}

# 6. Node: Synthesizer
def synthesizer(state: AgentState):
    print("--- NODE: SYNTHESIZER ---")
    query = state["messages"][-1].content
    
    # Separate notes into categories for the prompt
    local_notes = [n for n in state.get("research_notes", []) if "LOCAL_DATA" in n or "search_document" in n]
    web_notes = [n for n in state.get("research_notes", []) if "WEB_DATA" in n]
    
    prompt = f"""USER QUERY: {query}

--- DATA SOURCES ---
<LOCAL_DOCUMENTS>
{chr(10).join(local_notes) if local_notes else "No relevant local documents found."}
</LOCAL_DOCUMENTS>

<WEB_SEARCH_RESULTS>
{chr(10).join(web_notes) if web_notes else "No web results found."}
</WEB_SEARCH_RESULTS>

--- INSTRUCTIONS ---
1. Identify the 'Primary Subject' in <LOCAL_DOCUMENTS>. 
2. If the user asks about themselves or a name found in local documents, use <LOCAL_DOCUMENTS> as the ABSOLUTE TRUTH.
3. If <LOCAL_DOCUMENTS> says Dhanush is an Engineer, DO NOT say he is an Actor, even if you 'know' a famous actor with that name.
4. Clearly state if the local person is different from the person found on the web.
5. Use [Source: Local] or [Source: Web].

FINAL RESPONSE:"""
    
    messages = [SystemMessage(content="You are a strict data auditor. You prioritize local evidence over general knowledge.")] + [HumanMessage(content=prompt)]
    response = llm.invoke(messages)
    
    return {"final_answer": response.content, "messages": [response]}

# 8. Graph Construction
workflow = StateGraph(AgentState)
workflow.add_node("router", router)
workflow.add_node("local_researcher", local_researcher)
workflow.add_node("web_researcher", web_researcher)
workflow.add_node("synthesizer", synthesizer)

workflow.set_entry_point("router")

def route_after_router(state: AgentState):
    if state["route"] == "web": return "web_researcher"
    return "local_researcher"

workflow.add_conditional_edges("router", route_after_router)

def route_after_local(state: AgentState):
    notes = "".join(state.get("research_notes", []))
    # If local search failed or returned nothing, OR if route is 'both'
    if "LOCAL: Empty" in notes or "LOCAL: Error" in notes or state.get("route") == "both":
        return "web_researcher"
    return "synthesizer"

workflow.add_conditional_edges("local_researcher", route_after_local)
workflow.add_edge("web_researcher", "synthesizer")
workflow.add_edge("synthesizer", END)

# MongoDB Persistence Setup
mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
mongodb_client = MongoClient(mongodb_url)
memory = MongoDBSaver(mongodb_client)
app = workflow.compile(checkpointer=memory)
