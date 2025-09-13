# ETL Transformation Engine - Complete Guide

## 🚀 **What is this?**

This is a **Data Transformation Engine** that converts data from one format to another using custom rules. Think of it as a smart converter that can:
- Read data from files (CSV, Parquet, JSON, etc.)
- Transform the data using custom rules (like combining names, cleaning emails, etc.)
- Output the data in different formats (JSON, CSV, Excel, Fixed-Width, etc.)

## 🏗️ **Architecture**

```
root/
├── transformationEngine/     # Main transformation engine
│   ├── app/                  # Core transformation application
│   │   ├── main.py          # FastAPI application with endpoints
│   │   ├── reader.py        # Schema-based data reading
│   │   ├── transformer.py   # Advanced transformation engine
│   │   ├── writer.py        # Output writing (including fixed-width)
│   │   ├── error_handler.py # Error handling and reporting
│   │   ├── logger.py        # Logging configuration
│   │   └── exceptions.py    # Custom exception classes
│   ├── requirements.txt     # Python dependencies
│   └── start.py            # Startup script
├── storage/                 # Shared storage for all engines
│   ├── input/              # Input files (e.g., data.parquet)
│   ├── transformed/        # Output files (e.g., result.json)
│   ├── logs/              # Log files from all engines
│   └── transformation_error/ # Error files with detailed information
└── README.md              # This file
```

## 📡 **API Endpoints**

### **Base URL**
```
http://localhost:8001
```

