# Complete VS Code Setup & Testing Guide for ETL Engine

## 🎯 Overview
This guide will help you set up and test the ETL Engine on a new system using only VS Code's graphical interface.

---

## **PART 1: Initial Setup (One-Time Setup)**

### **Step 1: Install Required Software**

#### **1.1 Install Python**
1. Go to [python.org](https://www.python.org/downloads/)
2. Click "Download Python 3.11" (or latest version)
3. **IMPORTANT:** During installation, check "Add Python to PATH"
4. Click "Install Now"
5. Wait for installation to complete
6. Click "Close"

#### **1.2 Install VS Code**
1. Go to [code.visualstudio.com](https://code.visualstudio.com/)
2. Click "Download for Windows" (or your OS)
3. Run the installer
4. **IMPORTANT:** Check "Add to PATH" during installation
5. Click "Next" through all steps
6. Click "Install"
7. Click "Finish"

### **Step 2: Download the ETL Engine Code**

#### **2.1 Open VS Code**
1. Click the VS Code icon on desktop or start menu
2. Wait for VS Code to open completely

#### **2.2 Clone the Repository**
1. Press `Ctrl + Shift + P` (Command Palette)
2. Type: `Git: Clone`
3. Press Enter
4. Enter this URL: `https://github.com/Karthikb94/Hackathon_ETL_Engine_Updated.git`
5. Press Enter
6. Choose folder: Click "Browse" → Select "Desktop" → Click "Select Folder"
7. Wait for download to complete
8. Click "Open" when asked "Would you like to open the cloned repository?"

#### **2.3 Switch to Dev Branch**
1. Look at bottom-left corner of VS Code
2. You'll see "main" or a branch name
3. Click on it
4. Select "dev" from the dropdown
5. Wait for branch switch to complete

### **Step 3: Install Python Extension**

#### **3.1 Open Extensions Panel**
1. Click the Extensions icon (square icon) in left sidebar
2. Search for: `Python`
3. Find "Python" by Microsoft
4. Click "Install"
5. Wait for installation
6. Restart VS Code if prompted

### **Step 4: Install Project Dependencies**

#### **4.1 Open Terminal**
1. Click `Terminal` → `New Terminal` (or press `Ctrl + ``)
2. Terminal will open at bottom of VS Code

#### **4.2 Install Dependencies**
Type these commands one by one in the terminal:

```bash
cd transformationEngine
```
Press Enter

```bash
pip install -r requirements.txt
```
Press Enter and wait for installation

```bash
cd ..
```
Press Enter

---

## **PART 2: Running the ETL Engine**

### **Step 5: Start the ETL Engine Server**

#### **5.1 Start Server**
In the terminal, type:
```bash
python run.py
```
Press Enter

#### **5.2 Expected Output**
You should see:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
```

#### **5.3 Keep Terminal Open**
- **IMPORTANT:** Keep this terminal window open
- The server is now running
- Don't close this terminal

---

## **PART 3: Testing the ETL Engine**

### **Step 6: Test Server is Running**

#### **6.1 Open Web Browser**
1. Open any web browser (Chrome, Firefox, Edge)
2. Go to: `http://localhost:8001/docs`
3. You should see the API documentation page
4. If you see the docs page, the server is working!

### **Step 7: Test with Sample Data**

#### **7.1 Check Sample Files**
1. In VS Code, look at the left sidebar (Explorer)
2. Navigate to `storage/input/`
3. You should see these files:
   - `csv_source.parquet`
   - `fixedwidth_source.parquet`
   - `json_source.parquet`
   - `xml_source.parquet`

#### **7.2 Check Sample API Requests**
1. In VS Code Explorer, look for these files:
   - `scenario_1_csv_to_json.json`
   - `scenario_2_csv_to_fixedwidth.json`
   - `scenario_3_csv_to_xml.json`

### **Step 8: Test API Request (Method 1: Using API Documentation)**

#### **8.1 Open API Documentation**
1. Go to `http://localhost:8001/docs` in your browser
2. Find the `/transform` endpoint
3. Click on it to expand

#### **8.2 Test a Simple Request**
1. Click "Try it out" button
2. Click in the request body text area
3. Copy and paste this JSON:

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

4. Click "Execute" button
5. Wait for response
6. You should see a success response with status 200

### **Step 9: Test API Request (Method 2: Using Sample Files)**

#### **9.1 Open Sample File**
1. In VS Code, double-click `scenario_1_csv_to_json.json`
2. Select all content (Ctrl+A)
3. Copy it (Ctrl+C)

#### **9.2 Use in API Documentation**
1. Go to `http://localhost:8001/docs`
2. Find `/transform` endpoint
3. Click "Try it out"
4. Paste the copied JSON (Ctrl+V)
5. Click "Execute"

### **Step 10: Verify Results**

#### **10.1 Check Output Files**
1. In VS Code Explorer, go to `storage/transformed/`
2. You should see new files created (with timestamps)
3. Files will have extensions like `.json`, `.csv`, `.xml`, `.txt`

#### **10.2 Check Log Files**
1. In VS Code Explorer, go to `storage/logs/`
2. You should see log files with timestamps
3. Double-click a log file to view it

#### **10.3 View Output Content**
1. Double-click any output file in `storage/transformed/`
2. You should see the transformed data
3. For JSON files, you'll see formatted JSON data
4. For CSV files, you'll see comma-separated values

---

## **PART 4: Testing Different Scenarios**

### **Step 11: Test All 12 Scenarios**

#### **11.1 Test Scenario 2: CSV to Fixed-Width**
1. Open `scenario_2_csv_to_fixedwidth.json`
2. Copy all content (Ctrl+A, Ctrl+C)
3. Go to `http://localhost:8001/docs`
4. Use `/transform` endpoint
5. Paste and execute

#### **11.2 Test Scenario 3: CSV to XML**
1. Open `scenario_3_csv_to_xml.json`
2. Copy all content
3. Use API documentation to test

#### **11.3 Test Other Scenarios**
Repeat the same process for other scenario files if available.

### **Step 12: Test Different Source Files**

#### **12.1 Test with Fixed-Width Source**
1. Use `fixedwidth_source.parquet` as source
2. Change `source_file_path` to `"storage/input/fixedwidth_source.parquet"`
3. Change `source_schema.fileType` to `"fixedwidth"`
4. Test with different target formats

#### **12.2 Test with JSON Source**
1. Use `json_source.parquet` as source
2. Change `source_file_path` to `"storage/input/json_source.parquet"`
3. Change `source_schema.fileType` to `"json"`

#### **12.3 Test with XML Source**
1. Use `xml_source.parquet` as source
2. Change `source_file_path` to `"storage/input/xml_source.parquet"`
3. Change `source_schema.fileType` to `"xml"`

---

## **PART 5: Troubleshooting**

### **Step 13: Common Issues and Solutions**

#### **13.1 "Python not found" Error**
**Solution:**
1. Restart VS Code
2. In terminal, try `python3` instead of `python`
3. Make sure Python was installed with "Add to PATH" checked

#### **13.2 "Module not found" Error**
**Solution:**
1. In terminal, type:
```bash
pip install --upgrade pip
```
2. Then:
```bash
pip install -r transformationEngine/requirements.txt
```

#### **13.3 "Port already in use" Error**
**Solution:**
1. Close any other applications using port 8001
2. Or change port in `run.py` file
3. Restart the server

#### **13.4 Server won't start**
**Solution:**
1. Check if Python is installed correctly
2. Check if all dependencies are installed
3. Look at error messages in terminal
4. Restart VS Code

#### **13.5 API request fails**
**Solution:**
1. Check if server is running (terminal should show server info)
2. Check if you're using correct URL: `http://localhost:8001/docs`
3. Check JSON format in request body
4. Look at error messages in response

---

## **PART 6: Understanding the Results**

### **Step 14: Interpret the Results**

#### **14.1 Success Response**
A successful response looks like:
```json
{
  "status": "success",
  "run_id": "20250916_104654",
  "source_file": "storage/input/csv_source.parquet",
  "output_file": "storage/transformed/csv_source_transformed_20250916_104654.json",
  "output_format": "json",
  "rows_processed": 5,
  "columns_output": 8,
  "processing_time_seconds": 0.04,
  "log_file": "storage/logs/etl_20250916_104654.log",
  "error_file": null,
  "message": "Transformation completed successfully",
  "timestamp": "2025-09-16T10:46:54.123456"
}
```

#### **14.2 Error Response**
An error response looks like:
```json
{
  "status": "error",
  "run_id": "20250916_104500",
  "source_file": "storage/input/invalid_file.parquet",
  "output_file": "storage/transformed/invalid_file_transformed_20250916_104500.json",
  "log_file": "storage/logs/etl_20250916_104500.log",
  "error_file": "storage/transformation_error/transformation_error_20250916_104500.json",
  "error_message": "Source file not found",
  "message": "Transformation failed. Check error file for details.",
  "timestamp": "2025-09-16T10:45:00.123456"
}
```

---

## **PART 7: Next Steps**

### **Step 15: Explore More Features**

#### **15.1 Read Documentation**
1. Open `README.md` for quick start guide
2. Open `ETL_ENGINE_API_DOCUMENTATION.md` for detailed docs
3. Open `TRANSFORMATION_LOGIC_GUIDE.md` for transformation details

#### **15.2 Try Different Transformations**
1. Modify the transformation rules in your requests
2. Try different data types
3. Test with larger files
4. Experiment with different output formats

#### **15.3 Monitor Performance**
1. Check processing times in responses
2. Monitor memory usage
3. Test with different file sizes

---

## **🎉 Congratulations!**

You now have a fully functional ETL Engine running on your system! The engine supports:
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

**Need Help?** Check the log files in `storage/logs/` or refer to the comprehensive documentation included in the project! 🚀
