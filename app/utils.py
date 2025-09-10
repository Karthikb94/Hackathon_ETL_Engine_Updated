import re
import datetime as _dt
import polars as pl
from typing import Optional, Union, Any

_DEFAULT_DATE_FMT = "%m%d%Y"  # Interpreting MMDDCCYY as MMDDYYYY as a practical default

def timestamp_run_id():
    return _dt.datetime.now().strftime("%Y%m%d_%H%M%S")

def is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except:
        return False

def try_parse_literal(token: str):
    token = token.strip()
    # strings in single or double quotes
    if (len(token) >= 2) and ((token[0] == token[-1]) and token[0] in ("'", '"')):
        return pl.lit(token[1:-1])
    # numbers
    if is_number(token):
        if "." in token:
            return pl.lit(float(token))
        else:
            return pl.lit(int(float(token)))
    # booleans
    if token.lower() == "true":
        return pl.lit(True)
    if token.lower() == "false":
        return pl.lit(False)
    if token.lower() == "null":
        return pl.lit(None)
    return None

def split_args(arg_str: str):
    """Split a method args string by commas while respecting nested () and [] and quotes."""
    args = []
    cur = []
    depth_paren = 0
    depth_brack = 0
    in_quote = None
    i = 0
    while i < len(arg_str):
        ch = arg_str[i]
        if in_quote:
            cur.append(ch)
            if ch == in_quote and (i == 0 or arg_str[i-1] != '\\'):
                in_quote = None
        else:
            if ch in ("'", '"'):
                in_quote = ch
                cur.append(ch)
            elif ch == "(":
                depth_paren += 1
                cur.append(ch)
            elif ch == ")":
                depth_paren -= 1
                cur.append(ch)
            elif ch == "[":
                depth_brack += 1
                cur.append(ch)
            elif ch == "]":
                depth_brack -= 1
                cur.append(ch)
            elif ch == "," and depth_paren == 0 and depth_brack == 0:
                args.append("".join(cur).strip())
                cur = []
            else:
                cur.append(ch)
        i += 1
    if cur:
        args.append("".join(cur).strip())
    return args

def parse_attr(token: str):
    # Handle both attr('column') and ATTR(column) formats
    m = re.fullmatch(r"attr\(\s*['\"](.+?)['\"]\s*\)", token.strip(), re.IGNORECASE)
    if not m:
        # Try ATTR(column) format
        m = re.fullmatch(r"ATTR\(\s*([^)]+)\s*\)", token.strip())
    if not m:
        return None
    col = m.group(1).strip()
    return pl.col(col)

def parse_boolean_expr(expr: str):
    expr = expr.strip()
    # BOOLEAN[...] form
    if expr.startswith("BOOLEAN[") and expr.endswith("]"):
        inner = expr[len("BOOLEAN["):-1].strip()
        # method(args)
        m2 = re.match(r"(\w+)\s*\((.*)\)$", inner, re.DOTALL)
        if not m2:
            raise ValueError(f"Malformed BOOLEAN expression: {expr}")
        method = m2.group(1).upper()
        args = split_args(m2.group(2))
        if method == "EQUALS":
            a, b = args
            return parse_value(a).eq(parse_value(b))
        if method == "EQ":
            a, b = args
            return parse_value(a).eq(parse_value(b))
        if method == "NOT_EQUALS":
            a, b = args
            return parse_value(a).ne(parse_value(b))
        if method == "GREATER_THAN":
            a, b = args
            return parse_value(a) > parse_value(b)
        if method == "GT":
            a, b = args
            return parse_value(a) > parse_value(b)
        if method == "LESS_THAN":
            a, b = args
            return parse_value(a) < parse_value(b)
        if method == "GREATER_OR_EQUAL":
            a, b = args
            return parse_value(a) >= parse_value(b)
        if method == "LESS_OR_EQUAL":
            a, b = args
            return parse_value(a) <= parse_value(b)
        raise ValueError(f"Unsupported BOOLEAN method: {method}")
    
    # Handle IF statements for FILTER operations
    if expr.startswith("IF(") and expr.endswith(")"):
        inner = expr[len("IF("):-1].strip()
        args = split_args(inner)
        if len(args) >= 3:
            cond = parse_boolean_expr(args[0])
            tv = parse_value(args[1])
            fv = parse_value(args[2])
            return pl.when(cond).then(tv).otherwise(fv)
        else:
            raise ValueError(f"IF statement requires 3 arguments: {expr}")
    
    # Handle BOOLEAN method calls for FILTER operations
    if expr.startswith("EQ(") or expr.startswith("GT(") or expr.startswith("LT(") or expr.startswith("GTE(") or expr.startswith("LTE(") or expr.startswith("NE("):
        # Extract method name and arguments
        m = re.match(r"(\w+)\s*\((.*)\)$", expr.strip(), re.DOTALL)
        if m:
            method = m.group(1).upper()
            args_str = m.group(2)
            args = split_args(args_str)
            if method == "EQ":
                a, b = args
                return parse_value(a).eq(parse_value(b))
            elif method == "GT":
                a, b = args
                return parse_value(a) > parse_value(b)
            elif method == "LT":
                a, b = args
                return parse_value(a) < parse_value(b)
            elif method == "GTE":
                a, b = args
                return parse_value(a) >= parse_value(b)
            elif method == "LTE":
                a, b = args
                return parse_value(a) <= parse_value(b)
            elif method == "NE":
                a, b = args
                return parse_value(a).ne(parse_value(b))
            else:
                raise ValueError(f"Unsupported BOOLEAN method: {method}")
        else:
            raise ValueError(f"Malformed BOOLEAN expression: {expr}")
    
    # simple: left OP right (supports ==, !=, >=, <=, >, <)
    ops = ["==", "!=", ">=", "<=", ">", "<"]
    for op in ops:
        if op in expr:
            left, right = expr.split(op, 1)
            l = parse_value(left.strip())
            r = parse_value(right.strip())
            if op == "==":
                return l.eq(r)
            if op == "!=":
                return l.ne(r)
            if op == ">":
                return l > r
            if op == "<":
                return l < r
            if op == ">=":
                return l >= r
            if op == "<=":
                return l <= r
    raise ValueError(f"Unsupported boolean condition: {expr}")

