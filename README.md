# ETL Engine

A powerful and flexible ETL (Extract, Transform, Load) engine built with FastAPI and Polars for high-performance data processing.

## Quick Start

### Start the ETL Engine
```bash
python run.py
```

## Features

- **Fast Data Processing**: Built on Polars for high-performance data operations
- **Multiple Input Formats**: Supports CSV, Parquet, JSON, XML, and fixed-width files
- **Flexible Transformations**: Advanced transformation engine with support for complex expressions
- **REST API**: Full REST API with automatic documentation
- **Error Handling**: Comprehensive error tracking and detailed error reports
- **Schema Support**: Full schema validation and type casting

## API Endpoints

Once running, the ETL Engine provides:

- **Health Check**: `GET /health` - Service health status
- **Transform Data**: `POST /transform` - Main ETL transformation endpoint
- **API Documentation**: `http://localhost:8001/docs` - Interactive API docs
- **Alternative Docs**: `http://localhost:8001/redoc` - Alternative API documentation

## Requirements

- Python 3.8+
- Dependencies are automatically installed when using `run.py`

## Project Structure

```
├── run.py                    # Main runner script
├── transformationEngine/     # Core ETL engine
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── reader.py        # Data reading modules
│   │   ├── writer.py        # Data writing modules
│   │   ├── transformer.py   # Transformation engine
│   │   ├── utils.py         # Utility functions
│   │   ├── logger.py        # Logging configuration
│   │   ├── error_handler.py # Error handling
│   │   └── exceptions.py    # Custom exceptions
│   └── requirements.txt     # Python dependencies
├── storage/                 # Data storage directories
│   ├── input/              # Input data files
│   ├── transformed/        # Output data files
│   ├── logs/               # Log files
│   └── transformation_error/ # Error reports
└── config/                 # Configuration files
```

## Usage

1. Place your input data files in `storage/input/`
2. Run the ETL Engine: `python run.py`
3. The script will automatically:
   - Check Python version and dependencies
   - Install missing packages if needed
   - Verify directory structure
   - Start the server
4. Access the API documentation at `http://localhost:8001/docs`
5. Send transformation requests to the `/transform` endpoint
6. Find transformed data in `storage/transformed/`
7. Check logs in `storage/logs/` for processing details

## Configuration

The ETL Engine uses JSON configuration files for:
- Source and target schemas
- Transformation mappings
- Field definitions and data types

Example configurations are provided in the `config/` directory.

## Error Handling

The engine provides comprehensive error handling:
- Detailed error reports in `storage/transformation_error/`
- Processing logs in `storage/logs/`
- Graceful handling of data validation errors
- Schema validation and type checking

## Performance

- Built on Polars for high-performance data processing
- Supports large datasets with efficient memory usage
- Parallel processing capabilities
- Optimized for both speed and memory efficiency
