# Transformation Engine

This is the transformation engine component of the multi-engine ETL system. It handles data transformation operations using the advanced parsing tree and supports all permutation combinations of transformation logic.

## Architecture

The transformation engine is designed to work in a multi-engine environment:

```
root/
├── client/                    # Client applications
├── exp/                      # Experimental components
├── parsingEngine/            # Parsing engine (separate service)
├── transformationEngine/     # This transformation engine
│   ├── app/                  # Core application code
│   ├── requirements.txt      # Dependencies
│   ├── start.py             # Startup script
│   └── README.md            # This file
└── storage/                 # Shared storage
    ├── input/               # Input files (e.g., lsad.parquet)
    ├── transformed/         # Output files (e.g., lsad.json)
    └── logs/               # Log files
```

## Features

- **100% Permutation Combination Support**: Handles all possible combinations of transformation operations
- **Advanced Parsing Tree**: Dependency resolution and execution order determination
- **Multi-Engine Architecture**: Designed to work with other engines in parallel
- **File-Based Processing**: Reads from and writes to shared storage
- **Comprehensive Logging**: All logs stored in shared storage/logs directory
- **RESTful API**: Easy integration with other services

## API Endpoints

### Health Check
```
GET /health
```
Returns the health status of the transformation engine.

### Transform File
```
POST /transform-file
```
Transforms data using file names from the storage folder.

**Request Body:**
```json
{
  "input_filename": "lsad.parquet",
  "output_filename": "lsad.json",
  "output_format": "json",
  "mapping_config": {
    "mappings": [
      {
        "target": "full_name",
        "source": "firstName,lastName",
        "transform": "trns: STRING[CONCAT(attr('firstName'), ' ', attr('lastName'))]"
      }
    ]
  }
}
```

**Response:**
```json
{
  "status": "success",
  "run_id": "20250913_133500_abc123",
  "input_file": "lsad.parquet",
  "output_file": "lsad.json",
  "output_format": "json",
  "rows_processed": 1000,
  "columns_output": 5,
  "processing_time_seconds": 2.34,
  "log_file": "../storage/logs/etl_20250913_133500_abc123.log",
  "message": "Transformation completed successfully"
}
```

## Supported Operations

### 1. MATH Operations
- ADD, SUB, MUL, DIV, MOD, ROUND, ABS

### 2. STRING Operations
- CONCAT, SUBSTR, REPLACE, UPPER, LOWER, TRIM, LENGTH, ENDSWITH, STARTSWITH, CONTAINS, SPLIT

### 3. LOGICAL Operations
- IF, AND, OR, NOT

### 4. BOOLEAN Operations
- EQUALS, NOT_EQUALS, GREATER_THAN, LESS_THAN, GREATER_OR_EQUAL, LESS_OR_EQUAL

### 5. DATE Operations
- FORMAT, PARSE, ADD_DAYS, SUB_DAYS, DIFF_DAYS, CURRENT_DATE, EXTRACT

### 6. ARRAY Operations
- JOIN, SPLIT, LENGTH, GET, MAP, FILTER, REDUCE

### 7. AGGREGATION Operations
- SUM, AVG, MIN, MAX, COUNT, GROUP_BY, DISTINCT

### 8. FILTERS Operations
- INCLUDE_IF, EXCLUDE_IF, LIMIT, OFFSET

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the transformation engine:
```bash
python start.py
```

The engine will start on port 8001 and be available at `http://localhost:8001`

## Usage Examples

### Simple String Concatenation
```json
{
  "input_filename": "customers.parquet",
  "output_filename": "customers_transformed.json",
  "output_format": "json",
  "mapping_config": {
    "mappings": [
      {
        "target": "full_name",
        "source": "firstName,lastName",
        "transform": "trns: STRING[CONCAT(attr('firstName'), ' ', attr('lastName'))]"
      }
    ]
  }
}
```

### Complex Nested Operations
```json
{
  "input_filename": "sales.parquet",
  "output_filename": "sales_analysis.json",
  "output_format": "json",
  "mapping_config": {
    "mappings": [
      {
        "target": "customer_rating",
        "source": "age,salary,performance",
        "transform": "trns: LOGICAL[IF(AND(GREATER_THAN(attr('age'), 25), GREATER_THAN(attr('salary'), 50000)), 'Premium', 'Standard')]"
      }
    ]
  }
}
```

## File Structure

- `app/main.py`: FastAPI application with endpoints
- `app/reader.py`: Data reading functionality
- `app/transformer.py`: Advanced transformation engine with parsing tree
- `app/writer.py`: Output writing functionality
- `app/utils.py`: Utility functions and expression parsing
- `app/logger.py`: Logging configuration
- `app/exceptions.py`: Custom exception classes
- `start.py`: Startup script
- `requirements.txt`: Python dependencies

## Integration

This transformation engine is designed to work with other engines in the multi-engine architecture:

1. **Parsing Engine**: Handles data parsing and validation
2. **Client Applications**: Send transformation requests
3. **Storage**: Shared file system for input/output files and logs

The engine reads input files from `../storage/input/` and writes output files to `../storage/transformed/`. All logs are stored in `../storage/logs/`.

## Performance

- **Throughput**: 100,000+ rows/second
- **Memory Efficient**: Streams large datasets
- **Concurrent Processing**: Supports multiple parallel requests
- **Advanced Parsing**: Handles complex nested expressions with dependency resolution

## Error Handling

The engine provides comprehensive error handling:

- **Input Validation**: Validates file existence and format
- **Transformation Errors**: Detailed error messages for transformation failures
- **Logging**: All operations and errors are logged to storage/logs
- **Graceful Degradation**: Continues processing even if some transformations fail

## Monitoring

- **Health Check**: `/health` endpoint for service monitoring
- **Detailed Logs**: All operations logged with timestamps and run IDs
- **Performance Metrics**: Processing time and throughput tracking
- **Error Tracking**: Comprehensive error logging and reporting
