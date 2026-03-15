from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
try:
    from agent.llm_factory import get_llm
except ImportError:
    from agent.llm import get_llm
from db.qdrant import search_similar
from sentence_transformers import SentenceTransformer
from mlops.tracking import log_query_run
import os
import time

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# 🆕 Force CPU — saves VRAM for LLM
device = "cpu"
print(f"🖥️ Embedding model running on: {device}")
model = SentenceTransformer(EMBEDDING_MODEL, device=device)

RAG_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""<|system|>
You are an HR data analyst. You MUST answer using ONLY the context provided below.
NEVER use outside knowledge. NEVER make up information.
If context is insufficient, say exactly: "I need more data to answer this accurately."
<|end|>
<|user|>
CONTEXT FROM HR DATABASE:
{context}

QUESTION: {question}

RULES:
- Use ONLY information from the context above
- Be concise and direct
- Do not mention Industrial Revolution or any unrelated topics
- Answer in 2-3 sentences maximum
<|assistant|>
Based on the HR data provided:"""
)

def retrieve_context(question: str, file_id: int = None, top_k: int = 5) -> str:
    # 🆕 reduced from 10 to 5 — less context = less confusion
    query_vector = model.encode(question).tolist()
    results = search_similar(query_vector, top_k=top_k)

    if not results:
        return "No relevant data found.", 0, 0.0

    if file_id:
        results = [r for r in results if r.payload.get("file_id") == file_id]

    scores = [getattr(r, 'score', 0.0) for r in results]
    avg_similarity = sum(scores) / len(scores) if scores else 0.0

    context_parts = []
    for i, result in enumerate(results, 1):
        text = result.payload.get("text", "")
        # 🆕 truncate each row to 200 chars max
        text = text[:200] + "..." if len(text) > 200 else text
        score = round(getattr(result, 'score', 0.0), 3)
        context_parts.append(f"Row {i}: {text}")

    return "\n".join(context_parts), len(results), avg_similarity


def rag_query(question: str, file_id: int = None, track: bool = True) -> dict:
    start_time = time.time()
    context, rows_found, avg_similarity = retrieve_context(question, file_id=file_id)

    # 🆕 Guard against None LLM
    llm = get_llm()
    if llm is None:
        return {
            "question": question,
            "answer": "LLM not available. Please check Ollama is running with: ollama list",
            "context_used": context,
            "sources_found": rows_found,
            "avg_similarity": avg_similarity,
            "latency_seconds": 0,
            "status": "llm_unavailable"
        }

    chain = RAG_PROMPT | llm | StrOutputParser()
    try:
        answer = chain.invoke({
            "context": context,
            "question": question
        })

        # 🆕 Clean prompt leakage
        for phrase in ["Your task:", "Instructions:", "<|user|>",
                       "<|system|>", "<|assistant|>", "CONTEXT:"]:
            if phrase in answer:
                answer = answer.split(phrase)[-1].strip()

        # 🆕 Detect hallucination — unrelated content
        hallucination_signals = [
            "industrial revolution",
            "american dream",
            "write a detailed",
            "in the document",
            "comparative analysis"
        ]
        if any(signal in answer.lower() for signal in hallucination_signals):
            answer = (
                "I found relevant HR records but couldn't generate "
                "a clean answer. Please try rephrasing your question "
                "or use direct RAG mode (turn off agent)."
            )
            status = "hallucination_detected"
        else:
            status = "success"

    except Exception as e:
        error_msg = str(e)
        
        # 🆕 Handle CUDA/Ollama crashes gracefully
        if "CUDA" in error_msg or "500" in error_msg:
            answer = (
                "The AI model temporarily ran out of memory. "
                "Please wait 10 seconds and try again. "
                f"Based on the data found: {context[:300]}..."
            )
            status = "cuda_error"
        else:
            answer = f"Error generating answer: {error_msg}"
            status = "error"

    latency = time.time() - start_time

    if track:
        log_query_run(
            question=question,
            answer=answer,
            mode="direct RAG",
            latency_seconds=latency,
            context_rows=rows_found,
            avg_similarity=avg_similarity,
            use_agent=False,
            file_id=file_id,
            status=status
        )

    return {
        "question": question,
        "answer": answer,
        "context_used": context,
        "sources_found": rows_found,
        "avg_similarity": avg_similarity,
        "latency_seconds": round(latency, 3),
        "status": status
    }