import re
import polars as pl
from typing import Any, Dict, List, Tuple, Optional
from .exceptions import MappingError, TransformError, ValidationError
from .utils import parse_transform_expression, coerce_simple_transform, parse_boolean_expr

def _build_expr_for_mapping(df: pl.DataFrame, mapping: Dict[str, Any]) -> Optional[pl.Expr]:
    # Handle both old format (target) and new format (affected_target)
    target = mapping.get("target") or mapping.get("affected_target")
    # Handle both old format (source) and new format (affected_source)
    source = mapping.get("source") or mapping.get("affected_source")
    # Handle both old format (transform) and new format (trns)
    transform = mapping.get("transform") or mapping.get("trns")
    default = mapping.get("default")

    # Add logging for debugging
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Building expression for mapping: {mapping.get('id', 'no_id')}")
    logger.info(f"  Target: {target}")
    logger.info(f"  Source: {source}")
    logger.info(f"  Transform: {transform}")
    logger.info(f"  Default: {default}")

    if source is not None:
        # Handle comma-separated source fields
        source_columns = [col.strip() for col in source.split(',')]
        missing_columns = [col for col in source_columns if col not in df.columns]

        if missing_columns:
            if default is not None:
                src_expr = pl.lit(default)
                logger.info(f"  Using default value: {default}")
            else:
                logger.error(f"  Missing columns: {missing_columns}")
                raise MappingError(f"Source column(s) {missing_columns} not found and no default provided.")
        else:
            # Use the first source column for the source expression (for backward compatibility)
            src_expr = pl.col(source_columns[0])
            logger.info(f"  Using source column: {source_columns[0]}")
    else:
        if default is not None and transform is None:
            logger.info(f"  Using default value (no transform): {default}")
            return pl.lit(default)
        src_expr = pl.lit(None)
        logger.info(f"  No source, using None")

    if transform:
        try:
            logger.info(f"  Applying transform: {transform}")
            # Check if it's an advanced transform (starts with trns: or contains [])
            if (transform.strip().lower().startswith("trns:") or 
                ("[" in transform and "]" in transform and 
                 any(op in transform.upper() for op in ["DIRECT", "STRING", "MATH", "LOGICAL", "DATE", "BOOLEAN", "ARRAY", "FILTERS", "FILTER"]))):
                expr = parse_transform_expression(transform)
                logger.info(f"  Parsed expression: {expr}")
                if isinstance(expr, tuple) and expr[0] in ["FILTERS", "FILTER"]:
                    return None
                return expr
            else:
                expr = coerce_simple_transform(transform, src_expr)
                logger.info(f"  Coerced expression: {expr}")
                # Check if it's a FILTER operation that should return None
                if isinstance(expr, tuple) and expr[0] in ["FILTERS", "FILTER"]:
                    return None
                return expr
        except Exception as e:
            logger.error(f"  Transform failed: {e}")
            raise TransformError(f"Failed to apply transform for target '{target}': {e}") from e
    else:
        if source is None and default is None:
            raise MappingError(f"Mapping for target '{target}' requires at least one of source/transform/default.")
        logger.info(f"  No transform, using source expression")
        return src_expr

def _apply_filter(df: pl.DataFrame, mapping: Dict[str, Any]) -> pl.DataFrame:
    """Apply a single filter mapping to the DataFrame."""
    transform = str(mapping.get("trns", mapping.get("transform", ""))).strip()
    
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
                # Handle FILTER[INCLUDE(...)] format
                cond = parse_boolean_expr(args[0])
                return df.filter(cond)
            else:
                raise TransformError(f"Unsupported FILTER/FILTERS method: {method}")
        else:
            # Not a filter operation, return original DataFrame
            return df
    except Exception as e:
        raise TransformError(f"Failed to apply FILTER transform: {e}") from e

