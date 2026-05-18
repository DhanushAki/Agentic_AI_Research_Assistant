# 🧠 AI Engineer 30-Day TURBO TRACK: AI Research Assistant

> **AGENT SYNC INSTRUCTION:** Whenever a new session starts, READ THIS FILE ENTIRELY. It contains the project DNA, the 30-day roadmap, and the current state of execution. Upon reading, you must immediately synchronize your context to the current "Day" and "Level" as defined in the Progress Tracker.

---

## 📅 THE 30-DAY TURBO ROADMAP (April 02 - May 01, 2026)

**Goal:** Become a production-ready AI Engineer by mastering Levels 2–5 in 30 days.

### Phase 1: Level 2 – Controlled Intelligence (Days 1–4) (COMPLETED)
*   **Focus:** API Architecture, System Prompting, Model Routing, Streamlit UI.
*   **Milestone:** Day 4 - Working UI Chatbot with Model Switching (Ollama/Groq).

### Phase 2: Level 3 – Intelligent Systems (Days 5–15) (NEXT)
*   **Focus:** RAG (Retrieval-Augmented Generation), Vector DBs (Chroma), LangGraph, Agents.
*   **Milestone:** Day 15 - Multi-agent Research Assistant with context-aware RAG.

### Phase 3: Level 4 – Scaling AI Systems (Days 16–22)
*   **Focus:** Productionizing, Docker, Redis Caching, Cloud Deployment (Render/Railway).
*   **Milestone:** Day 22 - Live deployed app with global caching.

### Phase 4: Level 5 – Strategic AI Operations (Days 23–30)
*   **Focus:** LLMOps, DeepEval (Testing), Langfuse (Observability), Cost Optimization.
*   **Milestone:** Day 30 - Production-grade portfolio-ready application.

---

## 🛠 PROJECT BLUEPRINT: Personal AI Research Assistant
*   **Backend:** FastAPI (Python)
*   **Frontend:** Streamlit
*   **LLMs:** Ollama (Local) + Groq (Cloud Backup - Free Tier)
*   **Orchestration:** LangChain + LangGraph
*   **Vector Database:** ChromaDB
*   **Caching:** Redis
*   **Validation:** DeepEval

---

## 🚀 CURRENT PROGRESS LOG

### Day 1: Environment & Local Inference (COMPLETED)
- **Actions:** Initialized project, setup venv, verified Ollama `qwen2.5-coder:7b` connection.

### Day 2: API Architecture (COMPLETED)
- **Actions:** Built FastAPI backend (`main.py`) with `/chat` POST endpoint. Verified via Swagger.

### Day 3: UI Development & ChatGPT Styling (COMPLETED)
- **Actions:**
    - Created `app.py` for a real-time Streamlit chat interface.
    - Implemented ChatGPT-style spatial alignment (User on Right, AI on Left).
    - Connected Frontend to Backend via `requests`.
- **Outcome:** Fully functional chat UI with a polished look.

### Day 4: Advanced Prompt Engineering & Model Routing (COMPLETED)
- **Actions:**
    - Implemented `ChatPromptTemplate` with a "Research Assistant" System Persona.
    - Added a model selector (Ollama vs. Groq) in the Streamlit sidebar.
    - Created a routing layer in FastAPI to handle different LLM providers.
- **Outcome:** Working UI Chatbot with seamless switching between local and cloud models.

### Day 5: RAG Foundations - Document Loading & Splitting (COMPLETED)
- **Actions:**
    - Installed `langchain-community`, `pypdf`, and `chromadb`.
    - Created `ingest.py` for document processing.
    - Implemented `/chat/rag` endpoint in FastAPI for context-aware retrieval.
    - Added RAG toggle and source display in Streamlit.
- **Outcome:** System can now answer questions based on local documents.

### Day 6: Advanced RAG - Vector DB Optimization & Persistence (COMPLETED)
- **Actions:**
    - Upgraded `ingest.py` with `PyPDFLoader` and `TextLoader`.
    - Implemented incremental loading using unique Chunk IDs to prevent duplicates.
    - Added `/ingest` and `/clear_db` endpoints to FastAPI.
    - Added Database Management buttons (Refresh/Clear) to Streamlit UI.
    - **Optimized for 1B model**: Switched to a "Blunt Prompt" and increased context retrieval to `k=5` to reduce hallucinations.
