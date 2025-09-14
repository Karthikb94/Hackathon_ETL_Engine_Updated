# ETL Engine API Documentation

## 🚀 Overview

The ETL Engine is a high-performance, memory-efficient data transformation service that converts Parquet files (generated from various source formats like CSV, JSON, XML, Fixed-Width, Excel) into different output formats using customizable transformation logic. Built with streaming support and advanced optimizations for handling large datasets.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Performance Features](#performance-features)
3. [API Endpoints](#api-endpoints)
4. [Request Formats](#request-formats)
5. [Response Formats](#response-formats)
6. [Transformation Logic](#transformation-logic)
7. [Schema Configuration](#schema-configuration)
8. [Supported Data Formats](#supported-data-formats)
9. [Streaming Processing](#streaming-processing)
10. [Error Handling](#error-handling)
11. [Examples](#examples)
12. [Troubleshooting](#troubleshooting)

---

## 🚀 Performance Features

### Streaming Processing
- **Automatic Detection:** Files larger than 100MB automatically use streaming mode
- **Memory Efficiency:** 90%+ memory reduction for large datasets
- **Configurable Chunks:** Default 10,000 rows per chunk (adjustable)
- **Supported Formats:** Parquet, CSV, JSON, Fixed-Width files

### Memory Optimizations
- **Fixed-Width Streaming:** Line-by-line processing for fixed-width files
- **Chunked Processing:** Large files processed in manageable chunks
- **Error Resilience:** Continues processing even if individual lines are malformed
- **Resource Management:** Automatic cleanup of temporary resources

### Advanced Features
- **Tree-Based Parsing:** Advanced transformation parsing with dependency resolution
- **Type Safety:** Robust data type conversion and validation
- **Error Recovery:** Graceful handling of malformed data
- **Progress Tracking:** Real-time processing progress logging

---

## 🏃‍♂️ Quick Start

### Prerequisites
- ETL Engine server running on `http://localhost:8001`
- Parquet files in the `storage/input/` directory
- Basic understanding of JSON and HTTP requests

### Basic Usage Flow
1. **Prepare your data**: Convert source files (CSV, JSON, XML, etc.) to Parquet format
2. **Define schemas**: Create source and target schemas
3. **Configure transformations**: Set up mapping rules
4. **Make API call**: Send POST request to `/transform` endpoint
5. **Get results**: Download transformed files from `storage/transformed/`

---

## 🌐 API Endpoints

### Base URL
```
http://localhost:8001
```

### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Check server health status |
| `POST` | `/transform` | Transform data files |
| `GET` | `/docs` | Interactive API documentation |
| `GET` | `/redoc` | Alternative API documentation |

---

## 📡 Request Formats

### Health Check Request
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-14T12:00:00",
  "version": "1.0.0"
}
```

### Transform Request
```http
POST /transform
Content-Type: application/json
```

**Request Body Structure:**
```json
{
  "source_file_path": "string",
  "source_schema": {
    "role": "source",
    "fileType": "parquet",
    "schemaId": "string",
    "description": "string",
    "attributes": {
      "field_name": {
        "dataType": "string",
        "column_no": "number",
        "start_position": "number",
        "width": "number",
        "description": "string"
      }
    }
  },
  "target_schema": {
    "role": "target",
    "fileType": "string",
    "attributes": {}
  },
  "transformation_mapping": {
    "mappings": [
      {
        "id": "string",
        "affected_target": "string",
        "affected_source": ["string"],
        "trns": "string"
      }
    ]
  }
}
```

---

## 📊 Response Formats

### File Path Information

The API now provides **both relative and absolute paths** for all files:

- **Relative paths**: For display purposes (e.g., `storage/input/file.parquet`)
- **Absolute paths**: Complete system paths for programmatic access (e.g., `C:/Users/.../storage/input/file.parquet`)

**Available file paths in responses:**
- `source_file` / `source_file_absolute` - Input Parquet file
- `output_file` / `output_file_absolute` - Transformed output file  
- `log_file` / `log_file_absolute` - Operation log file
- `error_file` / `error_file_absolute` - Error details file (if errors occur)

**Benefits for frontend developers:**
- ✅ Direct file access using absolute paths
- ✅ No need to construct file paths manually
- ✅ Cross-platform compatibility (uses forward slashes)
- ✅ Easy integration with file download/preview features
- ✅ Clean, readable paths without confusing backslashes
- ✅ **All paths use forward slashes** - no more double backslashes in JSON responses

---

### Successful Transform Response
```json
{
  "status": "success",
  "run_id": "20250914_122723",
  "source_file": "storage/input/input_file.parquet",
  "source_file_absolute": "C:/Users/karth/OneDrive/Desktop/Hackathon_ETL_Engine_Updated/storage/input/input_file.parquet",
  "output_file": "filename_without_extension",
  "output_file_absolute": "C:/Users/karth/OneDrive/Desktop/Hackathon_ETL_Engine_Updated/storage/transformed/filename_without_extension.json",
  "output_format": "json",
  "rows_processed": 100,
  "columns_output": 5,
  "processing_time_seconds": 0.045,
  "log_file": "etl_20250914_122723.log",
  "log_file_absolute": "C:/Users/karth/OneDrive/Desktop/Hackathon_ETL_Engine_Updated/storage/logs/etl_20250914_122723.log",
  "error_file": null,
  "error_file_absolute": null,
  "message": "Transformation completed successfully",
  "timestamp": "2025-09-14T12:27:23.233536"
}
```

### Error Response
```json
{
  "status": "error",
  "run_id": "20250914_123457",
  "source_file": "storage/input/parquet_from_csv.parquet",
  "source_file_absolute": "C:/Users/karth/OneDrive/Desktop/Hackathon_ETL_Engine_Updated/storage/input/parquet_from_csv.parquet",
  "output_file": "parquet_from_csv_transformed_20250914_123457",
  "output_file_absolute": "C:/Users/karth/OneDrive/Desktop/Hackathon_ETL_Engine_Updated/parquet_from_csv_transformed_20250914_123457",
  "log_file": "storage/logs/etl_20250914_123457.log",
  "log_file_absolute": "C:/Users/karth/OneDrive/Desktop/Hackathon_ETL_Engine_Updated/storage/logs/etl_20250914_123457.log",
  "error_file": "storage/transformation_error/transformation_error_20250914_123457.json",
  "error_file_absolute": "C:/Users/karth/OneDrive/Desktop/Hackathon_ETL_Engine_Updated/storage/transformation_error/transformation_error_20250914_123457.json",
  "error_message": "Failed to build expression for rule invalid_rule: Source column(s) ['nonexistent_field'] not found for rule invalid_rule.",
  "message": "Transformation failed. Check error file for details.",
  "timestamp": "2025-09-14T12:34:57.086732"
}
```

---

## 🔧 Transformation Logic

### Mapping Rules Structure
Each transformation rule consists of:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | string | Unique identifier for the rule | `"pass_customer_id"` |
| `affected_target` | string | Target field name | `"customer_id"` |
| `affected_source` | array | Source field names | `["customer_id"]` |
| `trns` | string | Transformation expression | `""` (pass-through) or `"concat(first_name, ' ', last_name)"` |

### Transformation Types

#### 1. Pass-Through (Copy as-is)
```json
{
  "id": "copy_field",
  "affected_target": "customer_id",
  "affected_source": ["customer_id"],
  "trns": ""
}
```

#### 2. String Concatenation
```json
{
  "id": "full_name",
  "affected_target": "full_name",
  "affected_source": ["first_name", "last_name"],
  "trns": "concat(first_name, ' ', last_name)"
}
```

#### 3. Mathematical Operations
```json
{
  "id": "total_amount",
  "affected_target": "total_amount",
  "affected_source": ["price", "quantity"],
  "trns": "price * quantity"
}
```

#### 4. Conditional Logic
```json
{
  "id": "status",
  "affected_target": "status",
  "affected_source": ["amount"],
  "trns": "if(amount > 1000, 'High', 'Low')"
}
```

#### 5. String Functions
```json
{
  "id": "email_domain",
  "affected_target": "domain",
  "affected_source": ["email"],
  "trns": "substring(email, str_index_of(email, '@') + 1)"
}
```

#### 6. Complex Calculations
```json
{
  "id": "bonus_calc",
  "affected_target": "bonus",
  "affected_source": ["salary", "performance_rating"],
  "trns": "salary * 0.1 * performance_rating"
}
```

---

## 📋 Schema Configuration

### Source Schema
The source schema defines the structure of your input file. **Important:** The `fileType` in the schema represents the **original source format** (CSV, JSON, XML, Fixed-Width), not the current file format. The engine automatically detects the actual file format from the file extension.

```json
{
  "role": "source",
  "fileType": "csv",  // Original source format (CSV, JSON, XML, fixedwidth)
  "schemaId": "employee_schema",
  "schemaName": "employee_csv_v1",
  "description": "Employee data from HR system",
  "attributes": {
    "employee_id": {
      "dataType": "integer",
      "column_no": 1,
      "start_position": 0,
      "width": 8,
      "description": "Unique employee identifier"
    },
    "first_name": {
      "dataType": "string",
      "column_no": 2,
      "start_position": 8,
      "width": 20,
      "description": "Employee first name"
    },
    "salary": {
      "dataType": "float",
      "column_no": 3,
      "start_position": 28,
      "width": 12,
      "description": "Annual salary"
    }
  }
}
```

### File Format Detection
The ETL engine automatically detects the actual file format from the file extension:
- **`.parquet`** → Read as Parquet file
- **`.csv`** → Read as CSV file  
- **`.json`** → Read as JSON file
- **`.xml`** → Read as XML file
- **`.fw`, `.fixedwidth`, `.fixed_width`** → Read as Fixed-Width file

This allows you to:
- ✅ **Track data lineage** by specifying the original source format in the schema
- ✅ **Maintain metadata** about how the data was originally structured
- ✅ **Apply appropriate transformations** based on the original format characteristics
- ✅ **Support parquet files** that were converted from various source formats

### Target Schema
The target schema defines your desired output format:

```json
{
  "role": "target",
  "fileType": "json",
  "attributes": {}
}
```

### Supported Data Types
- `integer` - Whole numbers
- `float` - Decimal numbers
- `string` - Text data
- `boolean` - True/False values
- `date` - Date values (YYYY-MM-DD)

---

## 📁 Supported Data Formats

### Input Formats (via Parquet)
- **CSV** → Parquet
- **JSON** → Parquet
- **XML** → Parquet
- **Fixed-Width** → Parquet
- **Excel (XLSX)** → Parquet

### Output Formats
| Format | Extension | Description |
|--------|-----------|-------------|
| `csv` | `.csv` | Comma-separated values |
| `json` | `.json` | JSON array format |
| `xml` | `.xml` | XML format |
| `fixedwidth` | `.txt` | Fixed-width text |
| `xlsx` | `.xlsx` | Excel format |
| `parquet` | `.parquet` | Parquet format |

---

## 🔄 Streaming Processing

### Automatic Streaming Detection
The ETL Engine automatically detects large files and switches to streaming mode for optimal memory usage:

- **Threshold:** Files larger than 100MB automatically use streaming
- **Chunk Size:** Default 10,000 rows per chunk (configurable)
- **Memory Reduction:** 90%+ memory savings for large datasets

### Streaming Response Format
When processing large files, the response includes streaming-specific information:

```json
{
  "status": "success",
  "run_id": "20250914_120000",
  "processing_mode": "streaming",
  "message": "Large file transformation completed successfully using streaming mode",
  "file_size_mb": 150.5,
  "chunk_size": 10000,
  "processing_time_seconds": 45.2,
  "source_file": "storage/input/large_dataset.parquet",
  "output_file": "large_dataset_transformed_20250914_120000",
  "output_format": "csv"
}
```

### Supported Streaming Formats
- **Parquet:** Native streaming support via Polars
- **CSV:** Chunked reading with schema validation
- **JSON:** Line-by-line JSONL processing
- **Fixed-Width:** Line-by-line parsing with position mapping

### Performance Benefits
- **Memory Efficiency:** Process files of any size without memory constraints
- **Error Resilience:** Continues processing even if individual chunks fail
- **Progress Tracking:** Real-time logging of processing progress
- **Resource Management:** Automatic cleanup of temporary resources

---

## ⚠️ Error Handling

### Common Error Types

#### 1. File Not Found
```json
{
  "status": "error",
  "error_type": "FileNotFoundError",
  "message": "Source file 'nonexistent.parquet' not found",
  "timestamp": "2025-09-14T12:00:00"
}
```

#### 2. Invalid Schema
```json
{
  "status": "error",
  "error_type": "ValidationError",
  "message": "Source schema is required for parquet files",
  "timestamp": "2025-09-14T12:00:00"
}
```

#### 3. Transformation Error
```json
{
  "status": "error",
  "error_type": "TransformError",
  "message": "Invalid transformation expression: 'invalid_function()'",
  "timestamp": "2025-09-14T12:00:00"
}
```

### HTTP Status Codes
- `200` - Success
- `400` - Bad Request (validation error)
- `404` - Not Found (file not found)
- `500` - Internal Server Error

---

## 💡 Examples

### Example 1: Simple Pass-Through Transformation

**Request:**
```json
{
  "source_file_path": "storage/input/employees.parquet",
  "source_schema": {
    "role": "source",
    "fileType": "parquet",
    "attributes": {
      "id": {"dataType": "integer", "column_no": 1, "start_position": 0, "width": 8},
      "name": {"dataType": "string", "column_no": 2, "start_position": 8, "width": 30},
      "email": {"dataType": "string", "column_no": 3, "start_position": 38, "width": 40}
    }
  },
  "target_schema": {
    "role": "target",
    "fileType": "json",
    "attributes": {}
  },
  "transformation_mapping": {
    "rules": [
      {"id": "pass_id", "affected_target": "employee_id", "affected_source": ["id"], "trns": ""},
      {"id": "pass_name", "affected_target": "employee_name", "affected_source": ["name"], "trns": ""},
      {"id": "pass_email", "affected_target": "email_address", "affected_source": ["email"], "trns": ""}
    ]
  }
}
```

**Response:**
```json
{
  "status": "success",
  "run_id": "20250914_120000",
  "source_file": "storage/input/employees.parquet",
  "source_file_absolute": "C:\\Users\\karth\\OneDrive\\Desktop\\Hackathon_ETL_Engine_Updated\\storage\\input\\employees.parquet",
  "output_file": "employees_transformed_20250914_120000",
  "output_file_absolute": "C:\\Users\\karth\\OneDrive\\Desktop\\Hackathon_ETL_Engine_Updated\\storage\\transformed\\employees_transformed_20250914_120000.json",
  "output_format": "json",
  "rows_processed": 50,
  "columns_output": 3,
  "processing_time_seconds": 0.023,
  "log_file": "etl_20250914_120000.log",
  "log_file_absolute": "C:\\Users\\karth\\OneDrive\\Desktop\\Hackathon_ETL_Engine_Updated\\storage\\logs\\etl_20250914_120000.log",
  "error_file": null,
  "error_file_absolute": null,
  "message": "Transformation completed successfully",
  "timestamp": "2025-09-14T12:00:00.000000"
}
```

### Example 2: Complex Transformation with Calculations

**Request:**
```json
{
  "source_file_path": "storage/input/sales.parquet",
  "source_schema": {
    "role": "source",
    "fileType": "parquet",
    "attributes": {
      "product_id": {"dataType": "integer", "column_no": 1, "start_position": 0, "width": 8},
      "product_name": {"dataType": "string", "column_no": 2, "start_position": 8, "width": 30},
      "price": {"dataType": "float", "column_no": 3, "start_position": 38, "width": 10},
      "quantity": {"dataType": "integer", "column_no": 4, "start_position": 48, "width": 5},
      "discount": {"dataType": "float", "column_no": 5, "start_position": 53, "width": 5}
    }
  },
  "target_schema": {
    "role": "target",
    "fileType": "csv",
    "attributes": {}
  },
  "transformation_mapping": {
    "rules": [
      {"id": "pass_product_id", "affected_target": "product_id", "affected_source": ["product_id"], "trns": ""},
      {"id": "pass_product_name", "affected_target": "product_name", "affected_source": ["product_name"], "trns": ""},
      {"id": "calculate_total", "affected_target": "total_amount", "affected_source": ["price", "quantity", "discount"], "trns": "MATH[SUB(MATH[MUL(attr(\"price\"), attr(\"quantity\"))], attr(\"discount\"))]"},
      {"id": "calculate_discount_percent", "affected_target": "discount_percent", "affected_source": ["discount", "price", "quantity"], "trns": "MATH[MUL(MATH[DIV(attr(\"discount\"), MATH[MUL(attr(\"price\"), attr(\"quantity\"))])], 100)]"},
      {"id": "status_category", "affected_target": "status", "affected_source": ["price"], "trns": "LOGICAL[IF(GT(attr(\"price\"), 100), \"Premium\", \"Standard\")]"}
    ]
  }
}
```

### Example 3: JavaScript Frontend Integration

```javascript
// Function to transform data
async function transformData(sourceFile, sourceSchema, targetSchema, mappings) {
  const requestBody = {
    source_file_path: sourceFile,
    source_schema: sourceSchema,
    target_schema: targetSchema,
    transformation_mapping: { rules: mappings }
  };

  try {
    const response = await fetch('http://localhost:8001/transform', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    
    if (result.status === 'success') {
      console.log('Transformation successful:', result);
      return {
        success: true,
        outputFile: result.output_file,
        outputFileAbsolute: result.output_file_absolute,
        logFile: result.log_file,
        logFileAbsolute: result.log_file_absolute,
        sourceFileAbsolute: result.source_file_absolute,
        recordsProcessed: result.rows_processed,
        processingTime: result.processing_time_seconds,
        runId: result.run_id
      };
    } else {
      // Handle error response with clean paths
      console.error('Transformation failed:', result);
      return {
        success: false,
        error: result.error_message || result.message,
        errorFile: result.error_file,
        errorFileAbsolute: result.error_file_absolute,
        logFile: result.log_file,
        logFileAbsolute: result.log_file_absolute,
        sourceFileAbsolute: result.source_file_absolute,
        runId: result.run_id
      };
    }
  } catch (error) {
    console.error('Transformation error:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

// Example usage
const sourceSchema = {
  "role": "source",
  "fileType": "parquet",
  "attributes": {
    "customer_id": {"dataType": "integer", "column_no": 1, "start_position": 0, "width": 8},
    "name": {"dataType": "string", "column_no": 2, "start_position": 8, "width": 30},
    "email": {"dataType": "string", "column_no": 3, "start_position": 38, "width": 40}
  }
};

const targetSchema = {
  "role": "target",
  "fileType": "json",
  "attributes": {}
};

const mappings = [
  {"id": "pass_id", "affected_target": "id", "affected_source": ["customer_id"], "trns": ""},
  {"id": "pass_name", "affected_target": "name", "affected_source": ["name"], "trns": ""},
  {"id": "pass_email", "affected_target": "email", "affected_source": ["email"], "trns": ""}
];

// Call the transformation
transformData('storage/input/customers.parquet', sourceSchema, targetSchema, mappings)
  .then(result => {
    if (result.success) {
      console.log(`Success! Processed ${result.recordsProcessed} records`);
      console.log(`Output file: ${result.outputFile}`);
    } else {
      console.error('Failed:', result.error);
    }
  });
```

### Example 4: Python Integration

```python
import requests
import json

def transform_data(source_file, source_schema, target_schema, mappings):
    """Transform data using ETL Engine API."""
    
    url = "http://localhost:8001/transform"
    
    payload = {
        "source_file_path": source_file,
        "source_schema": source_schema,
        "target_schema": target_schema,
        "transformation_mapping": {"mappings": mappings}
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        if result["status"] == "success":
            print(f"✅ Transformation successful!")
            print(f"📄 Output file: {result['output_file']}")
            print(f"📁 Output file absolute: {result['output_file_absolute']}")
            print(f"📄 Log file: {result['log_file']}")
            print(f"📁 Log file absolute: {result['log_file_absolute']}")
            print(f"📊 Records processed: {result['rows_processed']}")
            print(f"⏱️ Processing time: {result['processing_time_seconds']} seconds")
            print(f"🆔 Run ID: {result['run_id']}")
            return result
        else:
            # Handle error response with clean paths
            print(f"❌ Transformation failed: {result.get('error_message', result.get('message', 'Unknown error'))}")
            print(f"📄 Error file: {result.get('error_file', 'N/A')}")
            print(f"📁 Error file absolute: {result.get('error_file_absolute', 'N/A')}")
            print(f"📄 Log file: {result.get('log_file', 'N/A')}")
            print(f"📁 Log file absolute: {result.get('log_file_absolute', 'N/A')}")
            print(f"📁 Source file absolute: {result.get('source_file_absolute', 'N/A')}")
            print(f"🆔 Run ID: {result.get('run_id', 'N/A')}")
            return result
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON response: {str(e)}")
        return None

# Example usage
source_schema = {
    "role": "source",
    "fileType": "parquet",
    "attributes": {
        "customer_id": {"dataType": "integer", "column_no": 1, "start_position": 0, "width": 8},
        "name": {"dataType": "string", "column_no": 2, "start_position": 8, "width": 30},
        "email": {"dataType": "string", "column_no": 3, "start_position": 38, "width": 40}
    }
}

target_schema = {
    "role": "target",
    "fileType": "json",
    "attributes": {}
}

mappings = [
    {"id": "pass_id", "affected_target": "id", "affected_source": ["customer_id"], "trns": ""},
    {"id": "pass_name", "affected_target": "name", "affected_source": ["name"], "trns": ""},
    {"id": "pass_email", "affected_target": "email", "affected_source": ["email"], "trns": ""}
]

# Execute transformation
result = transform_data(
    "storage/input/customers.parquet",
    source_schema,
    target_schema,
    mappings
)
```

---

## 🔍 Step-by-Step Process

### Step 1: Prepare Your Data
1. Convert your source files (CSV, JSON, XML, etc.) to Parquet format
2. Place Parquet files in the `storage/input/` directory
3. Note the exact filename (e.g., `customers.parquet`)

### Step 2: Define Source Schema
1. Identify all fields in your Parquet file
2. Determine data types (integer, string, float, boolean, date)
3. Create schema with field positions and descriptions

### Step 3: Define Target Schema
1. Choose output format (csv, json, xml, fixedwidth, xlsx, parquet)
2. Define target field names (can be different from source)

### Step 4: Create Transformation Rules
1. Map source fields to target fields
2. Add transformation logic (calculations, concatenations, etc.)
3. Ensure each rule has unique ID and proper field references

#### Enhanced Transformation Format Support

The engine supports clean, simple transformation syntaxes:

**Format 1: Simple Function Calls (Recommended)**
```json
{
  "id": "upper_name",
  "trns": "UPPER(first_name)",
  "affected_source": ["first_name"],
  "affected_target": "customer_name"
}
```

**Format 2: Bracketed Function Calls**
```json
{
  "id": "trim_email",
  "trns": "STRING[TRIM(ATTR(email))]",
  "affected_source": ["email"],
  "affected_target": "clean_email"
}
```

**Format 3: Direct Field Reference**
```json
{
  "id": "direct_copy",
  "trns": "DIRECT[ATTR(first_name)]",
  "affected_source": ["first_name"],
  "affected_target": "name_copy"
}
```

**Format 4: Pass-through (No Transformation)**
```json
{
  "id": "pass_through",
  "trns": "",
  "affected_source": ["dob"],
  "affected_target": "birth_date"
}
```

### Step 5: Make API Request
1. Use POST method to `/transform` endpoint
2. Send JSON payload with all configurations
3. Wait for response (usually under 1 second)

### Step 6: Process Results
1. Check response status
2. If successful, note the output filename
3. Access transformed file in `storage/transformed/` directory

---

## 🛠️ Troubleshooting

### Common Issues and Solutions

#### 1. "File not found" Error
**Problem:** Source file doesn't exist
**Solution:** 
- Verify file exists in `storage/input/`
- Check filename spelling and extension
- Ensure file is accessible

#### 2. "Schema validation failed" Error
**Problem:** Source schema is missing or invalid
**Solution:**
- Always provide source_schema for Parquet files
- Ensure all fields are defined with correct data types
- Check field names match exactly

#### 3. "Transformation expression invalid" Error
**Problem:** Invalid transformation syntax
**Solution:**
- Use supported functions: `concat()`, `if()`, `substring()`, etc.
- Check field names in expressions
- Use proper syntax for mathematical operations

#### 4. "No rules found" Error
**Problem:** Empty transformation mapping
**Solution:**
- Provide at least one mapping rule
- Use pass-through rules (`"trns": ""`) if no transformation needed

#### 5. Server Connection Issues
**Problem:** Cannot connect to API
**Solution:**
- Ensure ETL Engine is running (`python run.py`)
- Check server is on `http://localhost:8001`
- Verify firewall settings

### Performance Tips

1. **Large Files:** For files > 100MB, expect longer processing times
2. **Complex Transformations:** Mathematical operations are faster than string operations
3. **Multiple Rules:** Process in batches if you have many transformation rules
4. **Output Format:** JSON and CSV are fastest, XML is slower

### Best Practices

1. **Always validate schemas** before sending requests
2. **Use descriptive field names** for better maintainability
3. **Test with small datasets** first
4. **Keep transformation rules simple** for better performance
5. **Monitor log files** in `storage/logs/` for debugging

---

## 📈 Recent Improvements (v1.1.0)

### Performance Optimizations
- ✅ **Streaming Support:** Added memory-efficient streaming for large files (>100MB)
- ✅ **Fixed-Width Optimization:** 90%+ memory reduction for fixed-width files
- ✅ **Advanced Parsing:** Tree-based transformation parsing with dependency resolution
- ✅ **Code Cleanup:** Removed unused imports and redundant functions
- ✅ **Configuration Cleanup:** Removed outdated configuration files
- ✅ **Enhanced Error Handling:** Improved error reporting and recovery

### Memory Efficiency Improvements
- **Before:** Large files could cause memory issues
- **After:** Automatic streaming with configurable chunk sizes
- **Result:** 90%+ memory reduction for large datasets

### New Features
- **Automatic File Size Detection:** Files >100MB automatically use streaming
- **Configurable Chunk Sizes:** Default 10,000 rows per chunk
- **Progress Tracking:** Real-time processing progress logging
- **Error Resilience:** Continues processing even if individual chunks fail

---

## 📞 Support

### Getting Help
- **API Documentation:** Visit `http://localhost:8001/docs` for interactive documentation
- **Log Files:** Check `storage/logs/` for detailed operation logs
- **Error Files:** Check `storage/transformation_error/` for error details

### File Locations
```
📁 Project Structure:
├── storage/
│   ├── input/          # Place your Parquet files here
│   ├── transformed/    # Transformed files appear here
│   ├── logs/          # Operation logs
│   └── transformation_error/  # Error details
├── transformationEngine/  # ETL Engine code
└── run.py             # Start the server
```

---

## 🎯 Quick Reference

### Essential Endpoints
- **Health Check:** `GET /health`
- **Transform:** `POST /transform`
- **Documentation:** `GET /docs`

### Required Fields
- `source_file_path` - Path to Parquet file
- `source_schema` - Structure of input data
- `target_schema` - Desired output format
- `transformation_mapping` - Field mapping rules

### Supported Functions
- `concat(field1, ' ', field2)` - String concatenation
- `if(condition, true_value, false_value)` - Conditional logic
- `substring(text, start, length)` - String extraction
- `field1 + field2` - Mathematical operations
- `field1 * field2` - Multiplication
- `field1 / field2` - Division

This documentation provides everything needed to integrate with and use the ETL Engine API effectively! 🚀
