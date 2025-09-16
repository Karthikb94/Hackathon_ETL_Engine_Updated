# Complete API Testing Guide for ETL Engine

## 🎯 Overview
This guide provides everything you need to test the ETL Engine API with pre-generated test data and request bodies.

---

## **📁 Test Data Files Created**

### **Parquet Files (Input Data)**
- `storage/input/csv_source.parquet` - Sample data representing CSV source
- `storage/input/fixedwidth_source.parquet` - Sample data representing Fixed-Width source
- `storage/input/json_source.parquet` - Sample data representing JSON source
- `storage/input/xml_source.parquet` - Sample data representing XML source
- `storage/input/excel_source.parquet` - Sample data representing Excel source

### **API Request Files**
- `simple_test_request.json` - Simple test for quick verification
- `api_request_scenario_01_csv_to_json.json` - CSV source → JSON target
- `api_request_scenario_02_csv_to_csv.json` - CSV source → CSV target
- `api_request_scenario_03_csv_to_fixedwidth.json` - CSV source → Fixed-Width target
- `api_request_scenario_04_csv_to_xml.json` - CSV source → XML target
- `api_request_scenario_05_fixedwidth_to_json.json` - Fixed-Width source → JSON target
- `api_request_scenario_06_fixedwidth_to_csv.json` - Fixed-Width source → CSV target
- `api_request_scenario_07_fixedwidth_to_fixedwidth.json` - Fixed-Width source → Fixed-Width target
- `api_request_scenario_08_fixedwidth_to_xml.json` - Fixed-Width source → XML target
- `api_request_scenario_09_json_to_json.json` - JSON source → JSON target
- `api_request_scenario_10_json_to_csv.json` - JSON source → CSV target
- `api_request_scenario_11_json_to_fixedwidth.json` - JSON source → Fixed-Width target
- `api_request_scenario_12_json_to_xml.json` - JSON source → XML target
- `api_request_scenario_13_xml_to_json.json` - XML source → JSON target
- `api_request_scenario_14_xml_to_csv.json` - XML source → CSV target
- `api_request_scenario_15_xml_to_fixedwidth.json` - XML source → Fixed-Width target
- `api_request_scenario_16_xml_to_xml.json` - XML source → XML target

---

## **🚀 Quick Start Testing**

