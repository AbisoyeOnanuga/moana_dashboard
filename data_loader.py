import os
import pandas as pd

REQUIRED_COLUMNS = [
    "asset_name",
    "asset_type",
    "poly_count",
    "file_size_mb",
    "instance_count",
    "scene_name",
    "location"
]

def load_metadata(csv_path):
    """
    Load the Moana metadata CSV and validate required columns.
    Returns a pandas DataFrame.
    """

    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"Metadata CSV not found at: {csv_path}")

    df = pd.read_csv(csv_path)

    # Validate required columns
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in metadata CSV: {missing}")

    # Optional: convert numeric columns
    numeric_cols = ["poly_count", "file_size_mb", "instance_count"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df
