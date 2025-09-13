# ETL Engine API Documentation for Frontend Developers

## Overview
This is a high-performance ETL (Extract, Transform, Load) engine that processes data files and applies transformations based on mapping configurations. The API is built with FastAPI and uses Polars for fast data processing.

## Base URL
```
http://localhost:8001
```

## Authentication
No authentication required for this API.

---

## API Endpoints

### 1. Health Check
**Purpose:** Verify that the ETL service is running and healthy.

**Endpoint:** `GET /health`

**Request:**
```http
GET http://localhost:8001/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "ETL Engine",
  "version": "1.0.0"
}
```

**Status Codes:**
- `200 OK`: Service is healthy and running

---

### 2. Transform Data (Main Endpoint)
**Purpose:** Upload data files and mapping configuration to perform ETL transformations.

**Endpoint:** `POST /transform`

**Content-Type:** `multipart/form-data`

**Required Parameters:**
- `parquet_file` (file): The data file in Parquet format
- `mapping_file` (file): JSON configuration file defining transformations

**Optional Parameters:**
- `schema_file` (file): JSON schema file for positional data processing
- `layout` (string): JSON string containing layout configuration for positional data

**Request Example (JavaScript/Fetch):**
```javascript
const formData = new FormData();

// Add the parquet file
formData.append('parquet_file', parquetFile);

// Add the mapping configuration file
formData.append('mapping_file', mappingFile);

// Optional: Add schema file if needed
if (schemaFile) {
    formData.append('schema_file', schemaFile);
}

// Optional: Add layout as JSON string
if (layoutConfig) {
    formData.append('layout', JSON.stringify(layoutConfig));
}

const response = await fetch('http://localhost:8001/transform', {
    method: 'POST',
    body: formData
});

const result = await response.json();
```

**Request Example (cURL):**
```bash
curl -X POST "http://localhost:8001/transform" \
  -F "parquet_file=@your_data.parquet" \
  -F "mapping_file=@mapping_config.json"
```

**Success Response (200 OK):**
```json
{
  "status": "success",
  "run_id": "20241210_143022_123456",
  "input_rows": 1000,
  "output_rows": 1000,
  "processing_time_ms": 1250.5,
  "throughput_rows_per_sec": 800,
  "output_path": "/path/to/output/file.csv"
}
```

**Error Response (422 Unprocessable Entity):**
```json
{
  "detail": "Invalid parquet file. Please upload a .parquet file."
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "No 'mappings' found in mapping.json"
}
```

---

## Mapping Configuration Format

The `mapping_file` must be a JSON file with the following structure:

### Basic Structure
```json
{
  "output_path": "output/transformed_data",
  "output_format": "csv",
  "mappings": [
    {
      "source": "Original Column Name",
      "target": "new_column_name",
      "transform": "transformation_type"
    }
  ]
}
```

### Configuration Fields

#### `output_path` (string)
- **Required:** Yes
- **Description:** Base path for the output file (without extension)
- **Example:** `"output/customer_data"`

#### `output_format` (string)
- **Required:** Yes
- **Description:** Output file format
- **Valid values:** `"csv"`, `"json"`, `"json_array"`, `"xlsx"`, `"xml"`, `"positional"`
- **Example:** `"csv"`

#### `mappings` (array)
- **Required:** Yes
- **Description:** Array of field transformation rules

### Mapping Object Structure

Each mapping object must contain:

#### `source` (string)
- **Required:** Yes
- **Description:** Name of the source column in the input data
- **Example:** `"Customer Id"`

#### `target` (string)
- **Required:** Yes
- **Description:** Name of the target column in the output data
- **Example:** `"customer_id"`

#### `transform` (string)
- **Required:** Yes
- **Description:** Transformation to apply to the data
- **Valid values:** See transformation types below

---

## Transformation Types

### Simple Transformations
| Transform | Description | Example |
|-----------|-------------|---------|
| `trim` | Remove leading/trailing whitespace | `"trim"` |
| `upper` | Convert to uppercase | `"upper"` |
| `lower` | Convert to lowercase | `"lower"` |
| `to_str` | Convert to string | `"to_str"` |

### Advanced Transformations
For complex transformations, use the `trns:` prefix with Polars expressions:

#### String Operations
```json
{
  "source": "First Name",
  "target": "full_name",
  "transform": "trns: STRING[CONCAT(attr('First Name'), ' ', attr('Last Name'))]"
}
```

#### Date Operations
```json
{
  "source": "Date Field",
  "target": "parsed_date",
  "transform": "trns: DATE[PARSE(attr('Date Field'), 'MMDDYYYY')]"
}
```

#### Boolean Operations
```json
{
  "source": "Phone",
  "target": "has_phone",
  "transform": "trns: BOOLEAN[NOT_EQUALS(attr('Phone'), '')]"
}
```

