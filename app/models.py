from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union, Any
from enum import Enum

class FileType(str, Enum):
    CSV = "csv"
    PARQUET = "parquet"
    JSON = "json"
    XML = "xml"
    FIXED_WIDTH = "fixedWidth"
    POSITIONAL = "positional"

class DataType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"

class AttributeDefinition(BaseModel):
    name: str
    dataType: DataType
    column_no: Optional[int] = None  # For CSV/Parquet files
    start_pos: Optional[int] = None  # For fixed-width files
    width: Optional[int] = None      # For fixed-width files

class SchemaDefinition(BaseModel):
    role: str  # "source" or "target"
    fileType: FileType
    schemaId: str
    schemaName: str
    attributes: Dict[str, AttributeDefinition]

class MappingRule(BaseModel):
    id: str
    trns: str
    affected_source: List[str]
    affected_target: str

class MappingConfiguration(BaseModel):
    mappingId: str
    mappingName: str
    createdAt: str
    sourceSchemaId: str
    targetSchemaId: str
    rules: List[MappingRule]

class ETLRequest(BaseModel):
    source_file_path: str
    source_schema: SchemaDefinition
    target_schema: SchemaDefinition
    mapping_config: MappingConfiguration
    output_path: Optional[str] = None
    output_format: Optional[str] = "csv"

class ETLResponse(BaseModel):
    status: str
    run_id: str
    input_rows: int
    output_rows: int
    processing_time_ms: float
    throughput_rows_per_sec: float
    output_path: str
