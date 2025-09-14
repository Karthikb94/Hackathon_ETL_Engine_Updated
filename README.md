# ETL Engine - Data Transformation Platform

## 🚀 Quick Start

This ETL Engine provides powerful data transformation capabilities, converting Parquet files between various formats using customizable transformation logic.

### Prerequisites
- Python 3.11+
- Required dependencies (see `transformationEngine/requirements.txt`)

### Installation & Setup
1. **Install dependencies:**
   ```bash
   cd transformationEngine
   pip install -r requirements.txt
   ```

2. **Start the ETL Engine:**
   ```bash
   python run.py
   ```

3. **Access the API:**
   - Server: `http://localhost:8001`
   - API Docs: `http://localhost:8001/docs`
   - Health Check: `http://localhost:8001/health`

## 📚 Documentation

**👉 [Complete API Documentation](ETL_ENGINE_API_DOCUMENTATION.md)**

The comprehensive documentation includes:
- Step-by-step integration guide
- Complete API reference
- Request/response formats
- Transformation logic examples
- Frontend integration examples (JavaScript/Python)
- Troubleshooting guide

## 🏗️ Project Structure

```
📁 Hackathon_ETL_Engine_Updated/
├── transformationEngine/          # ETL Engine source code
│   ├── app/                      # Core application modules
│   │   ├── main.py              # FastAPI application
│   │   ├── reader.py            # Data reading logic
│   │   ├── transformer.py       # Transformation engine
│   │   ├── writer.py            # Output generation
│   │   └── ...
│   └── requirements.txt          # Python dependencies
├── storage/                      # Shared storage for all engines
│   ├── input/                   # Input Parquet files
│   ├── transformed/             # Output files
│   ├── logs/                    # Operation logs
│   └── transformation_error/    # Error files
├── config/                      # Configuration files
├── parsingEngine/               # Other engines (future)
├── run.py                       # Server startup script
└── ETL_ENGINE_API_DOCUMENTATION.md  # Complete documentation
```

## 🎯 Key Features

- **Multi-Format Support:** CSV, JSON, XML, Fixed-Width, Excel, Parquet
- **Flexible Transformations:** Mathematical, string, conditional logic
- **Positional Data Handling:** Support for fixed-width and positional data
- **High Performance:** Built with Polars for fast data processing
- **Multi-Engine Architecture:** Shared storage for multiple engines
- **Comprehensive Logging:** Detailed operation logs and error tracking

## 🔧 Quick Example

```bash
# 1. Start the server
python run.py

# 2. Make a transformation request
curl -X POST "http://localhost:8001/transform" \
  -H "Content-Type: application/json" \
  -d '{
    "source_file_path": "storage/input/employees.parquet",
    "source_schema": {
      "role": "source",
      "fileType": "parquet",
      "attributes": {
        "id": {"dataType": "integer", "column_no": 1, "start_position": 0, "width": 8},
        "name": {"dataType": "string", "column_no": 2, "start_position": 8, "width": 30}
      }
    },
    "target_schema": {"role": "target", "fileType": "json", "attributes": {}},
    "transformation_mapping": {
      "mappings": [
        {"id": "pass_id", "affected_target": "employee_id", "affected_source": ["id"], "trns": ""},
        {"id": "pass_name", "affected_target": "employee_name", "affected_source": ["name"], "trns": ""}
      ]
    }
  }'
```

## 📖 For Developers

### Frontend Integration
- **JavaScript:** See examples in [API Documentation](ETL_ENGINE_API_DOCUMENTATION.md)
- **Python:** Complete integration examples provided
- **REST API:** Standard HTTP/JSON interface

### Backend Development
- **FastAPI:** Modern Python web framework
- **Polars:** High-performance DataFrame library
- **Modular Design:** Easy to extend and customize

## 🆘 Support

1. **Check the logs:** `storage/logs/`
2. **Review errors:** `storage/transformation_error/`
3. **Interactive docs:** `http://localhost:8001/docs`
4. **Complete guide:** [ETL_ENGINE_API_DOCUMENTATION.md](ETL_ENGINE_API_DOCUMENTATION.md)

## 🎉 Ready to Transform Data?

1. Read the [Complete API Documentation](ETL_ENGINE_API_DOCUMENTATION.md)
2. Start the server: `python run.py`
3. Place your Parquet files in `storage/input/`
4. Make your first transformation!

---

**Happy Data Transforming! 🚀**
