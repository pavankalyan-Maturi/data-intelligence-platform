from langchain.tools import Tool
from agent.rag import rag_query
from db.postgres import SessionLocal
from backend.models.schemas import UploadedFile

def search_data_tool(query: str) -> str:
    """Search HR data and answer questions"""
    try:
        result = rag_query(query)
        return result["answer"]
    except Exception as e:
        return f"Search failed: {str(e)}"

def get_file_info_tool(query: str) -> str:
    """Get info about uploaded files"""
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

# 🆕 Simpler, cleaner tool descriptions
tools = [
    Tool(
        name="SearchData",
        func=search_data_tool,
        description="Search employee data to answer HR questions about attrition, income, departments, job roles, overtime, satisfaction scores etc. Input: a specific question about the data."
    ),
    Tool(
        name="GetFileInfo",
        func=get_file_info_tool,
        description="Get information about uploaded files like filename, row count, column names. Input: any text."
    ),
]