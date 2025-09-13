# Multi-Engine ETL System

This is a multi-engine ETL (Extract, Transform, Load) system designed for parallel processing and inter-engine communication.

## Architecture

```
root/
├── client/                    # Client applications and interfaces
├── exp/                      # Experience Engine (separate service)
├── parsingEngine/            # Parsing Engine (separate service)
├── transformationEngine/     # Transformation Engine (this repository)
│   ├── app/                  # Core transformation application
│   │   ├── main.py          # FastAPI application with endpoints
│   │   ├── reader.py        # Data reading functionality
│   │   ├── transformer.py   # Advanced transformation engine
│   │   ├── writer.py        # Output writing functionality
│   │   ├── utils.py         # Utility functions and parsing
│   │   ├── logger.py        # Logging configuration
│   │   └── exceptions.py    # Custom exception classes
│   ├── requirements.txt     # Python dependencies
│   ├── start.py            # Startup script
│   └── README.md           # Transformation engine documentation
├── storage/                 # Shared storage for all engines
│   ├── input/              # Input files (e.g., lsad.parquet)
│   ├── transformed/        # Output files (e.g., lsad.json)
│   └── logs/              # Log files from all engines
└── README.md              # This file
```

## Engines

### 1. Transformation Engine (Port 8001)
- **Purpose**: Handles data transformation operations
- **Features**: 100% permutation combination support, advanced parsing tree
- **API**: RESTful API with file-based processing
- **Storage**: Reads from `storage/input/`, writes to `storage/transformed/`

### 2. Parsing Engine (Port 8002)
- **Purpose**: Handles data parsing and validation
- **Features**: Multi-format parsing, schema validation
- **API**: RESTful API for parsing operations
- **Storage**: Reads from `storage/input/`, writes to `storage/transformed/`

### 3. Experience Engine (Port 8003)
- **Purpose**: Handles user experience and interface operations
- **Features**: UI components, user interactions
- **API**: RESTful API for experience operations
- **Storage**: Reads from `storage/transformed/`, writes to `storage/transformed/`

## Quick Start

### 1. Start Transformation Engine
```bash
cd transformationEngine
pip install -r requirements.txt
python start.py
```

The transformation engine will start on `http://localhost:8001`

### 2. Test the System
```bash
python test_transformation_engine.py
```

### 3. API Documentation
- Transformation Engine: http://localhost:8001/docs
- Parsing Engine: http://localhost:8002/docs (when running)
- Experience Engine: http://localhost:8003/docs (when running)

## File Processing Flow

1. **Input**: Files are placed in `storage/input/`
2. **Processing**: Engines process files from `storage/input/`
3. **Output**: Processed files are saved to `storage/transformed/`
4. **Logs**: All operations are logged to `storage/logs/`

## Example Usage

### Transform a Parquet File
```bash
# Place input file
cp your_data.parquet storage/input/lsad.parquet

# Send transformation request
curl -X POST "http://localhost:8001/transform-file" \
  -H "Content-Type: application/json" \
  -d '{
    "input_filename": "lsad.parquet",
    "output_filename": "lsad_transformed.json",
    "output_format": "json",
    "mapping_config": {
      "mappings": [
        {
          "target": "full_name",
          "source": "firstName,lastName",
          "transform": "trns: STRING[CONCAT(attr(\"firstName\"), \" \", attr(\"lastName\"))]"
        }
      ]
    }
  }'

# Check output
ls storage/transformed/
```

## Storage Structure

### Input Files (`storage/input/`)
- Raw data files in various formats (CSV, Parquet, JSON, XLSX, XML)
- Files are processed by engines based on API requests
- Example: `lsad.parquet`, `customer_data.csv`

### Transformed Files (`storage/transformed/`)
- Processed and transformed data files
- Output format depends on the transformation request
- Example: `lsad.json`, `customer_data_transformed.xlsx`

### Log Files (`storage/logs/`)
- Detailed logs from all engines
- Timestamped with run IDs for traceability
- Example: `etl_20250913_133500_abc123.log`

## Inter-Engine Communication

Engines communicate through:
1. **Shared Storage**: Files in `storage/` directory
2. **REST APIs**: HTTP requests between engines
3. **Logging**: Centralized logging in `storage/logs/`

## Development

### Adding New Engines
1. Create new engine directory (e.g., `newEngine/`)
2. Implement FastAPI application
3. Use shared storage for file I/O
4. Add to this README

### Modifying Transformation Engine
1. Edit files in `transformationEngine/app/`
2. Test with `test_transformation_engine.py`
3. Update `transformationEngine/README.md`

## Monitoring

- **Health Checks**: Each engine provides `/health` endpoint
- **Logs**: Centralized in `storage/logs/`
- **File Tracking**: Monitor `storage/input/` and `storage/transformed/`

## Troubleshooting

### Common Issues
1. **Port Conflicts**: Ensure each engine uses different ports
2. **File Permissions**: Check read/write access to `storage/` directory
3. **Dependencies**: Install requirements for each engine
4. **Path Issues**: Use relative paths from engine directories

### Debug Steps
1. Check engine health: `curl http://localhost:8001/health`
2. Check logs: `ls storage/logs/`
3. Check file permissions: `ls -la storage/`
4. Test with sample data: `python test_transformation_engine.py`