### **1. Health Check** (Test if server is running)
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "ETL Engine v1",
  "version": "1.0.0"
}
```

### **2. Main Transformation Endpoint** (File-based - This is what you'll use)
```
POST /transform-independent
```

### **3. Direct Transformation Endpoint** (All parameters in request body - Recommended for frontend)
```
POST /transform-direct
```

## 🔧 **How to Use the Transformation Engine**

### **Method 1: Direct API (Recommended for Frontend)**

All parameters are sent directly in the API request body - no files needed!

**Request Format:**
```json
{
  "source_file_path": "C:/path/to/your/data.parquet",
  "source_schema": {
    "role": "source",
    "fileType": "parquet",
    "schemaId": "schm-parquet-1001",
    "schemaName": "customer_data_v1",
    "attributes": {
      "first_name": {
        "name": "first_name",
        "dataType": "string",
        "column_no": 1
      },
      "last_name": {
        "name": "last_name",
        "dataType": "string",
        "column_no": 2
      }
    }
  },
  "target_schema": {
    "role": "target",
    "fileType": "json",
    "schemaId": "schm-json-2001",
    "schemaName": "customer_output_v1",
    "attributes": {
      "full_name": {
        "name": "full_name",
        "dataType": "string",
        "column_no": 1
      }
    }
  },
  "transformation_mapping": {
    "mappingId": "transform-001",
    "mappingName": "customer_transformation",
    "createdAt": "2025-01-27T10:00:00.000Z",
    "sourceSchemaId": "schm-parquet-1001",
    "targetSchemaId": "schm-json-2001",
    "rules": [
      {
        "id": "rule_001",
        "name": "Full Name Creation",
        "description": "Combine first and last name",
        "trns": "STRING[CONCAT(ATTR(first_name), ' ', ATTR(last_name))]",
        "affected_source": ["first_name", "last_name"],
        "affected_target": "full_name"
      }
    ]
  },
  "output_filename": "result",
  "output_format": "json"
}
```

### **Method 2: File-based API (Legacy)**

You need to place these files in the `storage/input/` folder:

1. **Source Data File** (your actual data)
   - `data.parquet` or `data.csv` or `data.json`
   
2. **Source Schema File** (describes your input data structure)
   - `source_schema.json`
   
3. **Target Schema File** (describes your desired output structure)
   - `target_schema.json`
   
4. **Transformation Rules File** (defines how to transform the data)
   - `transformation_mapping.json`

**Request Format:**
```json
{
  "source_parquet_file": "data.parquet",
  "source_schema_file": "source_schema.json",
  "target_schema_file": "target_schema.json",
  "transformation_mapping_file": "transformation_mapping.json",
  "output_filename": "result",
  "output_format": "json"
}
```

**Response (Success) - Direct API:**
```json
{
  "status": "success",
  "run_id": "20250913_174257",
  "source_file_path": "C:/path/to/your/data.parquet",
  "output_file": "result_20250913_174257",
  "output_format": "json",
  "rows_processed": 100,
  "columns_output": 5,
  "processing_time_seconds": 0.15,
  "log_file": "../storage/logs/etl_20250913_174257_20250913_174257.log",
  "error_file": null,
  "message": "Direct transformation completed successfully"
}
```

**Response (Success) - File-based API:**
```json
{
  "status": "success",
  "run_id": "20250913_174257",
  "source_parquet_file": "data.parquet",
  "source_schema_file": "source_schema.json",
  "target_schema_file": "target_schema.json",
  "transformation_mapping_file": "transformation_mapping.json",
  "output_file": "result_20250913_174257",
  "output_format": "json",
  "rows_processed": 100,
  "columns_output": 5,
  "processing_time_seconds": 0.15,
  "log_file": "../storage/logs/etl_20250913_174257_20250913_174257.log",
  "error_file": null,
  "message": "Independent transformation completed successfully"
}
```

**Response (Error):**
```json
{
  "status": "error",
  "run_id": "20250913_174257",
  "source_file": "data.parquet",
  "output_file": "result",
  "log_file": "../storage/logs/etl_20250913_174257_20250913_174257.log",
  "error_file": "../storage/transformation_error/transformation_error_20250913_174257.json",
  "error_message": "Source column 'email' not found",
  "message": "Transformation failed. Check error file for details."
}
```

## 📁 **File Format Examples**

### **1. Source Schema File** (`source_schema.json`)
```json
{
  "role": "source",
  "fileType": "parquet",
  "schemaId": "schm-parquet-1001",
  "schemaName": "customer_data_v1",
  "attributes": {
    "first_name": {
      "name": "first_name",
      "dataType": "string",
      "column_no": 1
    },
    "last_name": {
      "name": "last_name",
      "dataType": "string",
      "column_no": 2
    },
    "email": {
      "name": "email",
      "dataType": "string",
      "column_no": 3
    },
    "birth_date": {
      "name": "birth_date",
      "dataType": "date",
      "column_no": 4
    }
  }
}
```

### **2. Target Schema File** (`target_schema.json`)
```json
{
  "role": "target",
  "fileType": "json",
  "schemaId": "schm-json-2001",
  "schemaName": "customer_output_v1",
  "attributes": {
    "full_name": {
      "name": "full_name",
      "dataType": "string",
      "column_no": 1
    },
    "email_clean": {
      "name": "email_clean",
      "dataType": "string",
      "column_no": 2
    },
    "age_group": {
      "name": "age_group",
      "dataType": "string",
      "column_no": 3
    },
    "is_valid_email": {
      "name": "is_valid_email",
      "dataType": "boolean",
      "column_no": 4
    }
  }
}
```

### **3. Transformation Rules File** (`transformation_mapping.json`)
```json
{
  "mappingId": "transform-001",
  "mappingName": "customer_data_transformation",
  "createdAt": "2025-01-27T10:00:00.000Z",
  "sourceSchemaId": "schm-parquet-1001",
  "targetSchemaId": "schm-json-2001",
  "rules": [
    {
      "id": "rule_001",
      "name": "Full Name Creation",
      "description": "Combine first and last name",
      "trns": "STRING[CONCAT(ATTR(first_name), ' ', ATTR(last_name))]",
      "affected_source": ["first_name", "last_name"],
      "affected_target": "full_name"
    },
    {
      "id": "rule_002",
      "name": "Email Cleaning",
      "description": "Clean email address",
      "trns": "STRING[TRIM(ATTR(email))]",
      "affected_source": ["email"],
      "affected_target": "email_clean"
    },
    {
      "id": "rule_003",
      "name": "Age Group Classification",
      "description": "Classify based on birth year",
      "trns": "LOGICAL[IF(CONTAINS(ATTR(birth_date), '1990'), 'Adult', 'Young')]",
      "affected_source": ["birth_date"],
      "affected_target": "age_group"
    },
    {
      "id": "rule_004",
      "name": "Email Validation",
      "description": "Check if email is valid",
      "trns": "LOGICAL[IF(ENDSWITH(ATTR(email), '.com'), True, False)]",
      "affected_source": ["email"],
      "affected_target": "is_valid_email"
    }
  ]
}
```

## 🎯 **Transformation Language Reference**

### **Basic Syntax**
```
OPERATION[FUNCTION(ARGUMENTS)]
```

### **Available Operations**

#### **STRING Operations**
- `STRING[CONCAT(ATTR(column1), ' ', ATTR(column2))]` - Combine strings
- `STRING[UPPER(ATTR(column))]` - Convert to uppercase
- `STRING[LOWER(ATTR(column))]` - Convert to lowercase
- `STRING[TRIM(ATTR(column))]` - Remove whitespace
- `STRING[ENDSWITH(ATTR(column), '.com')]` - Check if ends with text
- `STRING[CONTAINS(ATTR(column), 'text')]` - Check if contains text
- `STRING[SUBSTR(ATTR(column), 0, 10)]` - Extract substring

#### **LOGICAL Operations**
- `LOGICAL[IF(condition, true_value, false_value)]` - Conditional logic
- `LOGICAL[AND(condition1, condition2)]` - Logical AND
- `LOGICAL[OR(condition1, condition2)]` - Logical OR
- `LOGICAL[NOT(condition)]` - Logical NOT

#### **MATH Operations**
- `MATH[ADD(ATTR(column1), ATTR(column2))]` - Addition
- `MATH[SUB(ATTR(column1), ATTR(column2))]` - Subtraction
- `MATH[MUL(ATTR(column1), ATTR(column2))]` - Multiplication
- `MATH[DIV(ATTR(column1), ATTR(column2))]` - Division

#### **DATE Operations**
- `DATE[FORMAT(ATTR(date_column), 'YYYY-MM-DD')]` - Format date
- `DATE[EXTRACT(ATTR(date_column), 'year')]` - Extract year

#### **ARRAY Operations**
- `ARRAY[SPLIT(ATTR(column), ',')]` - Split strings into arrays
- `ARRAY[JOIN(ATTR(column), ',')]` - Join arrays into strings

#### **AGGREGATION Operations**
- `AGGREGATION[SUM(ATTR(column))]` - Sum values
- `AGGREGATION[AVG(ATTR(column))]` - Average values
- `AGGREGATION[COUNT(ATTR(column))]` - Count values

#### **DIRECT Operations**
- `DIRECT[ATTR(column_name)]` - Direct column reference

### **Column References**
- `ATTR(column_name)` - Reference a column
- `'text'` - Literal text (use single quotes)
- `123` - Literal number

## 📤 **Output Formats**

### **Supported Formats**
- `"json"` - JSON format (.jsonl file)
- `"csv"` - CSV format (.csv file)
- `"xlsx"` - Excel format (.xlsx file)
- `"xml"` - XML format (.xml file)
- `"fixed_width"` - Fixed-width text (.txt file)
- `"txt"` - Text format (.txt file)

### **Output File Location**
All output files are saved in: `storage/transformed/`

### **Unique Filenames**
- **Automatic Timestamps**: All files (output, log, error) are automatically given unique names with timestamps
- **Output Files**: `{your_filename}_{YYYYMMDD_HHMMSS}.{extension}`
- **Log Files**: `etl_{YYYYMMDD_HHMMSS}.log`
- **Error Files**: `transformation_error_{run_id}.json`
- **Examples**: 
  - Output: `result_20250913_182532.jsonl`
  - Log: `etl_20250913_182532.log`
  - Error: `transformation_error_20250913_182532.json`
- **No Conflicts**: Multiple users can run transformations simultaneously without file conflicts
- **Easy Tracking**: Each transformation run has unique files for all outputs

### **Fixed-Width Output Features**

- **Precise Positioning**: Define exact start positions for each field
- **Fixed Widths**: Specify exact character widths for each column
- **Automatic Alignment**: Numeric values are right-aligned, text values are left-aligned
- **Truncation Handling**: Long values are automatically truncated with warnings
- **Gap Support**: Fields can have gaps between them

#### **Fixed-Width Target Schema Example**
```json
{
  "role": "target",
  "fileType": "fixed_width",
  "schemaId": "schm-fixed-2001",
  "schemaName": "customer_fixed_width_v1",
  "attributes": {
    "full_name": {
      "name": "full_name",
      "dataType": "string",
      "column_no": 1,
      "width": 30,
      "start_position": 0
    },
    "email_clean": {
      "name": "email_clean",
      "dataType": "string",
      "column_no": 2,
      "width": 40,
      "start_position": 30
    },
    "age_group": {
      "name": "age_group",
      "dataType": "string",
      "column_no": 3,
      "width": 10,
      "start_position": 70
    },
    "is_valid_email": {
      "name": "is_valid_email",
      "dataType": "boolean",
      "column_no": 4,
      "width": 5,
      "start_position": 80
    }
  }
}
```

#### **Fixed-Width Example Output**
```
John Doe                      john@example.com                        Adult     True 
Jane Smith                    jane@example.com                        Young     True 
Bob Johnson                   bob@example.com                         Young     True 
Alice Brown                   alice@example.com                       Young     True 
```

## 🚨 **Error Handling**

### **Error File System**
- **Location**: `storage/transformation_error/transformation_error_{run_id}.json`
- **Line Number Tracking**: Exact line numbers where errors occur
- **Rule-Level Details**: Specific transformation rule that caused the error
- **Stack Traces**: Full debugging information
- **Troubleshooting Guidance**: Built-in tips and solutions

### **Error Types**
- **TRANSFORMATION_RULE_ERROR**: Errors in individual transformation rules
- **FILTER_RULE_ERROR**: Errors in filter operations
- **TRANSFORMATION_EXECUTION_ERROR**: Errors during overall execution
- **SYSTEM_ERROR**: Unexpected system errors

### **API Response Integration**
- **Success**: `"error_file": null`
- **Error**: `"error_file": "../storage/transformation_error/transformation_error_{run_id}.json"`

### **Error File Contents**
```json
{
  "error_summary": {
    "run_id": "20250913_174257",
    "total_errors": 1,
    "source_file": "data.parquet",
    "output_file": "result",
    "status": "FAILED"
  },
  "errors": [
    {
      "error_type": "TRANSFORMATION_RULE_ERROR",
      "error_message": "Source column 'email' not found",
      "line_number": 2,
      "column_name": "email_clean",
      "transformation_rule": {
        "id": "rule_002",
        "trns": "STRING[TRIM(ATTR(email))]",
        "affected_target": "email_clean"
      }
    }
  ],
  "troubleshooting": {
    "common_solutions": [
      "Check column names in source data match schema definitions",
      "Verify transformation syntax in mapping rules",
      "Ensure data types are compatible with transformation functions"
    ]
  }
}
```

## 🧪 **How to Test**

### **Step 1: Start the Server**
```bash
cd transformationEngine
python start.py
```

### **Step 2: Test Health Check**
```bash
curl http://localhost:8001/health
```

### **Step 3: Test Transformation**
```bash
curl -X POST "http://localhost:8001/transform-independent" \
  -H "Content-Type: application/json" \
  -d '{
    "source_parquet_file": "lsad.parquet",
    "source_schema_file": "source_schema.json",
    "target_schema_file": "target_schema.json",
    "transformation_mapping_file": "transformation_mapping.json",
    "output_filename": "test_output",
    "output_format": "json"
  }'