### **Step 1: Start the ETL Engine**
1. Open VS Code terminal (`Ctrl + ``)
2. Run: `python run.py`
3. Keep terminal open (server must stay running)

### **Step 2: Test with Simple Request**
1. Open `simple_test_request.json` in VS Code
2. Copy all content (`Ctrl + A`, `Ctrl + C`)
3. Go to `http://localhost:8001/docs` in browser
4. Find `/transform` endpoint
5. Click "Try it out"
6. Paste JSON in request body
7. Click "Execute"
8. Check response (should be status 200)

### **Step 3: Verify Results**
1. Check `storage/transformed/` folder for output files
2. Check `storage/logs/` folder for log files
3. Open output files to see transformed data

---

## **🧪 Complete Testing Scenarios**

### **Method 1: Using API Documentation (Recommended)**

#### **Test All 16 Scenarios**
1. **Open API Documentation**: Go to `http://localhost:8001/docs`
2. **Find Transform Endpoint**: Click on `/transform` to expand
3. **Click "Try it out"**
4. **For each scenario**:
   - Open the corresponding JSON file in VS Code
   - Copy all content (`Ctrl + A`, `Ctrl + C`)
   - Paste in API documentation request body
   - Click "Execute"
   - Check response status (should be 200)
   - Note the output file path

#### **Expected Results for Each Test**
- **Status**: 200 OK
- **Response**: Success message with file paths
- **Output Files**: Created in `storage/transformed/`
- **Log Files**: Created in `storage/logs/`

### **Method 2: Using Test Script**

#### **Run Automated Test**
1. Open new terminal in VS Code (`Terminal` → `New Terminal`)
2. Run: `python test_etl_engine.py`
3. Check results (should show all tests passing)

---

## **📊 Sample Data Structure**

### **Input Data (10 records)**
Each parquet file contains:
- `employee_id` (integer): 1-10
- `first_name` (string): John, Jane, Bob, Alice, Charlie, Diana, Eve, Frank, Grace, Henry
- `last_name` (string): Doe, Smith, Johnson, Brown, Wilson, Davis, Miller, Garcia, Martinez, Anderson
- `email` (string): email addresses
- `department` (string): Engineering, Marketing, Sales, HR, Finance, IT, Operations, Legal, Support, Research
- `salary` (float): 60000-90000
- `hire_date` (date): Various dates from 2018-2022
- `is_active` (boolean): Mostly true, some false
- `performance_rating` (float): 3.8-4.9
- `years_experience` (integer): 1-8

### **Transformation Rules Applied**
1. `employee_id` → Direct copy
2. `first_name` → Convert to UPPERCASE
3. `last_name` → Convert to UPPERCASE
4. `email` → Convert to lowercase
5. `department` → Direct copy
6. `salary` → Round to 2 decimal places
7. `hire_date` → Format as YYYY-MM-DD
8. `is_active` → Direct copy
9. `performance_rating` → Round to 1 decimal place
10. `years_experience` → Direct copy

---

## **🔍 Understanding the Results**

### **Success Response Example**
```json
{
  "status": "success",
  "run_id": "20250916_123456",
  "source_file": "storage/input/csv_source.parquet",
  "output_file": "storage/transformed/csv_source_transformed_20250916_123456.json",
  "output_format": "json",
  "rows_processed": 10,
  "columns_output": 10,
  "processing_time_seconds": 0.05,
  "log_file": "storage/logs/etl_20250916_123456.log",
  "error_file": null,
  "message": "Transformation completed successfully",
  "timestamp": "2025-09-16T12:34:56.123456"
}
```

### **Output File Formats**

#### **JSON Output**
```json
[
  {
    "employee_id": 1,
    "first_name": "JOHN",
    "last_name": "DOE",
    "email": "john.doe@company.com",
    "department": "Engineering",
    "salary": 75000.5,
    "hire_date": "2020-01-15",
    "is_active": true,
    "performance_rating": 4.5,
    "years_experience": 5
  }
]
```

#### **CSV Output**
```csv
employee_id,first_name,last_name,email,department,salary,hire_date,is_active,performance_rating,years_experience
1,JOHN,DOE,john.doe@company.com,Engineering,75000.5,2020-01-15,true,4.5,5
```

#### **Fixed-Width Output**
```
         1JOHN                DOE                 john.doe@company.com          Engineering     75000.5  2020-01-15true 4.5  5
```

#### **XML Output**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<root>
  <row>
    <employee_id>1</employee_id>
    <first_name>JOHN</first_name>
    <last_name>DOE</last_name>
    <email>john.doe@company.com</email>
    <department>Engineering</department>
    <salary>75000.5</salary>
    <hire_date>2020-01-15</hire_date>
    <is_active>true</is_active>
    <performance_rating>4.5</performance_rating>
    <years_experience>5</years_experience>
  </row>
</root>
```

---

## **🛠️ Troubleshooting**

### **Common Issues**

#### **1. "Server not running" Error**
**Solution:**
- Make sure ETL Engine is running (`python run.py`)
- Check terminal shows server is running
- Try `http://localhost:8001/health` in browser

#### **2. "File not found" Error**
**Solution:**
- Check if parquet files exist in `storage/input/`
- Verify file paths in JSON requests
- Run `python create_test_data.py` to recreate files

#### **3. "Transformation failed" Error**
**Solution:**
- Check JSON format in request body
- Verify all required fields are present
- Check log files in `storage/logs/`

#### **4. "Port already in use" Error**
**Solution:**
- Close other applications using port 8001
- Change port in `run.py` if needed
- Restart the server

### **Debugging Steps**
1. **Check Server Status**: Visit `http://localhost:8001/health`
2. **Check Log Files**: Look in `storage/logs/` for detailed errors
3. **Verify File Paths**: Ensure all file paths are correct
4. **Test Simple Request**: Start with `simple_test_request.json`

---

## **📈 Performance Testing**

### **Test with Different Data Sizes**
1. **Small Dataset**: Use provided 10-record files
2. **Medium Dataset**: Modify `create_test_data.py` to create 1000 records
3. **Large Dataset**: Create 100,000+ records for streaming tests

### **Monitor Performance Metrics**
- **Processing Time**: Check `processing_time_seconds` in response
- **Memory Usage**: Monitor system resources
- **File Sizes**: Check output file sizes
- **Throughput**: Records processed per second

---

## **🎯 Next Steps**

### **1. Explore Different Transformations**
- Modify transformation rules in JSON files
- Try different data types
- Test complex calculations
- Experiment with string operations

### **2. Test with Your Own Data**
- Replace sample parquet files with your data
- Update schemas to match your data structure
- Create custom transformation rules

### **3. Integration Testing**
- Test with different client applications
- Test error handling scenarios
- Test with malformed data
- Test concurrent requests

### **4. Performance Optimization**
- Test with larger datasets
- Monitor memory usage
- Optimize transformation rules
- Test streaming capabilities

---

## **🎉 Congratulations!**

You now have a complete testing environment for the ETL Engine! The test data includes:
- ✅ **5 Sample Parquet Files** with realistic data
- ✅ **16 Complete API Request Scenarios** covering all transformations
- ✅ **1 Simple Test Request** for quick verification
- ✅ **Comprehensive Testing Guide** with step-by-step instructions

**Ready to test?** Start with the simple test request and work your way through all scenarios! 🚀
