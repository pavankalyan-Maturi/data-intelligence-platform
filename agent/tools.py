from agent.rag import rag_query
from db.postgres import SessionLocal
from backend.models.schemas import UploadedFile

def search_data_tool(query: str) -> str:
    try:
        result = rag_query(query, track=False)
        return result["answer"]
    except Exception as e:
        return f"Search failed: {str(e)}"

def get_file_info_tool(query: str) -> str:
    db = SessionLocal()
    try:
        files = db.query(UploadedFile).all()
        if not files:
            return "No files uploaded yet."
        info = []
        for f in files:
            info.append(
                f"File: {f.filename} | "
                f"Rows: {f.row_count} | "
                f"Columns: {f.columns}"
            )
        return "\n".join(info)
    finally:
        db.close()

# Keep tools list for future use
tools = []