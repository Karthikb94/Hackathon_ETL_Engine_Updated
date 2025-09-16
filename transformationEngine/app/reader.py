import os
import polars as pl
from typing import Optional, Dict, Any, List, Generator, Union
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
        # Determine actual file type from file extension, not schema
        file_extension = os.path.splitext(file_path)[1].lower()
        attributes = source_schema.get("attributes", {})
        schema_file_type = source_schema.get("fileType", "").lower()
        
        # Always read based on actual file extension, but apply schema attributes
        if file_extension == ".parquet":
            return _read_parquet_with_schema(file_path, attributes)
        elif file_extension == ".csv":
            return _read_csv_with_schema(file_path, attributes)
        elif file_extension == ".json":
            return _read_json_with_schema(file_path, attributes)
        elif file_extension in [".fw", ".fixedwidth", ".fixed_width"]:
            return _read_fixed_width_with_schema(file_path, attributes)
        elif file_extension == ".xml":
            return _read_xml_with_schema(file_path, attributes)
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
    """
    Read Parquet file with schema-based column ordering and type casting.
    Enhanced to handle parquet files converted from various formats (CSV, JSON, XML, fixed-width).
    """
    try:
        df = pl.read_parquet(file_path)
        # Successfully read Parquet file
    except Exception as e:
        # Error reading Parquet file
        raise ReaderError(f"Failed to read parquet file: {e}")
    
    # Apply schema-based column ordering and type casting
    if attributes:
        schema_columns = []
        dtypes = {}
        
        # Sort attributes by column_no if available
        sorted_attrs = sorted(attributes.items(), 
                             key=lambda x: x[1].get("column_no", 999))
        
        for attr_name, attr_info in sorted_attrs:
            if attr_name in df.columns:
                schema_columns.append(attr_name)
                
                # Apply data type casting based on schema
                data_type = attr_info.get("dataType", "string")
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
        
        # Select columns in schema order and cast types
        if schema_columns:
            df = df.select(schema_columns)
            if dtypes:
                # Apply type casting
                cast_exprs = []
                for col_name, dtype in dtypes.items():
                    if col_name in df.columns:
                        cast_exprs.append(pl.col(col_name).cast(dtype))
                    else:
                        cast_exprs.append(pl.col(col_name))
                if cast_exprs:
                    df = df.with_columns(cast_exprs)
        
        # Schema-ordered columns applied
    
    return df

def _read_json_with_schema(file_path: str, attributes: Dict[str, Any]) -> pl.DataFrame:
    """Read JSON file with schema-based column ordering and nested structure handling"""
    try:
        # Try JSONL first
        df = pl.read_ndjson(file_path)
    except:
        # Fallback to regular JSON
        df = pl.read_json(file_path)
    
    # Auto-flatten nested structures first
    df = auto_flatten_structs(df)
    
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
    # Check if file is large enough to warrant streaming
    if should_use_streaming(file_path):
        # Use streaming for large files
        chunks = []
        for chunk_df in _read_fixed_width_streaming(file_path, attributes, chunk_size=10000):
            chunks.append(chunk_df)
        
        if chunks:
            return pl.concat(chunks)
        else:
            # Return empty DataFrame with expected columns
            empty_data = {attr_name: [] for attr_name in attributes.keys()}
            return pl.DataFrame(empty_data)
    
    # For small files, use optimized vectorized approach
    try:
        # Read all lines at once for better performance
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.rstrip('\n\r') for line in f if line.strip()]
        
        if not lines:
            # Return empty DataFrame with expected columns
            empty_data = {attr_name: [] for attr_name in attributes.keys()}
            return pl.DataFrame(empty_data)
        
        # Use vectorized parsing for better performance
        return _parse_fixed_width_vectorized(lines, attributes)
        
    except Exception as e:
        # Fallback to line-by-line parsing if vectorized fails
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():  # Skip empty lines
                    row = _parse_fixed_width_line(line, attributes)
                    data.append(row)
        
        return pl.DataFrame(data)