- **Outcome:** Robust document management system with PDF support and improved accuracy on small local LLMs.

### Day 7: Vector DB Exploration & AI Forensics (COMPLETED)
- **The Challenge:** Encountered a "Vector Freeze" where all search queries returned identical similarity scores (0.6184).
- **The Investigation:**
    - Developed `diagnose_db.py` to verify database persistence.
    - Implemented **Vector Fingerprinting** to prove the Ollama embedding server was returning static data.
    - Identified a "Sticky State" issue in the Streamlit UI.
- **The Solution:**
    - Pivoted from `nomic-embed-text` to `qwen2.5-coder:7b` for generating embeddings to bypass the server freeze.
    - Implemented **Cache-Busting** (`?cb=timestamp`) and **Streamlit Forms** to ensure fresh UI updates.
    - Reduced `chunk_size` to 300 for higher retrieval precision.
- **Outcome:** A fully transparent and tunable Semantic Search Lab where raw mathematical distances (L2) can be audited in real-time.

### Day 8: LangGraph Fundamentals & Tool Integration (COMPLETED)
- **Actions:**
    - Installed and configured `langgraph`.
    - Created `agent_workflow.py` to establish a basic `StateGraph`.
    - Extracted RAG logic into a reusable `Tool` in `rag_tool_function.py`.
    - Integrated the RAG tool into the agent node with conditional LLM-based answering.
    - Updated `main.py` and `app.py` to support Agentic Mode, forensic data retrieval, and full database administration.
- **Outcome:** A functioning end-to-end AI Research platform with forensics and administrative controls.

### Day 9: ReAct Loop & Web Horizons (COMPLETED)
- **Actions:**
    - **ReAct Refactor:** Transformed the agent into a dynamic loop (Model -> Tool -> Model) using LangGraph.
    - **Web Search Tool:** Integrated `DuckDuckGoSearchRun` to allow the agent to fetch real-time data.
    - **Parallel Reasoning:** Developed a robust JSON extraction layer using `json.JSONDecoder` to handle multiple, nested tool calls from local LLMs.
    - **Thinking UI:** Updated Streamlit with a `st.status` "Reasoning Trace" to show the agent's step-by-step logic (e.g., Node: Agent -> Node: Tools).
    - **Memory Persistence:** (In Progress) Implementing `MemorySaver` for multi-turn conversation threads.
- **Outcome:** A true reasoning agent capable of combining local document facts with real-time web research in a single turn.

### Day 10: Persistent Memory with MongoDB (COMPLETED)
- **Actions:**
    - Installed `pymongo` and `langgraph-checkpoint-mongodb`.
    - Switched from in-memory `MemorySaver` to `MongoDBSaver` in `agent_workflow.py`.
    - Verified that conversation history persists even after server restarts and across independent script runs.
    - Successfully tested the agent's ability to remember user-provided facts (e.g., "My name is Raj") using a unique `thread_id`.
- **Outcome:** Conversation history is now production-ready, stored in a durable MongoDB database instead of volatile RAM.

#### 🧠 TECHNICAL DEEP DIVE: The Architecture of Memory
By moving to **MongoDBSaver**, the system now has a persistent "Hard Drive" for AI thoughts.
1.  **Storage Vault (MongoDB)**: Stores serialized snapshots (checkpoints) of the `AgentState`. Even if the FastAPI server restarts, the data is safe on disk.
2.  **The Librarian (MongoDBSaver)**: Acts as the bridge between LangGraph's Python objects and MongoDB's BSON format.
3.  **The Library Card (thread_id)**: A unique UUID generated by Streamlit that ensures User A never sees User B's history, even though they share the same database.
4.  **Data Flow**:
    - `UI` -> `FastAPI` -> `thread_id` -> `LangGraph`.
    - `LangGraph` queries MongoDB: *"Give me everything for thread_id X"*.
    - `Ollama` receives `[History] + [New Question]`.
    - `LangGraph` saves the new state back to MongoDB automatically.

### Day 11: Multi-Agent Architectures - Plan-and-Execute (COMPLETED)
- **Actions:**
    - **Architectural Shift:** Refactored the single ReAct loop into a **Plan-and-Execute** multi-agent pattern.
    - **Planner Node:** Implemented a node that decomposes complex queries into a structured 3-step research plan.
    - **Re-planner Node:** Added a supervisor node that tracks progress, updates the plan dynamically, and synthesizes final answers.
    - **Tool Assertiveness:** Optimized the executor agent's prompt to ensure rigorous tool usage for each plan step, preventing "hallucinated knowledge" bypasses.
