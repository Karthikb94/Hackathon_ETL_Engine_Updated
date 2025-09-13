# Minimal Request Format

## 🚀 **Ultra-Minimal API Request Format**

The ETL Transformation Engine now supports an ultra-minimal request format with only 4 required parameters.

---

## 📋 **Minimal Request Body**

### **Only 4 Required Parameters:**
```json
{
  "source_file_path": "C:/path/to/data.parquet",
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
      "email": {
        "name": "email",
        "dataType": "string",
        "column_no": 2
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
      "email": {
        "name": "email",
        "dataType": "string",
        "start_pos": 21,
        "width": 30
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
        "trns": "STRING[TRIM(ATTR(email))]",
        "affected_source": ["email"],
        "affected_target": "email"
      }
    ]
  }
}
```

---

## 🔧 **Automatic Defaults**

### **Output Filename:**
- **If provided**: Uses the specified name with timestamp
- **If not provided**: Auto-generates from source filename
  - Example: `data.parquet` → `data_transformed_20250913_190000`

### **Output Format:**
- **Default**: `json`
- **Can be overridden** by providing `output_format` parameter

---

## 📊 **API Response**

The API will return:
```json
{
  "status": "success",
  "run_id": "20250913_190000_abc123",
  "source_file": "C:/path/to/data.parquet",
  "output_file": "data_transformed_20250913_190000",
  "output_format": "json",
  "rows_processed": 1000,
  "columns_output": 2,
  "processing_time_seconds": 1.25,
  "log_file": "../storage/logs/etl_20250913_190000.log",
  "error_file": null,
  "message": "Transformation completed successfully"
}
```

---

## 🚀 **Usage Examples**

### **1. Minimal Request (Recommended)**
```json
{
  "source_file_path": "C:/data/customers.parquet",
  "source_schema": { /* schema */ },
  "target_schema": { /* schema */ },
  "transformation_mapping": { /* mapping */ }
}
```

### **2. With Custom Output Filename**
```json
{
  "source_file_path": "C:/data/customers.parquet",
  "source_schema": { /* schema */ },
  "target_schema": { /* schema */ },
  "transformation_mapping": { /* mapping */ },
  "output_filename": "my_custom_output"
}
```

### **3. With Custom Output Format**
```json
{
  "source_file_path": "C:/data/customers.parquet",
  "source_schema": { /* schema */ },
  "target_schema": { /* schema */ },
  "transformation_mapping": { /* mapping */ },
  "output_format": "fixed_width"
}
```

---

## ✅ **Benefits**

1. **Simpler Requests** - Fewer required parameters
2. **Auto-Generated Names** - No need to specify output filenames
3. **Sensible Defaults** - JSON output by default
4. **Flexible** - Can still override defaults when needed
5. **Cleaner Code** - Less boilerplate in API calls

---

## 🧪 **Testing**

Use the updated test script:
```bash
python test_new_format.py
```

The test now uses the minimal request format without `output_filename` and `output_format` parameters.

---

## 📚 **Backward Compatibility**

- **Old format still works** - You can still provide `output_filename` and `output_format`
- **Gradual migration** - No breaking changes for existing integrations
- **Flexible** - Mix and match parameters as needed

The API is now even simpler to use! 🎉
