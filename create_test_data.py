#!/usr/bin/env python3
"""
Create test data files for ETL Engine API testing.
This script creates sample parquet files and API request bodies.
"""

import polars as pl
import json
import os
from datetime import datetime, date

def create_sample_data():
    """Create sample data for testing."""
    print("📊 Creating sample test data...")
    
    # Sample employee data
    data = {
        "employee_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "first_name": ["John", "Jane", "Bob", "Alice", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry"],
        "last_name": ["Doe", "Smith", "Johnson", "Brown", "Wilson", "Davis", "Miller", "Garcia", "Martinez", "Anderson"],
        "email": [
            "john.doe@company.com", "jane.smith@company.com", "bob.johnson@company.com",
            "alice.brown@company.com", "charlie.wilson@company.com", "diana.davis@company.com",
            "eve.miller@company.com", "frank.garcia@company.com", "grace.martinez@company.com",
            "henry.anderson@company.com"
        ],
        "department": ["Engineering", "Marketing", "Sales", "HR", "Finance", "IT", "Operations", "Legal", "Support", "Research"],
        "salary": [75000.50, 68000.25, 72000.75, 65000.00, 80000.00, 70000.00, 75000.00, 85000.00, 60000.00, 90000.00],
        "hire_date": [
            "2020-01-15", "2019-03-22", "2021-06-10", "2018-11-05", "2022-02-14",
            "2020-07-30", "2019-12-01", "2021-04-18", "2018-09-12", "2022-01-08"
        ],
        "is_active": [True, True, False, True, True, True, False, True, True, True],
        "performance_rating": [4.5, 4.2, 3.8, 4.7, 4.9, 4.1, 3.9, 4.6, 4.3, 4.8],
        "years_experience": [5, 6, 3, 7, 2, 4, 5, 8, 6, 1]
    }
    
    return pl.DataFrame(data)

def create_parquet_files():
    """Create sample parquet files for different source formats."""
    print("📁 Creating parquet files...")
    
    # Ensure directories exist
    os.makedirs("storage/input", exist_ok=True)
    
    # Create sample data
    df = create_sample_data()
    
    # Create parquet files for different source formats
    print("   Creating CSV source parquet...")
    df.write_parquet("storage/input/csv_source.parquet")
    
    print("   Creating Fixed-Width source parquet...")
    df.write_parquet("storage/input/fixedwidth_source.parquet")
    
    print("   Creating JSON source parquet...")
    df.write_parquet("storage/input/json_source.parquet")
    
    print("   Creating XML source parquet...")
    df.write_parquet("storage/input/xml_source.parquet")
    
    print("   Creating Excel source parquet...")
    df.write_parquet("storage/input/excel_source.parquet")
    
    print("✅ Parquet files created successfully!")

