#!/usr/bin/env python3
"""
Test script for the restructured Transformation Engine
"""

import requests
import json
import os

# Test the new file-based transformation endpoint
def test_transformation_engine():
    base_url = "http://localhost:8001"
    
    # Test data
    test_request = {
        "input_filename": "lsad.parquet",
        "output_filename": "lsad_transformed.json",
        "output_format": "json",
        "mapping_config": {
            "mappings": [
                {
                    "target": "full_name",
                    "source": "firstName,lastName",
                    "transform": "trns: STRING[CONCAT(attr('firstName'), ' ', attr('lastName'))]"
                },
                {
                    "target": "email_status",
                    "source": "email",
                    "transform": "trns: LOGICAL[IF(ENDSWITH(TRIM(ATTR('email')), '@mail.com'), 'Valid', 'Invalid')]"
                },
                {
                    "target": "age_group",
                    "source": "age",
                    "transform": "trns: LOGICAL[IF(GREATER_THAN(attr('age'), 30), 'Adult', 'Young')]"
                }
            ]
        }
    }
    
    print("🧪 Testing Transformation Engine...")
    print(f"📁 Input file: {test_request['input_filename']}")
    print(f"📁 Output file: {test_request['output_filename']}")
    print(f"🔧 Transformations: {len(test_request['mapping_config']['mappings'])}")
    print("=" * 60)
    
    try:
        # Test health check
        print("1. Testing health check...")
        health_response = requests.get(f"{base_url}/health")
        if health_response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {health_response.json()}")
        else:
            print(f"❌ Health check failed: {health_response.status_code}")
            return
        
        # Test transformation
        print("\n2. Testing file-based transformation...")
        transform_response = requests.post(
            f"{base_url}/transform-file",
            json=test_request,
            headers={"Content-Type": "application/json"}
        )
        
        if transform_response.status_code == 200:
            result = transform_response.json()
            print("✅ Transformation completed successfully!")
            print(f"   Run ID: {result['run_id']}")
            print(f"   Rows processed: {result['rows_processed']}")
            print(f"   Columns output: {result['columns_output']}")
            print(f"   Processing time: {result['processing_time_seconds']}s")
            print(f"   Log file: {result['log_file']}")
            
            # Check if output file was created
            output_path = f"storage/transformed/{test_request['output_filename']}"
            if os.path.exists(output_path):
                print(f"✅ Output file created: {output_path}")
            else:
                print(f"❌ Output file not found: {output_path}")
        else:
            print(f"❌ Transformation failed: {transform_response.status_code}")
            print(f"   Error: {transform_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the transformation engine is running:")
        print("   cd transformationEngine && python start.py")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_transformation_engine()
