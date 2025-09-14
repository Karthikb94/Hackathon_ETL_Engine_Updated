import os
import json
import polars as pl
from openpyxl import Workbook
from xml.sax.saxutils import escape
from .exceptions import WriterError
from typing import List, Dict, Any, Optional, Generator, Union

EXCEL_MAX_ROWS = 1_048_000  # safe threshold

def ensure_parent(path: str):
    """Ensure parent directory exists for the given path."""
    parent_dir = os.path.dirname(path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)

def write_csv(df: pl.DataFrame, path: str):
    """Write DataFrame as CSV file."""
    if not isinstance(df, pl.DataFrame):
        raise WriterError("Input must be a Polars DataFrame")
    if not path or not isinstance(path, str):
        raise WriterError("Path must be a non-empty string")
    
    ensure_parent(path)
    try:
        df.write_csv(path)
    except Exception as e:
        raise WriterError(f"Failed to write CSV: {e}") from e

def write_ndjson(df: pl.DataFrame, path: str):
    """Write DataFrame as newline-delimited JSON."""
    ensure_parent(path)
    try:
        df.write_ndjson(path)
    except Exception as e:
        raise WriterError(f"Failed to write line-delimited JSON: {e}") from e

def write_json(df: pl.DataFrame, path: str):
    """Write DataFrame as traditional JSON array format."""
    ensure_parent(path)
    try:
        data = df.to_dicts()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    except Exception as e:
        raise WriterError(f"Failed to write JSON array: {e}") from e

def write_xlsx(df: pl.DataFrame, path: str):
    """Write DataFrame as Excel file with automatic chunking for large datasets."""
    if not isinstance(df, pl.DataFrame):
        raise WriterError("Input must be a Polars DataFrame")
    if not path or not isinstance(path, str):
        raise WriterError("Path must be a non-empty string")
    
    ensure_parent(path)
    try:
        total = df.height
        wb = Workbook()
        wb.remove(wb.active)
        
        start = 0
        sheet_idx = 1
        while start < total:
            end = min(start + EXCEL_MAX_ROWS, total)
            chunk = df.slice(start, end - start)
            
            ws = wb.create_sheet(f"Sheet{sheet_idx}")
            
            # Write headers
            for col_idx, col_name in enumerate(chunk.columns, 1):
                ws.cell(row=1, column=col_idx, value=col_name)
            
            # Write data
            for row_idx, row in enumerate(chunk.iter_rows(named=True), 2):
                for col_idx, col_name in enumerate(chunk.columns, 1):
                    value = row[col_name]
                    ws.cell(row=row_idx, column=col_idx, value=value)
            
            start = end
            sheet_idx += 1
        
        wb.save(path)
    except Exception as e:
        raise WriterError(f"Failed to write XLSX: {e}") from e

def write_xml(df: pl.DataFrame, path: str, root_tag: str = "records", row_tag: str = "record"):
    """Write DataFrame as XML file with proper encoding and formatting."""
    ensure_parent(path)
    try:
        with open(path, "w", encoding="utf-8") as f:
            # Write XML declaration
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(f"<{root_tag}>\n")
            cols = df.columns
            for row in df.iter_rows(named=True):
                f.write(f"  <{row_tag}>\n")
                for c in cols:
                    v = "" if row[c] is None else str(row[c])
                    # Escape XML special characters
                    escaped_v = escape(v)
                    f.write(f"    <{c}>{escaped_v}</{c}>\n")
                f.write(f"  </{row_tag}>\n")
            f.write(f"</{root_tag}>\n")
    except Exception as e:
        raise WriterError(f"Failed to write XML: {e}") from e

