#!/usr/bin/env python3
"""
Parser Engine - FastAPI Application
Handles data parsing and format conversion operations.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator

# Parser Engine Configuration
app = FastAPI(
    title="Parser Engine v1", 
    version="1.0.0",
    description="Data parsing and format conversion engine",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Updated paths for multi-engine architecture
BASE_OUTPUT_DIR = os.environ.get("PARSER_OUTPUT_DIR", "storage/transformed")
BASE_LOGS_DIR = os.environ.get("PARSER_LOGS_DIR", "storage/logs")
BASE_INPUT_DIR = os.environ.get("PARSER_INPUT_DIR", "storage/input")
BASE_ERROR_DIR = os.environ.get("PARSER_ERROR_DIR", "storage/parsing_error")

class ParseRequest(BaseModel):
    """Request model for parsing operations."""
    source_file_path: str = Field(..., description="Relative path to the source file")
    source_format: str = Field(..., description="Source file format (csv, json, xml, etc.)")
    target_format: str = Field(..., description="Target file format (parquet, json, csv, etc.)")
    parsing_config: dict = Field(default={}, description="Parsing configuration options")
    
    @validator('source_file_path')
    def validate_source_file_path(cls, v):
        if not v:
            raise ValueError('source_file_path cannot be empty')
        return v.replace("\\", "/")

@app.on_event("startup")
async def startup_event():
    """Ensure required directories exist on startup."""
    os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)
    os.makedirs(BASE_LOGS_DIR, exist_ok=True)
    os.makedirs(BASE_INPUT_DIR, exist_ok=True)
    os.makedirs(BASE_ERROR_DIR, exist_ok=True)

@app.get("/health")
async def health_check():
    """Health check endpoint to verify the service is running."""
    return {
        "status": "healthy", 
        "service": "Parser Engine v1", 
        "version": "1.0.0",
        "port": 8002
    }

@app.post("/parse")
async def parse_data(request: ParseRequest):
    """
    Parse data from one format to another.
    
    Args:
        request: ParseRequest containing source file, formats, and config
    
    Returns:
        JSON response with parsing results
    """
    run_id = f"parse_{int(time.time())}"
    start_time = time.time()
    
    try:
        # Validate source file exists
        if not os.path.exists(request.source_file_path):
            raise HTTPException(
                status_code=404, 
                detail=f"Source file not found: {request.source_file_path}"
            )
        
        # Generate output file path
        base_name = os.path.splitext(os.path.basename(request.source_file_path))[0]
        output_filename = f"{base_name}_parsed_{run_id}.{request.target_format}"
        output_path = os.path.join(BASE_OUTPUT_DIR, output_filename)
        
        # Simulate parsing operation (replace with actual parsing logic)
        parsing_result = {
            "source_file": request.source_file_path,
            "source_format": request.source_format,
            "target_format": request.target_format,
            "output_file": output_path.replace("\\", "/"),
            "status": "success",
            "run_id": run_id,
            "processing_time_seconds": round(time.time() - start_time, 2),
            "message": "Parsing completed successfully",
            "timestamp": datetime.now().isoformat()
        }
        
        # Create a simple output file for demonstration
        with open(output_path, 'w') as f:
            json.dump(parsing_result, f, indent=2)
        
        return JSONResponse(status_code=200, content=parsing_result)
        
    except HTTPException:
        raise
    except Exception as e:
        error_response = {
            "status": "error",
            "run_id": run_id,
            "source_file": request.source_file_path,
            "error_message": str(e),
            "message": "Parsing failed. Check error details.",
            "timestamp": datetime.now().isoformat()
        }
        return JSONResponse(status_code=500, content=error_response)

@app.get("/formats")
async def get_supported_formats():
    """Get list of supported input and output formats."""
    return {
        "input_formats": ["csv", "json", "xml", "xlsx", "txt", "yaml"],
        "output_formats": ["parquet", "json", "csv", "xml", "xlsx", "yaml"],
        "parser_engine": "v1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
