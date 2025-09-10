#!/usr/bin/env python3
"""
Simple ETL Engine Test Script
=============================

This script tests the basic functionality of the ETL transformation engine.
"""

import requests
import pandas as pd
import json
import os
import tempfile
import time
from typing import Dict, Any, List

class SimpleETLTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} {test_name}: {message}"
        self.test_results.append(result)
        print(result)
        
    def create_test_data(self) -> str:
        """Create sample test data in parquet format"""
        data = {
            'customer_id': [1, 2, 3, 4, 5],
            'first_name': ['John', 'Jane', 'Bob', 'Alice', 'Charlie'],
            'last_name': ['Doe', 'Smith', 'Johnson', 'Brown', 'Wilson'],
            'email': ['john@email.com', 'JANE@EMAIL.COM', 'bob@test.com', 'alice@example.com', 'charlie@demo.com'],
            'phone': ['123-456-7890', '987-654-3210', '', '555-123-4567', '111-222-3333'],
            'city': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'],
            'age': [25, 30, 35, 28, 42],
            'salary': [50000, 60000, 70000, 55000, 80000]
        }
        
        df = pd.DataFrame(data)
        
        # Create temporary parquet file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.parquet')
        df.to_parquet(temp_file.name, index=False)
        temp_file.close()
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
        
    def cleanup_files(self, *files):
        """Safely cleanup temporary files"""
        for file_path in files:
            try:
                if file_path and os.path.exists(file_path):
                    os.unlink(file_path)
            except (OSError, PermissionError):
                pass  # Ignore cleanup errors
        
    def test_health_check(self):
        """Test the health check endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("Health Check", True, f"Service is healthy - {data.get('version')}")
                else:
                    self.log_test("Health Check", False, f"Service not healthy: {data}")
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
            
    def test_simple_transformations(self):
        """Test simple transformation types"""
        print("\n🧪 Testing Simple Transformations...")
        
        parquet_file = None
        mapping_file = None
        
        try:
            # Create test data
            parquet_file = self.create_test_data()
            
            # Test trim transformation
            mappings = [
                {"source": "first_name", "target": "first_name_trim", "transform": "trim"},
                {"source": "last_name", "target": "last_name_trim", "transform": "trim"}
            ]
            mapping_file = self.create_mapping_file(mappings)
            
            with open(parquet_file, 'rb') as pf, open(mapping_file, 'rb') as mf:
                files = {'parquet_file': pf, 'mapping_file': mf}
                response = requests.post(f"{self.base_url}/transform", files=files, timeout=30)
                
            if response.status_code == 200:
                result = response.json()
                self.log_test("Simple Transform - Trim", True, 
                            f"Processed {result.get('input_rows')} rows in {result.get('processing_time_ms')}ms")
            else:
                self.log_test("Simple Transform - Trim", False, f"HTTP {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            self.log_test("Simple Transform - Trim", False, f"Error: {str(e)}")
        finally:
            self.cleanup_files(parquet_file, mapping_file)
            
        # Test case transformations
        parquet_file = None
        mapping_file = None
        
        try:
            parquet_file = self.create_test_data()
            mappings = [
                {"source": "email", "target": "email_lower", "transform": "lower"},
                {"source": "city", "target": "city_upper", "transform": "upper"}
            ]
            mapping_file = self.create_mapping_file(mappings)
            
            with open(parquet_file, 'rb') as pf, open(mapping_file, 'rb') as mf:
                files = {'parquet_file': pf, 'mapping_file': mf}
                response = requests.post(f"{self.base_url}/transform", files=files, timeout=30)
                
            if response.status_code == 200:
                result = response.json()
                self.log_test("Simple Transform - Case", True, 
                            f"Processed {result.get('input_rows')} rows")
            else:
                self.log_test("Simple Transform - Case", False, f"HTTP {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            self.log_test("Simple Transform - Case", False, f"Error: {str(e)}")
        finally:
            self.cleanup_files(parquet_file, mapping_file)
            
    def test_advanced_transformations(self):
        """Test advanced transformation expressions"""
        print("\n🧪 Testing Advanced Transformations...")
        
        parquet_file = None
        mapping_file = None
        
        try:
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
            
            with open(parquet_file, 'rb') as pf, open(mapping_file, 'rb') as mf:
                files = {'parquet_file': pf, 'mapping_file': mf}
                response = requests.post(f"{self.base_url}/transform", files=files, timeout=30)
                
            if response.status_code == 200:
                result = response.json()
                self.log_test("Advanced Transform - String Concat", True, 
                            f"Processed {result.get('input_rows')} rows")
            else:
                self.log_test("Advanced Transform - String Concat", False, f"HTTP {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            self.log_test("Advanced Transform - String Concat", False, f"Error: {str(e)}")
        finally:
            self.cleanup_files(parquet_file, mapping_file)
            
        # Test boolean transformation
        parquet_file = None
        mapping_file = None
        
        try:
            parquet_file = self.create_test_data()
            mappings = [
                {
                    "source": "phone",
                    "target": "has_phone",
                    "transform": "trns: BOOLEAN[NOT_EQUALS(attr('phone'), '')]"
                }
            ]
            mapping_file = self.create_mapping_file(mappings)
            
            with open(parquet_file, 'rb') as pf, open(mapping_file, 'rb') as mf:
                files = {'parquet_file': pf, 'mapping_file': mf}
                response = requests.post(f"{self.base_url}/transform", files=files, timeout=30)
                
            if response.status_code == 200:
                result = response.json()
                self.log_test("Advanced Transform - Boolean", True, 
                            f"Processed {result.get('input_rows')} rows")
            else:
                self.log_test("Advanced Transform - Boolean", False, f"HTTP {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            self.log_test("Advanced Transform - Boolean", False, f"Error: {str(e)}")
        finally:
            self.cleanup_files(parquet_file, mapping_file)
            
    def test_output_formats(self):
        """Test different output formats"""
        print("\n🧪 Testing Output Formats...")
        
        parquet_file = None
        mapping_file = None
        
        try:
            parquet_file = self.create_test_data()
            mappings = [
                {"source": "customer_id", "target": "id", "transform": "trim"},
                {"source": "first_name", "target": "name", "transform": "trim"}
            ]
            
            # Test CSV format
            mapping_file = self.create_mapping_file(mappings, "csv")
            
            with open(parquet_file, 'rb') as pf, open(mapping_file, 'rb') as mf:
                files = {'parquet_file': pf, 'mapping_file': mf}
                response = requests.post(f"{self.base_url}/transform", files=files, timeout=30)
                
            if response.status_code == 200:
                result = response.json()
                self.log_test("Output Format - CSV", True, 
                            f"Processed {result.get('input_rows')} rows")
            else:
                self.log_test("Output Format - CSV", False, f"HTTP {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            self.log_test("Output Format - CSV", False, f"Error: {str(e)}")
        finally:
            self.cleanup_files(parquet_file, mapping_file)
            
    def test_error_handling(self):
        """Test error handling scenarios"""
        print("\n🧪 Testing Error Handling...")
        
        # Test with missing required files
        try:
            response = requests.post(f"{self.base_url}/transform", timeout=10)
            if response.status_code == 422:
                self.log_test("Error Handling - Missing Files", True, "Correctly rejected request without files")
            else:
                self.log_test("Error Handling - Missing Files", False, f"Expected 422, got {response.status_code}")
        except Exception as e:
            self.log_test("Error Handling - Missing Files", False, f"Error: {str(e)}")
            
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Simple ETL Engine Test Suite")
        print("=" * 50)
        
        # Run all test categories
        self.test_health_check()
        self.test_simple_transformations()
        self.test_advanced_transformations()
        self.test_output_formats()
        self.test_error_handling()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if "PASS" in result)
        failed = sum(1 for result in self.test_results if "FAIL" in result)
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if failed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if "FAIL" in result:
                    print(f"  {result}")
        
        print("\n🎯 Test completed!")
        return passed == total

def main():
    """Main function to run the test suite"""
    print("Simple ETL Engine Test Suite")
    print("============================")
    print("Make sure the ETL Engine is running on http://localhost:8001")
    print("You can start it with: python start_app.py")
    print()
    
    # Check if user wants to continue
    response = input("Press Enter to start testing, or 'q' to quit: ")
    if response.lower() == 'q':
        print("Test cancelled.")
        return
        
    # Run tests
    tester = SimpleETLTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! Your ETL Engine is working perfectly.")
    else:
        print("\n⚠️  Some tests failed. Please check the ETL Engine configuration.")
        
    return success

if __name__ == "__main__":
    main()