def write_fixed_width(df: pl.DataFrame, path: str, mappings: List[Dict[str, Any]], logger: Optional[Any] = None):
    """
    Write DataFrame as fixed-width file using mapping definitions.
    
    Args:
        df: Input DataFrame
        path: Output file path
        mappings: List of mapping dictionaries with width information
        logger: Optional logger instance
    """
    ensure_parent(path)
    
    # Extract field definitions from mappings
    field_defs = []
    for mapping in mappings:
        target = mapping.get("target")
        width = mapping.get("width", 20)  # Default width
        if target:
            field_defs.append((target, width))
    
    try:
        with open(path, "w", encoding="utf-8") as f:
            for ridx, row in enumerate(df.iter_rows(named=True)):
                line_parts = []
                for field_name, width in field_defs:
                    val = row.get(field_name, "")
                    s = "" if val is None else str(val)
                    
                    # Truncate if too long
                    if len(s) > width:
                        if logger:
                            logger.warning(f"Truncating column '{field_name}' at row {ridx}: '{s}' -> width {width}")
                        s = s[:width]
                    
                    # Right-align numeric, left-align text
                    try:
                        float(s)
                        aligned = s.rjust(width)
                    except:
                        aligned = s.ljust(width)
                    
                    line_parts.append(aligned)
                
                f.write("".join(line_parts) + "\n")
    except Exception as e:
        raise WriterError(f"Failed to write fixed-width file: {e}")

def write_fixed_width_with_schema(df: pl.DataFrame, path: str, target_schema: Dict[str, Any], logger: Optional[Any] = None):
    """
    Write DataFrame as fixed-width file using target schema definitions.
    Enhanced to handle both fixed-width and positional formats.
    
    Args:
        df: Input DataFrame
        path: Output file path
        target_schema: Target schema containing field definitions with positions and widths
        logger: Optional logger instance
    """
    ensure_parent(path)
    
    # Extract field definitions from target schema
    field_defs = []
    attributes = target_schema.get("attributes", {})
    file_type = target_schema.get("fileType", "").lower()
    
    if logger:
        logger.info(f"Writing fixed-width file with {len(attributes)} fields")
        logger.info(f"Target schema file type: {file_type}")
    
    # Sort fields by column_no to maintain order
    sorted_fields = sorted(attributes.items(), key=lambda x: x[1].get("column_no", 0))
    
    for field_name, field_config in sorted_fields:
        # Get width from field config, default to 20
        width = field_config.get("width", 20)
        # Get start position for padding (optional)
        start_pos = field_config.get("start_position", 0)
        # Get alignment preference (left, right, center)
        alignment = field_config.get("alignment", "left").lower()
        field_defs.append((field_name, width, start_pos, alignment))
    
    try:
        with open(path, "w", encoding="utf-8") as f:
            for ridx, row in enumerate(df.iter_rows(named=True)):
                line_parts = []
                current_pos = 0
                
                for field_name, width, start_pos, alignment in field_defs:
                    val = row.get(field_name, "")
                    s = "" if val is None else str(val)
                    
                    # Truncate if too long
                    if len(s) > width:
                        if logger:
                            logger.warning(f"Truncating column '{field_name}' at row {ridx}: '{s}' -> width {width}")
                        s = s[:width]
                    
                    # Add padding to reach start position if specified
                    if start_pos > current_pos:
                        padding = " " * (start_pos - current_pos)
                        line_parts.append(padding)
                        current_pos = start_pos
                    
                    # Apply alignment based on field configuration
                    if alignment == "right":
                        aligned = s.rjust(width)
                    elif alignment == "center":
                        aligned = s.center(width)
                    else:  # left alignment (default)
                        # For numeric values, right-align; for text, left-align
                        try:
                            float(s)
                            aligned = s.rjust(width)
                        except:
                            aligned = s.ljust(width)
                    
                    line_parts.append(aligned)
                    current_pos += width
                
                f.write("".join(line_parts) + "\n")
                
        if logger:
            logger.info(f"Successfully wrote fixed-width file: {path}")
            
    except Exception as e:
        raise WriterError(f"Failed to write fixed-width file with schema: {e}") from e

