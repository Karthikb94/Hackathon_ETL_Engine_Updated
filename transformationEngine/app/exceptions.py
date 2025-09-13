"""
Custom exceptions for ETL Engine
"""

class ETLError(Exception):
    """Base exception for all ETL-related errors."""
    pass

class MappingError(ETLError):
    """Exception raised for mapping configuration errors."""
    pass

class TransformError(ETLError):
    """Exception raised for transformation errors."""
    pass

class ValidationError(ETLError):
    """Exception raised for data validation errors."""
    pass

class WriterError(ETLError):
    """Exception raised for output writing errors."""
    pass

class ReaderError(ETLError):
    """Exception raised for data reading errors."""
    pass
