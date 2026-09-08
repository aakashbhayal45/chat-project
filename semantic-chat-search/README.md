# Semantic Group Chat Search Engine

An AI-powered semantic search engine and chatbot for group chat messages, built with **Python 3.11**, **FastAPI**, **Sentence-Transformers**, **FAISS**, and **Vanilla JavaScript/HTML/CSS**.

Unlike standard keyword search, this system understands conversational intent, Hinglish (code-mixed Hindi-English), emojis, abbreviations, and context—allowing users to retrieve decision messages even when the search query and the target message share zero common words.

---

## 🌟 Problem Statement & Why Keyword Search Fails

In active group chats (e.g. WhatsApp, Slack, Telegram), critical group decisions are often made organically over long conversations. Traditional keyword search relies strictly on exact token matching, which fails in common real-world scenarios:

- **User Query**: `"When did we decide on the trip?"`
- **Target Chat Message**: `"haan bhai chalo Manali fix hai"`
- **Why Keyword Search Fails**: The query contains words like `decide`, `trip`, `when`. The message contains `haan`, `bhai`, `chalo`, `Manali`, `fix`. They have **zero common lexical words**, yet semantically mean the exact same decision!

Semantic vector search maps both queries and Hinglish chat messages into a high-dimensional dense embedding space, enabling concept matching, intent resolution, and context retrieval.

---

## 🏗️ Architecture & Technical Design

```
                     ┌─────────────────────────────────────────┐
                     │          Vanilla JS Frontend            │
                     │  Search Input / Context Views / Stats   │
                     └────────────────────┬────────────────────┘
                                          │ HTTP REST API
                                          ▼
                     ┌─────────────────────────────────────────┐
                     │            FastAPI Backend              │
                     └───────┬─────────────────────────┬───────┘
                             │                         │
                             ▼                         ▼
              ┌──────────────────────────┐  ┌──────────────────────────┐
              │      Query Parser        │  │     Data & Context       │
              │(Semantic/Attributed/Temp)│  │        Loader            │
              └──────────────┬───────────┘  └──────────┬───────────────┘
                             │                         │
                             ▼                         ▼
              ┌────────────────────────────────────────────────────────┐
              │                     Search Engine                      │
              │  - sentence-transformers/paraphrase-multilingual-MiniLM│
              │  - FAISS Vector Similarity Index (Flat Inner Product)  │
              │  - Deterministic Answer Generator                      │
              └────────────────────────────────────────────────────────┘
```

### Key Technical Subsystems

1. **Synthetic Chat Generator (`scripts/generate_chat.py`)**:
   - Generates 4,200+ realistic Hinglish and English chat messages across 8 participants (`Aman`, `Priya`, `Rahul`, `Neha`, `Ravi`, `Ankit`, `Simran`, `Karan`).
   - Spans a 6-month timeline with realistic timestamps, casual banter, food discussions, tech chatter, emojis, typos, and three long decision threads:
     - **Trip Decision Thread**: Destination negotiation ending in Manali.
     - **Budget Decision Thread**: Per-person expense agreement (8,000 INR).
     - **Date Decision Thread**: Schedule lock (April 18-22).
   - Fixed random seed (`42`) guarantees 100% reproducibility.

2. **Multilingual Embedding & FAISS Vector Search (`backend/search_engine.py`)**:
   - Uses `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` for code-mixed Hindi-English representation.
   - Enriches message vector representation using local conversational context windows (incorporating preceding messages).
   - FAISS `IndexFlatIP` performs fast Cosine Similarity vector retrieval.
   - Local disk persistence (`vector_store/faiss_index.bin` and `metadata.json`) ensures vector index is loaded instantaneously on server restart without re-computation.

