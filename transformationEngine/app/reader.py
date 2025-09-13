import os
import polars as pl
from typing import Optional, Dict, Any, List
from .exceptions import ETLError, ReaderError

def read_data_file_with_schema(file_path: str, source_schema: Dict[str, Any]) -> pl.DataFrame:
    """
    Read data file using source schema information.
    Supports CSV, Parquet, JSON, and fixed-width formats with schema.
    
    Args:
        file_path: Path to the data file
        source_schema: Source schema definition with attributes
        
    Returns:
        Polars DataFrame with proper column types and ordering
    """
    if not os.path.exists(file_path):
        raise ReaderError(f"Input file not found: {file_path}")
    
    try:
        file_type = source_schema.get("fileType", "").lower()
        attributes = source_schema.get("attributes", {})
        
        if file_type == "csv":
            return _read_csv_with_schema(file_path, attributes)
        elif file_type == "parquet":
            return _read_parquet_with_schema(file_path, attributes)
        elif file_type == "json":
            return _read_json_with_schema(file_path, attributes)
        elif file_type == "fixed_width":
            return _read_fixed_width_with_schema(file_path, attributes)
        else:
            # Fallback to extension-based reading
            return read_data_file(file_path)
            
    except Exception as e:
        raise ReaderError(f"Failed to read file with schema: {e}") from e

def _read_csv_with_schema(file_path: str, attributes: Dict[str, Any]) -> pl.DataFrame:
    """Read CSV file with schema-based column ordering and types"""
    # Extract column information from schema
    columns = []
    dtypes = {}
    
    # Sort attributes by column_no if available
    sorted_attrs = sorted(attributes.items(), 
                         key=lambda x: x[1].get("column_no", 999))
    
    for attr_name, attr_info in sorted_attrs:
        columns.append(attr_name)
        data_type = attr_info.get("dataType", "string")
        
        # Map schema data types to Polars types
        if data_type == "string":
            dtypes[attr_name] = pl.Utf8
        elif data_type == "date":
            dtypes[attr_name] = pl.Date
        elif data_type == "datetime":
            dtypes[attr_name] = pl.Datetime
        elif data_type == "integer":
            dtypes[attr_name] = pl.Int64
        elif data_type == "float":
            dtypes[attr_name] = pl.Float64
        elif data_type == "boolean":
            dtypes[attr_name] = pl.Boolean
    
    # Read CSV with specified columns and types
    df = pl.read_csv(file_path, columns=columns, dtypes=dtypes)
    return df

def _read_parquet_with_schema(file_path: str, attributes: Dict[str, Any]) -> pl.DataFrame:
    """Read Parquet file with schema-based column ordering"""
    df = pl.read_parquet(file_path)
    
    # Reorder columns according to schema
    schema_columns = []
    for attr_name, attr_info in sorted(attributes.items(), 
                                     key=lambda x: x[1].get("column_no", 999)):
        if attr_name in df.columns:
            schema_columns.append(attr_name)
    
    # Select columns in schema order
    if schema_columns:
        df = df.select(schema_columns)
    
    return df

def _read_json_with_schema(file_path: str, attributes: Dict[str, Any]) -> pl.DataFrame:
    """Read JSON file with schema-based column ordering"""
    try:
        # Try JSONL first
        df = pl.read_ndjson(file_path)
    except:
        # Fallback to regular JSON
        df = pl.read_json(file_path)
    
    # Reorder columns according to schema
    schema_columns = []
    for attr_name, attr_info in sorted(attributes.items(), 
                                     key=lambda x: x[1].get("column_no", 999)):
        if attr_name in df.columns:
            schema_columns.append(attr_name)
    
    # Select columns in schema order
    if schema_columns:
        df = df.select(schema_columns)
    
    return df

def _read_fixed_width_with_schema(file_path: str, attributes: Dict[str, Any]) -> pl.DataFrame:
    """Read fixed-width file with schema-based column definitions"""
    # This is a placeholder for fixed-width reading
    # In a real implementation, you would parse the fixed-width format
    # based on column positions and widths defined in the schema
    
    # For now, read as text and split by position
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Extract data based on schema column positions
    data = []
    for line in lines:
        row = {}
        for attr_name, attr_info in attributes.items():
            start_pos = attr_info.get("start_position", 0)
            width = attr_info.get("width", 10)
            end_pos = start_pos + width
            
            value = line[start_pos:end_pos].strip()
            row[attr_name] = value
        data.append(row)
    
    return pl.DataFrame(data)

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
