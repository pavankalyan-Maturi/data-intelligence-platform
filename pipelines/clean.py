from prefect import flow, task, get_run_logger
from pipelines.ingest import load_and_clean
from pipelines.embed import generate_and_store_embeddings
from db.qdrant import store_embeddings, init_qdrant_collection

@flow(name="Process File Pipeline")
def process_file_flow(
    file_bytes: bytes,
    file_type: str,
    file_id: int,
    filename: str
):
    logger = get_run_logger()
    logger.info(f"🚀 Starting pipeline for file: {filename}")

    # Initialize Qdrant collection if not exists
    init_qdrant_collection()

    # Task 1: Load and clean data
    df = load_and_clean(file_bytes, file_type)

    # Task 2: Generate embeddings
    points = generate_and_store_embeddings(df, file_id, filename)

    # Task 3: Store in Qdrant
    store_embeddings(points)

    logger.info(f"🎉 Pipeline complete for {filename}!")
    return {"status": "success", "rows_processed": len(df), "embeddings_stored": len(points)}