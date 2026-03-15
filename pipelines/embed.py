from prefect import task, get_run_logger
from sentence_transformers import SentenceTransformer
from qdrant_client.models import PointStruct
import pandas as pd
import os
import uuid
from sentence_transformers import SentenceTransformer
import torch

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# Force CPU for embeddings
device = "cpu"
print(f"🖥️ Embedding model running on: {device}")
model = SentenceTransformer(EMBEDDING_MODEL, device=device)


@task(name="Generate Embeddings", retries=1)
def generate_and_store_embeddings(
    df: pd.DataFrame,
    file_id: int,
    filename: str
) -> list[PointStruct]:
    logger = get_run_logger()
    logger.info(f"🧠 Generating embeddings for {len(df)} rows...")

    points = []

    for idx, row in df.iterrows():
        # 🆕 Build a more descriptive natural language sentence per row
        row_dict = row.to_dict()
        
        # Convert row to natural language description
        parts = []
        for col, val in row_dict.items():
            if val != "" and str(val).lower() != "nan":
                # Make it readable: "age is 41" instead of "age: 41"
                parts.append(f"{col.replace('_', ' ')} is {val}")
        
        row_text = ", ".join(parts)

        if not row_text.strip():
            continue

        # Generate embedding
        embedding = model.encode(row_text).tolist()

        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "text": row_text,
                "file_id": file_id,
                "filename": filename,
                "row_number": idx,
                "row_data": row_dict
            }
        )
        points.append(point)

    logger.info(f"✅ Generated {len(points)} embeddings!")
    return points