3. **Multi-Type Query Intent Resolver (`backend/query_parser.py`)**:
   - **Semantic Search**: Default vector similarity match across all messages.
   - **Attributed Search**: Detects participant mentions (e.g. `"Priya"`, `"Rahul"`) and pre-filters search scope to messages sent by that sender.
   - **Temporal Search**: Parses time expressions (`"last month"`, `"March 2024"`, `"first week of April"`, `"around March 18"`) and filters candidate message timestamps prior to vector ranking.

4. **Context Retrieval**:
   - For every retrieved result, extracts 5 messages before and 5 messages after chronologically based on message index, giving users full context of how decisions were reached.

5. **Deterministic Answer Generator**:
   - Extracts top evidence message and formats a clear, non-hallucinated answer based strictly on retrieved text and timestamp without external LLM API dependencies.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn, Sentence-Transformers, FAISS (`faiss-cpu`), NumPy, Pydantic.
- **Frontend**: HTML5, CSS3 (Glassmorphism & CSS Variables), Vanilla JavaScript (ES6+ fetch API).
- **Storage**: JSON files (`chat.json`, `evaluation.json`, `results.json`, `metadata.json`) + Binary FAISS index (`faiss_index.bin`).

---

## 📊 Evaluation & Benchmark Methodology

The engine is benchmarked against **40 evaluation queries** defined in `dataset/evaluation.json`.
At least 8 queries feature zero lexical word overlap with the correct answer message.

Metrics tracked in `evaluation/evaluate.py`:
- **Top-1 Accuracy**: Percentage of queries where the exact target message is ranked #1.
- **Top-3 Accuracy**: Percentage of queries where the target message is in the Top-3 results.
- **Top-5 Accuracy**: Percentage of queries where the target message is in the Top-5 results.
- **Mean Reciprocal Rank (MRR)**: Average inverse rank ($\frac{1}{\text{rank}}$) of the target message across all queries.

---

## 🚀 Quickstart & Setup Instructions

### 1. Prerequisites
Ensure Python 3.11+ is installed.

### 2. Installation & Requirements
```bash
# Navigate to project directory
cd semantic-chat-search

# Create virtual environment (optional)
python -m venv venv
# On Windows: venv\Scripts\activate
# On Linux/macOS: source venv/bin/activate

# Install required Python packages
pip install -r backend/requirements.txt
```

### 3. Generate Synthetic Chat Dataset
```bash
python scripts/generate_chat.py
```

### 4. Run Benchmark Evaluation
```bash
python evaluation/evaluate.py
```

### 5. Launch FastAPI Backend & Frontend
```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
Then open your web browser at:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 📡 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves the web frontend interface (`index.html`) |
| `GET` | `/api/health` | Healthcheck and active vector count status |
| `GET` | `/api/search?q={query}` | Perform semantic / attributed / temporal search |
| `GET` | `/api/message/{message_id}` | Fetch specific message with 5-before & 5-after context |
| `GET` | `/api/stats` | Dataset statistics and evaluation benchmark metrics |
| `GET` | `/api/evaluation` | Full evaluation benchmark results JSON |

---

## 💡 Example Queries to Try

1. **Semantic (Trip Decision - Zero Overlap)**:
   - `"When did we decide on the trip?"`
   - `"Which destination did everyone finally agree on?"`
2. **Attributed (Sender Specific)**:
   - `"What did Priya say about the budget?"`
   - `"What did Rahul mention about tickets?"`
3. **Temporal (Date Filtered)**:
   - `"What did we discuss last month?"`
   - `"What happened in January 2024?"`

---

## 📈 Limitations & Future Work

- **Static FAISS Index**: Incremental message inserts can be added using dynamic FAISS index updates or a persistent vector DB (e.g. Qdrant / ChromaDB).
- **Advanced Temporal NLP**: Complex relative time parsing (e.g. "two weeks before Diwali") can be extended using `dateparser`.
- **Hybrid Search**: Combining BM25 keyword search with FAISS dense vector search via Reciprocal Rank Fusion (RRF) for ultimate precision.
