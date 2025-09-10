#!/usr/bin/env python3
"""
Positional/Fixed-Width File Reader for ETL Engine
Handles fixed-position files stored in Parquet format with user-provided schema
"""
import os
import polars as pl
from typing import Dict, List, Any, Optional
from .exceptions import ETLError


class PositionalSchema:
    """Schema definition for fixed-position files"""
    
    def __init__(self, schema_config: Dict[str, Any]):
        """
        Initialize positional schema from configuration
        
        Args:
            schema_config: Dictionary containing schema definition
                {
                    "fields": [
                        {
                            "name": "field_name",
                            "start": 1,
                            "length": 10,
                            "type": "string|integer|decimal|date",
                            "format": "optional_format_string",
                            "padding": "left|right|none",
                            "pad_char": " "
                        }
                    ]
                }
        """
        self.fields = []
        self.total_length = 0
        
        if "fields" not in schema_config:
            raise ETLError("Schema configuration must contain 'fields' array")
        
        for field_config in schema_config["fields"]:
            field = self._parse_field_config(field_config)
            self.fields.append(field)
            self.total_length = max(self.total_length, field["end"])
    
    def _parse_field_config(self, field_config: Dict[str, Any]) -> Dict[str, Any]:
        """Parse individual field configuration"""
        required_fields = ["name", "start", "length", "type"]
        for field in required_fields:
            if field not in field_config:
                raise ETLError(f"Field configuration missing required field: {field}")
        
        start = int(field_config["start"])
        length = int(field_config["length"])
        
        return {
            "name": field_config["name"],
            "start": start,
            "end": start + length - 1,
            "length": length,
            "type": field_config["type"].lower(),
            "format": field_config.get("format", ""),
            "padding": field_config.get("padding", "right").lower(),
            "pad_char": field_config.get("pad_char", " ")
        }
    
    def get_field_names(self) -> List[str]:
        """Get list of field names"""
        return [field["name"] for field in self.fields]
    
    def validate_record_length(self, record_length: int) -> bool:
        """Validate if record length matches schema"""
        return record_length >= self.total_length


class PositionalReader:
    """Reader for fixed-position files stored in Parquet format"""
    
    def __init__(self):
        self.schema = None
    
    def set_schema(self, schema_config: Dict[str, Any]):
        """Set the positional schema"""
        self.schema = PositionalSchema(schema_config)
    
    def read_positional_parquet(self, file_path: str, schema_config: Dict[str, Any]) -> pl.DataFrame:
        """
        Read fixed-position data from Parquet file and parse according to schema
        
        Args:
            file_path: Path to Parquet file containing fixed-position data
            schema_config: Schema configuration for parsing fixed-position data
            
        Returns:
            Polars DataFrame with parsed fields
        """
        if not os.path.exists(file_path):
            raise ETLError(f"Positional Parquet file not found: {file_path}")
        
        try:
            # Set schema
            self.set_schema(schema_config)
            
            # Read the raw data from Parquet (assuming it contains fixed-position strings)
            df = pl.read_parquet(file_path)
            
            # Check if we have the expected column structure
            if df.width == 0:
                raise ETLError("Parquet file is empty")
            
            # Assume the first column contains the fixed-position data
            # If there are multiple columns, we'll use the first one
            data_column = df.columns[0]
            
            # Parse the fixed-position data
            parsed_df = self._parse_positional_data(df.select(data_column))
            
            return parsed_df
            
        except Exception as e:
            raise ETLError(f"Failed to read positional Parquet file: {e}") from e
    
    def _parse_positional_data(self, df: pl.DataFrame) -> pl.DataFrame:
        """Parse fixed-position data according to schema"""
        if not self.schema:
            raise ETLError("Schema not set for positional parsing")
        
        data_column = df.columns[0]
        expressions = []
        
        for field in self.schema.fields:
            # Extract substring for this field
            start_pos = field["start"] - 1  # Convert to 0-based indexing
            end_pos = field["end"]
            
            # Create expression to extract field
            field_expr = pl.col(data_column).str.slice(start_pos, field["length"]).alias(field["name"])
            
            # Apply type conversion and formatting
            field_expr = self._apply_field_conversion(field_expr, field)
            
            expressions.append(field_expr)
        
        # Apply all field extractions
        result_df = df.select(expressions)
        
        return result_df
    
    def _apply_field_conversion(self, field_expr: pl.Expr, field: Dict[str, Any]) -> pl.Expr:
        """Apply type conversion and formatting to field expression"""
        field_type = field["type"]
        
        if field_type == "string":
            # Handle padding
            if field["padding"] == "left":
                field_expr = field_expr.str.strip_chars_start(field["pad_char"])
            elif field["padding"] == "right":
                field_expr = field_expr.str.strip_chars_end(field["pad_char"])
            # For "none", keep as-is
            return field_expr.cast(pl.Utf8)
        
        elif field_type == "integer":
            # Strip padding and convert to integer
            if field["padding"] in ["left", "right"]:
                field_expr = field_expr.str.strip_chars(field["pad_char"])
            return field_expr.cast(pl.Int64, strict=False)
        
        elif field_type == "decimal":
            # Handle decimal with specified precision
            if field["padding"] in ["left", "right"]:
                field_expr = field_expr.str.strip_chars(field["pad_char"])
            return field_expr.cast(pl.Float64, strict=False)
        
        elif field_type == "date":
            # Handle date formatting
            if field["padding"] in ["left", "right"]:
                field_expr = field_expr.str.strip_chars(field["pad_char"])
            
            date_format = field.get("format", "%Y%m%d")
            try:
                return field_expr.str.strptime(pl.Date, date_format, strict=False)
            except:
                # If date parsing fails, return as string
                return field_expr.cast(pl.Utf8)
        
        else:
            # Unknown type, return as string
            return field_expr.cast(pl.Utf8)


def read_positional_parquet_file(file_path: str, schema_config: Dict[str, Any]) -> pl.DataFrame:
    """
    Convenience function to read fixed-position Parquet file
    
    Args:
        file_path: Path to Parquet file containing fixed-position data
        schema_config: Schema configuration for parsing
        
    Returns:
        Polars DataFrame with parsed fields
    """
    reader = PositionalReader()
    return reader.read_positional_parquet(file_path, schema_config)


# Example schema configuration
EXAMPLE_POSITIONAL_SCHEMA = {
    "fields": [
        {
            "name": "customer_id",
            "start": 1,
            "length": 10,
            "type": "string",
            "padding": "right",
            "pad_char": " "
        },
        {
            "name": "account_number",
            "start": 11,
            "length": 15,
            "type": "string",
            "padding": "left",
            "pad_char": "0"
        },
        {
            "name": "balance",
            "start": 26,
            "length": 12,
            "type": "decimal",
            "padding": "left",
            "pad_char": "0"
        },
        {
            "name": "transaction_date",
            "start": 38,
            "length": 8,
            "type": "date",
            "format": "%Y%m%d",
            "padding": "none"
        },
        {
            "name": "status",
            "start": 46,
            "length": 1,
            "type": "string",
            "padding": "none"
        }
    ]
}
