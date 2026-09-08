import os
import json
import numpy as np
import faiss
from datetime import datetime
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from backend.data_loader import DataLoader
from backend.query_parser import QueryParser

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
INDEX_PATH = "vector_store/faiss_index.bin"
METADATA_PATH = "vector_store/metadata.json"

class SearchEngine:
    def __init__(self, data_path: str = "dataset/chat.json", vector_store_dir: str = "vector_store"):
        self.data_loader = DataLoader(data_path)
        self.query_parser = QueryParser(self.data_loader.get_participants())
        self.vector_store_dir = vector_store_dir
        self.index_path = os.path.join(vector_store_dir, "faiss_index.bin")
        self.metadata_path = os.path.join(vector_store_dir, "metadata.json")
        
        self.model = None
        self.index = None
        self.metadata: List[Dict[str, Any]] = []

        self._initialize()

    def _get_model(self):
        if self.model is None:
            print(f"Loading embedding model: {MODEL_NAME}...")
            try:
                self.model = SentenceTransformer(MODEL_NAME)
            except Exception as e:
                print(f"Error loading {MODEL_NAME}: {e}. Trying fallback model...")
                self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        return self.model

    def _initialize(self):
        os.makedirs(self.vector_store_dir, exist_ok=True)
        
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            print("Loading FAISS index and metadata from local cache...")
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
            
            if len(self.metadata) == len(self.data_loader.messages):
                print(f"FAISS index loaded successfully with {self.index.ntotal} vectors.")
                return
            print("Cached metadata size mismatch. Rebuilding FAISS index...")

        self.build_index()

    def build_index(self):
        print("Building FAISS index for chat messages...")
        model = self._get_model()
        
        messages = self.data_loader.messages
        texts = [f"{m['sender']}: {m['message']}" for m in messages]

        print(f"Generating embeddings for {len(texts)} messages...")
        embeddings = model.encode(texts, batch_size=64, show_progress_bar=True, normalize_embeddings=True)
        embeddings = np.array(embeddings, dtype=np.float32)

        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Cosine Similarity
        self.index.add(embeddings)

        self.metadata = []
        for idx, m in enumerate(messages):
            self.metadata.append({
                "faiss_id": idx,
                "message_id": m["id"],
                "sender": m["sender"],
                "message": m["message"],
                "timestamp": m["timestamp"]
            })

        print("Saving FAISS index and metadata to local storage...")
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
            
        print("Index build complete!")

    def search(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        if not query or not query.strip():
            raise ValueError("Query string cannot be empty.")

        parse_res = self.query_parser.parse(query)
        q_type = parse_res["query_type"]
        sender_filter = parse_res["sender"]
        start_dt = parse_res["start_date"]
        end_dt = parse_res["end_date"]

        model = self._get_model()
        query_vector = model.encode([query], normalize_embeddings=True)
        query_vector = np.array(query_vector, dtype=np.float32)

        # Retrieve top candidates via FAISS (use large search_k if filtering by sender/date)
        search_k = min(self.index.ntotal, 1000 if (sender_filter or start_dt or end_dt) else top_k * 5)
        scores, faiss_indices = self.index.search(query_vector, search_k)
        
        scores = scores[0]
        faiss_indices = faiss_indices[0]

        filtered_results = []
        for score, f_idx in zip(scores, faiss_indices):
            if f_idx < 0 or f_idx >= len(self.metadata):
                continue
            
            meta = self.metadata[f_idx]
            
            # Attributed sender filter
            if sender_filter and meta["sender"].lower() != sender_filter.lower():
                continue

            # Temporal timestamp filter
            if start_dt or end_dt:
                msg_dt = datetime.fromisoformat(meta["timestamp"])
                if start_dt and msg_dt < start_dt:
                    continue
                if end_dt and msg_dt > end_dt:
                    continue

            ctx_before, ctx_after = self.data_loader.get_context(meta["message_id"], before_count=5, after_count=5)

            filtered_results.append({
                "message_id": meta["message_id"],
                "sender": meta["sender"],
                "message": meta["message"],
                "timestamp": meta["timestamp"],
                "score": float(score),
                "context_before": ctx_before,
                "context_after": ctx_after
            })

            if len(filtered_results) >= top_k:
                break

        # Fallback if filtered results are empty
        if not filtered_results:
            for score, f_idx in zip(scores[:top_k], faiss_indices[:top_k]):
                if f_idx < 0 or f_idx >= len(self.metadata):
                    continue
                meta = self.metadata[f_idx]
                ctx_before, ctx_after = self.data_loader.get_context(meta["message_id"])
                filtered_results.append({
                    "message_id": meta["message_id"],
                    "sender": meta["sender"],
                    "message": meta["message"],
                    "timestamp": meta["timestamp"],
                    "score": float(score),
                    "context_before": ctx_before,
                    "context_after": ctx_after
                })

        answer = self.generate_answer(query, filtered_results, q_type)

        return {
            "query": query,
            "query_type": q_type,
            "answer": answer,
            "results": filtered_results
        }

    def generate_answer(self, query: str, results: List[Dict[str, Any]], query_type: str) -> str:
        if not results:
            return "I couldn't find enough evidence in the chat history."

        top_match = results[0]
        score = top_match["score"]

        if score < 0.20:
            return "I couldn't find enough evidence in the chat history."

        sender = top_match["sender"]
        message = top_match["message"]
        ts_str = top_match["timestamp"]
        
        try:
            dt = datetime.fromisoformat(ts_str)
            formatted_date = dt.strftime("%B %d, %Y at %I:%M %p")
        except Exception:
            formatted_date = ts_str

        query_lower = query.lower()

        if "decide" in query_lower or "destination" in query_lower or "trip" in query_lower or "settle" in query_lower or "place" in query_lower or "holiday" in query_lower:
            return f"The group appears to have finalized the trip destination when {sender} confirmed '{message}' on {formatted_date}."

        if "budget" in query_lower or "cost" in query_lower or "expenditure" in query_lower or "amount" in query_lower:
            return f"The budget decision was finalized when {sender} stated '{message}' on {formatted_date}."

        if "date" in query_lower or "when" in query_lower or "days" in query_lower or "time" in query_lower or "window" in query_lower:
            return f"The schedule was confirmed when {sender} posted '{message}' on {formatted_date}."

        if query_type == "attributed":
            return f"{sender} said: '{message}' on {formatted_date}."

        return f"Based on chat evidence, {sender} confirmed: '{message}' on {formatted_date}."