def _parse_fixed_width_line(line: str, attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Parse a single line from a fixed-width file based on schema attributes"""
    row = {}
    for attr_name, attr_info in attributes.items():
        start_pos = attr_info.get("start_position", 0)
        width = attr_info.get("width", 10)
        end_pos = start_pos + width
        
        # Ensure we don't exceed line length
        if end_pos > len(line):
            end_pos = len(line)
        
        value = line[start_pos:end_pos].strip()
        
        # Apply data type conversion
        data_type = attr_info.get("dataType", "string").lower()
        if data_type == "integer":
            try:
                row[attr_name] = int(value) if value else 0
            except ValueError:
                row[attr_name] = 0
        elif data_type == "float":
            try:
                row[attr_name] = float(value) if value else 0.0
            except ValueError:
                row[attr_name] = 0.0
        elif data_type == "boolean":
            row[attr_name] = value.lower() in ('1', 'true', 'y', 'yes')
        elif data_type == "date":
            # Keep as string for now, date parsing will be handled by Polars
            row[attr_name] = value
        else:
            row[attr_name] = value
    
    return row

def _parse_fixed_width_vectorized(lines: List[str], attributes: Dict[str, Any]) -> pl.DataFrame:
    """Parse fixed-width data using vectorized operations for better performance"""
    if not lines:
        empty_data = {attr_name: [] for attr_name in attributes.keys()}
        return pl.DataFrame(empty_data)
    
    # Prepare column definitions
    column_defs = []
    for attr_name, attr_info in attributes.items():
        start_pos = attr_info.get("start_position", 0)
        width = attr_info.get("width", 10)
        data_type = attr_info.get("dataType", "string").lower()
        column_defs.append((attr_name, start_pos, width, data_type))
    
    # Create a DataFrame with raw string data first
    data = {}
    for attr_name, start_pos, width, data_type in column_defs:
        # Extract substrings for all lines at once
        values = []
        for line in lines:
            end_pos = min(start_pos + width, len(line))
            if start_pos < len(line):
                value = line[start_pos:end_pos].strip()
            else:
                value = ""
            values.append(value)
        data[attr_name] = values
    
    # Create DataFrame with string data
    df = pl.DataFrame(data)
    
    # Apply type conversions
    cast_exprs = []
    for attr_name, _, _, data_type in column_defs:
        if data_type == "integer":
            cast_exprs.append(pl.col(attr_name).cast(pl.Int64, strict=False).fill_null(0))
        elif data_type == "float":
            cast_exprs.append(pl.col(attr_name).cast(pl.Float64, strict=False).fill_null(0.0))
        elif data_type == "boolean":
            cast_exprs.append(pl.col(attr_name).str.to_lowercase().is_in(["1", "true", "y", "yes"]).cast(pl.Boolean))
        elif data_type == "date":
            # Keep as string for now, date parsing will be handled by Polars
            cast_exprs.append(pl.col(attr_name))
        else:  # string
            cast_exprs.append(pl.col(attr_name).cast(pl.Utf8))
    
    if cast_exprs:
        df = df.with_columns(cast_exprs)
    
    return df

def _read_fixed_width_streaming(file_path: str, attributes: Dict[str, Any], chunk_size: int = 10000) -> Generator[pl.DataFrame, None, None]:
    """Stream fixed-width file in chunks to reduce memory usage"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            chunk_data = []
            line_num = 0
            error_count = 0
            max_errors = 100  # Stop after too many errors
            
            for line_num, line in enumerate(f, 1):
                # Skip empty lines
                if not line.strip():
                    continue
                
                try:
                    row = _parse_fixed_width_line(line, attributes)
                    chunk_data.append(row)
                    
                    # Yield chunk when it reaches the desired size
                    if len(chunk_data) >= chunk_size:
                        if chunk_data:  # Only yield if we have data
                            yield pl.DataFrame(chunk_data)
                        chunk_data = []
                        
                except Exception as e:
                    error_count += 1
                    # Log parsing error but continue processing
                    print(f"Warning: Error parsing line {line_num}: {e}")
                    
                    # Stop if too many errors
                    if error_count >= max_errors:
                        print(f"Error: Too many parsing errors ({max_errors}), stopping processing")
                        break
                    continue
            
            # Yield remaining data
            if chunk_data:
                yield pl.DataFrame(chunk_data)
                
    except FileNotFoundError:
        raise ReaderError(f"Fixed-width file not found: {file_path}")
    except PermissionError:
        raise ReaderError(f"Permission denied reading file: {file_path}")
    except UnicodeDecodeError as e:
        raise ReaderError(f"Encoding error reading file: {e}. Try specifying encoding.")
    except Exception as e:
        raise ReaderError(f"Failed to stream fixed-width file: {e}") from e

def _read_xml_with_schema(file_path: str, attributes: Dict[str, Any]) -> pl.DataFrame:
    """Read XML file with schema-based column extraction"""
    try:
        import xml.etree.ElementTree as ET
    except ImportError:
        raise ReaderError("XML parsing requires xml.etree.ElementTree")
    
    # Parse XML file
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    data = []
    
    # Find all record elements (assuming records are direct children or in a specific path)
    records = root.findall('.//record') if root.findall('.//record') else [root]
    
    for record in records:
        row_data = {}
        
        for attr_name, attr_info in attributes.items():
            # Try to find the element by tag name or xpath
            element = record.find(attr_name)
            if element is not None:
                value = element.text.strip() if element.text else ""
                
                # Convert data type
                data_type = attr_info.get("dataType", "string")
                if data_type == "integer":
                    try:
                        value = int(value) if value else 0
                    except ValueError:
                        value = 0
                elif data_type == "float":
                    try:
                        value = float(value) if value else 0.0
                    except ValueError:
                        value = 0.0
                
                row_data[attr_name] = value
            else:
                # Set default value if element not found
                data_type = attr_info.get("dataType", "string")
                if data_type == "integer":
                    row_data[attr_name] = 0
                elif data_type == "float":
                    row_data[attr_name] = 0.0
                else:
                    row_data[attr_name] = ""
        
        data.append(row_data)
    
    # Create DataFrame from parsed data
    if data:
        df = pl.DataFrame(data)
    else:
        # Create empty DataFrame with expected columns
        empty_data = {attr_name: [] for attr_name in attributes.keys()}
        df = pl.DataFrame(empty_data)
    
    return df

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
            try:
                df = pl.read_parquet(file_path)
                # Successfully read Parquet file
            except Exception as e:
                # Error reading Parquet file
                raise
        elif file_ext == '.csv':
            df = pl.read_csv(file_path)
        elif file_ext in ['.json', '.jsonl']:
            try:
                # Try reading as JSONL first
                df = pl.read_ndjson(file_path)
            except:
                # Fallback to regular JSON
                df = pl.read_json(file_path)
        elif file_ext == '.xml':
            # For XML files, we need a basic schema for auto-detection
            # This is a simplified approach - in practice, you'd want more sophisticated XML parsing
            try:
                import xml.etree.ElementTree as ET
                tree = ET.parse(file_path)
                root = tree.getroot()
                
                # Extract all unique tag names as columns
                columns = set()
                for elem in root.iter():
                    if elem.text and elem.text.strip():
                        columns.add(elem.tag)
                
                # Create a simple DataFrame
                data = []
                for elem in root.iter():
                    if elem.tag in columns and elem.text and elem.text.strip():
                        row = {col: "" for col in columns}
                        row[elem.tag] = elem.text.strip()
                        data.append(row)
                
                if data:
                    df = pl.DataFrame(data)
                else:
                    # Create empty DataFrame with found columns
                    empty_data = {col: [] for col in columns}
                    df = pl.DataFrame(empty_data)
            except Exception as e:
                raise ETLError(f"Failed to parse XML file: {e}")
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
                        try:
                            df = pl.read_json(file_path)
                        except:
                            raise ETLError(f"Unsupported file format: {file_ext}")
        
        # Auto-flatten struct columns if they exist
        df = auto_flatten_structs(df)
        
        return df
        
    except Exception as e:
        raise ETLError(f"Failed to read file: {e}") from e

def auto_flatten_structs(df: pl.DataFrame) -> pl.DataFrame:
    """Automatically flatten struct columns to make them accessible"""
    # Auto-flattening struct columns
    
    # Check if df is None or has no schema
    if df is None:
        print("ERROR: DataFrame is None in auto_flatten_structs")
        return df
    
    if not hasattr(df, 'schema') or df.schema is None:
        print("ERROR: DataFrame schema is None in auto_flatten_structs")
        return df
    
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

# Streaming functions for large files
LARGE_FILE_THRESHOLD = 100 * 1024 * 1024  # 100MB

def should_use_streaming(file_path: str) -> bool:
    """Check if file is large enough to warrant streaming processing."""
    try:
        return os.path.getsize(file_path) > LARGE_FILE_THRESHOLD
    except OSError:
        return False

def read_data_file_with_schema_streaming(file_path: str, source_schema: Dict[str, Any], 
                                       chunk_size: int = 10000) -> Generator[pl.DataFrame, None, None]:
    """
    Read data file in streaming mode for large files.
    Yields DataFrames in chunks to reduce memory usage.
    
    Args:
        file_path: Path to the data file
        source_schema: Source schema definition with attributes
        chunk_size: Number of rows per chunk
        
    Yields:
        Polars DataFrame chunks
    """
    if not os.path.exists(file_path):
        raise ReaderError(f"Input file not found: {file_path}")
    
    try:
        file_type = source_schema.get("fileType", "").lower()
        attributes = source_schema.get("attributes", {})
        
        if file_type == "parquet":
            yield from _read_parquet_streaming(file_path, attributes, chunk_size)
        elif file_type == "csv":
            yield from _read_csv_streaming(file_path, attributes, chunk_size)
        elif file_type == "json":
            yield from _read_json_streaming(file_path, attributes, chunk_size)
        elif file_type == "fixed_width":
            yield from _read_fixed_width_streaming(file_path, attributes, chunk_size)
        else:
            # For unsupported streaming formats, fall back to regular reading
            df = read_data_file_with_schema(file_path, source_schema)
            yield df
            
    except Exception as e:
        raise ReaderError(f"Failed to read file with streaming: {e}") from e

def _read_parquet_streaming(file_path: str, attributes: Dict[str, Any], 
                           chunk_size: int) -> Generator[pl.DataFrame, None, None]:
    """Stream Parquet file in chunks."""
    try:
        # Use Polars streaming for Parquet files
        for df in pl.scan_parquet(file_path).collect_streaming(chunk_size=chunk_size):
            if not df.is_empty():
                # Apply schema-based column ordering and types
                df = _apply_schema_to_dataframe(df, attributes)
                yield df
    except Exception as e:
        raise ReaderError(f"Failed to stream Parquet file: {e}") from e

def _read_csv_streaming(file_path: str, attributes: Dict[str, Any], 
                       chunk_size: int) -> Generator[pl.DataFrame, None, None]:
    """Stream CSV file in chunks."""
    try:
        # Use Polars streaming for CSV files
        for df in pl.scan_csv(file_path).collect_streaming(chunk_size=chunk_size):
            if not df.is_empty():
                # Apply schema-based column ordering and types
                df = _apply_schema_to_dataframe(df, attributes)
                yield df
    except Exception as e:
        raise ReaderError(f"Failed to stream CSV file: {e}") from e

def _read_json_streaming(file_path: str, attributes: Dict[str, Any], 
                        chunk_size: int) -> Generator[pl.DataFrame, None, None]:
    """Stream JSON file in chunks."""
    try:
        # For JSON, we need to read in chunks manually
        import json
        
        with open(file_path, 'r', encoding='utf-8') as f:
            chunk = []
            line_num = 0
            error_count = 0
            max_errors = 100  # Stop after too many errors
            
            for line_num, line in enumerate(f, 1):
                if not line.strip():  # Skip empty lines
                    continue
                    
                try:
                    data = json.loads(line.strip())
                    chunk.append(data)
                    
                    if len(chunk) >= chunk_size:
                        if chunk:  # Only process if we have data
                            df = pl.DataFrame(chunk)
                            if not df.is_empty():
                                df = _apply_schema_to_dataframe(df, attributes)
                                yield df
                            chunk = []
                            
                except json.JSONDecodeError as e:
                    error_count += 1
                    print(f"Warning: JSON decode error on line {line_num}: {e}")
                    
                    # Stop if too many errors
                    if error_count >= max_errors:
                        print(f"Error: Too many JSON decode errors ({max_errors}), stopping processing")
                        break
                    continue
                except Exception as e:
                    error_count += 1
                    print(f"Warning: Error processing line {line_num}: {e}")
                    
                    if error_count >= max_errors:
                        print(f"Error: Too many processing errors ({max_errors}), stopping processing")
                        break
                    continue
            
            # Process remaining chunk
            if chunk:
                df = pl.DataFrame(chunk)
                if not df.is_empty():
                    df = _apply_schema_to_dataframe(df, attributes)
                    yield df
                    
    except FileNotFoundError:
        raise ReaderError(f"JSON file not found: {file_path}")
    except PermissionError:
        raise ReaderError(f"Permission denied reading file: {file_path}")
    except UnicodeDecodeError as e:
        raise ReaderError(f"Encoding error reading file: {e}. Try specifying encoding.")
    except Exception as e:
        raise ReaderError(f"Failed to stream JSON file: {e}") from e

def _apply_schema_to_dataframe(df: pl.DataFrame, attributes: Dict[str, Any]) -> pl.DataFrame:
    """Apply schema-based column ordering and types to DataFrame."""
    if not attributes:
        return df
    
    # Extract column information from schema
    columns = []
    dtypes = {}
    
    # Sort attributes by column_no if available
    sorted_attrs = sorted(attributes.items(), 
                         key=lambda x: x[1].get("column_no", 999))
    
    for field_name, field_info in sorted_attrs:
        if field_name in df.columns:
            columns.append(field_name)
            # Map data types
            data_type = field_info.get("dataType", "string").lower()
            if data_type == "integer":
                dtypes[field_name] = pl.Int64
            elif data_type == "float":
                dtypes[field_name] = pl.Float64
            elif data_type == "boolean":
                dtypes[field_name] = pl.Boolean
            elif data_type == "date":
                dtypes[field_name] = pl.Date
            elif data_type == "datetime":
                dtypes[field_name] = pl.Datetime
            else:
                dtypes[field_name] = pl.Utf8
    
    # Select and cast columns
    if columns:
        df = df.select(columns)
        for col, dtype in dtypes.items():
            if col in df.columns:
                df = df.with_columns(pl.col(col).cast(dtype, strict=False))
    
    return df
