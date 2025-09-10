# ETL Engine (FastAPI + Polars)

A high-performance ETL engine built with FastAPI and Polars, designed for processing large datasets efficiently.

## Features

- **Fast Data Processing**: Built on Polars for high-performance data manipulation
- **Multiple Input/Output Formats**: Supports CSV, XLSX, JSON, XML, and positional formats
- **Flexible Transformations**: Rich transformation language with support for complex operations
- **RESTful API**: Clean FastAPI interface with automatic documentation
- **Comprehensive Logging**: Detailed logging for debugging and monitoring
- **Error Handling**: Robust error handling with cleanup on failures

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd etl_engine
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Health Check
- **GET** `/health` - Check if the service is running

### Transform Data
- **POST** `/transform` - Transform data using uploaded files

## Usage

### 1. Prepare Your Data
- **Input**: Parquet file containing your data
- **Mapping**: JSON file defining transformations and output format

### 2. Create Mapping Configuration
Example mapping file (`mapping.json`):
```json
{
  "output_path": "output/customers",
  "output_format": "csv",
  "xml_config": {
    "root_tag": "customers",
    "row_tag": "customer"
  },
  "mappings": [
    {
      "source": "firstName",
      "target": "full_name",
      "transform": "trns: STRING[CONCAT(attr('firstName'), ' ', attr('lastName'))]"
    },
    {
      "source": "age",
      "target": "age_validated",
      "validate": ">=0 and <=120"
    }
  ]
}
```

### 3. Transform Data
```bash
curl -X POST "http://localhost:8000/transform" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "parquet_file=@data.parquet" \
  -F "mapping_file=@mapping.json"
```

## Transformation Language

### Basic Transforms
- `to_int`, `to_float`, `to_str`, `to_bool`
- `trim`, `upper`, `lower`
- `date_format('YYYY-MM-DD')`
- `to_date('MMDDYYYY')`

### Advanced Transforms
- **STRING**: `CONCAT`, `SUBSTR`, `REPLACE`, `UPPER`, `LOWER`, `TRIM`, `LENGTH`
- **MATH**: `ADD`, `SUB`, `MUL`, `DIV`, `MOD`, `ROUND`, `ABS`
- **LOGICAL**: `IF`, `AND`, `OR`, `NOT`
- **DATE**: `FORMAT`, `PARSE`, `ADD_DAYS`, `SUB_DAYS`, `DIFF_DAYS`, `CURRENT_DATE`, `EXTRACT`
- **ARRAY**: `JOIN`, `SPLIT`, `LENGTH`, `GET`
- **FILTERS**: `INCLUDE_IF`, `EXCLUDE_IF`, `LIMIT`, `OFFSET`

### Examples
```json
{
  "transform": "trns: STRING[CONCAT(attr('first'), ' ', attr('last'))]"
}
{
  "transform": "trns: LOGICAL[IF(attr('age') > 18, 'Adult', 'Minor')]"
}
{
  "transform": "trns: DATE[FORMAT(attr('dob'), 'YYYY-MM-DD')]"
}
```

## Output Formats

- **CSV**: Standard comma-separated values
- **XLSX**: Excel format with automatic chunking for large datasets
- **JSON**: Newline-delimited JSON (JSONL)
- **XML**: Customizable XML with configurable tags
- **Positional**: Fixed-width text format

## Configuration

### Environment Variables
- `ETL_OUTPUT_DIR`: Output directory (default: "output")
- `ETL_LOGS_DIR`: Logs directory (default: "logs")

### File Structure
```
etl_engine/
├── app/
│   ├── main.py          # FastAPI application
│   ├── reader.py        # Data reading logic
│   ├── transformer.py   # Data transformation logic
│   ├── writer.py        # Output writing logic
│   ├── utils.py         # Utility functions
│   ├── exceptions.py    # Custom exceptions
│   └── logger.py        # Logging configuration
├── config/
│   └── sample_mapping.json
├── requirements.txt
└── README.md
```

## Error Handling

The API provides detailed error messages for:
- Invalid file formats
- Malformed mapping configurations
- Transformation failures
- Output writing errors
- Validation rule violations

## Performance Features

- **Chunked Processing**: Large Excel files are automatically split into sheets
- **Memory Efficient**: Uses Polars for fast, memory-efficient data processing
- **Parallel Processing**: Polars provides parallel execution where possible

## Development

### Running Tests
```bash
# Add tests to your project and run with:
pytest
```

### Code Quality
- Type hints throughout the codebase
- Comprehensive error handling
- Detailed logging
- Clean separation of concerns

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]
