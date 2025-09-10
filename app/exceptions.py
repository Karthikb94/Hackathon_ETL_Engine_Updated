class ETLError(Exception):
    """Base ETL error."""
    pass

class MappingError(ETLError):
    """Mapping issues."""
    pass

class TransformError(ETLError):
    """Transform parse/apply issues."""
    pass

class ValidationError(ETLError):
    """Validation rule failures."""
    pass

class WriterError(ETLError):
    """Writer issues (CSV/XLSX/JSON/XML/Positional)."""
    pass
