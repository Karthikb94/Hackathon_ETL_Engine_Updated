#!/bin/bash

# ETL Engine API Examples
# Make sure the server is running: python run.py

BASE_URL="http://localhost:8001"

echo "🚀 ETL Engine API Examples"
echo "=========================="

# 1. Health Check
echo "1. Health Check"
echo "---------------"
curl -s "$BASE_URL/health" | python -m json.tool
echo ""

# 2. Simple Transformation Example
echo "2. Simple Pass-Through Transformation"
echo "------------------------------------"
curl -X POST "$BASE_URL/transform" \
  -H "Content-Type: application/json" \
  -d '{
    "source_file_path": "storage/input/parquet_from_csv.parquet",
    "source_schema": {
      "role": "source",
      "fileType": "parquet",
      "attributes": {
        "customer_id": {"dataType": "integer", "column_no": 1, "start_position": 0, "width": 8},
        "name": {"dataType": "string", "column_no": 2, "start_position": 8, "width": 30},
        "email": {"dataType": "string", "column_no": 3, "start_position": 38, "width": 40},
        "city": {"dataType": "string", "column_no": 4, "start_position": 78, "width": 20},
        "total_amount": {"dataType": "float", "column_no": 5, "start_position": 98, "width": 12}
      }
    },
    "target_schema": {"role": "target", "fileType": "json", "attributes": {}},
    "transformation_mapping": {
      "mappings": [
        {"id": "pass_customer_id", "affected_target": "customer_id", "affected_source": ["customer_id"], "trns": ""},
        {"id": "pass_name", "affected_target": "name", "affected_source": ["name"], "trns": ""},
        {"id": "pass_email", "affected_target": "email", "affected_source": ["email"], "trns": ""},
        {"id": "pass_city", "affected_target": "city", "affected_source": ["city"], "trns": ""},
        {"id": "pass_amount", "affected_target": "total_amount", "affected_source": ["total_amount"], "trns": ""}
      ]
    }
  }' | python -m json.tool
echo ""

# 3. CSV Output Example
echo "3. CSV Output Transformation"
echo "----------------------------"
curl -X POST "$BASE_URL/transform" \
  -H "Content-Type: application/json" \
  -d '{
    "source_file_path": "storage/input/parquet_from_csv.parquet",
    "source_schema": {
      "role": "source",
      "fileType": "parquet",
      "attributes": {
        "customer_id": {"dataType": "integer", "column_no": 1, "start_position": 0, "width": 8},
        "name": {"dataType": "string", "column_no": 2, "start_position": 8, "width": 30},
        "email": {"dataType": "string", "column_no": 3, "start_position": 38, "width": 40}
      }
    },
    "target_schema": {"role": "target", "fileType": "csv", "attributes": {}},
    "transformation_mapping": {
      "mappings": [
        {"id": "pass_customer_id", "affected_target": "customer_id", "affected_source": ["customer_id"], "trns": ""},
        {"id": "pass_name", "affected_target": "name", "affected_source": ["name"], "trns": ""},
        {"id": "pass_email", "affected_target": "email", "affected_source": ["email"], "trns": ""}
      ]
    }
  }' | python -m json.tool
echo ""

# 4. XML Output Example
echo "4. XML Output Transformation"
echo "----------------------------"
curl -X POST "$BASE_URL/transform" \
  -H "Content-Type: application/json" \
  -d '{
    "source_file_path": "storage/input/parquet_from_csv.parquet",
    "source_schema": {
      "role": "source",
      "fileType": "parquet",
      "attributes": {
        "customer_id": {"dataType": "integer", "column_no": 1, "start_position": 0, "width": 8},
        "name": {"dataType": "string", "column_no": 2, "start_position": 8, "width": 30},
        "email": {"dataType": "string", "column_no": 3, "start_position": 38, "width": 40}
      }
    },
    "target_schema": {"role": "target", "fileType": "xml", "attributes": {}},
    "transformation_mapping": {
      "mappings": [
        {"id": "pass_customer_id", "affected_target": "customer_id", "affected_source": ["customer_id"], "trns": ""},
        {"id": "pass_name", "affected_target": "name", "affected_source": ["name"], "trns": ""},
        {"id": "pass_email", "affected_target": "email", "affected_source": ["email"], "trns": ""}
      ]
    }
  }' | python -m json.tool
echo ""

echo "✅ Examples completed!"
echo "📁 Check storage/transformed/ for output files"
echo "📄 Check storage/logs/ for operation logs"
