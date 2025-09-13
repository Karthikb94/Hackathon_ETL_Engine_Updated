import os
import polars as pl
from typing import Dict, Any, Optional
from .exceptions import ETLError
from .positional_reader import read_positional_parquet_file
from .models import SchemaDefinition

def read_data_file(file_path: str, schema_config: Optional[Dict[str, Any]] = None, source_schema: Optional[SchemaDefinition] = None) -> pl.DataFrame:
    """
    Enhanced reader for Parquet files with automatic struct flattening
    and optional positional file support
    
    Args:
        file_path: Path to Parquet file
        schema_config: Optional schema configuration for positional files
        source_schema: Optional source schema definition for validation
        
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
            
            # Apply source schema validation and column ordering if provided
            if source_schema:
                df = apply_source_schema(df, source_schema)
        
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

def apply_source_schema(df: pl.DataFrame, source_schema: SchemaDefinition) -> pl.DataFrame:
    """
    Apply source schema validation and column ordering
    
    Args:
        df: Input DataFrame
        source_schema: Source schema definition
        
    Returns:
        DataFrame with validated and ordered columns
    """
    # Get expected column names from schema
    expected_columns = list(source_schema.attributes.keys())
    
    # Check if all expected columns exist
    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        raise ETLError(f"Missing required columns: {missing_columns}")
    
    # Reorder columns according to schema
    # Sort by column_no if available, otherwise use the order in attributes
    column_order = []
    for attr_name, attr_def in source_schema.attributes.items():
        if attr_def.column_no is not None:
            column_order.append((attr_def.column_no, attr_name))
        else:
            column_order.append((999, attr_name))  # Put columns without column_no at the end
    
    # Sort by column_no and extract column names
    column_order.sort(key=lambda x: x[0])
    ordered_columns = [col_name for _, col_name in column_order]
    
    # Select columns in the correct order
    return df.select(ordered_columns)

# Keep the old function for backward compatibility
def read_parquet_file(file_path: str) -> pl.DataFrame:
    return read_data_file(file_path)
