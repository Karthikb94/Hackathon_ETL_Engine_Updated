#!/usr/bin/env python3
"""
Simple test script to verify ETL Engine is working correctly.
Run this script to test all basic functionality.
"""

import requests
import json
import time
import os

def test_server_connection():
    """Test if the ETL Engine server is running."""
    print("🔍 Testing server connection...")
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and healthy!")
            return True
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        print("💡 Make sure the ETL Engine is running (python run.py)")
        return False

def test_simple_transformation():
    """Test a simple CSV to JSON transformation."""
    print("\n🧪 Testing simple transformation...")
    
    # Simple test request
    test_request = {
        "source_file_path": "storage/input/csv_source.parquet",
        "source_schema": {
            "role": "source",
            "fileType": "csv",
            "schemaId": "test-csv-001",
            "schemaName": "test_csv_schema",
            "attributes": {
                "employee_id": {"name": "employee_id", "dataType": "integer", "column_no": 1},
                "first_name": {"name": "first_name", "dataType": "string", "column_no": 2},
                "last_name": {"name": "last_name", "dataType": "string", "column_no": 3},
                "email": {"name": "email", "dataType": "string", "column_no": 4},
                "department": {"name": "department", "dataType": "string", "column_no": 5},
                "salary": {"name": "salary", "dataType": "float", "column_no": 6},
                "hire_date": {"name": "hire_date", "dataType": "date", "column_no": 7},
                "is_active": {"name": "is_active", "dataType": "boolean", "column_no": 8}
            }
        },
        "target_schema": {
            "role": "target",
            "fileType": "json",
            "schemaId": "test-json-001",
            "schemaName": "test_json_schema",
            "attributes": {
                "employee_id": {"name": "employee_id", "dataType": "integer"},
                "first_name": {"name": "first_name", "dataType": "string"},
                "last_name": {"name": "last_name", "dataType": "string"},
                "email": {"name": "email", "dataType": "string"},
                "department": {"name": "department", "dataType": "string"},
                "salary": {"name": "salary", "dataType": "float"},
                "hire_date": {"name": "hire_date", "dataType": "date"},
                "is_active": {"name": "is_active", "dataType": "boolean"}
            }
        },
        "transformation_mapping": {
            "mappingId": "test-mapping-001",
            "mappingName": "test_transformation",
            "createdAt": "2025-09-16T10:00:00Z",
            "sourceSchemaId": "test-csv-001",
            "targetSchemaId": "test-json-001",
            "rules": [
                {"id": "rule_1", "trns": "DIRECT[ATTR('employee_id')]", "affected_source": ["employee_id"], "affected_target": "employee_id"},
                {"id": "rule_2", "trns": "STRING[UPPER(attr('first_name'))]", "affected_source": ["first_name"], "affected_target": "first_name"},
                {"id": "rule_3", "trns": "STRING[UPPER(attr('last_name'))]", "affected_source": ["last_name"], "affected_target": "last_name"},
                {"id": "rule_4", "trns": "STRING[LOWER(attr('email'))]", "affected_source": ["email"], "affected_target": "email"},
                {"id": "rule_5", "trns": "DIRECT[ATTR('department')]", "affected_source": ["department"], "affected_target": "department"},
                {"id": "rule_6", "trns": "MATH[ROUND(attr('salary'), 2)]", "affected_source": ["salary"], "affected_target": "salary"},
                {"id": "rule_7", "trns": "DATE[FORMAT(attr('hire_date'), 'YYYY-MM-DD')]", "affected_source": ["hire_date"], "affected_target": "hire_date"},
                {"id": "rule_8", "trns": "DIRECT[ATTR('is_active')]", "affected_source": ["is_active"], "affected_target": "is_active"}
            ]
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:8001/transform",
            json=test_request,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Transformation successful!")
            print(f"   Run ID: {result.get('run_id')}")
            print(f"   Output File: {result.get('output_file')}")
            print(f"   Processing Time: {result.get('processing_time_seconds')}s")
            print(f"   Rows Processed: {result.get('rows_processed')}")
            print(f"   Columns Output: {result.get('columns_output')}")
            
            # Check if output file exists
            output_file = result.get('output_file')
            if output_file and os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"   Output File Size: {file_size} bytes")
                return True
            else:
                print(f"   ⚠️  Output file not found: {output_file}")
                return False
        else:
            print(f"❌ Transformation failed - HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error_message', 'Unknown error')}")
            except:
                print(f"   Raw response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_api_documentation():
    """Test if API documentation is accessible."""
    print("\n📚 Testing API documentation...")
    try:
        response = requests.get("http://localhost:8001/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API documentation is accessible!")
            print("   Visit: http://localhost:8001/docs")
            return True
        else:
            print(f"❌ API documentation returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot access API documentation: {e}")
        return False

def check_sample_files():
    """Check if sample files exist."""
    print("\n📁 Checking sample files...")
    
    sample_files = [
        "storage/input/csv_source.parquet",
        "storage/input/fixedwidth_source.parquet",
        "storage/input/json_source.parquet",
        "storage/input/xml_source.parquet"
    ]
    
    all_exist = True
    for file_path in sample_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✅ {file_path} ({file_size} bytes)")
        else:
            print(f"❌ {file_path} - NOT FOUND")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests."""
    print("🚀 ETL Engine Test Suite")
    print("=" * 50)
    
    # Test 1: Check sample files
    files_ok = check_sample_files()
    
    # Test 2: Test server connection
    server_ok = test_server_connection()
    
    if not server_ok:
        print("\n❌ Server is not running. Please start the ETL Engine first:")
        print("   1. Open VS Code")
        print("   2. Open terminal (Ctrl + `)")
        print("   3. Run: python run.py")
        print("   4. Keep terminal open")
        return
    
    # Test 3: Test API documentation
    docs_ok = test_api_documentation()
    
    # Test 4: Test simple transformation
    transform_ok = test_simple_transformation()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Sample Files: {'✅ PASS' if files_ok else '❌ FAIL'}")
    print(f"Server Connection: {'✅ PASS' if server_ok else '❌ FAIL'}")
    print(f"API Documentation: {'✅ PASS' if docs_ok else '❌ FAIL'}")
    print(f"Transformation: {'✅ PASS' if transform_ok else '❌ FAIL'}")
    
    if all([files_ok, server_ok, docs_ok, transform_ok]):
        print("\n🎉 ALL TESTS PASSED! Your ETL Engine is working perfectly!")
        print("\n📋 Next Steps:")
        print("   1. Visit http://localhost:8001/docs for interactive API documentation")
        print("   2. Try different transformation scenarios")
        print("   3. Check output files in storage/transformed/")
        print("   4. Read the documentation files for more details")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
        print("\n🔧 Troubleshooting:")
        print("   1. Make sure the ETL Engine is running (python run.py)")
        print("   2. Check if all dependencies are installed")
        print("   3. Verify sample files exist in storage/input/")
        print("   4. Check log files in storage/logs/ for detailed errors")

if __name__ == "__main__":
    main()