def write_output(df: pl.DataFrame, base_path: str, fmt: str, mappings: List[Dict[str, Any]], 
                xml_cfg: Optional[Dict[str, Any]] = None, logger: Optional[Any] = None) -> str:
    """Write DataFrame to file in the specified format."""
    fmt = fmt.lower()
    
    if fmt == "csv":
        out_path = f"{base_path}.csv"
        write_csv(df, out_path)
        return out_path
    elif fmt == "json":
        out_path = f"{base_path}.json"
        write_json(df, out_path)
        return out_path
    elif fmt == "jsonl":
        out_path = f"{base_path}.jsonl"
        write_ndjson(df, out_path)
        return out_path
    elif fmt == "json_array":
        out_path = f"{base_path}.json"
        write_json(df, out_path)
        return out_path
    elif fmt == "xlsx":
        out_path = f"{base_path}.xlsx"
        write_xlsx(df, out_path)
        return out_path
    elif fmt == "xml":
        out_path = f"{base_path}.xml"
        root_tag = (xml_cfg or {}).get("root_tag", "records")
        row_tag = (xml_cfg or {}).get("row_tag", "record")
        write_xml(df, out_path, root_tag, row_tag)
        return out_path
    elif fmt == "fixed_width":
        out_path = f"{base_path}.txt"
        write_fixed_width(df, out_path, mappings, logger=logger)
        return out_path
    elif fmt == "txt":
        out_path = f"{base_path}.txt"
        write_fixed_width(df, out_path, mappings, logger=logger)
        return out_path
    else:
        raise WriterError(f"Unsupported output format: {fmt}")

def write_output_with_schema(df: pl.DataFrame, base_path: str, fmt: str, mapping_config: Dict[str, Any], 
                           logger: Optional[Any] = None) -> str:
    """Write DataFrame to file in the specified format using target schema."""
    fmt = fmt.lower()
    
    if fmt == "csv":
        out_path = f"{base_path}.csv"
        write_csv(df, out_path)
        return out_path
    elif fmt == "json":
        out_path = f"{base_path}.json"
        write_json(df, out_path)
        return out_path
    elif fmt == "jsonl":
        out_path = f"{base_path}.jsonl"
        write_ndjson(df, out_path)
        return out_path
    elif fmt == "json_array":
        out_path = f"{base_path}.json"
        write_json(df, out_path)
        return out_path
    elif fmt == "xlsx":
        out_path = f"{base_path}.xlsx"
        write_xlsx(df, out_path)
        return out_path
    elif fmt == "xml":
        out_path = f"{base_path}.xml"
        write_xml(df, out_path)
        return out_path
    elif fmt == "fixed_width":
        out_path = f"{base_path}.txt"
        target_schema = mapping_config.get("targetSchema", {})
        write_fixed_width_with_schema(df, out_path, target_schema, logger=logger)
        return out_path
    elif fmt == "txt":
        out_path = f"{base_path}.txt"
        target_schema = mapping_config.get("targetSchema", {})
        write_fixed_width_with_schema(df, out_path, target_schema, logger=logger)
        return out_path
    else:
        raise WriterError(f"Unsupported output format: {fmt}")

# Streaming writer functions for large files
def write_output_streaming(df_chunks: Generator[pl.DataFrame, None, None], 
                          base_path: str, 
                          fmt: str, 
                          mapping_config: Dict[str, Any], 
                          logger: Optional[Any] = None) -> str:
    """
    Write output in streaming mode for large files.
    Processes DataFrame chunks and writes them incrementally.
    
    Args:
        df_chunks: Generator yielding DataFrame chunks
        base_path: Base path for output file
        fmt: Output format
        mapping_config: Mapping configuration
        logger: Optional logger
        
    Returns:
        Path to the output file
    """
    if fmt == "json":
        return _write_json_streaming(df_chunks, base_path, logger)
    elif fmt == "jsonl":
        return _write_jsonl_streaming(df_chunks, base_path, logger)
    elif fmt == "csv":
        return _write_csv_streaming(df_chunks, base_path, logger)
    elif fmt == "parquet":
        return _write_parquet_streaming(df_chunks, base_path, logger)
    else:
        # For unsupported streaming formats, fall back to regular writing
        # Collect all chunks into a single DataFrame
        all_chunks = list(df_chunks)
        if not all_chunks:
            raise WriterError("No data chunks to write")
        
        # Concatenate all chunks
        combined_df = pl.concat(all_chunks)
        return write_output_with_schema(combined_df, base_path, fmt, mapping_config, logger)

