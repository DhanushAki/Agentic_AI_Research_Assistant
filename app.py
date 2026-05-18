import streamlit as st
import requests
import pandas as pd
import uuid
import os

# Get API URL from environment variable, default to localhost for non-docker runs
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="AI Research Assistant", page_icon="🧠", layout="wide")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_retrieval" not in st.session_state:
    st.session_state.last_retrieval = None
if "last_trace" not in st.session_state:
    st.session_state.last_trace = None
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# --- SIDEBAR (Controls & DB Management) ---
with st.sidebar:
    st.title("Settings & Admin")
    
    # Connection Diagnostic
    try:
        # Simple ping check to backend (using a timeout)
        requests.get(f"{API_URL}/", timeout=2)
        st.success(f"✅ Connected to Backend: `{API_URL}`")
    except Exception:
        st.error(f"❌ Backend unreachable at `{API_URL}`")

    st.write(f"Session Thread: `{st.session_state.thread_id[:8]}...`")
    
    # 1. Chat Management
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_retrieval = None
        st.session_state.last_trace = None
        st.session_state.thread_id = str(uuid.uuid4()) # New thread for fresh start
        st.rerun()
    
    st.divider()
    
    # 2. Agent & Search Settings
    st.subheader("Search Lab Controls")
    agent_mode = st.toggle("Enable Agentic Mode", value=True)
    top_k = st.slider("Top-K (Similarity Count)", 1, 10, 5)
    
    st.divider()
    
    # 3. Vector Database Management
    st.subheader("Database Management")
    
    if st.button("🔄 Refresh Database", help="Ingests fresh document chunks", use_container_width=True):
        with st.spinner("Ingesting documents..."):
            try:
                res = requests.post(f"{API_URL}/ingest")
                if res.status_code == 200:
                    st.success("Ingestion Complete!")
                else:
                    st.error("Ingestion Failed.")
            except Exception as e:
                st.error(f"Error: {e}")

    if st.button("🔥 Clear Vector DB", help="Deletes all stored embeddings", use_container_width=True):
        try:
            res = requests.post(f"{API_URL}/clear_db")
            if res.status_code == 200:
                st.warning("Vector Store Deleted.")
            else:
                st.error("Clear Failed.")
        except Exception as e:
            st.error(f"Error: {e}")

# --- MAIN UI ---
st.title("🧠 Personal AI Research Assistant")
st.caption("Level 3: Intelligent Systems - LangGraph ReAct Loop & Search Lab")

# Display History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input
if prompt := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        full_response = "No response."
        retrieval_data = []
        
        # 1. Reasoning Status (Reasoning Trace)
        with st.status("Agent is thinking...", expanded=True) as status:
            try:
                payload = {
                    "message": prompt, 
                    "k": top_k,
                    "thread_id": st.session_state.thread_id
                }
                response_raw = requests.post(f"{API_URL}/chat/agent", json=payload, timeout=300)
                response = response_raw.json()
                
                trace = response.get("trace", [])
                for i, node in enumerate(trace):
                    if node == "router":
                        st.write("🚦 **Step:** Routing query to the best source...")
                    elif node == "local_researcher":
                        st.write("📂 **Step:** Searching local documents...")
                    elif node == "web_researcher":
                        st.write("🌐 **Step:** Searching the web (Fallback/Expansion)...")
                    elif node == "synthesizer":
                        st.write("🧩 **Step:** Synthesizing final answer...")
                    else:
                        st.write(f"✔️ Node `{node}` completed.")
                
                status.update(label="Research & Reflection Complete!", state="complete", expanded=False)
                
                # Extract data for use OUTSIDE the status box
                full_response = response.get("response", "No response found in API.")
                retrieval_data = response.get("retrieval_data", [])

            except Exception as e:
                status.update(label="Research Failed!", state="error")
                st.error(f"Error: {str(e)}")
                full_response = "Error occurred."
                retrieval_data = []

        # 2. Display Final Answer (OUTSIDE status box)
        st.markdown(full_response)
        
        # Update Session State
        st.session_state.last_retrieval = retrieval_data
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
        # 3. Forensic Panel (Search Lab)
        if st.session_state.last_retrieval:
            with st.expander("🔍 Semantic Search Lab (Forensics)", expanded=True):
                st.write("### Raw Vector Similarity Scores (L2 Distance)")
                df = pd.DataFrame(st.session_state.last_retrieval)
                st.dataframe(df.style.highlight_min(subset=['score'], color='#90EE90'), use_container_width=True)
                
                for i, chunk in enumerate(st.session_state.last_retrieval):
                    st.text_area(f"Chunk {i+1} (Score: {chunk['score']})", chunk['content'], height=100)
