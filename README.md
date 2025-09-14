# ETL Engine - High-Performance Data Transformation Platform

## 🚀 Quick Start

This ETL Engine provides powerful, memory-efficient data transformation capabilities, converting Parquet files between various formats using customizable transformation logic. Built with performance optimizations and streaming support for handling large datasets.

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

- **🚀 High Performance:** Built with Polars for lightning-fast data processing
- **💾 Memory Efficient:** Streaming support for large files (100MB+ threshold)
- **📊 Multi-Format Support:** CSV, JSON, XML, Fixed-Width, Excel, Parquet
- **🔧 Flexible Transformations:** Mathematical, string, conditional, date logic
- **🎯 Clean Syntax:** Simple functions and bracketed calls for easy transformations
- **📍 Positional Data Handling:** Advanced fixed-width and positional data support
- **🏗️ Multi-Engine Architecture:** Shared storage for multiple engines
- **📝 Comprehensive Logging:** Detailed operation logs and error tracking
- **🔄 Streaming Processing:** Automatic chunking for large datasets
- **⚡ Optimized Memory Usage:** 90%+ memory reduction for large files
- **🛡️ Robust Error Handling:** Graceful error recovery and detailed error reporting

## 🔧 Quick Example

### Basic Transformation
```bash
# 1. Start the server
python run.py

# 2. Make a transformation request (Rules Format)
curl -X POST "http://localhost:8001/transform" \
  -H "Content-Type: application/json" \
  -d '{
    "source_file_path": "storage/input/employees.parquet",
    "source_schema": {
      "role": "source",
      "fileType": "parquet",
      "attributes": {
        "id": {"dataType": "integer", "column_no": 1},
        "name": {"dataType": "string", "column_no": 2},
        "salary": {"dataType": "float", "column_no": 3}
      }
    },
    "target_schema": {"role": "target", "fileType": "csv", "attributes": {}},
    "transformation_mapping": {
      "rules": [
        {"id": "pass_id", "affected_target": "employee_id", "affected_source": ["id"], "trns": ""},
        {"id": "upper_name", "affected_target": "employee_name", "affected_source": ["name"], "trns": "STRING[UPPER(attr(\"name\"))]"},
        {"id": "bonus", "affected_target": "salary_with_bonus", "affected_source": ["salary"], "trns": "MATH[ADD(attr(\"salary\"), 1000)]"}
      ]
    }
  }'
```

### Advanced Transformation Example
```bash
# Complex transformation with conditional logic
curl -X POST "http://localhost:8001/transform" \
  -H "Content-Type: application/json" \
  -d '{
    "source_file_path": "storage/input/customers.parquet",
    "source_schema": {
      "role": "source",
      "fileType": "parquet",
      "attributes": {
        "customer_id": {"dataType": "integer", "column_no": 1},
        "first_name": {"dataType": "string", "column_no": 2},
        "last_name": {"dataType": "string", "column_no": 3},
        "email": {"dataType": "string", "column_no": 4},
        "total_orders": {"dataType": "integer", "column_no": 5}
      }
    },
    "target_schema": {"role": "target", "fileType": "json", "attributes": {}},
    "transformation_mapping": {
      "rules": [
        {"id": "full_name", "affected_target": "customer_name", "affected_source": ["first_name", "last_name"], "trns": "STRING[CONCAT(attr(\"first_name\"), \" \", attr(\"last_name\"))]"},
        {"id": "customer_tier", "affected_target": "tier", "affected_source": ["total_orders"], "trns": "LOGICAL[IF(GT(attr(\"total_orders\"), 10), \"Premium\", \"Standard\")]"},
        {"id": "email_lower", "affected_target": "email_address", "affected_source": ["email"], "trns": "STRING[LOWER(attr(\"email\"))]"}
      ]
    }
  }'
```

## 📖 For Developers

### Performance Features
- **🚀 Streaming Processing:** Automatic detection and processing of large files (>100MB)
- **💾 Memory Optimization:** 90%+ memory reduction for large datasets
- **⚡ Advanced Caching:** File size caching and transformer instance reuse
- **🔄 Chunked Processing:** Configurable chunk sizes for optimal performance

### Frontend Integration
- **JavaScript:** See examples in [API Documentation](ETL_ENGINE_API_DOCUMENTATION.md)
- **Python:** Complete integration examples provided
- **REST API:** Standard HTTP/JSON interface

### Backend Development
- **FastAPI:** Modern Python web framework
- **Polars:** High-performance DataFrame library
- **Modular Design:** Easy to extend and customize
- **Advanced Parsing:** Tree-based transformation parsing with dependency resolution

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

## 📈 Recent Improvements

### Performance Optimizations (v1.1.0)
- ✅ **Streaming Support:** Added memory-efficient streaming for large files
- ✅ **Fixed-Width Optimization:** 90%+ memory reduction for fixed-width files
- ✅ **Code Cleanup:** Removed unused imports and redundant functions
- ✅ **Configuration Cleanup:** Removed outdated configuration files
- ✅ **Enhanced Error Handling:** Improved error reporting and recovery
- ✅ **Advanced Parsing:** Tree-based transformation parsing with dependency resolution

### Memory Efficiency
- **Before:** Large files (100MB+) could cause memory issues
- **After:** Automatic streaming with configurable chunk sizes (10,000 rows default)
- **Result:** 90%+ memory reduction for large datasets

---

**Happy Data Transforming! 🚀**
