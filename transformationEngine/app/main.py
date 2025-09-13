import os
import json
import time
import polars as pl
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from .logger import get_logger
from .reader import read_data_file, read_data_file_with_schema
from .transformer import apply_transformations_from_rules
from .writer import write_output, write_output_with_schema
from .exceptions import ETLError, MappingError, TransformError, ValidationError, WriterError
from .utils import timestamp_run_id
from .error_handler import TransformationErrorHandler, create_error_response


class UnifiedTransformRequest(BaseModel):
    # Required parameters only - minimal format
    source_file_path: str  # Full path to the parquet file (ONLY parquet allowed)
    source_schema: dict    # Source schema as JSON object (MANDATORY for proper parquet reading)
    target_schema: dict    # Target schema as JSON object with new format
    transformation_mapping: dict  # Transformation mapping as JSON object

app = FastAPI(
    title="ETL Engine v1", 
    version="1.0.0",
    description="Simple and powerful ETL engine for data transformation",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Updated paths for multi-engine architecture
BASE_OUTPUT_DIR = os.environ.get("ETL_OUTPUT_DIR", "../storage/transformed")
BASE_LOGS_DIR = os.environ.get("ETL_LOGS_DIR", "../storage/logs")
BASE_INPUT_DIR = os.environ.get("ETL_INPUT_DIR", "../storage/input")
BASE_ERROR_DIR = os.environ.get("ETL_ERROR_DIR", "../storage/transformation_error")

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
    logger.info("Unified ETL run started")
    
    try:
        # Use the required source file path
        source_file_path = request.source_file_path
        logger.info(f"Using source file path: {source_file_path}")
        
        # Validate source file exists and is parquet
        if not os.path.exists(source_file_path):
            raise HTTPException(status_code=404, detail=f"Source file not found: {source_file_path}")
        
        # Validate that source file is parquet format
        if not source_file_path.lower().endswith('.parquet'):
            raise HTTPException(status_code=400, detail="Only parquet files are allowed as input. Please provide a .parquet file.")
        
        # Use the required source schema (mandatory for parquet files)
        source_schema = request.source_schema
        logger.info("Using provided source schema for parquet file reading")
        
        # Use the required target schema
        target_schema = request.target_schema
        logger.info("Using target schema")
        
        # Use the required transformation mapping
        transformation_mapping = request.transformation_mapping
        logger.info("Using transformation mapping")
        
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
        
        logger.info(f"Target output format determined: {output_format}")
        logger.info(f"Target schema file type: {target_schema.get('fileType', 'unknown')}")
        logger.info(f"Target schema attributes count: {len(target_schema.get('attributes', {}))}")
        
        # Extract rules from transformation mapping
        try:
            if "rules" in transformation_mapping:
                rules = transformation_mapping["rules"]
                logger.info(f"Found {len(rules)} transformation rules")
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
                logger.info(f"Converted legacy format to {len(rules)} rules")
            else:
                raise ValueError("No 'rules' or 'mappings' found in transformation mapping")
        except Exception as e:
            logger.error(f"Failed to extract rules: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to extract rules: {e}")
        
        # Create unique output filename with timestamp
        timestamp = timestamp_run_id()
        # Generate filename based on source file
        source_basename = os.path.splitext(os.path.basename(source_file_path))[0]
        output_filename_with_timestamp = f"{source_basename}_transformed_{timestamp}"
        output_path = os.path.join(BASE_OUTPUT_DIR, output_filename_with_timestamp)
        
        # Create unique log filename
        log_filename = f"etl_{timestamp}.log"
        log_path = os.path.join(BASE_LOGS_DIR, log_filename)
        
        logger.info(f"Processing files:")
        logger.info(f"  Source: {source_file_path}")
        logger.info(f"  Output: {output_path}")
        
        # Read parquet file using source schema (mandatory)
        try:
            # Always use source schema for parquet files (converted from fixed-width/XML need proper schema)
            logger.info("Reading parquet file using provided source schema")
            logger.info(f"Source schema file type: {source_schema.get('fileType', 'unknown')}")
            logger.info(f"Source schema attributes count: {len(source_schema.get('attributes', {}))}")
            
            df = read_data_file_with_schema(source_file_path, source_schema)
            logger.info(f"Parquet data loaded with schema: {df.shape[0]} rows, {df.shape[1]} columns")
            
            # Log column information for debugging
            logger.info(f"Available columns: {list(df.columns)}")
            logger.info(f"DataFrame schema: {df.schema}")
            logger.info(f"DataFrame shape: {df.shape}")
            
            # Log source format information for tracking
            original_format = source_schema.get('fileType', 'unknown')
            logger.info(f"Original source format before parquet conversion: {original_format}")
            logger.info("Parquet file is ready for processing with proper schema-based field mapping")
            
        except Exception as e:
            logger.error(f"Failed to read source data: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to read source data: {e}")
        
        # Apply transformations
        try:
            logger.info(f"About to apply transformations. DataFrame shape: {df.shape}")
            logger.info(f"Rules count: {len(rules)}")
            logger.info(f"DataFrame columns: {list(df.columns)}")
            
            error_handler = TransformationErrorHandler(BASE_ERROR_DIR, run_id)
            transformed_df = apply_transformations_from_rules(df, rules, error_handler)
            logger.info(f"Transformations applied: {transformed_df.shape[0]} rows, {transformed_df.shape[1]} columns")
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
                log_file=f"../storage/logs/{log_filename}"
            )
            
            error_response = create_error_response(
                run_id=run_id,
                error_file_path=error_file,
                source_file=source_file_path,
                output_file=output_filename_with_timestamp,
                log_file=f"../storage/logs/{log_filename}",
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
            logger.info(f"Output written successfully to: {output_path}")
        except Exception as e:
            logger.error(f"Failed to write output: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to write output: {e}")
        
        # Calculate processing time
        processing_time = time.time() - start_time
        logger.info(f"Unified ETL run completed successfully in {processing_time:.2f} seconds")
        
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
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "run_id": run_id,
                "source_file": source_file_path,
                "output_file": output_filename_with_timestamp,
                "output_format": output_format,
                "rows_processed": transformed_df.shape[0],
                "columns_output": transformed_df.shape[1],
                "processing_time_seconds": round(processing_time, 2),
                "log_file": f"../storage/logs/{log_filename}",
                "error_file": None,  # No errors occurred
                "message": "Transformation completed successfully"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)