from mlops.tracking import log_query_run
import time

def run_agent(question: str) -> dict:
    """
    Uses direct RAG — reliable across all environments.
    Agent with LangChain ReAct reserved for local dev only.
    """
    start_time = time.time()
    return _rag_fallback(question, start_time)


def _rag_fallback(question: str, start_time: float) -> dict:
    from agent.rag import rag_query
    result = rag_query(question, track=False)
    latency = time.time() - start_time

    log_query_run(
        question=question,
        answer=result["answer"],
        mode="RAG",
        latency_seconds=latency,
        context_rows=result.get("sources_found", 0),
        avg_similarity=result.get("avg_similarity", 0.0),
        use_agent=True,
        status="success"
    )

    return {
        "question": question,
        "answer": result["answer"],
        "latency_seconds": round(latency, 3),
        "status": "success (RAG)"
    }