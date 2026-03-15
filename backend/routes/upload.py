from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from db.postgres import get_db
from backend.models.schemas import UploadedFile
from pipelines.clean import process_file_flow
import pandas as pd
import io

router = APIRouter()

@router.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validate file type
    if not file.filename.endswith((".csv", ".xlsx")):
        raise HTTPException(status_code=400, detail="Only CSV and Excel files supported")

    # Read file bytes
    contents = await file.read()

    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse file: {str(e)}")

    # Save metadata to PostgreSQL
    file_type = "csv" if file.filename.endswith(".csv") else "xlsx"
    file_record = UploadedFile(
        filename=file.filename,
        file_type=file_type,
        row_count=len(df),
        columns=",".join(df.columns.tolist())
    )
    db.add(file_record)
    db.commit()
    db.refresh(file_record)

    # 🆕 Trigger Prefect pipeline in background
    background_tasks.add_task(
        process_file_flow,
        file_bytes=contents,
        file_type=file_type,
        file_id=file_record.id,
        filename=file.filename
    )

    return {
        "message": "✅ File uploaded! Pipeline triggered in background.",
        "file_id": file_record.id,
        "filename": file.filename,
        "rows": len(df),
        "columns": df.columns.tolist(),
        "pipeline_status": "running in background ⚙️"
    }

@router.get("/files")
def list_files(db: Session = Depends(get_db)):
    files = db.query(UploadedFile).all()
    return [
        {
            "id": f.id,
            "filename": f.filename,
            "rows": f.row_count,
            "columns": f.columns,
            "uploaded_at": f.uploaded_at
        }
        for f in files
    ]