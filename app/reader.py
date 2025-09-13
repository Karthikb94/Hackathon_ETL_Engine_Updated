import os
import polars as pl
from typing import Optional
from .exceptions import ETLError

def read_data_file(file_path: str) -> pl.DataFrame:
    """
    Read data file and return as Polars DataFrame.
    Supports CSV, Parquet, and JSON formats.
    
    Args:
        file_path: Path to the data file
        
    Returns:
        Polars DataFrame
    """
    if not os.path.exists(file_path):
        raise ETLError(f"Input file not found: {file_path}")
    
    try:
        # Determine file type by extension
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.parquet':
            df = pl.read_parquet(file_path)
        elif file_ext == '.csv':
            df = pl.read_csv(file_path)
        elif file_ext in ['.json', '.jsonl']:
            try:
                # Try reading as JSONL first
                df = pl.read_ndjson(file_path)
            except:
                # Fallback to regular JSON
                df = pl.read_json(file_path)
        else:
            # Try to auto-detect format
            try:
                df = pl.read_parquet(file_path)
            except:
                try:
                    df = pl.read_csv(file_path)
                except:
                    try:
                        df = pl.read_ndjson(file_path)
                    except:
                        raise ETLError(f"Unsupported file format: {file_ext}")
        
        # Auto-flatten struct columns if they exist
        df = auto_flatten_structs(df)
        
        return df
        
    except Exception as e:
        raise ETLError(f"Failed to read file: {e}") from e

def auto_flatten_structs(df: pl.DataFrame) -> pl.DataFrame:
    """Automatically flatten struct columns to make them accessible"""
    flattened_columns = []
    
    for col_name, dtype in df.schema.items():
        if str(dtype).startswith('Struct'):
            # Flatten struct columns using struct.field()
            try:
                # Get all fields from the struct
                struct_fields = df.select(pl.col(col_name).struct.field("*")).columns
                for field in struct_fields:
                    flattened_columns.append(pl.col(col_name).struct.field(field).alias(f"{col_name}.{field}"))
            except Exception:
                # If struct flattening fails, keep the original column
                flattened_columns.append(pl.col(col_name))
        else:
            # Keep regular columns as-is
            flattened_columns.append(pl.col(col_name))
    
    if flattened_columns:
        return df.select(flattened_columns)
    else:
        return df