```

### **Step 4: Check Results**
- **Success**: Check `storage/transformed/test_output.jsonl`
- **Error**: Check `storage/transformation_error/transformation_error_{run_id}.json`

### **Step 5: Run Test Script**
```bash
python test_api_usage.py
```

## 📝 **Frontend Integration Examples**

### **JavaScript/Fetch Example**
```javascript
async function transformData() {
  const requestData = {
    source_parquet_file: "data.parquet",
    source_schema_file: "source_schema.json",
    target_schema_file: "target_schema.json",
    transformation_mapping_file: "transformation_mapping.json",
    output_filename: "result",
    output_format: "json"
  };

  try {
    const response = await fetch('http://localhost:8001/transform-independent', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData)
    });

    const result = await response.json();
    
    if (result.status === 'success') {
      console.log('Transformation successful!');
      console.log(`Processed ${result.rows_processed} rows`);
      console.log(`Output file: ${result.output_file}`);
    } else {
      console.error('Transformation failed:', result.error_message);
      console.log('Check error file:', result.error_file);
    }
  } catch (error) {
    console.error('Request failed:', error);
  }
}
```

### **Python Requests Example**
```python
import requests
import json

def transform_data():
    url = "http://localhost:8001/transform-independent"
    
    data = {
        "source_parquet_file": "data.parquet",
        "source_schema_file": "source_schema.json",
        "target_schema_file": "target_schema.json",
        "transformation_mapping_file": "transformation_mapping.json",
        "output_filename": "result",
        "output_format": "json"
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        
        if result['status'] == 'success':
            print(f"Success! Processed {result['rows_processed']} rows")
            print(f"Output file: {result['output_file']}")
        else:
            print(f"Error: {result['error_message']}")
            print(f"Error file: {result['error_file']}")
            
    except Exception as e:
        print(f"Request failed: {e}")

transform_data()
```

## 🔍 **Troubleshooting**

### **Common Issues**

1. **Server Not Running**
   - **Error**: Connection refused
   - **Solution**: Start server with `cd transformationEngine && python start.py`

2. **File Not Found**
   - **Error**: Input files not found
   - **Solution**: Ensure all files are in `storage/input/` folder

3. **Column Not Found**
   - **Error**: Source column 'email' not found
   - **Solution**: Check column names in source data match schema

4. **Transformation Syntax Error**
   - **Error**: Unknown function or syntax error
   - **Solution**: Check transformation syntax in rules

5. **Data Type Mismatch**
   - **Error**: Data type incompatible
   - **Solution**: Ensure data types match transformation functions

### **Debug Steps**

1. **Check Health**: `GET /health`
2. **Check Error File**: Look at `error_file` in response
3. **Check Log File**: Review detailed logs
4. **Test Individual Rules**: Test each transformation rule separately
5. **Verify File Formats**: Ensure all files are valid JSON

## 📊 **API Response Fields**

| Field | Description |
|-------|-------------|
| `status` | "success" or "error" |
| `run_id` | Unique identifier for this run |
| `source_parquet_file` | Input data file name |
| `source_schema_file` | Source schema file name |
| `target_schema_file` | Target schema file name |
| `transformation_mapping_file` | Transformation rules file name |
| `output_file` | Output file name |
| `output_format` | Output format used |
| `rows_processed` | Number of rows processed |
| `columns_output` | Number of output columns |
| `processing_time_seconds` | Time taken to process |
| `log_file` | Path to detailed log file |
| `error_file` | Path to error file (if error occurred) |
| `error_message` | Error message (if error occurred) |
| `message` | Human-readable status message |

## 🎯 **Quick Start Checklist**

1. ✅ **Start Server**: `cd transformationEngine && python start.py`
2. ✅ **Test Health**: `curl http://localhost:8001/health`
3. ✅ **Prepare Files**: Place all files in `storage/input/`
4. ✅ **Make Request**: POST to `/transform-independent`
5. ✅ **Check Results**: Look in `storage/transformed/` or `storage/transformation_error/`

## 🚀 **Setup and Installation**

### **1. Install Dependencies**
```bash
cd transformationEngine
pip install -r requirements.txt
```

### **2. Create Directories**
```bash
mkdir -p storage/input storage/transformed storage/logs storage/transformation_error
```

### **3. Start Server**
```bash
python start.py
```

### **4. Test Setup**
```bash
python test_api_usage.py
```

## 📞 **Support**

- **API Documentation**: `http://localhost:8001/docs`
- **Health Check**: `http://localhost:8001/health`
- **Log Files**: Check `storage/logs/` for detailed information
- **Error Files**: Check `storage/transformation_error/` for error details

## 🎯 **Key Features**

### **Core Features**
- **Schema-Based Reading**: Reads input files using provided source schema
- **Flexible Transformations**: Supports complex transformation expressions
- **Multiple Output Formats**: JSON, CSV, XLSX, XML, Fixed-Width
- **Comprehensive Logging**: Detailed logs for debugging and monitoring
- **Error Handling**: Robust error handling with detailed error messages
- **Validation**: Input validation and data type checking
- **Independent Operation**: Works with separate schema and mapping files

### **Advanced Features**
- **Fixed-Width Output**: Precise positioning and alignment
- **Gap Support**: Fields can have gaps between them
- **Mixed Data Types**: Smart alignment based on data type
- **Truncation Handling**: Automatic truncation with warnings
- **Performance Optimization**: Memory efficient processing
- **Streaming Support**: Suitable for large datasets

## 📈 **Performance**

- **Fast Processing**: Optimized for high-performance data processing
- **Memory Efficient**: Suitable for large datasets
- **Streaming Support**: Can handle large files without memory issues
- **Parallel Processing**: Supports concurrent requests

## 🎯 **Use Cases**

### **Legacy System Integration**
- Mainframe data feeds
- COBOL program interfaces
- Fixed-format report generation

### **Data Exchange**
- EDI (Electronic Data Interchange)
- Banking file formats
- Government reporting formats

### **Report Generation**
- Formatted reports
- Print-ready output
- Structured data files

### **Data Transformation**
- ETL pipelines
- Data migration
- Format conversion
- Data cleansing

## 📋 **Best Practices**

1. **Schema Design**: Carefully design schemas for optimal performance
2. **Field Positioning**: Plan field positions for fixed-width output
3. **Error Handling**: Always check response status and error messages
4. **Logging**: Monitor logs for debugging and performance
5. **Testing**: Test with representative data before production
6. **Documentation**: Keep detailed documentation of transformations

---

**ETL Transformation Engine v1.0.0** - Complete Guide for Developers and Frontend Integration
