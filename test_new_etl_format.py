#!/usr/bin/env python3
"""
Test script for the new ETL engine format with source schema, target schema, and mapping configuration.
"""

import json
import polars as pl
import os
from app.models import ETLRequest, SchemaDefinition, AttributeDefinition, MappingConfiguration, MappingRule, FileType, DataType

def create_sample_parquet():
    """Create a sample parquet file for testing"""
    # Sample data
    data = {
        "first_name": ["John", "Jane", "Bob", "Alice"],
        "dob": ["1990-01-15", "1985-05-20", "1992-12-10", "1988-08-25"],
        "email": ["john@example.com", "jane@example.com", "bob@example.com", "alice@example.com"]
    }
    
    df = pl.DataFrame(data)
    df.write_parquet("sample_data.parquet")
    print("Created sample_data.parquet")
    return "sample_data.parquet"

def create_source_schema():
    """Create source schema definition"""
    return SchemaDefinition(
        role="source",
        fileType=FileType.PARQUET,
        schemaId="schm-parquet-1001",
        schemaName="customer_parquet_v1",
        attributes={
            "first_name": AttributeDefinition(
                name="first_name",
                dataType=DataType.STRING,
                column_no=1
            ),
            "dob": AttributeDefinition(
                name="dob",
                dataType=DataType.DATE,
                column_no=2
            ),
            "email": AttributeDefinition(
                name="email",
                dataType=DataType.STRING,
                column_no=3
            )
        }
    )

def create_target_schema():
    """Create target schema definition for fixed-width output"""
    return SchemaDefinition(
        role="target",
        fileType=FileType.FIXED_WIDTH,
        schemaId="schm-fix-2001",
        schemaName="customer_fixedwidth_v1",
        attributes={
            "first_name": AttributeDefinition(
                name="first_name",
                dataType=DataType.STRING,
                start_pos=1,
                width=20
            ),
            "dob": AttributeDefinition(
                name="dob",
                dataType=DataType.DATE,
                start_pos=21,
                width=10
            ),
            "email": AttributeDefinition(
                name="email",
                dataType=DataType.STRING,
                start_pos=31,
                width=30
            )
        }
    )

def create_mapping_config():
    """Create mapping configuration"""
    return MappingConfiguration(
        mappingId="d98f31c3-7973-4049-a719-a9359bdbfdef",
        mappingName="customer_parquet_to_fixedwidth",
        createdAt="2025-09-11T07:32:22.113Z",
        sourceSchemaId="schm-parquet-1001",
        targetSchemaId="schm-fix-2001",
        rules=[
            MappingRule(
                id="m1",
                trns="DIRECT[ATTR(first_name)]",
                affected_source=["first_name"],
                affected_target="first_name"
            ),
            MappingRule(
                id="m2",
                trns="DATE[FORMAT(attr('dob'), 'YYYY-MM-DD')]",
                affected_source=["dob"],
                affected_target="dob"
            ),
            MappingRule(
                id="m3",
                trns="STRING[TRIM(ATTR(email))]",
                affected_source=["email"],
                affected_target="email"
            )
        ]
    )

def create_etl_request():
    """Create complete ETL request"""
    return ETLRequest(
        source_file_path="sample_data.parquet",
        source_schema=create_source_schema(),
        target_schema=create_target_schema(),
        mapping_config=create_mapping_config(),
        output_path="output/test_fixed_width",
        output_format="fixedwidth"
    )

def test_etl_components():
    """Test individual ETL components"""
    print("Testing ETL components...")
    
    # Create sample data
    parquet_path = create_sample_parquet()
    
    # Test reader
    from app.enhanced_reader import read_data_file
    from app.transformer import apply_transformations
    from app.writer import write_fixed_width
    
    print("\n1. Testing reader with source schema...")
    source_schema = create_source_schema()
    df = read_data_file(parquet_path, source_schema=source_schema)
    print(f"Read {df.height} rows, {df.width} columns")
    print(f"Columns: {df.columns}")
    print(f"Sample data:\n{df.head()}")
    
    # Test transformer
    print("\n2. Testing transformer...")
    mapping_config = create_mapping_config()
    mappings = []
    for rule in mapping_config.rules:
        mapping = {
            "id": rule.id,
            "trns": rule.trns,
            "affected_source": rule.affected_source,
            "affected_target": rule.affected_target
        }
        mappings.append(mapping)
    
    transformed = apply_transformations(df, mappings, mapping_config.model_dump())
    print(f"Transformed {transformed.height} rows, {transformed.width} columns")
    print(f"Transformed columns: {transformed.columns}")
    print(f"Sample transformed data:\n{transformed.head()}")
    
    # Test writer
    print("\n3. Testing fixed-width writer...")
    target_schema = create_target_schema()
    os.makedirs("output", exist_ok=True)
    write_fixed_width(transformed, "output/test_fixed_width.txt", target_schema)
    print("Fixed-width file written to output/test_fixed_width.txt")
    
    # Show the fixed-width output
    with open("output/test_fixed_width.txt", "r") as f:
        print("Fixed-width output:")
        for i, line in enumerate(f):
            print(f"Line {i+1}: '{line.rstrip()}' (length: {len(line.rstrip())})")
    
    print("\n✅ All components tested successfully!")

def create_api_test_json():
    """Create JSON for API testing"""
    etl_request = create_etl_request()
    
    # Convert to dict for JSON serialization
    request_dict = etl_request.model_dump()
    
    # Write to file
    with open("test_etl_request.json", "w") as f:
        json.dump(request_dict, f, indent=2)
    
    print("Created test_etl_request.json for API testing")
    print("\nSample API request JSON:")
    print(json.dumps(request_dict, indent=2))

if __name__ == "__main__":
    print("ETL Engine v2 Test Script")
    print("=" * 50)
    
    # Test components
    test_etl_components()
    
    print("\n" + "=" * 50)
    print("Creating API test JSON...")
    create_api_test_json()
    
    print("\n" + "=" * 50)
    print("Test completed! You can now:")
    print("1. Start the server: uvicorn app.main:app --reload")
    print("2. Test the API with: curl -X POST 'http://localhost:8000/transform-v2' -H 'Content-Type: application/json' -d @test_etl_request.json")
    print("3. View the API docs at: http://localhost:8000/docs")