def _apply_filters(df: pl.DataFrame, mappings: List[Dict[str, Any]]) -> pl.DataFrame:
    out = df
    for mp in mappings:
        # Handle both old format (transform) and new format (trns)
        transform = str(mp.get("transform", mp.get("trns", ""))).strip()
        # Check for both trns: prefix and direct FILTER operations
        is_filter_op = ("FILTERS[" in transform.upper() or "FILTER[" in transform.upper())
        if (transform.lower().startswith("trns:") and is_filter_op) or (not transform.lower().startswith("trns:") and is_filter_op):
            try:
                expr = parse_transform_expression(transform)
                if isinstance(expr, tuple) and expr[0] in ["FILTERS", "FILTER"]:
                    method = expr[1].upper()
                    args = expr[2]
                    if method == "INCLUDE_IF":
                        cond = parse_boolean_expr(args[0])
                        out = out.filter(cond)
                    elif method == "EXCLUDE_IF":
                        cond = parse_boolean_expr(args[0])
                        out = out.filter(~cond)
                    elif method == "LIMIT":
                        n = int(float(args[0]))
                        out = out.head(n)
                    elif method == "OFFSET":
                        n = int(float(args[0]))
                        out = out.slice(n)
                    elif method == "INCLUDE":
                        # Handle FILTER[INCLUDE(...)] format
                        cond = parse_boolean_expr(args[0])
                        out = out.filter(cond)
                    else:
                        raise TransformError(f"Unsupported FILTER/FILTERS method: {method}")
            except Exception as e:
                raise TransformError(f"Failed to apply FILTER/FILTERS transform: {e}") from e
    return out

def apply_transformations(df: pl.DataFrame, mappings: List[Dict]) -> pl.DataFrame:
    """
    Apply transformations to a DataFrame based on mapping configuration.
    
    Args:
        df: Input Polars DataFrame
        mappings: List of mapping dictionaries
        
    Returns:
        Transformed Polars DataFrame
    """
    import time
    
    if not mappings:
        raise TransformError("Mappings list cannot be empty")
    
    # Add detailed logging for debugging
    import logging
    logger = logging.getLogger(__name__)
    
    # Start transformation timing
    transform_start = time.time()
    
    # Log to logger
    logger.info(f"=== TRANSFORMATION DEBUG INFO ===")
    logger.info(f"Input DataFrame shape: {df.shape}")
    logger.info(f"Input DataFrame schema: {df.schema}")
    
    # Log sample data for each column
    logger.info("Sample data from each column:")
    for col_name, dtype in df.schema.items():
        try:
            sample_values = df.select(pl.col(col_name)).head(3).to_series().to_list()
            logger.info(f"  {col_name} ({dtype}): {sample_values}")
        except Exception as e:
            logger.warning(f"  {col_name} ({dtype}): Error getting sample - {e}")
    
    logger.info(f"Number of mappings to apply: {len(mappings)}")
    for i, mp in enumerate(mappings):
        logger.info(f"  Mapping {i+1}: {mp.get('id', 'no_id')} -> {mp.get('affected_target', mp.get('target', 'no_target'))}")
        logger.info(f"    Transform: {mp.get('trns', 'no_trns')}")
        logger.info(f"    Source: {mp.get('affected_source', mp.get('source', 'no_source'))}")
    
    # Build expressions for each mapping
    select_exprs = []
    mapping_times = []
    
    for mp in mappings:
        mapping_start = time.time()
        expr = _build_expr_for_mapping(df, mp)
        mapping_time = (time.time() - mapping_start) * 1000
        mapping_times.append(mapping_time)
        
        # Skip None expressions (filter operations)
        if expr is None:
            logger.info(f"Skipping filter mapping: {mp.get('id', 'no_id')}")
            continue
            
        # Log the final expression being built
        logger.info(f"Final expression for {mp.get('affected_target', mp.get('target', 'no_target'))}: {expr}")
        select_exprs.append(expr.alias(mp.get('affected_target', mp.get('target', 'no_target'))))
    
    logger.info(f"Total expressions to apply: {len(select_exprs)}")
    logger.info("=== END TRANSFORMATION DEBUG INFO ===")
    
    # Apply transformations
    execution_start = time.time()
    try:
        # Apply any filters first
        df2 = df
        for mp in mappings:
            if mp.get('trns', '').startswith('FILTER[') or mp.get('trns', '').startswith('FILTERS['):
                df2 = _apply_filter(df2, mp)
        
        # Apply all transformations
        out = df2.select(select_exprs)
        execution_time = (time.time() - execution_start) * 1000
        
        # Log performance metrics
        total_transform_time = (time.time() - transform_start) * 1000
        avg_mapping_time = sum(mapping_times) / len(mapping_times) if mapping_times else 0
        
        logger.info(f"Transformation execution completed in {execution_time:.2f}ms")
        logger.info(f"Average mapping build time: {avg_mapping_time:.2f}ms")
        logger.info(f"Total transformation time: {total_transform_time:.2f}ms")
        
        return out
        
    except Exception as e:
        execution_time = (time.time() - execution_start) * 1000
        logger.error(f"Transformation execution failed after {execution_time:.2f}ms: {e}")
        raise TransformError(f"Transformation failed: {e}")
