# 🤖 Data Intelligence Platform

> An end-to-end AI-powered data analysis platform — upload any dataset, ask questions in natural language, and get intelligent answers powered by RAG, LLMs, and vector search.

## ✨ Key Features

- **Natural Language Querying** — Ask questions about your data in plain English, no SQL required
- **RAG Pipeline** — Retrieval-Augmented Generation using Qdrant vector search for accurate, context-aware answers
- **MLflow Observability** — Every query tracked with latency, similarity scores, and success metrics
- **Prefect Orchestration** — Automated data ingestion, cleaning, and embedding generation pipelines
- **Multi-format Support** — Upload CSV and Excel files up to 200MB
- **Real-time Analytics** — Live dashboard showing query patterns, performance metrics, and system health
- **Production Ready** — Dockerized, CI/CD with GitHub Actions, deployed on Render

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                           │
│                    Streamlit (Port 8501)                        │
│          Upload Data │ Ask Questions │ View Analytics           │
└─────────────────────────────┬───────────────────────────────────┘
                               │ HTTP
┌─────────────────────────────▼───────────────────────────────────┐
│                         API LAYER                               │
│                    FastAPI (Port 8000)                          │
│           /upload  │  /query  │  /stats  │  /files             │
└──────┬──────────────┬─────────┬──────────────────────────────────┘
       │              │         │
┌──────▼──────┐ ┌─────▼─────────▼──────┐ ┌─────────────────────┐
│    DATA     │ │     LLM / RAG         │ │      MLOps          │
│  PIPELINE   │ │      LAYER            │ │      LAYER          │
│             │ │                       │ │                     │
│ • Prefect   │ │ • Groq / Ollama LLM   │ │ • MLflow Tracking   │
│   Flows     │ │ • LangChain RAG       │ │ • Latency Metrics   │
│ • Ingestion │ │ • Vector Search       │ │ • Success Rates     │
│ • Cleaning  │ │ • Prompt Engineering  │ │ • Query Analytics   │
│ • Embedding │ │                       │ │                     │
└──────┬──────┘ └────────┬──────────────┘ └─────────────────────┘
       │                 │
┌──────▼─────────────────▼────────────────────────────────────────┐
│                       STORAGE LAYER                             │
│    PostgreSQL (metadata)  │  Qdrant (vector embeddings)         │
└─────────────────────────────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                     DEPLOYMENT LAYER                            │
│         Docker Compose (local)  │  Render + Qdrant Cloud        │
│         GitHub Actions CI/CD    │  (production)                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | Streamlit + Plotly | Interactive UI + analytics charts |
| **Backend** | FastAPI + Uvicorn | REST API + async request handling |
| **LLM** | Groq (prod) / Ollama (local) | Language model inference |
| **RAG** | LangChain + sentence-transformers | Retrieval-augmented generation |
| **Vector DB** | Qdrant | Semantic similarity search |
| **Database** | PostgreSQL + SQLAlchemy | File metadata storage |
| **Pipelines** | Prefect | Data orchestration |
| **MLOps** | MLflow | Experiment tracking + observability |
| **Containers** | Docker + Docker Compose | Containerization |
| **CI/CD** | GitHub Actions | Automated testing |
| **Deployment** | Render + Qdrant Cloud | Production hosting |

---

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

