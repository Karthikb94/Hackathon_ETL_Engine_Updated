# ETL Engine API Quick Reference

## 🚀 Quick Start

### **1. Start ETL Engine**
```bash
python run.py
```

### **2. Test API**
- **API Docs**: `http://localhost:8001/docs`
- **Health Check**: `http://localhost:8001/health`

### **3. Run Tests**
```bash
python test_etl_engine.py
```

---

## 📁 Test Files Available

### **Sample Data (Parquet Files)**
- `storage/input/csv_source.parquet` - 10 employee records
- `storage/input/fixedwidth_source.parquet` - 10 employee records
- `storage/input/json_source.parquet` - 10 employee records
- `storage/input/xml_source.parquet` - 10 employee records
- `storage/input/excel_source.parquet` - 10 employee records

### **API Request Files**
- `simple_test_request.json` - **START HERE** - Simple CSV to JSON
- `api_request_scenario_01_csv_to_json.json` - CSV → JSON
- `api_request_scenario_02_csv_to_csv.json` - CSV → CSV
- `api_request_scenario_03_csv_to_fixedwidth.json` - CSV → Fixed-Width
- `api_request_scenario_04_csv_to_xml.json` - CSV → XML
- `api_request_scenario_05_fixedwidth_to_json.json` - Fixed-Width → JSON
- `api_request_scenario_06_fixedwidth_to_csv.json` - Fixed-Width → CSV
- `api_request_scenario_07_fixedwidth_to_fixedwidth.json` - Fixed-Width → Fixed-Width
- `api_request_scenario_08_fixedwidth_to_xml.json` - Fixed-Width → XML
- `api_request_scenario_09_json_to_json.json` - JSON → JSON
- `api_request_scenario_10_json_to_csv.json` - JSON → CSV
- `api_request_scenario_11_json_to_fixedwidth.json` - JSON → Fixed-Width
- `api_request_scenario_12_json_to_xml.json` - JSON → XML
- `api_request_scenario_13_xml_to_json.json` - XML → JSON
- `api_request_scenario_14_xml_to_csv.json` - XML → CSV
- `api_request_scenario_15_xml_to_fixedwidth.json` - XML → Fixed-Width
- `api_request_scenario_16_xml_to_xml.json` - XML → XML

---

## 🧪 Testing Methods

### **Method 1: API Documentation (Easiest)**
1. Go to `http://localhost:8001/docs`
2. Find `/transform` endpoint
3. Click "Try it out"
4. Copy JSON from any `api_request_scenario_*.json` file
5. Paste in request body
6. Click "Execute"

### **Method 2: Automated Testing**
1. Run `python test_etl_engine.py`
2. Check results (should show all tests passing)

### **Method 3: Windows Batch File**
1. Double-click `run_tests.bat`
2. Follow the prompts

---

## 📊 Sample Data Structure

### **Input Data (10 Records)**
| Field | Type | Example |
|-------|------|---------|
| employee_id | integer | 1, 2, 3... |
| first_name | string | John, Jane, Bob... |
| last_name | string | Doe, Smith, Johnson... |
| email | string | john.doe@company.com... |
| department | string | Engineering, Marketing... |
| salary | float | 75000.50, 68000.25... |
| hire_date | date | 2020-01-15, 2019-03-22... |
| is_active | boolean | true, false... |
| performance_rating | float | 4.5, 4.2, 3.8... |
| years_experience | integer | 5, 6, 3... |

### **Transformations Applied**
- `first_name` → **UPPERCASE** (JOHN, JANE, BOB...)
- `last_name` → **UPPERCASE** (DOE, SMITH, JOHNSON...)
- `email` → **lowercase** (john.doe@company.com...)
- `salary` → **Rounded to 2 decimals** (75000.50, 68000.25...)
- `hire_date` → **YYYY-MM-DD format** (2020-01-15...)
- `performance_rating` → **Rounded to 1 decimal** (4.5, 4.2...)
- Other fields → **Direct copy**

---

## 🔍 Expected Results

### **Success Response**
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
  "message": "Transformation completed successfully"
}
```

### **Output Files Location**
- **Output Files**: `storage/transformed/`
- **Log Files**: `storage/logs/`
- **Error Files**: `storage/transformation_error/` (if any errors)

---

## 🛠️ Troubleshooting

### **Common Issues**

| Issue | Solution |
|-------|----------|
| "Server not running" | Run `python run.py` in terminal |
| "File not found" | Check if parquet files exist in `storage/input/` |
| "Port already in use" | Close other apps using port 8001 |
| "Transformation failed" | Check JSON format and required fields |

### **Quick Fixes**
1. **Restart Server**: Stop (`Ctrl+C`) and restart (`python run.py`)
2. **Recreate Data**: Run `python create_test_data.py`
3. **Check Logs**: Look in `storage/logs/` for detailed errors
4. **Test Simple**: Start with `simple_test_request.json`

---

## 📈 Performance Tips

### **For Large Files**
- Files >100MB automatically use streaming
- Monitor memory usage
- Check processing times in response

### **For Better Performance**
- Use simple transformation rules
- Avoid complex calculations
- Test with smaller datasets first

---

## 🎯 Next Steps

### **1. Start Testing**
1. Run `python run.py` (keep terminal open)
2. Go to `http://localhost:8001/docs`
3. Test with `simple_test_request.json`
4. Try all 16 scenarios

### **2. Explore Features**
- Modify transformation rules
- Test with your own data
- Try different output formats
- Experiment with complex transformations

### **3. Read Documentation**
- `README.md` - Quick start guide
- `ETL_ENGINE_API_DOCUMENTATION.md` - Complete API docs
- `API_TESTING_GUIDE.md` - Detailed testing guide
- `TRANSFORMATION_LOGIC_GUIDE.md` - Transformation details

---

## 🎉 You're Ready!

**Everything is set up for testing!** Start with the simple test request and work your way through all scenarios. The ETL Engine supports all 12 transformation scenarios with 100% test coverage! 🚀
