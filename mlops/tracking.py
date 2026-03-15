import mlflow
import mlflow.langchain
from datetime import datetime
from dotenv import load_dotenv
import os
load_dotenv()

# 🆕 Read from environment variable
MLFLOW_TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "sqlite:///mlflow.db"   # fallback for local dev
)



# MLflow configuration
MLFLOW_EXPERIMENT_NAME = "HR-Data-Intelligence-Platform"

def setup_mlflow():
    """Initialize MLflow with experiment"""
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    
    # Create experiment if it doesn't exist
    experiment = mlflow.get_experiment_by_name(MLFLOW_EXPERIMENT_NAME)
    if experiment is None:
        mlflow.create_experiment(
            MLFLOW_EXPERIMENT_NAME,
            tags={
                "project": "Data Intelligence Platform",
                "version": "1.0",
                "team": "AI Engineering"
            }
        )
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
    print(f"✅ MLflow initialized! Experiment: {MLFLOW_EXPERIMENT_NAME}")


def log_query_run(
    question: str,
    answer: str,
    mode: str,
    latency_seconds: float,
    context_rows: int = 0,
    avg_similarity: float = 0.0,
    use_agent: bool = False,
    file_id: int = None,
    status: str = "success",
    model: str = "phi3",
    top_k: int = 10
):
    """
    Log a complete query run to MLflow.
    Called after every query — RAG or Agent.
    """
    setup_mlflow()

    with mlflow.start_run(run_name=f"query_{datetime.now().strftime('%H%M%S')}"):

        # ── PARAMETERS (inputs we control) ──────────────────
        mlflow.log_param("question", question[:250])  # truncate long questions
        mlflow.log_param("model", model)
        mlflow.log_param("top_k", top_k)
        mlflow.log_param("use_agent", use_agent)
        mlflow.log_param("file_id", file_id)

        # ── METRICS (things we measure) ──────────────────────
        mlflow.log_metric("latency_seconds", round(latency_seconds, 3))
        mlflow.log_metric("context_rows_found", context_rows)
        mlflow.log_metric("avg_similarity_score", round(avg_similarity, 4))
        mlflow.log_metric("answer_length_chars", len(answer))

        # ── TAGS (labels for filtering) ───────────────────────
        mlflow.set_tag("status", status)
        mlflow.set_tag("mode", mode)
        mlflow.set_tag("timestamp", datetime.now().isoformat())
        mlflow.set_tag("question_category", _categorize_question(question))

    print(f"✅ MLflow run logged! Latency: {latency_seconds:.2f}s | Mode: {mode}")


def _categorize_question(question: str) -> str:
    """
    Auto-categorize questions for better filtering in MLflow UI.
    Simple keyword matching — no LLM needed!
    """
    question_lower = question.lower()

    if any(word in question_lower for word in ["attrition", "left", "quit", "resign"]):
        return "attrition"
    elif any(word in question_lower for word in ["income", "salary", "pay", "wage", "rate"]):
        return "compensation"
    elif any(word in question_lower for word in ["department", "team", "division"]):
        return "department"
    elif any(word in question_lower for word in ["overtime", "hours", "work"]):
        return "workload"
    elif any(word in question_lower for word in ["satisfaction", "happy", "engagement"]):
        return "satisfaction"
    elif any(word in question_lower for word in ["age", "gender", "education"]):
        return "demographics"
    else:
        return "general"


def get_experiment_stats() -> dict:
    """
    Pull summary statistics from MLflow.
    Used by our API to expose metrics.
    """
    setup_mlflow()

    experiment = mlflow.get_experiment_by_name(MLFLOW_EXPERIMENT_NAME)
    if not experiment:
        return {"error": "No experiment found"}

    # Get all runs
    runs = mlflow.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["start_time DESC"]
    )

    if runs.empty:
        return {"total_runs": 0, "message": "No queries logged yet"}

    # Calculate statistics
    stats = {
        "total_queries": len(runs),
        "avg_latency_seconds": round(runs["metrics.latency_seconds"].mean(), 3),
        "avg_similarity_score": round(runs["metrics.avg_similarity_score"].mean(), 4),
        "avg_answer_length": round(runs["metrics.answer_length_chars"].mean(), 1),
        "success_rate": round(
            len(runs[runs["tags.status"] == "success"]) / len(runs) * 100, 1
        ),
        "mode_breakdown": runs["tags.mode"].value_counts().to_dict(),
        "category_breakdown": runs["tags.question_category"].value_counts().to_dict(),
        "recent_queries": runs["params.question"].head(5).tolist()
    }

    return stats