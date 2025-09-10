# Positional File Processing Guide

The ETL Engine now supports processing fixed-width/positional files stored in Parquet format. This guide explains how to use this feature.

## Overview

Positional files contain data where each field is located at a specific position within each record. The ETL Engine can parse these files using a schema definition that specifies the position, length, and type of each field.

## API Usage

### Endpoint
```
POST /transform
```

### Parameters

1. **parquet_file** (required): The Parquet file containing positional data
2. **mapping_file** (required): JSON file with transformation mappings
3. **schema_file** (optional): JSON file with positional schema definition
4. **layout** (optional): JSON string with positional schema definition (takes priority over schema_file)

### Schema Definition Format

The positional schema is defined as a JSON object with a `fields` array:

```json
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
```

#### Field Properties

- **name**: The name of the field in the output
- **start**: Starting position (1-based)
- **length**: Number of characters for this field
- **type**: Data type (`string`, `integer`, `decimal`, `date`)
- **format**: Format string for date fields (e.g., `%Y%m%d`)
- **padding**: How to handle padding (`left`, `right`, `none`)
- **pad_char**: Character used for padding (default: space)

## Usage Examples

### Example 1: Using Layout Parameter

```python
import requests
import json

# Define the positional layout
layout = {
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
        }
    ]
}

# Create mapping
mapping = {
    "output_path": "output",
    "output_format": "csv",
    "mappings": [
        {
            "id": "m1",
            "trns": "DIRECT[ATTR(customer_id)]",
            "affected_source": "customer_id",
            "affected_target": "customer_id"
        },
        {
            "id": "m2",
            "trns": "MATH[ROUND(ATTR(balance), 2)]",
            "affected_source": "balance",
            "affected_target": "balance_rounded"
        }
    ]
}

# Send request
with open("data.parquet", "rb") as pf, open("mapping.json", "rb") as mf:
    files = {
        "parquet_file": ("data.parquet", pf, "application/octet-stream"),
        "mapping_file": ("mapping.json", mf, "application/json")
    }
    data = {"layout": json.dumps(layout)}
    
    response = requests.post("http://localhost:8000/transform", files=files, data=data)
```

### Example 2: Using Schema File

```python
import requests

# Create schema file
schema = {
    "fields": [
        {
            "name": "account_number",
            "start": 11,
            "length": 15,
            "type": "string",
            "padding": "left",
            "pad_char": "0"
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

with open("schema.json", "w") as f:
    json.dump(schema, f, indent=2)

# Send request
with open("data.parquet", "rb") as pf, \
     open("mapping.json", "rb") as mf, \
     open("schema.json", "rb") as sf:
    
    files = {
        "parquet_file": ("data.parquet", pf, "application/octet-stream"),
        "mapping_file": ("mapping.json", mf, "application/json"),
        "schema_file": ("schema.json", sf, "application/json")
    }
    
    response = requests.post("http://localhost:8000/transform", files=files)
```

### Example 3: cURL Command

```bash
curl -X POST "http://localhost:8000/transform" \
  -F "parquet_file=@data.parquet" \
  -F "mapping_file=@mapping.json" \
  -F 'layout={"fields":[{"name":"customer_id","start":1,"length":10,"type":"string","padding":"right","pad_char":" "}]}'
```

## Data Types

### String
- **Type**: `"string"`
- **Padding**: Removes specified padding characters
- **Example**: `"CUST001    "` → `"CUST001"`

### Integer
- **Type**: `"integer"`
- **Padding**: Removes padding and converts to integer
- **Example**: `"0000012345"` → `12345`

### Decimal
- **Type**: `"decimal"`
- **Padding**: Removes padding and converts to float
- **Example**: `"000012345.67"` → `12345.67`

### Date
- **Type**: `"date"`
- **Format**: Uses Python strptime format strings
- **Example**: `"20240101"` with format `"%Y%m%d"` → `2024-01-01`

## Padding Options

- **left**: Remove padding from the left side
- **right**: Remove padding from the right side
- **none**: Keep padding as-is

## Priority

When both `layout` parameter and `schema_file` are provided, the `layout` parameter takes priority.

## Error Handling

The API will return appropriate error messages for:
- Invalid JSON in layout parameter
- Missing required fields in schema
- Invalid field types
- Position conflicts in schema definition

## Performance

Positional file processing is optimized for:
- Large files with many records
- Complex field definitions
- Multiple data types
- Various padding configurations

The processing time depends on:
- Number of records
- Number of fields
- Complexity of transformations
- Output format
