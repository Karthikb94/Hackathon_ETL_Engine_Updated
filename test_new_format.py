#!/usr/bin/env python3
"""
Test script for the new schema format API.
Tests the /transform endpoint with the new structured schema format.
"""

import requests
import json
import time

# API endpoint
API_URL = "http://localhost:8000/transform"

def test_new_format_api():
    """Test the minimal API format with only 4 required parameters."""
    print("🧪 Testing Minimal API Format (4 Required Parameters)")
    print("=" * 50)
    
    # Test data using the minimal format - only 4 required parameters
    test_request = {
        "source_file_path": "C:/Users/karth/OneDrive/Desktop/course/Hackathon_ETL_Engine_Updated/storage/input/lsad.parquet",
        "source_schema": {
            "role": "source",
            "fileType": "parquet",
            "schemaId": "schm-parquet-1001",
            "schemaName": "customer_parquet_v1",
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
                "age": {
                    "name": "age",
                    "dataType": "integer",
                    "column_no": 4
                },
                "city": {
                    "name": "city",
                    "dataType": "string",
                    "column_no": 5
                }
            }
        },
        "target_schema": {
            "role": "target",
            "fileType": "fixedWidth",
            "schemaId": "schm-fix-2001",
            "schemaName": "customer_fixedwidth_v1",
            "attributes": {
                "first_name": {
                    "name": "first_name",
                    "dataType": "string",
                    "start_pos": 1,
                    "width": 20
                },
                "last_name": {
                    "name": "last_name",
                    "dataType": "string", 
                    "start_pos": 21,
                    "width": 20
                },
                "email": {
                    "name": "email",
                    "dataType": "string",
                    "start_pos": 41,
                    "width": 30
                },
                "age": {
                    "name": "age",
                    "dataType": "integer",
                    "start_pos": 71,
                    "width": 3
                },
                "city": {
                    "name": "city",
                    "dataType": "string",
                    "start_pos": 74,
                    "width": 20
                }
            }
        },
        "transformation_mapping": {
            "mappingId": "d98f31c3-7973-4049-a719-a9359bdbfdef",
            "mappingName": "customer_parquet_to_fixedwidth",
            "createdAt": "2025-09-13T19:00:00.000Z",
            "sourceSchemaId": "schm-parquet-1001",
            "targetSchemaId": "schm-fix-2001",
            "rules": [
                {
                    "id": "m1",
                    "trns": "DIRECT[ATTR(first_name)]",
                    "affected_source": ["first_name"],
                    "affected_target": "first_name"
                },
                {
                    "id": "m2", 
                    "trns": "DIRECT[ATTR(last_name)]",
                    "affected_source": ["last_name"],
                    "affected_target": "last_name"
                },
                {
                    "id": "m3",
                    "trns": "STRING[TRIM(ATTR(email))]",
                    "affected_source": ["email"],
                    "affected_target": "email"
                },
                {
                    "id": "m4",
                    "trns": "DIRECT[ATTR(age)]",
                    "affected_source": ["age"],
                    "affected_target": "age"
                },
                {
                    "id": "m5",
                    "trns": "STRING[UPPER(ATTR(city))]",
                    "affected_source": ["city"],
                    "affected_target": "city"
                }
            ]
        }
    }
    
    print("📋 Test Request:")
    print(f"  Source File: {test_request['source_file_path']}")
    print(f"  Source Schema ID: {test_request['source_schema']['schemaId']}")
    print(f"  Target Schema ID: {test_request['target_schema']['schemaId']}")
    print(f"  Mapping ID: {test_request['transformation_mapping']['mappingId']}")
    print()
    
    try:
        print("🚀 Sending request to API...")
        response = requests.post(API_URL, json=test_request, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Transformation successful!")
            print(f"  Run ID: {result['run_id']}")
            print(f"  Output File: {result['output_file']}")
            print(f"  Rows Processed: {result['rows_processed']}")
            print(f"  Columns Output: {result['columns_output']}")
            print(f"  Processing Time: {result['processing_time_seconds']} seconds")
            print(f"  Log File: {result['log_file']}")
            print(f"  Error File: {result['error_file']}")
            
            # Check if output file exists
            import os
            output_path = f"../storage/transformed/{result['output_file']}"
            if os.path.exists(output_path):
                print(f"✅ Output file created: {output_path}")
                # Show first few lines of output
                with open(output_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:3]
                    print("📄 Sample output:")
                    for i, line in enumerate(lines, 1):
                        print(f"  Line {i}: {line.strip()}")
            else:
                print(f"❌ Output file not found: {output_path}")
                
        else:
            print("❌ Transformation failed!")
            try:
                error_data = response.json()
                print(f"  Error: {error_data.get('detail', 'Unknown error')}")
                if 'error_file' in error_data:
                    print(f"  Error File: {error_data['error_file']}")
            except:
                print(f"  Raw response: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed! Make sure the API server is running.")
        print("   Run: python -m transformationEngine.start")
    except requests.exceptions.Timeout:
        print("❌ Request timed out!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_health_check():
    """Test the health check endpoint."""
    print("\n🏥 Testing Health Check...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ API is healthy: {health_data['service']} v{health_data['version']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 ETL Engine - Minimal API Test (4 Required Parameters)")
    print("=" * 60)
    
    # Test health check first
    if test_health_check():
        # Run the main test
        test_new_format_api()
    else:
        print("\n💡 To start the API server, run:")
        print("   cd transformationEngine")
        print("   python start.py")
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!")
