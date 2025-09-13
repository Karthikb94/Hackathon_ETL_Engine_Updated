import os
import time
from fastapi import FastAPI, HTTPException
from .logger import get_logger
from .enhanced_reader import read_data_file
from .transformer import apply_transformations
from .writer import write_output
from .exceptions import ETLError, MappingError, TransformError, ValidationError, WriterError
from .utils import timestamp_run_id
from .models import ETLRequest, ETLResponse

app = FastAPI(
    title="ETL Engine v2", 
    version="2.0.0",
    description="High-performance ETL engine with schema-driven transformations",
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
    return {"status": "healthy", "service": "ETL Engine v2", "version": "2.0.0"}

@app.post("/transform", response_model=ETLResponse)
async def transform_endpoint(request: ETLRequest):
    """
    ETL endpoint that accepts JSON configuration with source file path,
    source schema, target schema, and mapping configuration.
    """
    run_id = timestamp_run_id()
    logger, log_path = get_logger(run_id, logs_dir=BASE_LOGS_DIR)
    
    start_time = time.time()
    logger.info("ETL run started")
    
    try:
        # Validate source file exists
        if not os.path.exists(request.source_file_path):
            raise HTTPException(status_code=400, detail=f"Source file not found: {request.source_file_path}")
        
        # Read and validate parquet file with source schema
        read_start = time.time()
        df = read_data_file(request.source_file_path, source_schema=request.source_schema)
        if df.height == 0:
            logger.warning("Input file is empty")
        read_time = (time.time() - read_start) * 1000
        logger.info(f"Read file: {request.source_file_path} | rows={df.height}, cols={df.width} | time={read_time:.2f}ms")

        # Convert mapping rules to internal format
        mappings = []
        for rule in request.mapping_config.rules:
            mapping = {
                "id": rule.id,
                "trns": rule.trns,
                "affected_source": rule.affected_source,
                "affected_target": rule.affected_target
            }
            mappings.append(mapping)

        # Apply transformations
        try:
            transform_start = time.time()
            transformed = apply_transformations(df, mappings, request.mapping_config.model_dump())
            transform_time = (time.time() - transform_start) * 1000
            logger.info(f"Transform complete | rows={transformed.height}, cols={transformed.width} | time={transform_time:.2f}ms")
        except Exception as e:
            logger.error(f"Transformation failed: {e}")
            raise TransformError(f"Failed to apply transformations: {e}")

        # Determine output format from target schema
        output_format = request.target_schema.fileType.value
        if output_format == "fixedWidth":
            output_format = "fixedwidth"

        # Write output
        try:
            write_start = time.time()
            output_path = request.output_path or os.path.join(BASE_OUTPUT_DIR, f"output_{run_id}")
            
            # Ensure output directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                logger.info(f"Created output directory: {output_dir}")
            
            final_output_path = write_output(
                transformed, 
                output_path, 
                output_format, 
                mappings, 
                target_schema=request.target_schema
            )
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
        
        return ETLResponse(
            status="success",
            run_id=run_id,
            input_rows=input_rows,
            output_rows=output_rows,
            processing_time_ms=round(total_time, 2),
            throughput_rows_per_sec=round(throughput, 0),
            output_path=final_output_path
        )
    except (MappingError, TransformError, ValidationError, WriterError, ETLError) as e:
        logger.error(f"ETL failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")