- **Outcome:** The system can now handle complex, multi-part research tasks by breaking them down into verifiable sub-steps.

### Day 12: Reflection Pattern - Analyze, Refactor & Attribution (COMPLETED)
- **Actions:**
    - **Architecture Upgrade:** Enhanced the Plan-and-Execute workflow with a **Reflection Loop**.
    - **Analyze Node:** Added a quality auditor that critiques research drafts for hallucinations, missing data, and poor attribution.
    - **Refactor Node:** Implemented a final synthesis layer that applies critiques and enforces **Harvard-style attribution** ([Source: Local/Web]).
    - **State Expansion:** Tracked `draft` and `critique` separately in `AgentState` for full transparency.
- **Outcome:** Significantly higher reliability and verifiability in research reports.

### Day 13: Parallel Multi-Agent Research & Turbo Consolidation (COMPLETED)
- **Actions:**
    - **Parallel Shift:** Refactored sequential execution into a parallel "Fork-Join" architecture using a Supervisor.
    - **Turbo Consolidation:** Merged synthesis and reflection nodes into a single high-speed node to optimize for local LLM inference speeds.
    - **Context Capping:** Implemented strict truncation in researcher nodes to prevent LLM "context choking."
    - **UI Trace Update:** Added parallel node visualization to the Streamlit Reasoning Trace.
- **Outcome:** Drastically faster response times (70% reduction in turns) without sacrificing research depth or attribution quality.

### Day 14: Semantic Routing & Resilient Fallback (COMPLETED)
- **Actions:**
    - **Semantic Router:** Implemented a router node that classifies queries (Local, Web, Both).
    - **Resilient Fallback:** Developed a "Silent Fail" logic where the system automatically pivots to web search if local documents are empty.
- **Outcome:** A highly reliable research flow that handles missing data without hallucinating.

### Day 15: Multi-agent Research Assistant & Final Level 3 Milestone (COMPLETED)
- **Actions:**
    - **Architecture Sync:** Verified and solidified the "Turbo Parallel" Multi-Agent architecture.
    - **Orchestration:** Refined the collaboration between specialized agents (Dispatcher, Local Researcher, Web Researcher).
    - **Context Awareness:** Confirmed deep context-aware synthesis using MongoDB persistent history.
- **Outcome:** Achieved the Level 3 milestone of a production-ready, intelligent multi-agent research platform.

### Day 17: Containerization & Deployment Refinement (COMPLETED)
- **Actions:**
    - Refactored `agent_workflow_v3.py` to use `MONGODB_URL` environment variable for database persistence.
    - Enhanced `docker-compose.yml` with healthchecks and specific network bridging.
    - Resolved critical dependency conflicts (`ddgs` package rename) and optimized Docker build timeouts.
    - Standardized environment management with `.env.example`.
    - **Cleanup:** Purged obsolete versions (v1, v2) and consolidated testing logic into `/tests/test_suite.py`.
- **Outcome:** Production-ready container stack fully operational on local Docker environment with a lean, organized workspace.

---

=== PROGRESS TRACKER ===

Current Day: 17 / 30

Progress %: 56.6% complete

Current Level: Level 4 (Scaling AI Systems)

Project Status: [X] Level 2 | [X] Level 3 | [X] Level 4 (Day 17 Complete) | [ ] Level 5

Milestones Achieved:
- Level 2: Controlled Intelligence (UI + Model Routing) COMPLETED.
- Day 7: **Deep Debugging & Vector Forensics COMPLETED.**
- Day 8: **LangGraph Agent with RAG Tool Integration COMPLETED.**
- Day 9: **ReAct Reasoning Loop & Web Search Integration COMPLETED.**
- Day 11: **Plan-and-Execute Multi-Agent Architecture COMPLETED.**
- Day 12: **Reflection Pattern (Analyze, Refactor, Attribution) COMPLETED.**
- Day 13: **Parallel Multi-Agent Research & Turbo Consolidation COMPLETED.**

Next Milestone: Day 22 - Live deployed app with global caching.

Today’s Status: Refined Docker architecture and environment handling for production readiness.
