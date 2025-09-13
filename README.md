# ETL Engine v2

A high-performance ETL engine built with FastAPI and Polars, supporting schema-driven transformations with source and target schema definitions.

## Features

- **Schema-Driven**: Define source and target schemas for data validation and transformation
- **Multiple Formats**: Support for Parquet, CSV, JSON, XML, Excel, and Fixed-Width output
- **Flexible Transformations**: Rich transformation language with support for complex operations
- **RESTful API**: Clean FastAPI interface with automatic documentation
- **High Performance**: Built on Polars for fast, memory-efficient data processing
- **Type Safety**: Full Pydantic model validation

## Quick Start

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Start the Server

```bash
uvicorn app.main:app --reload
```

### 3. Test the API

```bash
curl -X POST 'http://localhost:8000/transform' \
  -H 'Content-Type: application/json' \
  -d @etl_request_example.json
```

### 4. View Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## API Usage

### Endpoint

**POST** `/transform` - Transform data using JSON configuration

### Request Format

```json
{
  "source_file_path": "path/to/input.parquet",
  "source_schema": {
    "role": "source",
    "fileType": "parquet",
    "schemaId": "schm-parquet-1001",
    "schemaName": "customer_parquet_v1",
    "attributes": {
      "first_name": {
        "name": "first_name",
        "dataType": "string",
        "column_no": 1
      }
    }
  },
  "target_schema": {
    "role": "target",
    "fileType": "fixedWidth",
    "schemaId": "schm-fix-2001",
    "schemaName": "customer_fixedwidth_v1",
    "attributes": {
      "first_name": {
        "name": "first_name",
        "dataType": "string",
        "start_pos": 1,
        "width": 20
      }
    }
  },
  "mapping_config": {
    "mappingId": "mapping-001",
    "mappingName": "customer_parquet_to_fixedwidth",
    "createdAt": "2025-09-11T07:32:22.113Z",
    "sourceSchemaId": "schm-parquet-1001",
    "targetSchemaId": "schm-fix-2001",
    "rules": [
      {
        "id": "r1",
        "trns": "DIRECT[ATTR(first_name)]",
        "affected_source": ["first_name"],
        "affected_target": "first_name"
      }
    ]
  },
  "output_path": "output/result",
  "output_format": "fixedwidth"
}
```

### Response Format

```json
{
  "status": "success",
  "run_id": "20250911_143022",
  "input_rows": 1000,
  "output_rows": 1000,
  "processing_time_ms": 1250.5,
  "throughput_rows_per_sec": 800,
  "output_path": "output/result_20250911_143022.txt"
}
```

## Schema Definitions

### Source Schema

Defines the structure of your input data:

```json
{
  "role": "source",
  "fileType": "parquet",
  "schemaId": "schm-parquet-1001",
  "schemaName": "customer_parquet_v1",
  "attributes": {
    "field_name": {
      "name": "field_name",
      "dataType": "string",
      "column_no": 1
    }
  }
}
```

### Target Schema

Defines the structure of your output data:

```json
{
  "role": "target",
  "fileType": "fixedWidth",
  "schemaId": "schm-fix-2001",
  "schemaName": "customer_fixedwidth_v1",
  "attributes": {
    "field_name": {
      "name": "field_name",
      "dataType": "string",
      "start_pos": 1,
      "width": 20
    }
  }
}
```

## Transformation Language

### Basic Operations

- `DIRECT[ATTR('column')]` - Direct field mapping
- `STRING[CONCAT(attr('col1'), ' ', attr('col2'))]` - String concatenation
- `DATE[FORMAT(attr('date_col'), 'YYYY-MM-DD')]` - Date formatting
- `STRING[TRIM(ATTR('column'))]` - String trimming

### Advanced Operations

- **STRING**: `CONCAT`, `SUBSTR`, `REPLACE`, `UPPER`, `LOWER`, `TRIM`, `LENGTH`
- **MATH**: `ADD`, `SUB`, `MUL`, `DIV`, `MOD`, `ROUND`, `ABS`
- **LOGICAL**: `IF`, `AND`, `OR`, `NOT`
- **DATE**: `FORMAT`, `PARSE`, `ADD_DAYS`, `SUB_DAYS`, `DIFF_DAYS`, `CURRENT_DATE`, `EXTRACT`
- **ARRAY**: `JOIN`, `SPLIT`, `LENGTH`, `GET`
- **FILTERS**: `INCLUDE_IF`, `EXCLUDE_IF`, `LIMIT`, `OFFSET`

## Supported File Types

### Input
- **Parquet** - Primary format with automatic struct flattening

### Output
- **CSV** - Comma-separated values
- **JSON** - Newline-delimited JSON (JSONL)
- **JSON Array** - Traditional JSON array format
- **Excel** - XLSX format with automatic chunking for large datasets
- **XML** - Customizable XML with configurable tags
- **Fixed-Width** - Fixed-width text format with precise positioning

## Project Structure

```
etl_engine/
├── app/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic data models
│   ├── enhanced_reader.py   # Data reading logic
│   ├── transformer.py       # Data transformation logic
│   ├── writer.py            # Output writing logic
│   ├── utils.py             # Utility functions
│   ├── exceptions.py        # Custom exceptions
│   └── logger.py            # Logging configuration
├── etl_request_example.json # Example API request
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Error Handling

The API provides detailed error messages for:
- Invalid file paths
- Malformed schema definitions
- Transformation failures
- Output writing errors
- Validation rule violations

## Performance Features

- **Chunked Processing**: Large Excel files are automatically split into sheets
- **Memory Efficient**: Uses Polars for fast, memory-efficient data processing
- **Parallel Processing**: Polars provides parallel execution where possible
- **Schema Validation**: Early validation prevents processing errors

## Development

### Running Tests

```bash
python -c "
import json
from app.models import ETLRequest
from app.enhanced_reader import read_data_file
from app.transformer import apply_transformations
from app.writer import write_fixed_width

# Load example request
with open('etl_request_example.json') as f:
    request_data = json.load(f)

request = ETLRequest(**request_data)
print('✅ ETL Engine v2 is working correctly!')
"
```

### Code Quality

- Type hints throughout the codebase
- Comprehensive error handling
- Detailed logging
- Clean separation of concerns
- Pydantic model validation

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.