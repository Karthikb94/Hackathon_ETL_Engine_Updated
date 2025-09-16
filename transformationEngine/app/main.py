import os
import json
import time
import polars as pl
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from .logger import get_logger
from .reader import read_data_file, read_data_file_with_schema, should_use_streaming, read_data_file_with_schema_streaming
from .transformer import apply_transformations_from_rules
from .writer import write_output, write_output_with_schema, write_output_streaming
from .exceptions import ETLError, MappingError, TransformError, ValidationError, WriterError
from .utils import timestamp_run_id
from .error_handler import TransformationErrorHandler, create_error_response


class UnifiedTransformRequest(BaseModel):
    # Required parameters with validation
    source_file_path: str = Field(..., description="Relative path to the parquet file (ONLY parquet allowed)")
    source_schema: dict = Field(..., description="Source schema as JSON object (MANDATORY for proper parquet reading)")
    target_schema: dict = Field(..., description="Target schema as JSON object with new format")
    transformation_mapping: dict = Field(..., description="Transformation mapping as JSON object")
    
    @validator('source_file_path')
    def validate_source_file_path(cls, v):
        if not v:
            raise ValueError('source_file_path cannot be empty')
        if not v.lower().endswith('.parquet'):
            raise ValueError('Only .parquet files are allowed as input')
        # Convert to forward slashes for consistency
        return v.replace("\\", "/")
    
    @validator('source_schema')
    def validate_source_schema(cls, v):
        if not v:
            raise ValueError('source_schema cannot be empty')
        if 'fileType' not in v:
            raise ValueError('source_schema must contain fileType field')
        if 'attributes' not in v:
            raise ValueError('source_schema must contain attributes field')
        return v
    
    @validator('target_schema')
    def validate_target_schema(cls, v):
        if not v:
            raise ValueError('target_schema cannot be empty')
        if 'fileType' not in v:
            raise ValueError('target_schema must contain fileType field')
        return v
    
    @validator('transformation_mapping')
    def validate_transformation_mapping(cls, v):
        if not v:
            raise ValueError('transformation_mapping cannot be empty')
        if 'rules' not in v and 'mappings' not in v:
            raise ValueError('transformation_mapping must contain either "rules" or "mappings" field')
        return v

