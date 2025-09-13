# ETL Engine v2 - New JSON Format Guide

This guide explains how to use the new JSON format for the ETL Engine that supports source schema, target schema, and transformation mapping configuration.

## Overview

The new format provides a more structured approach to ETL processing with:
- **Source Schema**: Defines the structure and validation of input data
- **Target Schema**: Defines the structure and format of output data
- **Mapping Configuration**: Defines transformation rules between source and target

## API Endpoint

**POST** `/transform-v2` - New ETL endpoint with JSON configuration

## Request Format

### Complete Request Structure

```json
{
  "source_file_path": "path/to/input.parquet",
  "source_schema": { ... },
  "target_schema": { ... },
  "mapping_config": { ... },
  "output_path": "path/to/output",
  "output_format": "fixedwidth"
}
```

### Source Schema

Defines the structure of your input data:

```json
{
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
    "dob": {
      "name": "dob",
      "dataType": "date",
      "column_no": 2
    },
    "email": {
      "name": "email",
      "dataType": "string",
      "column_no": 3
    }
  }
}
```

**Field Descriptions:**
- `role`: Always "source" for input data
- `fileType`: Type of input file ("parquet", "csv", "json", "xml")
- `schemaId`: Unique identifier for the schema
- `schemaName`: Human-readable name for the schema
- `attributes`: Object defining each field
  - `name`: Field name
  - `dataType`: Data type ("string", "integer", "float", "boolean", "date", "datetime")
  - `column_no`: Column position (for CSV/Parquet files)

### Target Schema

Defines the structure of your output data:

```json
{
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
    "dob": {
      "name": "dob",
      "dataType": "date",
      "start_pos": 21,
      "width": 10
    },
    "email": {
      "name": "email",
      "dataType": "string",
      "start_pos": 31,
      "width": 30
    }
  }
}
```

**Field Descriptions:**
- `role`: Always "target" for output data
- `fileType`: Type of output file ("fixedWidth", "csv", "json", "xml", "xlsx")
- `schemaId`: Unique identifier for the schema
- `schemaName`: Human-readable name for the schema
- `attributes`: Object defining each field
  - `name`: Field name
  - `dataType`: Data type ("string", "integer", "float", "boolean", "date", "datetime")
  - `start_pos`: Starting position (for fixed-width files)
  - `width`: Field width (for fixed-width files)

### Mapping Configuration

Defines transformation rules between source and target:

```json
{
  "mappingId": "d98f31c3-7973-4049-a719-a9359bdbfdef",
  "mappingName": "customer_parquet_to_fixedwidth",
  "createdAt": "2025-09-11T07:32:22.113Z",
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
      "trns": "DATE[FORMAT(attr('dob'), 'YYYY-MM-DD')]",
      "affected_source": ["dob"],
      "affected_target": "dob"
    },
    {
      "id": "m3",
      "trns": "STRING[TRIM(ATTR(email))]",
      "affected_source": ["email"],
      "affected_target": "email"
    }
  ]
}
```

**Field Descriptions:**
- `mappingId`: Unique identifier for the mapping
- `mappingName`: Human-readable name for the mapping
- `createdAt`: ISO timestamp of creation
- `sourceSchemaId`: Reference to source schema
- `targetSchemaId`: Reference to target schema
- `rules`: Array of transformation rules
  - `id`: Unique identifier for the rule
  - `trns`: Transformation expression
  - `affected_source`: Array of source field names
  - `affected_target`: Target field name

## Transformation Language

The transformation language supports various operations:

### Basic Operations
- `DIRECT[ATTR('column')]` - Direct field mapping
- `STRING[CONCAT(attr('col1'), ' ', attr('col2'))]` - String concatenation
- `DATE[FORMAT(attr('date_col'), 'YYYY-MM-DD')]` - Date formatting
- `STRING[TRIM(ATTR('column'))]` - String trimming

### Advanced Operations
- **STRING**: `CONCAT`, `SUBSTR`, `REPLACE`, `UPPER`, `LOWER`, `TRIM`, `LENGTH`
- **MATH**: `ADD`, `SUB`, `MUL`, `DIV`, `MOD`, `ROUND`, `ABS`
- **LOGICAL**: `IF`, `AND`, `OR`, `NOT`
- **DATE**: `FORMAT`, `PARSE`, `ADD_DAYS`, `SUB_DAYS`, `DIFF_DAYS`, `CURRENT_DATE`, `EXTRACT`
- **ARRAY**: `JOIN`, `SPLIT`, `LENGTH`, `GET`
- **FILTERS**: `INCLUDE_IF`, `EXCLUDE_IF`, `LIMIT`, `OFFSET`

## Usage Examples

### 1. Basic CSV to Fixed-Width

