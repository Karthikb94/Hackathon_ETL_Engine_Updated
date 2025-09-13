import polars as pl
from typing import Any, Dict, List, Optional
from .exceptions import MappingError, TransformError
from .utils import parse_transform_expression, coerce_simple_transform, parse_boolean_expr

def _build_expr_for_mapping(df: pl.DataFrame, mapping: Dict[str, Any]) -> Optional[pl.Expr]:
    """Build a Polars expression for a single mapping rule."""
    target = mapping.get("target")
    source = mapping.get("source")
    transform = mapping.get("transform")
    default = mapping.get("default")

    if source is not None:
        # Handle comma-separated source fields
        source_columns = [col.strip() for col in source.split(',')]
        missing_columns = [col for col in source_columns if col not in df.columns]

        if missing_columns:
            if default is not None:
                src_expr = pl.lit(default)
            else:
                raise MappingError(f"Source column(s) {missing_columns} not found and no default provided.")
        else:
            # Use the first source column for the source expression
            src_expr = pl.col(source_columns[0])
    else:
        if default is not None and transform is None:
            return pl.lit(default)
        src_expr = pl.lit(None)

    if transform:
        try:
            # Check if it's an advanced transform
            if (transform.strip().lower().startswith("trns:") or 
                ("[" in transform and "]" in transform and 
                 any(op in transform.upper() for op in ["DIRECT", "STRING", "MATH", "LOGICAL", "DATE", "BOOLEAN", "ARRAY", "FILTERS", "FILTER"]))):
                expr = parse_transform_expression(transform)
                if isinstance(expr, tuple) and expr[0] in ["FILTERS", "FILTER"]:
                    return None
                return expr
            else:
                expr = coerce_simple_transform(transform, src_expr)
                if isinstance(expr, tuple) and expr[0] in ["FILTERS", "FILTER"]:
                    return None
                return expr
        except Exception as e:
            raise TransformError(f"Failed to apply transform for target '{target}': {e}") from e
    else:
        if source is None and default is None:
            raise MappingError(f"Mapping for target '{target}' requires at least one of source/transform/default.")
        return src_expr

def _apply_filter(df: pl.DataFrame, mapping: Dict[str, Any]) -> pl.DataFrame:
    """Apply a single filter mapping to the DataFrame."""
    transform = str(mapping.get("transform", "")).strip()
    
    try:
        expr = parse_transform_expression(transform)
        if isinstance(expr, tuple) and expr[0] in ["FILTERS", "FILTER"]:
            method = expr[1].upper()
            args = expr[2]
            if method == "INCLUDE_IF":
                cond = parse_boolean_expr(args[0])
                return df.filter(cond)
            elif method == "EXCLUDE_IF":
                cond = parse_boolean_expr(args[0])
                return df.filter(~cond)
            elif method == "LIMIT":
                n = int(float(args[0]))
                return df.head(n)
            elif method == "OFFSET":
                n = int(float(args[0]))
                return df.slice(n)
            elif method == "INCLUDE":
                cond = parse_boolean_expr(args[0])
                return df.filter(cond)
            else:
                raise TransformError(f"Unsupported FILTER/FILTERS method: {method}")
        else:
            return df
    except Exception as e:
        raise TransformError(f"Failed to apply FILTER transform: {e}") from e

def apply_transformations(df: pl.DataFrame, mappings: List[Dict]) -> pl.DataFrame:
    """
    Apply transformations to a DataFrame based on mapping configuration.
    
    Args:
        df: Input Polars DataFrame
        mappings: List of mapping dictionaries
        
    Returns:
        Transformed Polars DataFrame
    """
    if not mappings:
        raise TransformError("Mappings list cannot be empty")
    
    # Build expressions for each mapping
    select_exprs = []
    
    for mp in mappings:
        expr = _build_expr_for_mapping(df, mp)
        
        # Skip None expressions (filter operations)
        if expr is None:
            continue
            
        select_exprs.append(expr.alias(mp.get('target', 'unknown')))
    
    # Apply transformations
    try:
        # Apply any filters first
        df2 = df
        for mp in mappings:
            if mp.get('transform', '').startswith('FILTER[') or mp.get('transform', '').startswith('FILTERS['):
                df2 = _apply_filter(df2, mp)
        
        # Apply all transformations
        out = df2.select(select_exprs)
        return out
        
    except Exception as e:
        raise TransformError(f"Transformation failed: {e}")