from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from agent.agent import run_agent
from agent.rag import rag_query
from mlops.tracking import get_experiment_stats, setup_mlflow  # 🆕

router = APIRouter()

class QueryRequest(BaseModel):
    question: str
    file_id: int = None
    use_agent: bool = True

@router.post("/query")
async def query_data(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        if request.use_agent:
            result = run_agent(request.question)
        else:
            result = rag_query(request.question, file_id=request.file_id)
            result["status"] = "success (direct RAG)"

        return {
            "question": result["question"],
            "answer": result["answer"],
            "mode": result.get("status", "success"),
            "latency_seconds": result.get("latency_seconds", 0),  # 🆕
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 🆕 New endpoint — exposes MLflow stats via API
@router.get("/stats")
def get_stats():
    """Returns aggregated query statistics from MLflow"""
    try:
        stats = get_experiment_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))