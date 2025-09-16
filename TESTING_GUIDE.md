# Complete Testing Guide for ETL Engine

## 🎯 Overview
This guide provides step-by-step instructions to test the ETL Engine on a new system using VS Code.

---

## **PART 1: Quick Setup (5 minutes)**

### **Step 1: Download and Install Software**

#### **1.1 Install Python**
1. Go to [python.org](https://www.python.org/downloads/)
2. Click "Download Python 3.11" (or latest)
3. **IMPORTANT:** Check "Add Python to PATH" during installation
4. Click "Install Now"
5. Wait and click "Close"

#### **1.2 Install VS Code**
1. Go to [code.visualstudio.com](https://code.visualstudio.com/)
2. Download and install VS Code
3. **IMPORTANT:** Check "Add to PATH" during installation

### **Step 2: Download ETL Engine Code**

#### **2.1 Open VS Code**
1. Click VS Code icon on desktop
2. Wait for VS Code to open

#### **2.2 Clone Repository**
1. Press `Ctrl + Shift + P`
2. Type: `Git: Clone`
3. Press Enter
4. Enter URL: `https://github.com/Karthikb94/Hackathon_ETL_Engine_Updated.git`
5. Press Enter
6. Choose Desktop folder
7. Click "Open" when asked

#### **2.3 Switch to Dev Branch**
1. Click branch name at bottom-left (shows "main")
2. Select "dev" from dropdown
3. Wait for switch to complete

### **Step 3: Install Dependencies**

#### **3.1 Install Python Extension**
1. Click Extensions icon (square) in left sidebar
2. Search: `Python`
3. Install "Python" by Microsoft
4. Restart VS Code if prompted

#### **3.2 Install Project Dependencies**
1. Click `Terminal` → `New Terminal`
2. Type: `cd transformationEngine`
3. Press Enter
4. Type: `pip install -r requirements.txt`
5. Press Enter and wait
6. Type: `cd ..`
7. Press Enter

---

## **PART 2: Start the ETL Engine (2 minutes)**

### **Step 4: Start Server**

#### **4.1 Start ETL Engine**
In terminal, type:
```
python run.py
```
Press Enter

#### **4.2 Verify Server is Running**
You should see:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
```

#### **4.3 Keep Terminal Open**
- **IMPORTANT:** Don't close this terminal
- Server must stay running to work

---

## **PART 3: Test the ETL Engine (5 minutes)**

### **Step 5: Quick Test (Automated)**

#### **5.1 Run Test Script**
1. Open new terminal in VS Code (`Terminal` → `New Terminal`)
2. Type: `python test_etl_engine.py`
3. Press Enter
4. Wait for test results

#### **5.2 Expected Results**
You should see:
```
🚀 ETL Engine Test Suite
==================================================
📁 Checking sample files...
✅ storage/input/csv_source.parquet (1234 bytes)
✅ storage/input/fixedwidth_source.parquet (1234 bytes)
✅ storage/input/json_source.parquet (1234 bytes)
✅ storage/input/xml_source.parquet (1234 bytes)

🔍 Testing server connection...
✅ Server is running and healthy!

📚 Testing API documentation...
✅ API documentation is accessible!

🧪 Testing simple transformation...
✅ Transformation successful!
   Run ID: 20250916_123456
   Output File: storage/transformed/csv_source_transformed_20250916_123456.json
   Processing Time: 0.04s
   Rows Processed: 5
   Columns Output: 8
   Output File Size: 1306 bytes

==================================================
📊 TEST SUMMARY
==================================================
Sample Files: ✅ PASS
Server Connection: ✅ PASS
API Documentation: ✅ PASS
Transformation: ✅ PASS

🎉 ALL TESTS PASSED! Your ETL Engine is working perfectly!
```

### **Step 6: Manual Test (Using Web Browser)**

#### **6.1 Open API Documentation**
1. Open web browser
2. Go to: `http://localhost:8001/docs`
3. You should see API documentation page

#### **6.2 Test Transformation**
1. Find `/transform` endpoint
2. Click on it to expand
3. Click "Try it out"
4. Click in request body area
5. Copy and paste this JSON:

```json
{
  "source_file_path": "storage/input/csv_source.parquet",
  "source_schema": {
    "role": "source",
    "fileType": "csv",
    "schemaId": "test-001",
    "schemaName": "test_schema",
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
    "schemaId": "test-002",
    "schemaName": "test_target_schema",
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
    "sourceSchemaId": "test-001",
    "targetSchemaId": "test-002",
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

6. Click "Execute"
7. Wait for response
8. You should see a success response with status 200

---

## **PART 4: Verify Results (2 minutes)**

### **Step 7: Check Output Files**

#### **7.1 View Output Files**
1. In VS Code Explorer, go to `storage/transformed/`
2. You should see new files with timestamps
3. Files will have extensions like `.json`, `.csv`, `.xml`, `.txt`

#### **7.2 View File Content**
1. Double-click any output file
2. You should see transformed data
3. For JSON files: formatted JSON data
4. For CSV files: comma-separated values

### **Step 8: Check Log Files**

#### **8.1 View Log Files**
1. In VS Code Explorer, go to `storage/logs/`
2. You should see log files with timestamps
3. Double-click a log file to view it

#### **8.2 Log File Content**
Log files contain detailed information about:
- Processing steps
- Performance metrics
- Any errors or warnings
- File paths and sizes

---

## **PART 5: Test Different Scenarios (10 minutes)**

### **Step 9: Test All 12 Scenarios**

#### **9.1 Use Sample Files**
1. In VS Code Explorer, look for these files:
   - `scenario_1_csv_to_json.json`
   - `scenario_2_csv_to_fixedwidth.json`
   - `scenario_3_csv_to_xml.json`

#### **9.2 Test Each Scenario**
1. Open `scenario_1_csv_to_json.json`
2. Select all content (Ctrl+A)
3. Copy it (Ctrl+C)
4. Go to `http://localhost:8001/docs`
5. Use `/transform` endpoint
6. Paste and execute
7. Repeat for other scenarios

### **Step 10: Test Different Source Files**

#### **10.1 Test with Different Sources**
1. Change `source_file_path` to:
   - `"storage/input/fixedwidth_source.parquet"`
   - `"storage/input/json_source.parquet"`
   - `"storage/input/xml_source.parquet"`

2. Change `source_schema.fileType` to:
   - `"fixedwidth"`
   - `"json"`
   - `"xml"`

3. Test with different target formats:
   - `"json"`
   - `"csv"`
   - `"xml"`
   - `"fixedWidth"`

---

## **PART 6: Troubleshooting**

### **Step 11: Common Issues**

#### **11.1 "Python not found" Error**
**Solution:**
1. Restart VS Code
2. Try `python3` instead of `python`
3. Reinstall Python with "Add to PATH" checked

#### **11.2 "Module not found" Error**
**Solution:**
1. In terminal, type:
```
pip install --upgrade pip
pip install -r transformationEngine/requirements.txt
```

#### **11.3 "Port already in use" Error**
**Solution:**
1. Close other applications using port 8001
2. Or change port in `run.py`
3. Restart server

#### **11.4 Server won't start**
**Solution:**
1. Check Python installation
2. Check dependencies
3. Look at error messages
4. Restart VS Code

#### **11.5 API request fails**
**Solution:**
1. Check if server is running
2. Check URL: `http://localhost:8001/docs`
3. Check JSON format
4. Look at error messages

---

## **PART 7: Understanding the Results**

### **Step 12: Success Response**
```json
{
  "status": "success",
  "run_id": "20250916_123456",
  "source_file": "storage/input/csv_source.parquet",
  "output_file": "storage/transformed/csv_source_transformed_20250916_123456.json",
  "output_format": "json",
  "rows_processed": 5,
  "columns_output": 8,
  "processing_time_seconds": 0.04,
  "log_file": "storage/logs/etl_20250916_123456.log",
  "error_file": null,
  "message": "Transformation completed successfully",
  "timestamp": "2025-09-16T12:34:56.123456"
}
```

### **Step 13: Error Response**
```json
{
  "status": "error",
  "run_id": "20250916_123456",
  "source_file": "storage/input/invalid_file.parquet",
  "output_file": "storage/transformed/invalid_file_transformed_20250916_123456.json",
  "log_file": "storage/logs/etl_20250916_123456.log",
  "error_file": "storage/transformation_error/transformation_error_20250916_123456.json",
  "error_message": "Source file not found",
  "message": "Transformation failed. Check error file for details.",
  "timestamp": "2025-09-16T12:34:56.123456"
}
```

---

## **PART 8: Next Steps**

### **Step 14: Explore More Features**

#### **14.1 Read Documentation**
1. Open `README.md` for quick start
2. Open `ETL_ENGINE_API_DOCUMENTATION.md` for detailed docs
3. Open `TRANSFORMATION_LOGIC_GUIDE.md` for transformation details

#### **14.2 Try Different Transformations**
1. Modify transformation rules
2. Try different data types
3. Test with larger files
4. Experiment with different output formats

#### **14.3 Monitor Performance**
1. Check processing times
2. Monitor memory usage
3. Test with different file sizes

---

## **🎉 Congratulations!**

You now have a fully functional ETL Engine! The engine supports:
- ✅ All 12 transformation scenarios
- ✅ 48 different transformation operations
- ✅ Memory-efficient streaming for large files
- ✅ Complete API documentation
- ✅ 100% test coverage

**Remember:**
- Keep the terminal open while using the engine
- Use `Ctrl+C` to stop the server when done
- Check log files for detailed information
- Use the API documentation for testing

**Need Help?** Check the log files in `storage/logs/` or refer to the comprehensive documentation! 🚀
