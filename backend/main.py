from fastapi import FastAPI
from backend.routes.upload import router as upload_router
from backend.routes.query import router as query_router
from db.postgres import init_db
from db.qdrant import init_qdrant_collection
from mlops.tracking import setup_mlflow  # 🆕

app = FastAPI(
    title="Data Intelligence Platform",
    description="Autonomous AI-powered data analysis platform",
    version="1.0.0"
)

@app.on_event("startup")
def startup_event():
    init_db()
    init_qdrant_collection()
    setup_mlflow()             # 🆕

app.include_router(upload_router, prefix="/api", tags=["Upload"])
app.include_router(query_router, prefix="/api", tags=["Query"])

@app.get("/")
def root():
    return {"message": "🚀 Data Intelligence Platform is running!"}