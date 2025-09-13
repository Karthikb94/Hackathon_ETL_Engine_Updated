# ETL Engine v1

A simple and powerful ETL (Extract, Transform, Load) engine built with FastAPI and Polars. This version focuses on ease of use with file uploads and straightforward mapping configurations.

## Features

- **Simple File Upload**: Upload data files and mapping configurations via web interface
- **Multiple Input Formats**: Support for CSV, Parquet, and JSON files
- **Multiple Output Formats**: CSV, JSON, Excel, XML, and Fixed-Width output
- **Rich Transformations**: Powerful transformation language for data manipulation
- **RESTful API**: Clean FastAPI interface with automatic documentation
- **High Performance**: Built on Polars for fast, memory-efficient data processing

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
# Test with curl
curl -X POST 'http://localhost:8000/transform' \
  -F 'data_file=@sample_data.csv' \
  -F 'mapping_file=@mapping_example.json' \
  -F 'output_format=csv'
```

### 4. View Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## API Usage

### Endpoint

**POST** `/transform` - Transform data using uploaded files

### Parameters

- `data_file` (file): Input data file (CSV, Parquet, or JSON)
- `mapping_file` (file): JSON file containing transformation mappings
- `output_format` (string): Output format (csv, json, xlsx, xml, fixed_width)
- `output_path` (string, optional): Output file path

### Response

```json
{
  "status": "success",
  "run_id": "20250911_143022",
  "input_rows": 1000,
  "output_rows": 1000,
  "processing_time_ms": 1250.5,
  "throughput_rows_per_sec": 800,
  "output_path": "output/run_20250911_143022/output_20250911_143022.csv",
  "input_file": "sample_data.csv",
  "output_format": "csv"
}
```

## Mapping Configuration

Create a JSON file with your transformation mappings:

```json
{
  "mappings": [
    {
      "target": "full_name",
      "source": "first_name,last_name",
      "transform": "trns: STRING[CONCAT(attr('first_name'), ' ', attr('last_name'))]"
    },
    {
      "target": "email_clean",
      "source": "email",
      "transform": "trns: STRING[TRIM(ATTR(email))]"
    },
    {
      "target": "age_group",
      "source": "age",
      "transform": "trns: LOGICAL[IF(attr('age') >= 18, 'Adult', 'Minor')]"
    }
  ]
}
```

### Mapping Fields

- `target`: Name of the output column
- `source`: Source column(s) - comma-separated for multiple columns
- `transform`: Transformation expression (optional)
- `default`: Default value if source is missing (optional)

## Transformation Language

### Basic Operations

- `to_int`, `to_float`, `to_str`, `to_bool` - Type conversions
- `trim`, `upper`, `lower` - String operations
- `date_format('YYYY-MM-DD')` - Date formatting

### Advanced Operations

- **STRING**: `CONCAT`, `SUBSTR`, `REPLACE`, `UPPER`, `LOWER`, `TRIM`, `LENGTH`
- **MATH**: `ADD`, `SUB`, `MUL`, `DIV`, `MOD`, `ROUND`, `ABS`
- **LOGICAL**: `IF`, `AND`, `OR`, `NOT`
- **DATE**: `FORMAT`, `PARSE`, `ADD_DAYS`, `SUB_DAYS`, `DIFF_DAYS`, `CURRENT_DATE`, `EXTRACT`
- **ARRAY**: `JOIN`, `SPLIT`, `LENGTH`, `GET`
- **FILTERS**: `INCLUDE_IF`, `EXCLUDE_IF`, `LIMIT`, `OFFSET`

### Examples

```json
{
  "target": "full_name",
  "source": "first_name,last_name",
  "transform": "trns: STRING[CONCAT(attr('first_name'), ' ', attr('last_name'))]"
}
```

```json
{
  "target": "is_adult",
  "source": "age",
  "transform": "trns: LOGICAL[IF(attr('age') >= 18, 'Yes', 'No')]"
}
```

```json
{
  "target": "formatted_date",
  "source": "dob",
  "transform": "trns: DATE[FORMAT(attr('dob'), 'YYYY-MM-DD')]"
}
```

## Supported File Types

### Input
- **CSV** - Comma-separated values
- **Parquet** - Columnar format with automatic struct flattening
- **JSON** - JSON and JSONL formats

### Output
- **CSV** - Comma-separated values
- **JSON** - Newline-delimited JSON (JSONL)
- **JSON Array** - Traditional JSON array format
- **Excel** - XLSX format with automatic chunking for large datasets
- **XML** - Customizable XML with configurable tags
- **Fixed-Width** - Fixed-width text format

## Project Structure

```
etl_engine/
├── app/
│   ├── main.py              # FastAPI application
│   ├── reader.py            # Data reading logic
│   ├── transformer.py       # Data transformation logic
│   ├── writer.py            # Output writing logic
│   ├── utils.py             # Utility functions
│   ├── exceptions.py        # Custom exceptions
│   └── logger.py            # Logging configuration
├── mapping_example.json     # Example mapping configuration
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Testing

Run the test script to verify everything works:

```bash
python test_etl_v1.py
```

This will:
1. Create sample data
2. Test all components
3. Generate example output files
4. Show you how to use the API

## Error Handling

The API provides detailed error messages for:
- Invalid file formats
- Malformed mapping configurations
- Transformation failures
- Output writing errors
- Missing required fields

## Performance Features

- **Chunked Processing**: Large Excel files are automatically split into sheets
- **Memory Efficient**: Uses Polars for fast, memory-efficient data processing
- **Parallel Processing**: Polars provides parallel execution where possible
- **Auto-cleanup**: Temporary files are automatically cleaned up after processing

## Examples

### Simple Field Mapping

```json
{
  "mappings": [
    {
      "target": "customer_name",
      "source": "name"
    }
  ]
}
```

### String Concatenation

```json
{
  "mappings": [
    {
      "target": "full_address",
      "source": "street,city,state",
      "transform": "trns: STRING[CONCAT(attr('street'), ', ', attr('city'), ', ', attr('state'))]"
    }
  ]
}
```

### Conditional Logic

```json
{
  "mappings": [
    {
      "target": "status",
      "source": "age",
      "transform": "trns: LOGICAL[IF(attr('age') >= 18, 'Adult', 'Minor')]"
    }
  ]
}
```

### Data Filtering

```json
{
  "mappings": [
    {
      "target": "filtered_data",
      "source": "all_data",
      "transform": "trns: FILTERS[INCLUDE_IF(attr('age') >= 18)]"
    }
  ]
}
```

## Development

### Code Quality

- Type hints throughout the codebase
- Comprehensive error handling
- Detailed logging
- Clean separation of concerns

### Running Tests

```bash
python test_etl_v1.py
```

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.