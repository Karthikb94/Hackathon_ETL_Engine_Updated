import os
import json
import time
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from .logger import get_logger
from .reader import read_data_file
from .transformer import apply_transformations
from .writer import write_output
from .exceptions import ETLError, MappingError, TransformError, ValidationError, WriterError
from .utils import timestamp_run_id

app = FastAPI(
    title="ETL Engine v1", 
    version="1.0.0",
    description="Simple and powerful ETL engine for data transformation",
    docs_url="/docs",
    redoc_url="/redoc"
)

BASE_OUTPUT_DIR = os.environ.get("ETL_OUTPUT_DIR", "output")
BASE_LOGS_DIR = os.environ.get("ETL_LOGS_DIR", "logs")

@app.on_event("startup")
async def startup_event():
    """Ensure required directories exist on startup."""
    os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)
    os.makedirs(BASE_LOGS_DIR, exist_ok=True)

@app.get("/health")
async def health_check():
    """Health check endpoint to verify the service is running."""
    return {"status": "healthy", "service": "ETL Engine v1", "version": "1.0.0"}

@app.post("/transform")
async def transform_endpoint(
    data_file: UploadFile = File(..., description="Data file (CSV, Parquet, JSON)"),
    mapping_file: UploadFile = File(..., description="Mapping configuration JSON file"),
    output_format: str = Form("csv", description="Output format: csv, json, xlsx, xml, fixed_width"),
    output_path: str = Form(None, description="Output file path (optional)")
):
    """
    Transform data using uploaded files and mapping configuration.
    
    Args:
        data_file: Input data file (CSV, Parquet, or JSON)
        mapping_file: JSON file containing transformation mappings
        output_format: Desired output format (csv, json, xlsx, xml, fixed_width)
        output_path: Optional output file path
    
    Returns:
        JSON response with transformation results
    """
    run_id = timestamp_run_id()
    logger, log_path = get_logger(run_id, logs_dir=BASE_LOGS_DIR)
    
    start_time = time.time()
    logger.info("ETL run started")
    
    # Create run directory
    run_dir = os.path.join(BASE_OUTPUT_DIR, f"run_{run_id}")
    os.makedirs(run_dir, exist_ok=True)
    
    # Save uploaded files
    data_path = os.path.join(run_dir, data_file.filename or "input_data")
    mapping_path = os.path.join(run_dir, mapping_file.filename or "mapping.json")
    
    try:
        # Save uploaded files
        with open(data_path, "wb") as f:
            f.write(await data_file.read())
        with open(mapping_path, "wb") as f:
            f.write(await mapping_file.read())
        
        logger.info(f"Files saved: {data_file.filename}, {mapping_file.filename}")
        
        # Load mapping configuration
        try:
            with open(mapping_path, "r", encoding="utf-8") as f:
                mapping_config = json.load(f)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON in mapping file: {e}")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read mapping file: {e}")
        
        # Validate mapping configuration
        if not isinstance(mapping_config, dict):
            raise HTTPException(status_code=400, detail="Mapping configuration must be a JSON object")
        
        mappings = mapping_config.get("mappings", [])
        if not isinstance(mappings, list) or not mappings:
            raise HTTPException(status_code=400, detail="No valid mappings found in mapping file")
        
        # Read data file
        read_start = time.time()
        df = read_data_file(data_path)
        if df.height == 0:
            logger.warning("Input file is empty")
        read_time = (time.time() - read_start) * 1000
        logger.info(f"Read file: {data_file.filename} | rows={df.height}, cols={df.width} | time={read_time:.2f}ms")
        
        # Apply transformations
        try:
            transform_start = time.time()
            transformed = apply_transformations(df, mappings)
            transform_time = (time.time() - transform_start) * 1000
            logger.info(f"Transform complete | rows={transformed.height}, cols={transformed.width} | time={transform_time:.2f}ms")
        except Exception as e:
            logger.error(f"Transformation failed: {e}")
            raise TransformError(f"Failed to apply transformations: {e}")
        
        # Write output
        try:
            write_start = time.time()
            if output_path:
                base_path = output_path
            else:
                base_path = os.path.join(run_dir, f"output_{run_id}")
            
            # Ensure output directory exists
            output_dir = os.path.dirname(base_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            final_output_path = write_output(transformed, base_path, output_format, mappings)
            write_time = (time.time() - write_start) * 1000
            logger.info(f"Wrote output: {final_output_path} | time={write_time:.2f}ms")
        except Exception as e:
            logger.error(f"Failed to write output: {e}")
            raise WriterError(f"Failed to write output: {e}")
        
        # Calculate performance metrics
        total_time = (time.time() - start_time) * 1000
        input_rows = df.height
        output_rows = transformed.height
        throughput = input_rows / (total_time / 1000) if total_time > 0 else 0
        
        logger.info(f"ETL completed successfully in {total_time:.2f}ms")
        logger.info(f"Performance: {throughput:,.0f} rows/second")
        logger.info(f"Data reduction: {input_rows:,} → {output_rows:,} rows ({((input_rows-output_rows)/input_rows*100):.1f}% reduction)")
        
        return {
            "status": "success",
            "run_id": run_id,
            "input_rows": input_rows,
            "output_rows": output_rows,
            "processing_time_ms": round(total_time, 2),
            "throughput_rows_per_sec": round(throughput, 0),
            "output_path": final_output_path,
            "input_file": data_file.filename,
            "output_format": output_format
        }
        
    except (MappingError, TransformError, ValidationError, WriterError, ETLError) as e:
        logger.error(f"ETL failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
    finally:
        # Clean up temporary files
        try:
            if os.path.exists(data_path):
                os.remove(data_path)
            if os.path.exists(mapping_path):
                os.remove(mapping_path)
        except Exception as cleanup_error:
            logger.warning(f"Failed to cleanup temporary files: {cleanup_error}")