def parse_date_format(fmt: Optional[str]) -> str:
    # Accept user-given format; if absent, use default MMDDYYYY
    return fmt or _DEFAULT_DATE_FMT

def parse_value(token: str):
    token = token.strip()
    # nested trns expression allowed inside
    if token.startswith("trns:"):
        return parse_transform_expression(token)
    # Handle transform expressions without trns: prefix
    if token.startswith(("MATH[", "STRING[", "LOGICAL[", "BOOLEAN[", "FILTER[", "DATE[", "ARRAY[", "DIRECT[")):
        return parse_transform_expression(token)
    # Handle bare method calls like CONCAT(...) by wrapping them in STRING[...]
    if token.startswith(("CONCAT(", "UPPER(", "LOWER(", "TRIM(", "LENGTH(", "REPLACE(", "SUBSTR(")):
        return parse_transform_expression(f"STRING[{token}]")
    # attr('col')
    col = parse_attr(token)
    if col is not None:
        return col
    # boolean literals
    if token.lower() == "true":
        return pl.lit(True)
    if token.lower() == "false":
        return pl.lit(False)
    if token.lower() == "null":
        return pl.lit(None)
    # literal
    lit = try_parse_literal(token)
    if lit is not None:
        return lit
    # fallback: treat as column name
    return pl.col(token)

def parse_method_call(op: str, content: str):
    # content looks like: METHOD(arg1, arg2, ...)
    m = re.match(r"(\w+)\s*\((.*)\)$", content.strip(), re.DOTALL)
    if not m:
        raise ValueError(f"Malformed method in {op}[{content}]")
    method = m.group(1).upper()
    args_str = m.group(2)
    args = split_args(args_str)
    return method, args

