import os
import json
import sys
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Ensure root path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.search_engine import SearchEngine
from backend.models import (
    SearchResponse,
    SingleMessageResponse,
    StatsResponse,
    EvaluationResponse
)

app = FastAPI(
    title="Semantic Group Chat Search API",
    description="Vector similarity & semantic search engine for Hinglish group chats",
    version="1.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global SearchEngine singleton instance
search_engine: SearchEngine = None

@app.on_event("startup")
def startup_event():
    global search_engine
    print("Initializing Search Engine service on startup...")
    data_path = os.path.join("dataset", "chat.json")
    vector_dir = os.path.join("vector_store")
    search_engine = SearchEngine(data_path=data_path, vector_store_dir=vector_dir)
    print("Search Engine service ready!")

# ─── API Routes (must be defined BEFORE the static mount) ────────────────────

@app.get("/api/health")
def get_health():
    if search_engine is None:
        raise HTTPException(status_code=503, detail="Search Engine service initializing")
    return {
        "status": "ok",
        "messages_count": len(search_engine.data_loader.messages),
        "index_vectors": search_engine.index.ntotal if search_engine.index else 0
    }

@app.get("/api/search", response_model=SearchResponse)
def search_messages(q: str = Query(..., description="User search query")):
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="Search query parameter 'q' cannot be empty")
    try:
        results = search_engine.search(q.strip(), top_k=5)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search execution error: {str(e)}")

@app.get("/api/message/{message_id}", response_model=SingleMessageResponse)
def get_message(message_id: int):
    msg = search_engine.data_loader.get_message_by_id(message_id)
    if not msg:
        raise HTTPException(status_code=404, detail=f"Message ID {message_id} not found")
    ctx_before, ctx_after = search_engine.data_loader.get_context(message_id, before_count=5, after_count=5)
    return {
        "message_id": msg["id"],
        "sender": msg["sender"],
        "message": msg["message"],
        "timestamp": msg["timestamp"],
        "context_before": ctx_before,
        "context_after": ctx_after
    }

@app.get("/api/stats", response_model=StatsResponse)
def get_stats():
    stats_data = search_engine.data_loader.get_stats()
    eval_summary = None
    eval_file = os.path.join("evaluation", "results.json")
    if os.path.exists(eval_file):
        with open(eval_file, "r", encoding="utf-8") as f:
            eval_data = json.load(f)
            eval_summary = {
                "top1_accuracy": eval_data.get("top1_accuracy", 0.0),
                "top3_accuracy": eval_data.get("top3_accuracy", 0.0),
                "top5_accuracy": eval_data.get("top5_accuracy", 0.0),
                "mrr": eval_data.get("mrr", 0.0),
                "total_queries": eval_data.get("total_queries", 0)
            }
    return {
        "total_messages": stats_data.get("total_messages", 0),
        "participants_count": stats_data.get("participants_count", 0),
        "participants": stats_data.get("participants", []),
        "date_range": stats_data.get("date_range", "N/A"),
        "embedding_model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "vector_search": "FAISS (Flat Inner Product)",
        "evaluation_summary": eval_summary
    }

@app.get("/api/evaluation")
def get_evaluation():
    eval_file = os.path.join("evaluation", "results.json")
    if not os.path.exists(eval_file):
        raise HTTPException(status_code=404, detail="Evaluation results.json not found. Run evaluation/evaluate.py first.")
    with open(eval_file, "r", encoding="utf-8") as f:
        return json.load(f)

# ─── Serve Frontend (MUST be LAST — catches all non-API routes) ──────────────
# StaticFiles with html=True auto-serves index.html for "/" and "/index.html"
frontend_dir = os.path.join("frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
