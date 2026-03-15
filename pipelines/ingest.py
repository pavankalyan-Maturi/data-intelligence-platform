from prefect import flow, task, get_run_logger
import pandas as pd
import io

@task(name="Load and Clean Data", retries=2, retry_delay_seconds=5)
def load_and_clean(file_bytes: bytes, file_type: str) -> pd.DataFrame:
    logger = get_run_logger()
    logger.info("📥 Loading file...")

    # Load file
    if file_type == "csv":
        df = pd.read_csv(io.BytesIO(file_bytes))
    else:
        df = pd.read_excel(io.BytesIO(file_bytes))

    logger.info(f"📊 Loaded {len(df)} rows, {len(df.columns)} columns")

    # Clean data
    df = df.dropna(how="all")           # remove fully empty rows
    df = df.fillna("")                   # fill remaining NaN with empty string
    df.columns = [str(c).strip().lower().replace(" ", "_") 
                  for c in df.columns]  # normalize column names

    logger.info(f"✅ Cleaned data: {len(df)} rows remaining")
    return df