def parse_transform_expression(expr: str):
    """
    Parse an expression like:
      trns: STRING[CONCAT(attr('a'), ' ', attr('b'))]
      trns: LOGICAL[IF(attr('age') > 18, 'Adult', 'Minor')]
    and return a Polars expression.
    
    Also handles expressions without 'trns:' prefix for backward compatibility.
    """
    expr = expr.strip()
    
    # Handle both formats: with and without 'trns:' prefix
    if expr.lower().startswith("trns:"):
        m = re.match(r"trns:\s*(\w+)\s*\[(.*)\]\s*$", expr, re.DOTALL | re.IGNORECASE)
    else:
        # New format without 'trns:' prefix
        m = re.match(r"(\w+)\s*\[(.*)\]\s*$", expr, re.DOTALL | re.IGNORECASE)
    
    if not m:
        raise ValueError(f"Malformed transform expression: {expr}")
    op = m.group(1).upper()
    inner = m.group(2).strip()
    method, args = parse_method_call(op, inner)

    # Dispatch
    if op == "MATH":
        a = parse_value(args[0])
        if method == "ADD":
            return a + parse_value(args[1])
        if method == "SUB":
            return a - parse_value(args[1])
        if method == "MUL":
            return a * parse_value(args[1])
        if method == "DIV":
            return a / parse_value(args[1])
        if method == "MOD":
            return a % parse_value(args[1])
        if method == "ROUND":
            prec = int(float(str(args[1]).strip()))
            # Always cast to numeric for ROUND operations
            a = a.cast(pl.Float64, strict=False)
            return a.round(prec)
        if method == "ABS":
            return a.abs()
        raise ValueError(f"Unsupported MATH method: {method}")

    if op == "STRING":
        if method == "CONCAT":
            parts = [parse_value(arg) for arg in args]
            return pl.concat_str(parts)
        if method == "SUBSTR":
            base = parse_value(args[0]).cast(pl.Utf8)
            start = parse_value(args[1])
            length = parse_value(args[2]) if len(args) > 2 else None
            if length is None:
                return base.str.slice(start)
            return base.str.slice(start, length)
        if method == "REPLACE":
            base = parse_value(args[0]).cast(pl.Utf8)
            find = parse_value(args[1])
            repl = parse_value(args[2])
            return base.str.replace_all(find, repl, literal=True)
        if method == "UPPER":
            base = parse_value(args[0]).cast(pl.Utf8)
            return base.str.to_uppercase()
        if method == "LOWER":
            base = parse_value(args[0]).cast(pl.Utf8)
            return base.str.to_lowercase()
        if method == "TRIM":
            base = parse_value(args[0]).cast(pl.Utf8)
            return base.str.strip_chars()
        if method == "LENGTH":
            base = parse_value(args[0]).cast(pl.Utf8)
            return base.str.len_chars()
        raise ValueError(f"Unsupported STRING method: {method}")

    if op == "LOGICAL":
        if method == "IF":
            cond = parse_boolean_expr(args[0])
            tv = parse_value(args[1])
            fv = parse_value(args[2])
            return pl.when(cond).then(tv).otherwise(fv)
        if method == "AND":
            exps = [parse_boolean_expr(a) for a in args]
            out = exps[0]
            for e in exps[1:]:
                out = out & e
            return out
        if method == "OR":
            exps = [parse_boolean_expr(a) for a in args]
            out = exps[0]
            for e in exps[1:]:
                out = out | e
            return out
        if method == "NOT":
            return ~parse_boolean_expr(args[0])
        raise ValueError(f"Unsupported LOGICAL method: {method}")

    if op == "BOOLEAN":
        inner = f"BOOLEAN[{method}({', '.join(args)})]"
        return parse_boolean_expr(inner)

    if op == "FILTERS":
        return ("FILTERS", method, args)
    
    if op == "FILTER":
        return ("FILTER", method, args)
    
    if op == "DIRECT":
        # DIRECT[ATTR('column')] - directly use the column value
        if method == "ATTR":
            return parse_value(args[0])
        raise ValueError(f"Unsupported DIRECT method: {method}")

    if op == "DATE":
        if method == "FORMAT":
            base = parse_value(args[0])
            fmt = args[1].strip().strip("'\"")
            
            # Check if this is a column reference and handle both datetime and string dates
            if isinstance(base, pl.Expr) and str(base).startswith('col('):
                # This is a column reference - handle both datetime and string columns
                # Use a runtime approach that works with both types
                # We'll use a simple string parsing approach that works with both
                return base.str.strptime(pl.Datetime, fmt, strict=False).dt.strftime(fmt)
            else:
                # This is a literal or computed expression
                try:
                    # Try to use it as datetime first
                    result = base.dt.strftime(fmt)
                    return result
                except Exception as e:
                    # If that fails, try to parse it as a string and format it
                    try:
                        result = base.str.strptime(pl.Datetime, fmt, strict=False).dt.strftime(fmt)
                        return result
                    except Exception as e2:
                        # Fallback: return the original string as-is
                        return base
        if method == "PARSE":
            base = parse_value(args[0]).cast(pl.Utf8)
            fmt = parse_date_format(args[1].strip().strip("'\"") if len(args) > 1 else None)
            return base.str.strptime(pl.Date, fmt, strict=False)
        if method == "ADD_DAYS":
            base = parse_value(args[0])
            n = int(float(str(args[1])))
            return base.dt.offset_by(f"{n}d")
        if method == "SUB_DAYS":
            base = parse_value(args[0])
            n = int(float(str(args[1])))
            return base.dt.offset_by(f"-{n}d")
        if method == "DIFF_DAYS":
            d1 = parse_value(args[0])
            d2 = parse_value(args[1])
            return (d1 - d2).dt.total_days()
        if method == "DIFF":
            d1 = parse_value(args[0])
            d2 = parse_value(args[1])
            unit = args[2].strip().strip("'\"") if len(args) > 2 else "days"
            
            # Check if these are column references and handle both datetime and string columns
            if (isinstance(d1, pl.Expr) and str(d1).startswith('col(') and 
                isinstance(d2, pl.Expr) and str(d2).startswith('col(')):
                # This is a column reference - handle both datetime and string columns
                # Use a runtime approach that works with both types
                if unit.lower() == "days":
                    # Parse both columns to datetime first, then calculate difference
                    # This works with both string and datetime columns
                    d1_parsed = d1.str.strptime(pl.Datetime, "%Y-%m-%d", strict=False)
                    d2_parsed = d2.str.strptime(pl.Datetime, "%Y-%m-%d", strict=False)
                    return (d1_parsed - d2_parsed).dt.total_days()
                else:
                    raise ValueError(f"Unsupported DATE DIFF unit: {unit}")
            else:
                # Standard approach for non-column references
                if unit.lower() == "days":
                    return (d1 - d2).dt.total_days()
                else:
                    raise ValueError(f"Unsupported DATE DIFF unit: {unit}")
        if method == "CURRENT_DATE":
            import datetime as _dt
            return pl.lit(_dt.date.today())
        if method == "EXTRACT":
            base = parse_value(args[0])
            part = args[1].strip().strip("'\"").lower()
            if part == "year":
                return base.dt.year()
            if part == "month":
                return base.dt.month()
            if part == "day":
                return base.dt.day()
            raise ValueError(f"Unsupported DATE EXTRACT part: {part}")
        raise ValueError(f"Unsupported DATE method: {method}")

    if op == "ARRAY":
        if method == "JOIN":
            base = parse_value(args[0])
            delim = args[1].strip().strip("'\"")
            # For ARRAY[JOIN], since we're working with comma-separated strings,
            # we'll just return the string as-is for now to avoid list type issues
            # This maintains compatibility while avoiding the Polars list type limitation
            return base
        if method == "SPLIT":
            s = parse_value(args[0]).cast(pl.Utf8)
            delim = args[1].strip().strip("'\"")
            return s.str.split(delim)
        if method == "LENGTH":
            return parse_value(args[0]).arr.lengths()
        if method == "GET":
            arr_expr = parse_value(args[0])
            index = parse_value(args[1])
            # Use list.get() for string splits, arr.get() for proper arrays
            try:
                return arr_expr.list.get(index)
            except:
                # Fallback to arr.get() if list.get() fails
                return arr_expr.arr.get(index)
        raise ValueError(f"Unsupported ARRAY method: {method}")

    if op == "AGGREGATION":
        if method == "SUM":
            return parse_value(args[0]).arr.sum()
        if method == "AVG":
            return parse_value(args[0]).arr.mean()
        if method == "MIN":
            return parse_value(args[0]).arr.min()
        if method == "MAX":
            return parse_value(args[0]).arr.max()
        if method == "COUNT":
            return parse_value(args[0]).arr.lengths()
        raise ValueError(f"Unsupported AGGREGATION method: {method}")

    raise ValueError(f"Unsupported OPERATION: {op}")

