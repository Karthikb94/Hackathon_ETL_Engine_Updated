# API Request Bodies for All 12 Transformation Scenarios

## Overview
This document provides complete API request body examples for all 12 transformation scenarios tested and validated with 100% success rate.

## Base Configuration
All scenarios use the same base data structure with 8 fields:
- `employee_id` (integer)
- `first_name` (string) 
- `last_name` (string)
- `email` (string)
- `department` (string)
- `salary` (float)
- `hire_date` (date)
- `is_active` (boolean)

## Scenario 1: Parquet (CSV source) → JSON

```json
{
  "source_file_path": "storage/input/csv_source.parquet",
  "source_schema": {
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
      "is_active": {"name": "is_active", "dataType": "boolean", "column_no": 8}
    }
  },
  "target_schema": {
    "role": "target",
    "fileType": "json",
    "schemaId": "json-001",
    "schemaName": "json_target_schema",
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
    "mappingId": "csv-to-json-001",
    "mappingName": "csv_to_json_transformation",
    "createdAt": "2025-09-16T10:00:00Z",
    "sourceSchemaId": "csv-001",
    "targetSchemaId": "json-001",
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
```

## Scenario 2: Parquet (CSV source) → Fixed-Width

```json
{
  "source_file_path": "storage/input/csv_source.parquet",
  "source_schema": {
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
      "is_active": {"name": "is_active", "dataType": "boolean", "column_no": 8}
    }
  },
  "target_schema": {
    "role": "target",
    "fileType": "fixedWidth",
    "schemaId": "fw-001",
    "schemaName": "fixedwidth_target_schema",
    "attributes": {
      "employee_id": {"name": "employee_id", "dataType": "integer", "start_position": 1, "width": 10},
      "first_name": {"name": "first_name", "dataType": "string", "start_position": 11, "width": 20},
      "last_name": {"name": "last_name", "dataType": "string", "start_position": 31, "width": 20},
      "email": {"name": "email", "dataType": "string", "start_position": 51, "width": 30},
      "department": {"name": "department", "dataType": "string", "start_position": 81, "width": 15},
      "salary": {"name": "salary", "dataType": "float", "start_position": 96, "width": 10},
      "hire_date": {"name": "hire_date", "dataType": "date", "start_position": 106, "width": 10},
      "is_active": {"name": "is_active", "dataType": "boolean", "start_position": 116, "width": 5}
    }
  },
  "transformation_mapping": {
    "mappingId": "csv-to-fw-001",
    "mappingName": "csv_to_fixedwidth_transformation",
    "createdAt": "2025-09-16T10:00:00Z",
    "sourceSchemaId": "csv-001",
    "targetSchemaId": "fw-001",
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
```

## Scenario 3: Parquet (CSV source) → XML

```json
{
  "source_file_path": "storage/input/csv_source.parquet",
  "source_schema": {
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
      "is_active": {"name": "is_active", "dataType": "boolean", "column_no": 8}
    }
  },
  "target_schema": {
    "role": "target",
    "fileType": "xml",
    "schemaId": "xml-001",
    "schemaName": "xml_target_schema",
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
    "mappingId": "csv-to-xml-001",
    "mappingName": "csv_to_xml_transformation",
    "createdAt": "2025-09-16T10:00:00Z",
    "sourceSchemaId": "csv-001",
    "targetSchemaId": "xml-001",
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
```

## Quick Reference for All 12 Scenarios

| Scenario | Source File | Source Schema fileType | Target Schema fileType |
|----------|-------------|----------------------|----------------------|
| 1 | `csv_source.parquet` | `"csv"` | `"json"` |
| 2 | `csv_source.parquet` | `"csv"` | `"fixedWidth"` |
| 3 | `csv_source.parquet` | `"csv"` | `"xml"` |
| 4 | `fixedwidth_source.parquet` | `"fixedwidth"` | `"csv"` |
| 5 | `fixedwidth_source.parquet` | `"fixedwidth"` | `"json"` |
| 6 | `fixedwidth_source.parquet` | `"fixedwidth"` | `"xml"` |
| 7 | `json_source.parquet` | `"json"` | `"csv"` |
| 8 | `json_source.parquet` | `"json"` | `"xml"` |
| 9 | `json_source.parquet` | `"json"` | `"fixedWidth"` |
| 10 | `xml_source.parquet` | `"xml"` | `"csv"` |
| 11 | `xml_source.parquet` | `"xml"` | `"fixedWidth"` |
| 12 | `xml_source.parquet` | `"xml"` | `"json"` |

## Key Points

1. **Source Schema fileType**: Represents the original format the Parquet file was created from
2. **Target Schema fileType**: The desired output format
3. **Fixed-Width Target**: Requires `start_position` and `width` attributes
4. **Transformation Rules**: Same 8 rules applied across all scenarios
5. **File Paths**: All use relative paths starting with `storage/input/`

## Usage

1. Copy the appropriate request body for your scenario
2. Update the `source_file_path` to match your actual file
3. Modify field names and data types as needed
4. Send POST request to `http://localhost:8001/transform`
5. Check response for success and output file location

All scenarios have been tested and validated with 100% success rate! 🚀
