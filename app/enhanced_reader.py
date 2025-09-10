import os
import polars as pl
from typing import Dict, Any, Optional
from .exceptions import ETLError
from .positional_reader import read_positional_parquet_file

def read_data_file(file_path: str, schema_config: Optional[Dict[str, Any]] = None) -> pl.DataFrame:
    """
    Enhanced reader for Parquet files with automatic struct flattening
    and optional positional file support
    
    Args:
        file_path: Path to Parquet file
        schema_config: Optional schema configuration for positional files
        
    Returns:
        Polars DataFrame
    """
    if not os.path.exists(file_path):
        raise ETLError(f"Input parquet file not found: {file_path}")
    
    try:
        # Check if this is a positional file
        if schema_config and "fields" in schema_config:
            # Read as positional file
            df = read_positional_parquet_file(file_path, schema_config)
        else:
            # Read as regular parquet file
            df = pl.read_parquet(file_path)
            
            # Auto-flatten struct columns if they exist
            df = auto_flatten_structs(df)
        
        return df
    except Exception as e:
        raise ETLError(f"Failed to read parquet file: {e}") from e

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

# Keep the old function for backward compatibility
def read_parquet_file(file_path: str) -> pl.DataFrame:
    return read_data_file(file_path)
