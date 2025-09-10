#!/usr/bin/env python3
"""
Comprehensive Test Script for ETL Engine
========================================

This script tests all functionality of the ETL transformation engine including:
- Health check endpoint
- All transformation types (simple and advanced)
- Different output formats
- Error handling
- Performance testing

Usage:
    python test_etl_engine.py

Requirements:
    - ETL Engine running on http://localhost:8001
    - requests library: pip install requests
    - pandas library: pip install pandas
    - pyarrow library: pip install pyarrow
"""

import requests
import pandas as pd
import json
import os
import tempfile
import time
from typing import Dict, Any, List
import pyarrow as pa
import pyarrow.parquet as pq

class ETLTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.test_results = []
        self.session = requests.Session()
        
    def log_test(self, test_name: str, success: bool, message: str = "", duration: float = 0):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "duration": duration
        }
        self.test_results.append(result)
        print(f"{status} {test_name}: {message}")
        
    def create_test_data(self) -> str:
        """Create sample test data in parquet format"""
        # Create sample data
        data = {
            'customer_id': [1, 2, 3, 4, 5],
            'first_name': ['John', 'Jane', 'Bob', 'Alice', 'Charlie'],
            'last_name': ['Doe', 'Smith', 'Johnson', 'Brown', 'Wilson'],
            'email': ['john@email.com', 'JANE@EMAIL.COM', 'bob@test.com', 'alice@example.com', 'charlie@demo.com'],
            'phone': ['123-456-7890', '987-654-3210', '', '555-123-4567', '111-222-3333'],
            'city': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'],
            'country': ['USA', 'USA', 'USA', 'USA', 'USA'],
            'age': [25, 30, 35, 28, 42],
            'salary': [50000, 60000, 70000, 55000, 80000],
            'created_date': ['2023-01-15', '2023-02-20', '2023-03-10', '2023-04-05', '2023-05-12'],
            'is_active': [True, True, False, True, True]
        }
        
        df = pd.DataFrame(data)
        
        # Create temporary parquet file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.parquet')
        df.to_parquet(temp_file.name, index=False)
        return temp_file.name
        
    def create_mapping_file(self, mappings: List[Dict[str, Any]], output_format: str = "csv") -> str:
        """Create a mapping configuration file"""
        config = {
            "output_path": "output/test_transformation",
            "output_format": output_format,
            "mappings": mappings
        }
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump(config, temp_file, indent=2)
        temp_file.close()
        return temp_file.name
        
    def test_health_check(self):
        """Test the health check endpoint"""
        start_time = time.time()
        try:
            response = self.session.get(f"{self.base_url}/health")
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("Health Check", True, f"Service is healthy - {data.get('version')}", duration)
                else:
                    self.log_test("Health Check", False, f"Service not healthy: {data}")
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Health Check", False, f"Connection error: {str(e)}", duration)
            
    def test_simple_transformations(self):
        """Test simple transformation types"""
        print("\n🧪 Testing Simple Transformations...")
        
        # Create test data
        parquet_file = self.create_test_data()
        
        # Test trim transformation
        mappings = [
            {"source": "first_name", "target": "first_name_trim", "transform": "trim"},
            {"source": "last_name", "target": "last_name_trim", "transform": "trim"}
        ]
        mapping_file = self.create_mapping_file(mappings)
        
        start_time = time.time()
        try:
            with open(parquet_file, 'rb') as pf, open(mapping_file, 'rb') as mf:
                files = {'parquet_file': pf, 'mapping_file': mf}
                response = self.session.post(f"{self.base_url}/transform", files=files)
                
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                self.log_test("Simple Transform - Trim", True, 
                            f"Processed {result.get('input_rows')} rows in {result.get('processing_time_ms')}ms", duration)
            else:
                self.log_test("Simple Transform - Trim", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Simple Transform - Trim", False, f"Error: {str(e)}", duration)
        finally:
            try:
                os.unlink(parquet_file)
            except FileNotFoundError:
                pass
            try:
                os.unlink(mapping_file)
            except FileNotFoundError:
                pass
            
        # Test case transformations
        parquet_file = self.create_test_data()  # Create new parquet file
        mappings = [
            {"source": "email", "target": "email_lower", "transform": "lower"},
            {"source": "city", "target": "city_upper", "transform": "upper"}
        ]
        mapping_file = self.create_mapping_file(mappings)
        
        start_time = time.time()
        try:
            with open(parquet_file, 'rb') as pf, open(mapping_file, 'rb') as mf:
                files = {'parquet_file': pf, 'mapping_file': mf}
                response = self.session.post(f"{self.base_url}/transform", files=files)
                
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                self.log_test("Simple Transform - Case", True, 
                            f"Processed {result.get('input_rows')} rows", duration)
            else:
                self.log_test("Simple Transform - Case", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Simple Transform - Case", False, f"Error: {str(e)}", duration)
        finally:
            try:
                os.unlink(parquet_file)
            except FileNotFoundError:
                pass
            try:
                os.unlink(mapping_file)
            except FileNotFoundError:
                pass
            
    def test_advanced_transformations(self):
        """Test advanced transformation expressions"""
        print("\n🧪 Testing Advanced Transformations...")
        
        parquet_file = self.create_test_data()
        
        # Test string concatenation
        mappings = [
            {
                "source": "first_name",
                "target": "full_name",
                "transform": "trns: STRING[CONCAT(attr('first_name'), ' ', attr('last_name'))]"
            }
        ]
        mapping_file = self.create_mapping_file(mappings)
        
        start_time = time.time()
        try:
            with open(parquet_file, 'rb') as pf, open(mapping_file, 'rb') as mf:
                files = {'parquet_file': pf, 'mapping_file': mf}
                response = self.session.post(f"{self.base_url}/transform", files=files)
                
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                self.log_test("Advanced Transform - String Concat", True, 
                            f"Processed {result.get('input_rows')} rows", duration)
            else:
                self.log_test("Advanced Transform - String Concat", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Advanced Transform - String Concat", False, f"Error: {str(e)}", duration)
        finally:
            try:
                os.unlink(parquet_file)
            except FileNotFoundError:
                pass
            try:
                os.unlink(mapping_file)
            except FileNotFoundError:
                pass
            
        # Test boolean transformation
        mappings = [
            {
                "source": "phone",
                "target": "has_phone",
                "transform": "trns: BOOLEAN[NOT_EQUALS(attr('phone'), '')]"
            }
        ]
        mapping_file = self.create_mapping_file(mappings)
        
        start_time = time.time()
        try:
            with open(parquet_file, 'rb') as pf, open(mapping_file, 'rb') as mf:
                files = {'parquet_file': pf, 'mapping_file': mf}
                response = self.session.post(f"{self.base_url}/transform", files=files)
                
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                self.log_test("Advanced Transform - Boolean", True, 
                            f"Processed {result.get('input_rows')} rows", duration)
            else:
                self.log_test("Advanced Transform - Boolean", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Advanced Transform - Boolean", False, f"Error: {str(e)}", duration)
        finally:
            try:
                os.unlink(parquet_file)
            except FileNotFoundError:
                pass
            try:
                os.unlink(mapping_file)
            except FileNotFoundError:
                pass
            
        # Test mathematical transformation
        mappings = [
            {
                "source": "salary",
                "target": "salary_with_bonus",
                "transform": "trns: MATH[MUL(attr('salary'), 1.1)]"
            }
        ]
        mapping_file = self.create_mapping_file(mappings)
        
        start_time = time.time()
        try:
            with open(parquet_file, 'rb') as pf, open(mapping_file, 'rb') as mf:
                files = {'parquet_file': pf, 'mapping_file': mf}
                response = self.session.post(f"{self.base_url}/transform", files=files)
                
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                self.log_test("Advanced Transform - Math", True, 
                            f"Processed {result.get('input_rows')} rows", duration)
            else:
                self.log_test("Advanced Transform - Math", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Advanced Transform - Math", False, f"Error: {str(e)}", duration)
        finally:
            try:
                os.unlink(parquet_file)
            except FileNotFoundError:
                pass
            try:
                os.unlink(mapping_file)
            except FileNotFoundError:
                pass
            
    def test_output_formats(self):
        """Test different output formats"""
        print("\n🧪 Testing Output Formats...")
        
        parquet_file = self.create_test_data()
        mappings = [
            {"source": "customer_id", "target": "id", "transform": "to_str"},
            {"source": "first_name", "target": "name", "transform": "trim"}
        ]
        
        formats = ["csv", "json", "json_array", "xlsx"]
        
        for fmt in formats:
            mapping_file = self.create_mapping_file(mappings, fmt)
            
            start_time = time.time()
            try:
                with open(parquet_file, 'rb') as pf, open(mapping_file, 'rb') as mf:
                    files = {'parquet_file': pf, 'mapping_file': mf}
                    response = self.session.post(f"{self.base_url}/transform", files=files)
                    
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    self.log_test(f"Output Format - {fmt.upper()}", True, 
                                f"Processed {result.get('input_rows')} rows", duration)
                else:
                    self.log_test(f"Output Format - {fmt.upper()}", False, f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                duration = time.time() - start_time
                self.log_test(f"Output Format - {fmt.upper()}", False, f"Error: {str(e)}", duration)
            finally:
                os.unlink(mapping_file)
                
        os.unlink(parquet_file)
        
    def test_error_handling(self):
        """Test error handling scenarios"""
        print("\n🧪 Testing Error Handling...")
        
        # Test with invalid parquet file
        start_time = time.time()
        try:
            # Create a fake parquet file (just text)
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.parquet')
            temp_file.write("This is not a parquet file")
            temp_file.close()
            
            mappings = [{"source": "test", "target": "test", "transform": "trim"}]
            mapping_file = self.create_mapping_file(mappings)
            
            with open(temp_file.name, 'rb') as pf, open(mapping_file, 'rb') as mf:
                files = {'parquet_file': pf, 'mapping_file': mf}
                response = self.session.post(f"{self.base_url}/transform", files=files)
                
            duration = time.time() - start_time
            
            if response.status_code == 400:
                self.log_test("Error Handling - Invalid Parquet", True, "Correctly rejected invalid parquet file", duration)
            else:
                self.log_test("Error Handling - Invalid Parquet", False, f"Expected 400, got {response.status_code}")
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Error Handling - Invalid Parquet", False, f"Error: {str(e)}", duration)
        finally:
            try:
                os.unlink(temp_file.name)
            except FileNotFoundError:
                pass
            try:
                os.unlink(mapping_file)
            except FileNotFoundError:
                pass
            
        # Test with invalid mapping file
        start_time = time.time()
        try:
            parquet_file = self.create_test_data()
            
            # Create invalid JSON
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
            temp_file.write('{"invalid": json}')
            temp_file.close()
            
            with open(parquet_file, 'rb') as pf, open(temp_file.name, 'rb') as mf:
                files = {'parquet_file': pf, 'mapping_file': mf}
                response = self.session.post(f"{self.base_url}/transform", files=files)
                
            duration = time.time() - start_time
            
            if response.status_code == 400:
                self.log_test("Error Handling - Invalid Mapping", True, "Correctly rejected invalid mapping file", duration)
            else:
                self.log_test("Error Handling - Invalid Mapping", False, f"Expected 400, got {response.status_code}")
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Error Handling - Invalid Mapping", False, f"Error: {str(e)}", duration)
        finally:
            try:
                os.unlink(parquet_file)
            except FileNotFoundError:
                pass
            try:
                os.unlink(temp_file.name)
            except FileNotFoundError:
                pass
            
        # Test with missing required files
        start_time = time.time()
        try:
            response = self.session.post(f"{self.base_url}/transform")
            duration = time.time() - start_time
            
            if response.status_code == 422:
                self.log_test("Error Handling - Missing Files", True, "Correctly rejected request without files", duration)
            else:
                self.log_test("Error Handling - Missing Files", False, f"Expected 422, got {response.status_code}")
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Error Handling - Missing Files", False, f"Error: {str(e)}", duration)
            
    def test_performance(self):
        """Test performance with larger dataset"""
        print("\n🧪 Testing Performance...")
        
        # Create larger dataset
        data = {
            'id': list(range(1, 1001)),
            'name': [f'User_{i}' for i in range(1, 1001)],
            'value': [i * 10 for i in range(1, 1001)]
        }
        
        df = pd.DataFrame(data)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.parquet')
        df.to_parquet(temp_file.name, index=False)
        
        mappings = [
            {"source": "id", "target": "user_id", "transform": "to_str"},
            {"source": "name", "target": "user_name", "transform": "upper"},
            {
                "source": "value",
                "target": "value_doubled",
                "transform": "trns: MATH[MUL(attr('value'), 2)]"
            }
        ]
        mapping_file = self.create_mapping_file(mappings)
        
        start_time = time.time()
        try:
            with open(temp_file.name, 'rb') as pf, open(mapping_file, 'rb') as mf:
                files = {'parquet_file': pf, 'mapping_file': mf}
                response = self.session.post(f"{self.base_url}/transform", files=files)
                
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                throughput = result.get('throughput_rows_per_sec', 0)
                self.log_test("Performance - 1000 Rows", True, 
                            f"Processed {result.get('input_rows')} rows at {throughput:.0f} rows/sec", duration)
            else:
                self.log_test("Performance - 1000 Rows", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Performance - 1000 Rows", False, f"Error: {str(e)}", duration)
        finally:
            try:
                os.unlink(temp_file.name)
            except FileNotFoundError:
                pass
            try:
                os.unlink(mapping_file)
            except FileNotFoundError:
                pass
            
    def test_complex_transformation(self):
        """Test a complex transformation scenario"""
        print("\n🧪 Testing Complex Transformation...")
        
        parquet_file = self.create_test_data()
        
        # Complex mapping with multiple transformation types
        mappings = [
            {"source": "customer_id", "target": "id", "transform": "to_str"},
            {
                "source": "first_name",
                "target": "full_name",
                "transform": "trns: STRING[CONCAT(attr('first_name'), ' ', attr('last_name'))]"
            },
            {"source": "email", "target": "email_clean", "transform": "lower"},
            {
                "source": "phone",
                "target": "has_phone",
                "transform": "trns: BOOLEAN[NOT_EQUALS(attr('phone'), '')]"
            },
            {
                "source": "salary",
                "target": "salary_category",
                "transform": "trns: LOGICAL[IF(GREATER_THAN(attr('salary'), 60000), 'High', 'Low')]"
            },
            {
                "source": "age",
                "target": "age_group",
                "transform": "trns: LOGICAL[IF(GREATER_THAN(attr('age'), 30), 'Adult', 'Young')]"
            }
        ]
        mapping_file = self.create_mapping_file(mappings)
        
        start_time = time.time()
        try:
            with open(parquet_file, 'rb') as pf, open(mapping_file, 'rb') as mf:
                files = {'parquet_file': pf, 'mapping_file': mf}
                response = self.session.post(f"{self.base_url}/transform", files=files)
                
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                self.log_test("Complex Transformation", True, 
                            f"Processed {result.get('input_rows')} rows with 6 transformations", duration)
            else:
                self.log_test("Complex Transformation", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Complex Transformation", False, f"Error: {str(e)}", duration)
        finally:
            try:
                os.unlink(parquet_file)
            except FileNotFoundError:
                pass
            try:
                os.unlink(mapping_file)
            except FileNotFoundError:
                pass
            
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting ETL Engine Comprehensive Test Suite")
        print("=" * 60)
        
        # Run all test categories
        self.test_health_check()
        self.test_simple_transformations()
        self.test_advanced_transformations()
        self.test_output_formats()
        self.test_error_handling()
        self.test_performance()
        self.test_complex_transformation()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if "PASS" in result["status"])
        failed = sum(1 for result in self.test_results if "FAIL" in result["status"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if failed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if "FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n🎯 Test completed!")
        return passed == total

def main():
    """Main function to run the test suite"""
    print("ETL Engine Test Suite")
    print("====================")
    print("Make sure the ETL Engine is running on http://localhost:8001")
    print("You can start it with: python start_app.py")
    print()
    
    # Check if user wants to continue
    response = input("Press Enter to start testing, or 'q' to quit: ")
    if response.lower() == 'q':
        print("Test cancelled.")
        return
        
    # Run tests
    tester = ETLTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! Your ETL Engine is working perfectly.")
    else:
        print("\n⚠️  Some tests failed. Please check the ETL Engine configuration.")
        
    return success

if __name__ == "__main__":
    main()
