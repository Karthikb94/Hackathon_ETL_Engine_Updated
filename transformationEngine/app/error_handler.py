"""
Error handling and error file generation system for ETL Engine.
Creates detailed error files with line numbers and user-friendly details.
"""

import os
import json
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List
from .utils import timestamp_run_id
from .exceptions import ETLError, MappingError, TransformError, ValidationError, WriterError, ReaderError


class TransformationErrorHandler:
    """Handles transformation errors and creates detailed error files."""
    
    def __init__(self, base_error_dir: str, run_id: str):
        self.base_error_dir = base_error_dir
        self.run_id = run_id
        self.error_file_path = None
        self.errors = []
        
        # Ensure error directory exists
        os.makedirs(base_error_dir, exist_ok=True)
    
    def add_error(self, 
                  error_type: str,
                  error_message: str,
                  line_number: Optional[int] = None,
                  column_name: Optional[str] = None,
                  row_data: Optional[Dict[str, Any]] = None,
                  transformation_rule: Optional[Dict[str, Any]] = None,
                  stack_trace: Optional[str] = None):
        """Add an error to the error collection."""
        
        error_detail = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": error_message,
            "line_number": line_number,
            "column_name": column_name,
            "row_data": row_data,
            "transformation_rule": transformation_rule,
            "stack_trace": stack_trace
        }
        
        self.errors.append(error_detail)
    
    def create_error_file(self, 
                         source_file: str,
                         output_file: str,
                         log_file: str,
                         processing_summary: Dict[str, Any]) -> str:
        """Create a comprehensive error file."""
        
        if not self.errors:
            return None
        
        # Create error file name
        error_filename = f"transformation_error_{self.run_id}.json"
        self.error_file_path = os.path.join(self.base_error_dir, error_filename)
        
        # Create error file content
        error_file_content = {
            "error_summary": {
                "run_id": self.run_id,
                "timestamp": datetime.now().isoformat(),
                "total_errors": len(self.errors),
                "source_file": source_file,
                "output_file": output_file,
                "log_file": log_file,
                "status": "FAILED"
            },
            "processing_summary": processing_summary,
            "errors": self.errors,
            "troubleshooting": {
                "common_solutions": [
                    "Check column names in source data match schema definitions",
                    "Verify transformation syntax in mapping rules",
                    "Ensure data types are compatible with transformation functions",
                    "Check for null or missing values in required fields",
                    "Validate date formats and numeric ranges"
                ],
                "debugging_steps": [
                    "1. Review the error details below",
                    "2. Check the log file for additional context",
                    "3. Verify source data format and content",
                    "4. Test transformation rules individually",
                    "5. Check schema definitions for accuracy"
                ]
            }
        }
        
        # Write error file
        try:
            with open(self.error_file_path, 'w', encoding='utf-8') as f:
                json.dump(error_file_content, f, indent=2, ensure_ascii=False, default=str)
            
            return self.error_file_path.replace("\\", "/")
        except Exception as e:
            # If we can't write the error file, at least log it
            print(f"Failed to create error file: {e}")
            return None
    
    def create_simple_error_file(self, 
                                error_message: str,
                                source_file: str,
                                output_file: str,
                                log_file: str) -> str:
        """Create a simple error file for basic errors."""
        
        error_filename = f"transformation_error_{self.run_id}.json"
        self.error_file_path = os.path.join(self.base_error_dir, error_filename)
        
        error_file_content = {
            "error_summary": {
                "run_id": self.run_id,
                "timestamp": datetime.now().isoformat(),
                "total_errors": 1,
                "source_file": source_file,
                "output_file": output_file,
                "log_file": log_file,
                "status": "FAILED"
            },
            "errors": [{
                "timestamp": datetime.now().isoformat(),
                "error_type": "SYSTEM_ERROR",
                "error_message": error_message,
                "line_number": None,
                "column_name": None,
                "row_data": None,
                "transformation_rule": None,
                "stack_trace": traceback.format_exc()
            }],
            "troubleshooting": {
                "common_solutions": [
                    "Check if all required files exist in storage/input/",
                    "Verify file formats and permissions",
                    "Check API request format and parameters",
                    "Review server logs for additional details"
                ]
            }
        }
        
        try:
            with open(self.error_file_path, 'w', encoding='utf-8') as f:
                json.dump(error_file_content, f, indent=2, ensure_ascii=False, default=str)
            
            return self.error_file_path.replace("\\", "/")
        except Exception as e:
            print(f"Failed to create simple error file: {e}")
            return None


def handle_transformation_error(error: Exception, 
                              row_index: int,
                              column_name: str = None,
                              row_data: Dict[str, Any] = None,
                              transformation_rule: Dict[str, Any] = None) -> Dict[str, Any]:
    """Handle transformation errors with detailed context."""
    
    error_type = type(error).__name__
    error_message = str(error)
    stack_trace = traceback.format_exc()
    
    return {
        "error_type": error_type,
        "error_message": error_message,
        "line_number": row_index + 1,  # Convert 0-based to 1-based
        "column_name": column_name,
        "row_data": row_data,
        "transformation_rule": transformation_rule,
        "stack_trace": stack_trace
    }


def create_error_response(run_id: str,
                         error_file_path: str,
                         source_file: str,
                         output_file: str,
                         log_file: str,
                         error_message: str) -> Dict[str, Any]:
    """Create a standardized error response."""
    
    # Convert paths to absolute paths with forward slashes for cleaner JSON
    import os
    source_file_absolute = os.path.abspath(source_file).replace("\\", "/") if source_file else None
    output_file_absolute = os.path.abspath(output_file).replace("\\", "/") if output_file else None
    log_file_absolute = os.path.abspath(log_file).replace("\\", "/") if log_file else None
    error_file_absolute = os.path.abspath(error_file_path).replace("\\", "/") if error_file_path else None
    
    return {
        "status": "error",
        "run_id": run_id,
        "source_file": source_file_absolute,
        "output_file": output_file_absolute,
        "log_file": log_file_absolute,
        "error_file": error_file_absolute,
        "error_message": error_message,
        "message": "Transformation failed. Check error file for details.",
        "timestamp": datetime.now().isoformat()
    }
