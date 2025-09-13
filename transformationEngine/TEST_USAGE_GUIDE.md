# ETL Engine Test Script Usage Guide

## Overview
The `test_etl_engine.py` script is a comprehensive test suite that validates all functionality of your ETL transformation engine. It tests every aspect of the system including transformations, output formats, error handling, and performance.

## Prerequisites

### 1. ETL Engine Must Be Running
Before running the test script, ensure your ETL Engine is running:
```bash
python start_app.py
```
The engine should be accessible at `http://localhost:8001`

### 2. Install Test Dependencies
Install the required Python packages:
```bash
pip install -r test_requirements.txt
```

Or install individually:
```bash
pip install requests pandas pyarrow
```

## How to Run the Test Script

### Step 1: Start the ETL Engine
Open a terminal/command prompt and navigate to your project directory:
```bash
cd C:\Users\karth\OneDrive\Desktop\course\Hackathon_ETL_Engine_Updated
python start_app.py
```

You should see output like:
```
Starting ETL Engine on 0.0.0.0:8001
Reload mode: True
Output directory: output
Logs directory: logs
Press Ctrl+C to stop
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

### Step 2: Run the Test Script
Open a **new** terminal/command prompt (keep the ETL engine running in the first one) and run:
```bash
python test_etl_engine.py
```

### Step 3: Follow the Prompts
The script will ask you to confirm before starting:
```
ETL Engine Test Suite
====================
Make sure the ETL Engine is running on http://localhost:8001
You can start it with: python start_app.py

Press Enter to start testing, or 'q' to quit:
```
Press Enter to continue.

## What the Test Script Does

### 🏥 Health Check Test
- Tests the `/health` endpoint
- Verifies the service is running and responding correctly

### 🔧 Simple Transformations Test
- **Trim**: Tests whitespace removal
- **Case Conversion**: Tests `upper()` and `lower()` transformations
- **Type Conversion**: Tests `to_str` conversion

### 🚀 Advanced Transformations Test
- **String Operations**: Tests `CONCAT` for combining fields
- **Boolean Operations**: Tests `NOT_EQUALS` for conditional logic
- **Mathematical Operations**: Tests `MUL` for calculations

### 📄 Output Formats Test
Tests all supported output formats:
- CSV
- JSON
- JSON Array
- Excel (XLSX)

### ⚠️ Error Handling Test
- Invalid parquet files
- Invalid mapping configurations
- Missing required files
- Malformed requests

### ⚡ Performance Test
- Tests with 1000 rows of data
- Measures processing speed
- Reports throughput (rows per second)

### 🎯 Complex Transformation Test
- Combines multiple transformation types
- Tests real-world scenarios
- Validates complex mapping configurations

## Expected Output

### Successful Test Run
```
🚀 Starting ETL Engine Comprehensive Test Suite
============================================================
✅ PASS Health Check: Service is healthy - 1.0.0
🧪 Testing Simple Transformations...
✅ PASS Simple Transform - Trim: Processed 5 rows in 45.2ms
✅ PASS Simple Transform - Case: Processed 5 rows
🧪 Testing Advanced Transformations...
✅ PASS Advanced Transform - String Concat: Processed 5 rows
✅ PASS Advanced Transform - Boolean: Processed 5 rows
✅ PASS Advanced Transform - Math: Processed 5 rows
🧪 Testing Output Formats...
✅ PASS Output Format - CSV: Processed 5 rows
✅ PASS Output Format - JSON: Processed 5 rows
✅ PASS Output Format - JSON_ARRAY: Processed 5 rows
✅ PASS Output Format - XLSX: Processed 5 rows
🧪 Testing Error Handling...
✅ PASS Error Handling - Invalid Parquet: Correctly rejected invalid parquet file
✅ PASS Error Handling - Invalid Mapping: Correctly rejected invalid mapping file
✅ PASS Error Handling - Missing Files: Correctly rejected request without files
🧪 Testing Performance...
✅ PASS Performance - 1000 Rows: Processed 1000 rows at 2500 rows/sec
🧪 Testing Complex Transformation...
✅ PASS Complex Transformation: Processed 5 rows with 6 transformations

============================================================
📊 TEST SUMMARY
============================================================
Total Tests: 15
✅ Passed: 15
❌ Failed: 0
Success Rate: 100.0%

🎯 Test completed!

🎉 All tests passed! Your ETL Engine is working perfectly.
```

### Failed Test Example
```
❌ FAIL Health Check: Connection error: HTTPConnectionPool(host='localhost', port=8001): Max retries exceeded
```

## Troubleshooting

### Common Issues

#### 1. "Connection error" or "Connection refused"
**Problem**: ETL Engine is not running
**Solution**: 
```bash
python start_app.py
```
Make sure you see "Uvicorn running on http://0.0.0.0:8001"

#### 2. "ModuleNotFoundError: No module named 'requests'"
**Problem**: Missing dependencies
**Solution**:
```bash
pip install -r test_requirements.txt
```

#### 3. "HTTP 500" errors
**Problem**: ETL Engine has internal errors
**Solution**: Check the ETL Engine logs for detailed error messages

#### 4. "HTTP 422" errors
**Problem**: Validation errors in test data
**Solution**: This might indicate an issue with the test script or ETL Engine validation

### Debug Mode
To see more detailed information, you can modify the test script to add debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Test Data
The script creates temporary test data including:
- Customer information (ID, name, email, phone)
- Location data (city, country)
- Numeric data (age, salary)
- Date information
- Boolean flags

## Customizing Tests
You can modify the test script to:
- Test with your own data files
- Add new transformation types
- Test different mapping configurations
- Adjust performance test parameters

## Integration with CI/CD
The test script returns `True` if all tests pass, making it suitable for automated testing:

```bash
python test_etl_engine.py
if [ $? -eq 0 ]; then
    echo "All tests passed!"
else
    echo "Some tests failed!"
    exit 1
fi
```

## Support
If you encounter issues:
1. Check that the ETL Engine is running and accessible
2. Verify all dependencies are installed
3. Check the ETL Engine logs for detailed error messages
4. Ensure you have write permissions in the output directory