```json
{
  "source_file_path": "data/customers.csv",
  "source_schema": {
    "role": "source",
    "fileType": "csv",
    "schemaId": "schm-csv-1001",
    "schemaName": "customer_csv_v1",
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
      }
    }
  },
  "target_schema": {
    "role": "target",
    "fileType": "fixedWidth",
    "schemaId": "schm-fix-2001",
    "schemaName": "customer_fixedwidth_v1",
    "attributes": {
      "full_name": {
        "name": "full_name",
        "dataType": "string",
        "start_pos": 1,
        "width": 30
      },
      "email": {
        "name": "email",
        "dataType": "string",
        "start_pos": 31,
        "width": 40
      }
    }
  },
  "mapping_config": {
    "mappingId": "mapping-001",
    "mappingName": "csv_to_fixedwidth",
    "createdAt": "2025-09-11T07:32:22.113Z",
    "sourceSchemaId": "schm-csv-1001",
    "targetSchemaId": "schm-fix-2001",
    "rules": [
      {
        "id": "r1",
        "trns": "STRING[CONCAT(attr('first_name'), ' ', attr('last_name'))]",
        "affected_source": ["first_name", "last_name"],
        "affected_target": "full_name"
      },
      {
        "id": "r2",
        "trns": "STRING[TRIM(ATTR(email))]",
        "affected_source": ["email"],
        "affected_target": "email"
      }
    ]
  },
  "output_path": "output/customers_fixed",
  "output_format": "fixedwidth"
}
```

### 2. Parquet to CSV with Data Validation

```json
{
  "source_file_path": "data/sales.parquet",
  "source_schema": {
    "role": "source",
    "fileType": "parquet",
    "schemaId": "schm-parquet-2001",
    "schemaName": "sales_parquet_v1",
    "attributes": {
      "product_id": {
        "name": "product_id",
        "dataType": "integer",
        "column_no": 1
      },
      "quantity": {
        "name": "quantity",
        "dataType": "integer",
        "column_no": 2
      },
      "price": {
        "name": "price",
        "dataType": "float",
        "column_no": 3
      },
      "sale_date": {
        "name": "sale_date",
        "dataType": "date",
        "column_no": 4
      }
    }
  },
  "target_schema": {
    "role": "target",
    "fileType": "csv",
    "schemaId": "schm-csv-2001",
    "schemaName": "sales_csv_v1",
    "attributes": {
      "product_id": {
        "name": "product_id",
        "dataType": "integer"
      },
      "total_amount": {
        "name": "total_amount",
        "dataType": "float"
      },
      "sale_date": {
        "name": "sale_date",
        "dataType": "string"
      }
    }
  },
  "mapping_config": {
    "mappingId": "mapping-002",
    "mappingName": "sales_parquet_to_csv",
    "createdAt": "2025-09-11T07:32:22.113Z",
    "sourceSchemaId": "schm-parquet-2001",
    "targetSchemaId": "schm-csv-2001",
    "rules": [
      {
        "id": "r1",
        "trns": "DIRECT[ATTR(product_id)]",
        "affected_source": ["product_id"],
        "affected_target": "product_id"
      },
      {
        "id": "r2",
        "trns": "MATH[MUL(attr('quantity'), attr('price'))]",
        "affected_source": ["quantity", "price"],
        "affected_target": "total_amount"
      },
      {
        "id": "r3",
        "trns": "DATE[FORMAT(attr('sale_date'), 'YYYY-MM-DD')]",
        "affected_source": ["sale_date"],
        "affected_target": "sale_date"
      }
    ]
  },
  "output_path": "output/sales_summary",
  "output_format": "csv"
}
```

## Testing

1. **Start the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Test with curl:**
   ```bash
   curl -X POST 'http://localhost:8000/transform-v2' \
     -H 'Content-Type: application/json' \
     -d @example_new_format.json
   ```

3. **View API documentation:**
   Visit `http://localhost:8000/docs` for interactive API documentation.

## Response Format

The API returns a structured response:

```json
{
  "status": "success",
  "run_id": "20250911_143022",
  "input_rows": 1000,
  "output_rows": 1000,
  "processing_time_ms": 1250.5,
  "throughput_rows_per_sec": 800,
  "output_path": "output/customer_fixed_width_20250911_143022.txt"
}
```

## Error Handling

The API provides detailed error messages for:
- Invalid file paths
- Malformed schema definitions
- Transformation failures
- Output writing errors
- Validation rule violations

## Migration from v1

The original `/transform` endpoint remains available for backward compatibility. To migrate:

1. Convert your mapping file to the new schema format
2. Define source and target schemas
3. Update transformation rules to use the new format
4. Use the `/transform-v2` endpoint

## Best Practices

1. **Schema Validation**: Always define complete source and target schemas
2. **Field Mapping**: Use descriptive field names and maintain consistency
3. **Transformation Rules**: Keep transformations simple and testable
4. **Error Handling**: Include validation rules for data quality
5. **Documentation**: Document your schemas and mappings for team use