app = FastAPI(
    title="ETL Engine v1", 
    version="1.0.0",
    description="Simple and powerful ETL engine for data transformation",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Updated paths for multi-engine architecture
BASE_OUTPUT_DIR = os.environ.get("ETL_OUTPUT_DIR", "storage/transformed")
BASE_LOGS_DIR = os.environ.get("ETL_LOGS_DIR", "storage/logs")
BASE_INPUT_DIR = os.environ.get("ETL_INPUT_DIR", "storage/input")
BASE_ERROR_DIR = os.environ.get("ETL_ERROR_DIR", "storage/transformation_error")

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
    return {"status": "healthy", "service": "ETL Engine v1", "version": "1.0.0"}


@app.post("/transform")
async def transform_data(request: UnifiedTransformRequest):
    """
    ETL transformation endpoint for Parquet files only.
    
    Required Parameters:
    - source_file_path: Full path to the parquet file (ONLY .parquet files allowed)
    - source_schema: Source schema as JSON object (MANDATORY for proper parquet reading)
    - target_schema: Target schema as JSON object with new format  
    - transformation_mapping: Transformation mapping as JSON object
    
    Important Notes:
    - Only Parquet files are accepted as input
    - Source schema is mandatory (parquet files may be converted from fixed-width/XML and need schema)
    - Source/Target schemas use the new format with role, fileType, schemaId, schemaName, attributes
    - Transformation mapping uses the new format with mappingId, mappingName, sourceSchemaId, targetSchemaId, rules
    
    Args:
        request: UnifiedTransformRequest containing the 4 required parameters
    
    Returns:
        JSON response with transformation results
    """
    run_id = timestamp_run_id()
    logger, log_path = get_logger(run_id, logs_dir=BASE_LOGS_DIR)
    
    start_time = time.time()
    
    try:
        # Use the required source file path
        source_file_path = request.source_file_path
        
        # Validate source file exists and is parquet
        if not os.path.exists(source_file_path):
            raise HTTPException(status_code=404, detail=f"Source file not found: {source_file_path}")
        
        # Validate that source file is parquet format
        if not source_file_path.lower().endswith('.parquet'):
            raise HTTPException(status_code=400, detail="Only parquet files are allowed as input. Please provide a .parquet file.")
        
        # Use the required source schema (mandatory for parquet files)
        source_schema = request.source_schema
        
        # Use the required target schema
        target_schema = request.target_schema
        
        # Use the required transformation mapping
        transformation_mapping = request.transformation_mapping
        
        # Determine output format from target schema
        output_format = "json"  # Default format
        if target_schema and "fileType" in target_schema:
            file_type = target_schema.get("fileType", "").lower()
            if file_type == "fixedwidth":
                output_format = "fixed_width"
            elif file_type in ["csv", "xlsx", "xml", "json", "jsonl"]:
                output_format = file_type
            elif file_type == "positional":
                output_format = "fixed_width"  # Positional is a type of fixed-width
            else:
                output_format = "json"
        
        # Extract rules from transformation mapping
        try:
            if "rules" in transformation_mapping:
                rules = transformation_mapping["rules"]
            elif "mappings" in transformation_mapping:
                # Legacy format - convert to rules format
                rules = []
                for mapping in transformation_mapping["mappings"]:
                    rule = {
                        "id": mapping.get("id", f"rule_{len(rules)+1}"),
                        "trns": mapping.get("trns", ""),
                        "affected_source": mapping.get("affected_source", []),
                        "affected_target": mapping.get("affected_target", "")
                    }
                    rules.append(rule)
            else:
                raise ValueError("No 'rules' or 'mappings' found in transformation mapping")
        except Exception as e:
            logger.error(f"Failed to extract rules: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to extract rules: {e}")
        
        # Create unique output filename with timestamp (reuse run_id)
        # Generate filename based on source file
        source_basename = os.path.splitext(os.path.basename(source_file_path))[0]
        output_filename_with_timestamp = f"{source_basename}_transformed_{run_id}"
        output_path = os.path.join(BASE_OUTPUT_DIR, output_filename_with_timestamp)
        
        # Create unique log filename (reuse run_id)
        log_filename = f"etl_{run_id}.log"
        log_path = os.path.join(BASE_LOGS_DIR, log_filename)
        
        # Structured logging - batch all processing info
        processing_info = {
            "run_id": run_id,
            "source_file": source_file_path,
            "source_schema_type": source_schema.get('fileType', 'unknown'),
            "source_schema_attributes": len(source_schema.get('attributes', {})),
            "target_schema_type": target_schema.get('fileType', 'unknown'),
            "target_schema_attributes": len(target_schema.get('attributes', {})),
            "output_format": output_format,
            "rules_count": len(rules),
            "output_path": output_path
        }
        logger.info(f"ETL processing started: {processing_info}")
        
        # Check if file is large enough for streaming
        use_streaming = should_use_streaming(source_file_path)
        
        if use_streaming:
            # Process large file with streaming
            try:
                # Structured logging for streaming processing
                streaming_info = {
                    "file_size_mb": round(os.path.getsize(source_file_path) / (1024 * 1024), 2),
                    "processing_mode": "streaming",
                    "chunk_size": 10000
                }
                logger.info(f"Large file detected, using streaming: {streaming_info}")
                
                # Process in streaming mode
                _process_large_file_streaming(
                    source_file_path, source_schema, target_schema, 
                    transformation_mapping, output_path, output_format, 
                    run_id, logger
                )
                
                # Structured logging for streaming completion
                completion_info = {
                    "processing_mode": "streaming",
                    "status": "success"
                }
                logger.info(f"Streaming processing completed: {completion_info}")
                
            except Exception as e:
                logger.error(f"Streaming processing failed: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                
                # Create error file
                error_handler = TransformationErrorHandler(BASE_ERROR_DIR, run_id)
                error_file = error_handler.create_simple_error_file(
                    error_message=str(e),
                    source_file=source_file_path,
                    output_file=output_filename_with_timestamp,
                    log_file=log_path.replace("\\", "/")
                )
                
                error_response = create_error_response(
                    run_id=run_id,
                    error_file_path=error_file.replace("\\", "/"),
                    source_file=source_file_path,
                    output_file=output_filename_with_timestamp,
                    log_file=log_path.replace("\\", "/"),
                    error_message=str(e)
                )
                
                return JSONResponse(status_code=400, content=error_response)
        else:
            # Process small file normally
            try:
                df = read_data_file_with_schema(source_file_path, source_schema)
                
                # Structured logging for data loading
                data_info = {
                    "rows_loaded": df.shape[0],
                    "columns_loaded": df.shape[1],
                    "available_columns": list(df.columns),
                    "dataframe_schema": str(df.schema),
                    "original_format": source_schema.get('fileType', 'unknown'),
                    "processing_mode": "standard"
                }
                logger.info(f"Data loaded successfully: {data_info}")
                
            except Exception as e:
                logger.error(f"Failed to read source data: {e}")
                raise HTTPException(status_code=400, detail=f"Failed to read source data: {e}")
            
            # Apply transformations
            try:
                error_handler = TransformationErrorHandler(BASE_ERROR_DIR, run_id)
                transformed_df = apply_transformations_from_rules(df, rules, error_handler)
                
                # Structured logging for transformation results
                transformation_info = {
                    "input_rows": df.shape[0],
                    "input_columns": df.shape[1],
                    "output_rows": transformed_df.shape[0],
                    "output_columns": transformed_df.shape[1],
                    "rules_applied": len(rules)
                }
                logger.info(f"Transformations completed: {transformation_info}")
            except Exception as e:
                logger.error(f"Transformation failed: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                
                # Create error file
                error_handler = TransformationErrorHandler(BASE_ERROR_DIR, run_id)
                error_file = error_handler.create_simple_error_file(
                    error_message=str(e),
                    source_file=source_file_path,
                    output_file=output_filename_with_timestamp,
                    log_file=log_path.replace("\\", "/")
                )
                
                error_response = create_error_response(
                    run_id=run_id,
                    error_file_path=error_file.replace("\\", "/"),
                    source_file=source_file_path,
                    output_file=output_filename_with_timestamp,
                    log_file=log_path.replace("\\", "/"),
                    error_message=str(e)
                )
                
                return JSONResponse(status_code=400, content=error_response)
            
            # Write output
            try:
                # Use target schema for writing
                mapping_config = {
                    "targetSchema": target_schema,
                    "rules": rules
                }
                write_output_with_schema(transformed_df, output_path, output_format, mapping_config, logger=logger)
                
                # Structured logging for output writing
                output_info = {
                    "output_path": output_path,
                    "output_format": output_format,
                    "rows_written": transformed_df.shape[0],
                    "columns_written": transformed_df.shape[1]
                }
                logger.info(f"Output written successfully: {output_info}")
            except Exception as e:
                logger.error(f"Failed to write output: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to write output: {e}")
        
        # Calculate processing time and log completion
        processing_time = time.time() - start_time
        
        # Structured logging for completion
        if use_streaming:
            completion_info = {
                "run_id": run_id,
                "processing_time_seconds": round(processing_time, 2),
                "status": "success",
                "processing_mode": "streaming"
            }
        else:
            completion_info = {
                "run_id": run_id,
                "processing_time_seconds": round(processing_time, 2),
                "status": "success",
                "rows_processed": transformed_df.shape[0],
                "columns_output": transformed_df.shape[1],
                "processing_mode": "standard"
            }
        logger.info(f"ETL run completed successfully: {completion_info}")
        
        # Create log file with unique filename
        with open(log_path, 'w') as f:
            f.write(f"ETL Run ID: {run_id}\n")
            f.write(f"Source File: {source_file_path}\n")
            f.write(f"Output File: {output_filename_with_timestamp}\n")
            f.write(f"Output Format: {output_format}\n")
            f.write(f"Rows Processed: {transformed_df.shape[0]}\n")
            f.write(f"Columns Output: {transformed_df.shape[1]}\n")
            f.write(f"Processing Time: {processing_time:.2f} seconds\n")
            f.write(f"Status: Success\n")
        
        # Get relative paths for all files and convert to forward slashes for cleaner JSON
        output_file_relative = f"{output_path}.{output_format}".replace("\\", "/")
        log_file_relative = log_path.replace("\\", "/")
        source_file_relative = source_file_path.replace("\\", "/")
        
        # Prepare response content based on processing mode
        response_content = {
            "status": "success",
            "run_id": run_id,
            "source_file": source_file_relative,
            "output_file": output_file_relative,
            "output_format": output_format,
            "processing_time_seconds": round(processing_time, 2),
            "log_file": log_file_relative,
            "error_file": None,  # No errors occurred
            "message": "Transformation completed successfully",
            "timestamp": datetime.now().isoformat()
        }
        
        # Add mode-specific information
        if use_streaming:
            response_content.update({
                "processing_mode": "streaming",
                "message": "Large file transformation completed successfully using streaming mode"
            })
        else:
            response_content.update({
                "rows_processed": transformed_df.shape[0],
                "columns_output": transformed_df.shape[1],
                "processing_mode": "standard"
            })

        return JSONResponse(status_code=200, content=response_content)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

def _process_large_file_streaming(source_file_path: str, source_schema: Dict[str, Any], 
                                 target_schema: Dict[str, Any], transformation_mapping: Dict[str, Any],
                                 output_path: str, output_format: str, run_id: str, logger) -> None:
    """
    Process large files using streaming mode for memory efficiency.
    
    Args:
        source_file_path: Path to source file
        source_schema: Source schema definition
        target_schema: Target schema definition
        transformation_mapping: Transformation mapping
        output_path: Output file path
        output_format: Output format
        run_id: Run ID for logging
        logger: Logger instance
    """
    # Extract rules from transformation mapping
    if "rules" in transformation_mapping:
        rules = transformation_mapping["rules"]
    elif "mappings" in transformation_mapping:
        # Legacy format - convert to rules format
        rules = []
        for mapping in transformation_mapping["mappings"]:
            rule = {
                "id": mapping.get("id", f"rule_{len(rules)+1}"),
                "trns": mapping.get("trns", ""),
                "affected_source": mapping.get("affected_source", []),
                "affected_target": mapping.get("affected_target", "")
            }
            rules.append(rule)
    else:
        raise ValueError("No 'rules' or 'mappings' found in transformation mapping")
    
    # Create mapping config for writer
    mapping_config = {
        "targetSchema": target_schema,
        "rules": rules
    }
    
    # Process file in streaming mode
    chunk_size = 10000  # Process 10k rows at a time
    total_rows_processed = 0
    total_chunks_processed = 0
    
    try:
        # Read file in chunks
        df_chunks = read_data_file_with_schema_streaming(source_file_path, source_schema, chunk_size)
        
        # Create generator for transformed chunks (memory efficient)
        def transformed_chunk_generator():
            nonlocal total_rows_processed, total_chunks_processed
            error_handler = TransformationErrorHandler(BASE_ERROR_DIR, run_id)
            
            for chunk in df_chunks:
                if chunk.is_empty():
                    continue
                    
                try:
                    # Apply transformations to chunk
                    transformed_chunk = apply_transformations_from_rules(chunk, rules, error_handler)
                    
                    total_rows_processed += chunk.shape[0]
                    total_chunks_processed += 1
                    
                    # Log progress every 10 chunks
                    if total_chunks_processed % 10 == 0:
                        progress_info = {
                            "chunks_processed": total_chunks_processed,
                            "rows_processed": total_rows_processed,
                            "current_chunk_size": chunk.shape[0]
                        }
                        logger.info(f"Streaming progress: {progress_info}")
                    
                    # Yield transformed chunk immediately (don't store in memory)
                    yield transformed_chunk
                        
                except Exception as e:
                    logger.error(f"Failed to transform chunk {total_chunks_processed + 1}: {e}")
                    raise e
        
        # Write output in streaming mode using the generator
        write_output_streaming(transformed_chunk_generator(), output_path, output_format, mapping_config, logger)
        
        # Log final streaming results
        final_info = {
            "total_chunks_processed": total_chunks_processed,
            "total_rows_processed": total_rows_processed,
            "output_path": output_path,
            "output_format": output_format
        }
        logger.info(f"Streaming processing completed: {final_info}")
        
    except Exception as e:
        logger.error(f"Streaming processing failed: {e}")
        raise e

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)