def coerce_simple_transform(transform: str, source_expr: pl.Expr) -> pl.Expr:
    t = transform.strip()

    if t.lower().startswith("trns:"):
        return parse_transform_expression(t)
    
    # Handle new format without 'trns:' prefix
    if t.startswith(("MATH[", "STRING[", "LOGICAL[", "BOOLEAN[", "FILTER[", "DATE[", "ARRAY[", "DIRECT[")):
        expr = parse_transform_expression(t)
        # Check if it's a FILTER operation that should return None
        if isinstance(expr, tuple) and expr[0] in ["FILTERS", "FILTER"]:
            return expr
        return expr

    if t == "to_int":
        return source_expr.cast(pl.Int64, strict=False)
    if t == "to_float":
        return source_expr.cast(pl.Float64, strict=False)
    if t == "to_str":
        # Only cast if not already string
        if source_expr.dtype != pl.Utf8:
            return source_expr.cast(pl.Utf8, strict=False)
        else:
            return source_expr

    if t == "to_bool":
        return (source_expr.cast(pl.Utf8).str.to_lowercase().is_in(["1","true","y","yes"])).cast(pl.Boolean)

    if t == "trim":
        return source_expr.cast(pl.Utf8).str.strip_chars()
    if t == "upper":
        return source_expr.cast(pl.Utf8).str.to_uppercase()
    if t == "lower":
        return source_expr.cast(pl.Utf8).str.to_lowercase()

    m = re.match(r"date_format\s*\(\s*['\"](.+?)['\"]\s*\)", t, re.IGNORECASE)
    if m:
        fmt = m.group(1)
        # Handle both datetime and string inputs
        try:
            # Try to use it as datetime first
            return source_expr.dt.strftime(fmt)
        except:
            # If that fails, try to parse it as a string and format it
            # This handles the case where the column is a string representation of a date
            return source_expr.str.strptime(pl.Datetime, fmt, strict=False).dt.strftime(fmt)

    m = re.match(r"to_date\s*\(\s*['\"](.+?)['\"]\s*\)", t, re.IGNORECASE)
    if m:
        fmt = m.group(1) if m.group(1) else _DEFAULT_DATE_FMT
        return source_expr.cast(pl.Utf8).str.strptime(pl.Date, fmt, strict=False)

    raise ValueError(f"Unsupported simple transform: {t}")
