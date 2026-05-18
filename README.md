# 🧠 AI Research Assistant

A production-grade, multi-agent AI research platform built with LangGraph, FastAPI, and Streamlit. Optimized for local LLMs (Ollama) with persistent memory and real-time forensics.

## 🚀 Quick Start (Docker)

Ensure you have **Docker Desktop** installed and **Ollama** running on your host machine.

1. **Configure Environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your keys (e.g., GROQ_API_KEY)
   ```

2. **Launch the Stack:**
   ```bash
   # Standard start
   docker compose up --build

   # Fresh start (ignores cache and rebuilds everything)
   docker compose build --no-cache && docker compose up
   ```

3. **Access the App:**
   *   **Frontend (UI):** [http://localhost:8501](http://localhost:8501)
   *   **Backend (API/Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)

## 🏗️ Architecture
*   **Frontend:** Streamlit UI with "Reasoning Trace" and "Forensic Lab."
*   **Backend:** FastAPI orchestrating a LangGraph `agent_workflow_v3` (Parallel Multi-Agent).
*   **Database:** MongoDB (Persistent Memory) + ChromaDB (Vector Store).
*   **Orchestration:** LangGraph with Semantic Routing and Parallel Research.

## 🧹 Maintenance & Space Management

### Stop and Clean Project
```bash
# Stop containers
docker compose stop

# Stop and remove containers + networks
docker compose down

# Stop and remove containers + networks + ALL volumes (Wipes Database!)
docker compose down -v
```

### Reclaim Disk Space
If your machine is running low on space due to old Docker builds:
```bash
# Remove unused data (safe)
docker system prune -f

# The "Deep Clean" (Removes all unused images, volumes, and cache)
docker system prune -a --volumes -f
```

### Manual Database Reset
To wipe the local vector database without stopping Docker:
```bash
rm -rf ./chroma_db/*
```

## 🧪 Testing
```bash
# Run the test suite (requires local python environment)
python3 -m tests.test_suite
```