#### Mathematical Operations
```json
{
  "source": "Price",
  "target": "price_with_tax",
  "transform": "trns: FLOAT[attr('Price') * 1.1]"
}
```

---

## Complete Example

### Input Data (Parquet file)
Your parquet file should contain columns like:
- Customer Id
- First Name
- Last Name
- Company
- City
- Country
- Phone 1
- Email

### Mapping Configuration (JSON file)
```json
{
  "output_path": "output/customer_transformation",
  "output_format": "csv",
  "mappings": [
    {
      "source": "Customer Id",
      "target": "customer_id",
      "transform": "to_str"
    },
    {
      "source": "First Name",
      "target": "full_name",
      "transform": "trns: STRING[CONCAT(attr('First Name'), ' ', attr('Last Name'))]"
    },
    {
      "source": "Company",
      "target": "company_clean",
      "transform": "trim"
    },
    {
      "source": "City",
      "target": "city_upper",
      "transform": "upper"
    },
    {
      "source": "Email",
      "target": "email_lower",
      "transform": "lower"
    },
    {
      "source": "Phone 1",
      "target": "has_phone",
      "transform": "trns: BOOLEAN[NOT_EQUALS(attr('Phone 1'), '')]"
    }
  ]
}
```

### Frontend Implementation Example

```javascript
class ETLService {
  constructor(baseUrl = 'http://localhost:8001') {
    this.baseUrl = baseUrl;
  }

  async checkHealth() {
    const response = await fetch(`${this.baseUrl}/health`);
    return await response.json();
  }

  async transformData(parquetFile, mappingFile, options = {}) {
    const formData = new FormData();
    formData.append('parquet_file', parquetFile);
    formData.append('mapping_file', mappingFile);

    if (options.schemaFile) {
      formData.append('schema_file', options.schemaFile);
    }

    if (options.layout) {
      formData.append('layout', JSON.stringify(options.layout));
    }

    const response = await fetch(`${this.baseUrl}/transform`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Transformation failed');
    }

    return await response.json();
  }
}

// Usage example
const etlService = new ETLService();

// Check if service is running
const health = await etlService.checkHealth();
console.log('Service status:', health.status);

// Perform transformation
try {
  const result = await etlService.transformData(
    parquetFile,    // File object from input
    mappingFile     // File object from input
  );
  
  console.log('Transformation successful:', result);
  console.log(`Processed ${result.input_rows} rows in ${result.processing_time_ms}ms`);
  console.log(`Output saved to: ${result.output_path}`);
} catch (error) {
  console.error('Transformation failed:', error.message);
}
```

---

## Error Handling

### Common Error Scenarios

1. **Invalid File Format**
   ```json
   {
     "detail": "Invalid parquet file. Please upload a .parquet file."
   }
   ```

2. **Missing Required Files**
   ```json
   {
     "detail": "No 'mappings' found in mapping.json"
   }
   ```

3. **Invalid Mapping Configuration**
   ```json
   {
     "detail": "Invalid JSON in mapping file: Expecting ',' delimiter: line 5 column 3"
   }
   ```

4. **Transformation Errors**
   ```json
   {
     "detail": "Failed to apply transformations: Column 'NonExistentColumn' not found"
   }
   ```

### Frontend Error Handling
```javascript
async function handleTransformation(parquetFile, mappingFile) {
  try {
    const result = await etlService.transformData(parquetFile, mappingFile);
    // Handle success
    showSuccessMessage(`Transformation completed! Processed ${result.input_rows} rows.`);
  } catch (error) {
    // Handle different error types
    if (error.message.includes('Invalid parquet file')) {
      showErrorMessage('Please select a valid Parquet file.');
    } else if (error.message.includes('mapping')) {
      showErrorMessage('Please check your mapping configuration file.');
    } else {
      showErrorMessage(`Transformation failed: ${error.message}`);
    }
  }
}
```

---

## Testing the API

### Using the Interactive Documentation
1. Open your browser and go to: `http://localhost:8001/docs`
2. You'll see the Swagger UI with all available endpoints
3. Click on the `/transform` endpoint
4. Click "Try it out"
5. Upload your files and test the transformation

### Using cURL for Testing
```bash
# Test health endpoint
curl http://localhost:8001/health

# Test transformation
curl -X POST "http://localhost:8001/transform" \
  -F "parquet_file=@sample_data.parquet" \
  -F "mapping_file=@mapping_config.json"
```

---

## Performance Considerations

- The API processes data using Polars, which is optimized for large datasets
- Processing time depends on data size and complexity of transformations
- The response includes performance metrics (throughput, processing time)
- For very large files, consider implementing progress indicators in your frontend

---

## Support

If you encounter issues:
1. Check the health endpoint first: `GET /health`
2. Verify your mapping configuration JSON is valid
3. Ensure your parquet file is properly formatted
4. Check the interactive documentation at `/docs` for detailed API information