def _write_json_streaming(df_chunks: Generator[pl.DataFrame, None, None], 
                         base_path: str, 
                         logger: Optional[Any] = None) -> str:
    """Write JSON output in streaming mode."""
    out_path = f"{base_path}.json"
    ensure_parent(out_path)
    
    try:
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write('[')
            first_chunk = True
            
            for chunk in df_chunks:
                if chunk.is_empty():
                    continue
                    
                data = chunk.to_dicts()
                
                for i, record in enumerate(data):
                    if not first_chunk or i > 0:
                        f.write(',')
                    f.write('\n  ')
                    json.dump(record, f, indent=2, ensure_ascii=False, default=str)
                    first_chunk = False
            
            f.write('\n]')
        
        if logger:
            logger.info(f"JSON streaming output written to: {out_path}")
        return out_path
        
    except Exception as e:
        raise WriterError(f"Failed to write streaming JSON: {e}") from e

def _write_jsonl_streaming(df_chunks: Generator[pl.DataFrame, None, None], 
                          base_path: str, 
                          logger: Optional[Any] = None) -> str:
    """Write JSONL output in streaming mode."""
    out_path = f"{base_path}.jsonl"
    ensure_parent(out_path)
    
    try:
        with open(out_path, 'w', encoding='utf-8') as f:
            for chunk in df_chunks:
                if chunk.is_empty():
                    continue
                    
                data = chunk.to_dicts()
                for record in data:
                    json.dump(record, f, ensure_ascii=False, default=str)
                    f.write('\n')
        
        if logger:
            logger.info(f"JSONL streaming output written to: {out_path}")
        return out_path
        
    except Exception as e:
        raise WriterError(f"Failed to write streaming JSONL: {e}") from e

def _write_csv_streaming(df_chunks: Generator[pl.DataFrame, None, None], 
                        base_path: str, 
                        logger: Optional[Any] = None) -> str:
    """Write CSV output in streaming mode."""
    out_path = f"{base_path}.csv"
    ensure_parent(out_path)
    
    try:
        first_chunk = True
        for chunk in df_chunks:
            if chunk.is_empty():
                continue
                
            if first_chunk:
                # Write header for first chunk
                chunk.write_csv(out_path)
                first_chunk = False
            else:
                # Append data without header
                chunk.write_csv(out_path, include_header=False, append=True)
        
        if logger:
            logger.info(f"CSV streaming output written to: {out_path}")
        return out_path
        
    except Exception as e:
        raise WriterError(f"Failed to write streaming CSV: {e}") from e

def _write_parquet_streaming(df_chunks: Generator[pl.DataFrame, None, None], 
                            base_path: str, 
                            logger: Optional[Any] = None) -> str:
    """Write Parquet output in streaming mode."""
    out_path = f"{base_path}.parquet"
    ensure_parent(out_path)
    
    try:
        # For Parquet, we need to collect all chunks and write at once
        # as Parquet doesn't support true streaming append
        all_chunks = list(df_chunks)
        if not all_chunks:
            raise WriterError("No data chunks to write")
        
        # Concatenate all chunks
        combined_df = pl.concat(all_chunks)
        combined_df.write_parquet(out_path)
        
        if logger:
            logger.info(f"Parquet streaming output written to: {out_path}")
        return out_path
        
    except Exception as e:
        raise WriterError(f"Failed to write streaming Parquet: {e}") from e