def create_api_request_bodies():
    """Create API request body files for all 12 scenarios."""
    print("📝 Creating API request bodies...")
    
    # Base source schema for CSV
    csv_source_schema = {
        "role": "source",
        "fileType": "csv",
        "schemaId": "csv-001",
        "schemaName": "csv_source_schema",
        "attributes": {
            "employee_id": {"name": "employee_id", "dataType": "integer", "column_no": 1},
            "first_name": {"name": "first_name", "dataType": "string", "column_no": 2},
            "last_name": {"name": "last_name", "dataType": "string", "column_no": 3},
            "email": {"name": "email", "dataType": "string", "column_no": 4},
            "department": {"name": "department", "dataType": "string", "column_no": 5},
            "salary": {"name": "salary", "dataType": "float", "column_no": 6},
            "hire_date": {"name": "hire_date", "dataType": "date", "column_no": 7},
            "is_active": {"name": "is_active", "dataType": "boolean", "column_no": 8},
            "performance_rating": {"name": "performance_rating", "dataType": "float", "column_no": 9},
            "years_experience": {"name": "years_experience", "dataType": "integer", "column_no": 10}
        }
    }
    
    # Base source schema for Fixed-Width
    fixedwidth_source_schema = {
        "role": "source",
        "fileType": "fixedwidth",
        "schemaId": "fw-001",
        "schemaName": "fixedwidth_source_schema",
        "attributes": {
            "employee_id": {"name": "employee_id", "dataType": "integer", "column_no": 1},
            "first_name": {"name": "first_name", "dataType": "string", "column_no": 2},
            "last_name": {"name": "last_name", "dataType": "string", "column_no": 3},
            "email": {"name": "email", "dataType": "string", "column_no": 4},
            "department": {"name": "department", "dataType": "string", "column_no": 5},
            "salary": {"name": "salary", "dataType": "float", "column_no": 6},
            "hire_date": {"name": "hire_date", "dataType": "date", "column_no": 7},
            "is_active": {"name": "is_active", "dataType": "boolean", "column_no": 8},
            "performance_rating": {"name": "performance_rating", "dataType": "float", "column_no": 9},
            "years_experience": {"name": "years_experience", "dataType": "integer", "column_no": 10}
        }
    }
    
    # Base source schema for JSON
    json_source_schema = {
        "role": "source",
        "fileType": "json",
        "schemaId": "json-001",
        "schemaName": "json_source_schema",
        "attributes": {
            "employee_id": {"name": "employee_id", "dataType": "integer", "column_no": 1},
            "first_name": {"name": "first_name", "dataType": "string", "column_no": 2},
            "last_name": {"name": "last_name", "dataType": "string", "column_no": 3},
            "email": {"name": "email", "dataType": "string", "column_no": 4},
            "department": {"name": "department", "dataType": "string", "column_no": 5},
            "salary": {"name": "salary", "dataType": "float", "column_no": 6},
            "hire_date": {"name": "hire_date", "dataType": "date", "column_no": 7},
            "is_active": {"name": "is_active", "dataType": "boolean", "column_no": 8},
            "performance_rating": {"name": "performance_rating", "dataType": "float", "column_no": 9},
            "years_experience": {"name": "years_experience", "dataType": "integer", "column_no": 10}
        }
    }
    
    # Base source schema for XML
    xml_source_schema = {
        "role": "source",
        "fileType": "xml",
        "schemaId": "xml-001",
        "schemaName": "xml_source_schema",
        "attributes": {
            "employee_id": {"name": "employee_id", "dataType": "integer", "column_no": 1},
            "first_name": {"name": "first_name", "dataType": "string", "column_no": 2},
            "last_name": {"name": "last_name", "dataType": "string", "column_no": 3},
            "email": {"name": "email", "dataType": "string", "column_no": 4},
            "department": {"name": "department", "dataType": "string", "column_no": 5},
            "salary": {"name": "salary", "dataType": "float", "column_no": 6},
            "hire_date": {"name": "hire_date", "dataType": "date", "column_no": 7},
            "is_active": {"name": "is_active", "dataType": "boolean", "column_no": 8},
            "performance_rating": {"name": "performance_rating", "dataType": "float", "column_no": 9},
            "years_experience": {"name": "years_experience", "dataType": "integer", "column_no": 10}
        }
    }
    
    # Target schemas
    json_target_schema = {
        "role": "target",
        "fileType": "json",
        "schemaId": "json-target-001",
        "schemaName": "json_target_schema",
        "attributes": {
            "employee_id": {"name": "employee_id", "dataType": "integer"},
            "first_name": {"name": "first_name", "dataType": "string"},
            "last_name": {"name": "last_name", "dataType": "string"},
            "email": {"name": "email", "dataType": "string"},
            "department": {"name": "department", "dataType": "string"},
            "salary": {"name": "salary", "dataType": "float"},
            "hire_date": {"name": "hire_date", "dataType": "date"},
            "is_active": {"name": "is_active", "dataType": "boolean"},
            "performance_rating": {"name": "performance_rating", "dataType": "float"},
            "years_experience": {"name": "years_experience", "dataType": "integer"}
        }
    }
    
    csv_target_schema = {
        "role": "target",
        "fileType": "csv",
        "schemaId": "csv-target-001",
        "schemaName": "csv_target_schema",
        "attributes": {
            "employee_id": {"name": "employee_id", "dataType": "integer"},
            "first_name": {"name": "first_name", "dataType": "string"},
            "last_name": {"name": "last_name", "dataType": "string"},
            "email": {"name": "email", "dataType": "string"},
            "department": {"name": "department", "dataType": "string"},
            "salary": {"name": "salary", "dataType": "float"},
            "hire_date": {"name": "hire_date", "dataType": "date"},
            "is_active": {"name": "is_active", "dataType": "boolean"},
            "performance_rating": {"name": "performance_rating", "dataType": "float"},
            "years_experience": {"name": "years_experience", "dataType": "integer"}
        }
    }
    
    fixedwidth_target_schema = {
        "role": "target",
        "fileType": "fixedWidth",
        "schemaId": "fw-target-001",
        "schemaName": "fixedwidth_target_schema",
        "attributes": {
            "employee_id": {"name": "employee_id", "dataType": "integer", "start_position": 1, "width": 10},
            "first_name": {"name": "first_name", "dataType": "string", "start_position": 11, "width": 20},
            "last_name": {"name": "last_name", "dataType": "string", "start_position": 31, "width": 20},
            "email": {"name": "email", "dataType": "string", "start_position": 51, "width": 30},
            "department": {"name": "department", "dataType": "string", "start_position": 81, "width": 15},
            "salary": {"name": "salary", "dataType": "float", "start_position": 96, "width": 10},
            "hire_date": {"name": "hire_date", "dataType": "date", "start_position": 106, "width": 10},
            "is_active": {"name": "is_active", "dataType": "boolean", "start_position": 116, "width": 5},
            "performance_rating": {"name": "performance_rating", "dataType": "float", "start_position": 121, "width": 5},
            "years_experience": {"name": "years_experience", "dataType": "integer", "start_position": 126, "width": 3}
        }
    }
    
    xml_target_schema = {
        "role": "target",
        "fileType": "xml",
        "schemaId": "xml-target-001",
        "schemaName": "xml_target_schema",
        "attributes": {
            "employee_id": {"name": "employee_id", "dataType": "integer"},
            "first_name": {"name": "first_name", "dataType": "string"},
            "last_name": {"name": "last_name", "dataType": "string"},
            "email": {"name": "email", "dataType": "string"},
            "department": {"name": "department", "dataType": "string"},
            "salary": {"name": "salary", "dataType": "float"},
            "hire_date": {"name": "hire_date", "dataType": "date"},
            "is_active": {"name": "is_active", "dataType": "boolean"},
            "performance_rating": {"name": "performance_rating", "dataType": "float"},
            "years_experience": {"name": "years_experience", "dataType": "integer"}
        }
    }
    
    # Transformation rules
    transformation_rules = [
        {"id": "rule_1", "trns": "DIRECT[ATTR('employee_id')]", "affected_source": ["employee_id"], "affected_target": "employee_id"},
        {"id": "rule_2", "trns": "STRING[UPPER(attr('first_name'))]", "affected_source": ["first_name"], "affected_target": "first_name"},
        {"id": "rule_3", "trns": "STRING[UPPER(attr('last_name'))]", "affected_source": ["last_name"], "affected_target": "last_name"},
        {"id": "rule_4", "trns": "STRING[LOWER(attr('email'))]", "affected_source": ["email"], "affected_target": "email"},
        {"id": "rule_5", "trns": "DIRECT[ATTR('department')]", "affected_source": ["department"], "affected_target": "department"},
        {"id": "rule_6", "trns": "MATH[ROUND(attr('salary'), 2)]", "affected_source": ["salary"], "affected_target": "salary"},
        {"id": "rule_7", "trns": "DATE[FORMAT(attr('hire_date'), 'YYYY-MM-DD')]", "affected_source": ["hire_date"], "affected_target": "hire_date"},
        {"id": "rule_8", "trns": "DIRECT[ATTR('is_active')]", "affected_source": ["is_active"], "affected_target": "is_active"},
        {"id": "rule_9", "trns": "MATH[ROUND(attr('performance_rating'), 1)]", "affected_source": ["performance_rating"], "affected_target": "performance_rating"},
        {"id": "rule_10", "trns": "DIRECT[ATTR('years_experience')]", "affected_source": ["years_experience"], "affected_target": "years_experience"}
    ]
    
    # Create all 12 scenarios
    scenarios = [
        # CSV source scenarios
        {"name": "csv_to_json", "source_file": "csv_source.parquet", "source_schema": csv_source_schema, "target_schema": json_target_schema},
        {"name": "csv_to_csv", "source_file": "csv_source.parquet", "source_schema": csv_source_schema, "target_schema": csv_target_schema},
        {"name": "csv_to_fixedwidth", "source_file": "csv_source.parquet", "source_schema": csv_source_schema, "target_schema": fixedwidth_target_schema},
        {"name": "csv_to_xml", "source_file": "csv_source.parquet", "source_schema": csv_source_schema, "target_schema": xml_target_schema},
        
        # Fixed-Width source scenarios
        {"name": "fixedwidth_to_json", "source_file": "fixedwidth_source.parquet", "source_schema": fixedwidth_source_schema, "target_schema": json_target_schema},
        {"name": "fixedwidth_to_csv", "source_file": "fixedwidth_source.parquet", "source_schema": fixedwidth_source_schema, "target_schema": csv_target_schema},
        {"name": "fixedwidth_to_fixedwidth", "source_file": "fixedwidth_source.parquet", "source_schema": fixedwidth_source_schema, "target_schema": fixedwidth_target_schema},
        {"name": "fixedwidth_to_xml", "source_file": "fixedwidth_source.parquet", "source_schema": fixedwidth_source_schema, "target_schema": xml_target_schema},
        
        # JSON source scenarios
        {"name": "json_to_json", "source_file": "json_source.parquet", "source_schema": json_source_schema, "target_schema": json_target_schema},
        {"name": "json_to_csv", "source_file": "json_source.parquet", "source_schema": json_source_schema, "target_schema": csv_target_schema},
        {"name": "json_to_fixedwidth", "source_file": "json_source.parquet", "source_schema": json_source_schema, "target_schema": fixedwidth_target_schema},
        {"name": "json_to_xml", "source_file": "json_source.parquet", "source_schema": json_source_schema, "target_schema": xml_target_schema},
        
        # XML source scenarios
        {"name": "xml_to_json", "source_file": "xml_source.parquet", "source_schema": xml_source_schema, "target_schema": json_target_schema},
        {"name": "xml_to_csv", "source_file": "xml_source.parquet", "source_schema": xml_source_schema, "target_schema": csv_target_schema},
        {"name": "xml_to_fixedwidth", "source_file": "xml_source.parquet", "source_schema": xml_source_schema, "target_schema": fixedwidth_target_schema},
        {"name": "xml_to_xml", "source_file": "xml_source.parquet", "source_schema": xml_source_schema, "target_schema": xml_target_schema}
    ]
    
    # Create API request files for each scenario
    for i, scenario in enumerate(scenarios, 1):
        filename = f"api_request_scenario_{i:02d}_{scenario['name']}.json"
        
        request_body = {
            "source_file_path": f"storage/input/{scenario['source_file']}",
            "source_schema": scenario['source_schema'],
            "target_schema": scenario['target_schema'],
            "transformation_mapping": {
                "mappingId": f"mapping-{scenario['name']}-001",
                "mappingName": f"{scenario['name']}_transformation",
                "createdAt": datetime.now().isoformat(),
                "sourceSchemaId": scenario['source_schema']['schemaId'],
                "targetSchemaId": scenario['target_schema']['schemaId'],
                "rules": transformation_rules
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(request_body, f, indent=2)
        
        print(f"   Created {filename}")
    
    print("✅ API request bodies created successfully!")

def create_simple_test_request():
    """Create a simple test request for quick testing."""
    print("📝 Creating simple test request...")
    
    simple_request = {
        "source_file_path": "storage/input/csv_source.parquet",
        "source_schema": {
            "role": "source",
            "fileType": "csv",
            "schemaId": "simple-csv-001",
            "schemaName": "simple_csv_schema",
            "attributes": {
                "employee_id": {"name": "employee_id", "dataType": "integer", "column_no": 1},
                "first_name": {"name": "first_name", "dataType": "string", "column_no": 2},
                "last_name": {"name": "last_name", "dataType": "string", "column_no": 3},
                "email": {"name": "email", "dataType": "string", "column_no": 4},
                "department": {"name": "department", "dataType": "string", "column_no": 5},
                "salary": {"name": "salary", "dataType": "float", "column_no": 6}
            }
        },
        "target_schema": {
            "role": "target",
            "fileType": "json",
            "schemaId": "simple-json-001",
            "schemaName": "simple_json_schema",
            "attributes": {
                "employee_id": {"name": "employee_id", "dataType": "integer"},
                "first_name": {"name": "first_name", "dataType": "string"},
                "last_name": {"name": "last_name", "dataType": "string"},
                "email": {"name": "email", "dataType": "string"},
                "department": {"name": "department", "dataType": "string"},
                "salary": {"name": "salary", "dataType": "float"}
            }
        },
        "transformation_mapping": {
            "mappingId": "simple-mapping-001",
            "mappingName": "simple_transformation",
            "createdAt": datetime.now().isoformat(),
            "sourceSchemaId": "simple-csv-001",
            "targetSchemaId": "simple-json-001",
            "rules": [
                {"id": "rule_1", "trns": "DIRECT[ATTR('employee_id')]", "affected_source": ["employee_id"], "affected_target": "employee_id"},
                {"id": "rule_2", "trns": "STRING[UPPER(attr('first_name'))]", "affected_source": ["first_name"], "affected_target": "first_name"},
                {"id": "rule_3", "trns": "STRING[UPPER(attr('last_name'))]", "affected_source": ["last_name"], "affected_target": "last_name"},
                {"id": "rule_4", "trns": "STRING[LOWER(attr('email'))]", "affected_source": ["email"], "affected_target": "email"},
                {"id": "rule_5", "trns": "DIRECT[ATTR('department')]", "affected_source": ["department"], "affected_target": "department"},
                {"id": "rule_6", "trns": "MATH[ROUND(attr('salary'), 2)]", "affected_source": ["salary"], "affected_target": "salary"}
            ]
        }
    }
    
    with open("simple_test_request.json", 'w') as f:
        json.dump(simple_request, f, indent=2)
    
    print("✅ Simple test request created!")

def main():
    """Create all test data and API requests."""
    print("🚀 ETL Engine Test Data Generator")
    print("=" * 50)
    
    # Create parquet files
    create_parquet_files()
    
    # Create API request bodies
    create_api_request_bodies()
    
    # Create simple test request
    create_simple_test_request()
    
    print("\n" + "=" * 50)
    print("🎉 Test Data Generation Complete!")
    print("=" * 50)
    print("📁 Files created:")
    print("   • storage/input/csv_source.parquet")
    print("   • storage/input/fixedwidth_source.parquet")
    print("   • storage/input/json_source.parquet")
    print("   • storage/input/xml_source.parquet")
    print("   • storage/input/excel_source.parquet")
    print("   • api_request_scenario_01_csv_to_json.json")
    print("   • api_request_scenario_02_csv_to_csv.json")
    print("   • ... (16 total scenario files)")
    print("   • simple_test_request.json")
    print("\n📋 Next steps:")
    print("   1. Start the ETL Engine: python run.py")
    print("   2. Test with simple request: simple_test_request.json")
    print("   3. Test all scenarios: api_request_scenario_*.json")
    print("   4. Use API docs: http://localhost:8001/docs")

if __name__ == "__main__":
    main()