**Prerequisites:** [Docker Desktop](https://docker.com/products/docker-desktop)

```bash
# Clone the repository
git clone https://github.com/PavanKalyanMaturi/data-intelligence-platform.git
cd data-intelligence-platform

# Start all services with one command
docker-compose up --build
```

Services will be available at:
| Service | URL |
|---|---|
| Streamlit UI | http://localhost:8501 |
| FastAPI Docs | http://localhost:8000/docs |
| MLflow UI | http://localhost:5000 |
| Qdrant Dashboard | http://localhost:6333/dashboard |

---

### Option 2: Local Development (4 Terminals)

**Prerequisites:** Python 3.11, PostgreSQL, Docker (for Qdrant), Ollama

**Step 1: Clone and setup environment**
```bash
git clone https://github.com/PavanKalyanMaturi/data-intelligence-platform.git
cd data-intelligence-platform
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

**Step 2: Configure environment**
```bash
# Create .env file
cp .env.example .env
# Edit .env with your values
```

**Step 3: Start services**
```bash
# Terminal 1 — Qdrant
docker run -p 6333:6333 -v qdrant_storage:/qdrant/storage qdrant/qdrant

# Terminal 2 — FastAPI
uvicorn backend.main:app --reload

# Terminal 3 — MLflow
mlflow ui --port 5000 --backend-store-uri sqlite:///mlflow.db

# Terminal 4 — Streamlit
streamlit run frontend/app.py --server.port 8501
```

**Step 4: Install and run Ollama (local LLM)**
```bash
# Download from https://ollama.com
ollama pull phi3:mini
```

---

## ⚙️ Environment Variables

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres @localhost:5432/dataintel

# Qdrant Vector DB
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_API_KEY=           # required for Qdrant Cloud only

# AI Settings
COLLECTION_NAME=data_intel
EMBEDDING_MODEL=all-MiniLM-L6-v2

# MLflow
MLFLOW_TRACKING_URI=sqlite:///mlflow.db

# LLM (leave empty for local Ollama)
GROQ_API_KEY=             # set for production Groq inference
```

---

## 📡 API Documentation

### Base URL
```
Local:      http://localhost:8000/api
Production: https://dataintel-api.onrender.com/api
```

---

### `POST /api/upload`
Upload a CSV or Excel file for AI processing.

**Request:** `multipart/form-data`
| Field | Type | Description |
|---|---|---|
| `file` | File | CSV or XLSX file (max 200MB) |

**Response:**
```json
{
  "message": "✅ File uploaded! Pipeline triggered in background.",
  "file_id": 1,
  "filename": "Human_Resources.csv",
  "rows": 1470,
  "columns": ["Age", "Attrition", "Department", "..."],
  "pipeline_status": "running in background ⚙️"
}
```

---

### `POST /api/query`
Query your uploaded data using natural language.

**Request:** `application/json`
```json
{
  "question": "How many employees have attrition Yes?",
  "file_id": 1,
  "use_agent": false
}
```

| Field | Type | Default | Description |
|---|---|---|---|
| `question` | string | required | Natural language question |
| `file_id` | integer | null | Filter by specific file |
| `use_agent` | boolean | true | Use LangChain agent or direct RAG |

**Response:**
```json
{
  "question": "How many employees have attrition Yes?",
  "answer": "Based on the HR data, 237 employees have attrition Yes (16.1% of total workforce).",
  "mode": "success (direct RAG)",
  "latency_seconds": 3.621
}
```

---

### `GET /api/files`
List all uploaded files.

**Response:**
```json
[
  {
    "id": 1,
    "filename": "Human_Resources.csv",
    "rows": 1470,
    "columns": "Age,Attrition,Department,...",
    "uploaded_at": "2026-03-10T14:30:00Z"
  }
]
```

---

### `GET /api/stats`
Get aggregated MLflow query statistics.

**Response:**
```json
{
  "total_queries": 47,
  "avg_latency_seconds": 3.821,
  "avg_similarity_score": 0.7234,
  "avg_answer_length": 312.4,
  "success_rate": 94.7,
  "mode_breakdown": {
    "direct RAG": 38,
    "RAG fallback": 9
  },
  "category_breakdown": {
    "attrition": 18,
    "compensation": 12,
    "workload": 10,
    "general": 7
  },
  "recent_queries": [
    "How many employees have attrition Yes?",
    "What is average monthly income by department?"
  ]
}
```

---

## 📁 Project Structure

```
data-intelligence-platform/
│
├── backend/                    # FastAPI application
│   ├── main.py                 # App entry point + startup events
│   ├── routes/
│   │   ├── upload.py           # File upload endpoints
│   │   └── query.py            # Query + stats endpoints
│   └── models/
│       └── schemas.py          # SQLAlchemy database models
│
├── agent/                      # AI/LLM layer
│   ├── llm.py                  # LLM connection (Ollama local)
│   ├── llm_factory.py          # LLM factory (Groq prod / Ollama dev)
│   ├── rag.py                  # RAG pipeline with MLflow tracking
│   ├── agent.py                # LangChain ReAct agent
│   ├── tools.py                # Agent tools (SearchData, GetFileInfo)
│   └── parser.py               # Custom ReAct output parser
│
├── pipelines/                  # Prefect data pipelines
│   ├── ingest.py               # Data loading + cleaning task
│   ├── embed.py                # Embedding generation task
│   └── clean.py                # Main Prefect flow orchestrator
│
├── db/                         # Database connections
│   ├── postgres.py             # SQLAlchemy engine + session
│   └── qdrant.py               # Qdrant client + vector operations
│
├── mlops/                      # MLflow tracking
│   └── tracking.py             # Query logging + stats retrieval
│
├── frontend/                   # Streamlit UI
│   └── app.py                  # 3-tab app (Upload/Query/Analytics)
│
├── tests/                      # CI test suite
│   └── test_api.py             # FastAPI endpoint tests
│
├── .github/workflows/          # GitHub Actions
│   └── ci.yml                  # CI pipeline
│
├── Dockerfile                  # FastAPI container
├── Dockerfile.streamlit        # Streamlit container
├── docker-compose.yml          # Full stack orchestration
├── render.yaml                 # Render deployment config
├── requirements.txt            # Python dependencies
└── .env.example                # Environment variables template
```

---

## 🔄 How It Works

### Upload Flow
```
User uploads CSV/Excel
        ↓
FastAPI validates + reads file metadata
        ↓
PostgreSQL stores file record (filename, rows, columns)
        ↓
Prefect pipeline triggers in background:
  ├── Task 1: Load + clean data (remove nulls, normalize columns)
  ├── Task 2: Generate embeddings (sentence-transformers)
  └── Task 3: Store vectors in Qdrant (with payload)
```

### Query Flow
```
User asks natural language question
        ↓
sentence-transformers converts question → 384-dim vector
        ↓
Qdrant cosine similarity search → top 10 relevant rows
        ↓
Rows formatted as context → injected into LLM prompt
        ↓
Groq/Ollama LLM generates answer from context
        ↓
MLflow logs: question, answer, latency, similarity scores
        ↓
Response returned to Streamlit UI
```

---

## 🧪 Running Tests

```bash
# Activate virtual environment
venv\Scripts\activate

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=backend --cov-report=html
```

Tests cover:
- API health check
- File upload endpoint
- Query endpoint
- Stats endpoint
- Files listing endpoint

CI runs automatically on every push via GitHub Actions.

---

## 🚀 Deployment

### Production Stack
| Service | Provider | Cost |
|---|---|---|
| FastAPI Backend | Render Web Service | Free |
| Streamlit Frontend | Render Web Service | Free |
| PostgreSQL | Render Managed DB | Free (90 days) |
| Qdrant Vector DB | Qdrant Cloud | Free |
| LLM Inference | Groq API | Free |
| CI/CD | GitHub Actions | Free |

### Deploy Your Own

1. **Fork this repository**

2. **Set up free accounts:**
   - [Render](https://render.com) — connect GitHub
   - [Qdrant Cloud](https://cloud.qdrant.io) — create free cluster
   - [Groq](https://console.groq.com) — get free API key

3. **Deploy on Render:**
```bash
# Render reads render.yaml automatically
# Just connect your GitHub repo and click Deploy
```

4. **Set environment variables in Render dashboard:**
```
GROQ_API_KEY     = your_groq_key
QDRANT_HOST      = your-cluster.cloud.qdrant.io
QDRANT_API_KEY   = your_qdrant_key
DATABASE_URL     = (auto-set by Render PostgreSQL)
COLLECTION_NAME  = data_intel
EMBEDDING_MODEL  = all-MiniLM-L6-v2
```

---

## 🔧 Troubleshooting

### Docker Compose Issues

**Problem:** `docker-compose up` fails with port already in use
```bash
# Find and stop the process using the port
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Problem:** FastAPI container keeps restarting
```bash
# Check FastAPI logs
docker logs dataintel_fastapi
```

**Problem:** Qdrant collection not found
```bash
# Restart and re-upload your file
docker-compose down -v
docker-compose up --build
# Then re-upload via Streamlit UI
```

---

### Local Development Issues

**Problem:** `pip install` fails with `greenlet` error (Windows)
```bash
pip install -r requirements.txt --prefer-binary
```

**Problem:** Ollama CUDA out of memory error
```bash
# Switch to smaller model
ollama pull phi3:mini
# Update agent/llm.py to use phi3:mini
```

**Problem:** MLflow UI shows empty experiments
```bash
# Make sure you're pointing to the correct database
mlflow ui --port 5000 --backend-store-uri sqlite:///mlflow.db
```

**Problem:** Low similarity scores (< 0.4)
```
Re-upload your file after the embedding pipeline improvement.
Better text format = higher similarity = better answers.
```

---

### Production (Render) Issues

**Problem:** Upload fails with `localhost:8000` error
```
Check Render environment variables:
API_URL = https://dataintel-api.onrender.com/api
```

**Problem:** First load takes 60+ seconds
```
Expected behavior on free tier (cold start).
Service spins down after 15 min inactivity.
Consider upgrading to paid tier for always-on.
```

**Problem:** `DATABASE_URL is None` error
```
Add DATABASE_URL from Render PostgreSQL dashboard
to FastAPI service environment variables.
```

---

## 📊 Performance

| Metric | Local (Ollama) | Production (Groq) |
|---|---|---|
| Avg query latency | 3–10 seconds | 0.5–2 seconds |
| Embedding generation | ~8s / 1470 rows | ~3s / 1470 rows |
| Vector search | < 100ms | < 50ms |
| Success rate | ~85% | ~95% |

---

## 🗺️ Roadmap

- [ ] PDF file support
- [ ] Auto-generated data visualizations from queries
- [ ] Multi-turn conversational memory
- [ ] User authentication + isolated data per user
- [ ] Support for multiple simultaneous datasets
- [ ] Export query history and insights as PDF report

---

## 👤 Author

**PavanKalyan Maturi**

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <strong>Built with ❤️ using FastAPI + LangChain + Qdrant + MLflow + Streamlit</strong>
</div>
