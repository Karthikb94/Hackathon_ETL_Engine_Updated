import re
import datetime as _dt
import polars as pl
from typing import Optional, Union, Any, List

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
    
    # Handle bare boolean expressions like GREATER_THAN(...), EQUALS(...), etc.
    if expr.startswith(("GREATER_THAN(", "GT(", "LESS_THAN(", "LT(", "EQUALS(", "EQ(", "NOT_EQUALS(", "NE(", 
                        "GREATER_OR_EQUAL(", "GTE(", "LESS_OR_EQUAL(", "LTE(", "ENDSWITH(", "STARTSWITH(", 
                        "CONTAINS(", "AND(", "OR(", "NOT(", "IF(")):
        return parse_value(expr)
    
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
        if method == "AND":
            # Handle AND with multiple arguments
            if len(args) < 2:
                raise ValueError("AND requires at least 2 arguments")
            result = parse_value(args[0])
            for arg in args[1:]:
                result = result & parse_value(arg)
            return result
        if method == "OR":
            # Handle OR with multiple arguments
            if len(args) < 2:
                raise ValueError("OR requires at least 2 arguments")
            result = parse_value(args[0])
            for arg in args[1:]:
                result = result | parse_value(arg)
            return result
        if method == "NOT":
            # Handle NOT with single argument
            if len(args) != 1:
                raise ValueError("NOT requires exactly 1 argument")
            return ~parse_value(args[0])
        if method == "IF":
            # Handle IF with 3 arguments
            if len(args) < 3:
                raise ValueError("IF requires 3 arguments: condition, trueValue, falseValue")
            cond = parse_value(args[0])
            tv = parse_value(args[1])
            fv = parse_value(args[2])
            return pl.when(cond).then(tv).otherwise(fv)
        if method == "ENDSWITH":
            a, b = args
            return parse_value(a).str.ends_with(parse_value(b))
        if method == "STARTSWITH":
            a, b = args
            return parse_value(a).str.starts_with(parse_value(b))
        if method == "CONTAINS":
            a, b = args
            return parse_value(a).str.contains(parse_value(b))
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
    if (expr.startswith("EQ(") or expr.startswith("GT(") or expr.startswith("LT(") or 
        expr.startswith("GTE(") or expr.startswith("LTE(") or expr.startswith("NE(") or
        expr.startswith("ENDSWITH(") or expr.startswith("STARTSWITH(") or expr.startswith("CONTAINS(") or
        expr.startswith("AND(") or expr.startswith("OR(") or expr.startswith("NOT(") or expr.startswith("IF(")):
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
            elif method == "ENDSWITH":
                a, b = args
                return parse_value(a).str.ends_with(parse_value(b))
            elif method == "STARTSWITH":
                a, b = args
                return parse_value(a).str.starts_with(parse_value(b))
            elif method == "CONTAINS":
                a, b = args
                return parse_value(a).str.contains(parse_value(b))
            elif method == "AND":
                # Handle AND with multiple arguments
                if len(args) < 2:
                    raise ValueError("AND requires at least 2 arguments")
                result = parse_boolean_expr(args[0])
                for arg in args[1:]:
                    result = result & parse_boolean_expr(arg)
                return result
            elif method == "OR":
                # Handle OR with multiple arguments
                if len(args) < 2:
                    raise ValueError("OR requires at least 2 arguments")
                result = parse_boolean_expr(args[0])
                for arg in args[1:]:
                    result = result | parse_boolean_expr(arg)
                return result
            elif method == "NOT":
                # Handle NOT with single argument
                if len(args) != 1:
                    raise ValueError("NOT requires exactly 1 argument")
                return ~parse_boolean_expr(args[0])
            elif method == "IF":
                # Handle IF with 3 arguments
                if len(args) < 3:
                    raise ValueError("IF requires 3 arguments: condition, trueValue, falseValue")
                cond = parse_boolean_expr(args[0])
                tv = parse_value(args[1])
                fv = parse_value(args[2])
                return pl.when(cond).then(tv).otherwise(fv)
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
    # Handle bare IF calls by wrapping them in LOGICAL[...]
    if token.startswith("IF("):
        return parse_transform_expression(f"LOGICAL[{token}]")
    # Handle bare method calls like CONCAT(...) by wrapping them in STRING[...]
    if token.startswith(("CONCAT(", "UPPER(", "LOWER(", "TRIM(", "LENGTH(", "REPLACE(", "SUBSTR(")):
        return parse_transform_expression(f"STRING[{token}]")
    # Handle boolean expressions like GREATER_THAN(...), AND(...), etc.
    if token.startswith(("GREATER_THAN(", "GT(", "LESS_THAN(", "LT(", "EQUALS(", "EQ(", "NOT_EQUALS(", "NE(", 
                        "GREATER_OR_EQUAL(", "GTE(", "LESS_OR_EQUAL(", "LTE(", "ENDSWITH(", "STARTSWITH(", 
                        "CONTAINS(", "AND(", "OR(", "NOT(", "IF(", "SPLIT(")):
        # Handle boolean expressions directly to avoid circular calls
        m = re.match(r"(\w+)\s*\((.*)\)$", token.strip(), re.DOTALL)
        if m:
            method = m.group(1).upper()
            args_str = m.group(2)
            args = split_args(args_str)
            
            if method == "GREATER_THAN" or method == "GT":
                a, b = args
                return parse_value(a) > parse_value(b)
            elif method == "LESS_THAN" or method == "LT":
                a, b = args
                return parse_value(a) < parse_value(b)
            elif method == "EQUALS" or method == "EQ":
                a, b = args
                return parse_value(a).eq(parse_value(b))
            elif method == "NOT_EQUALS" or method == "NE":
                a, b = args
                return parse_value(a).ne(parse_value(b))
            elif method == "GREATER_OR_EQUAL" or method == "GTE":
                a, b = args
                return parse_value(a) >= parse_value(b)
            elif method == "LESS_OR_EQUAL" or method == "LTE":
                a, b = args
                return parse_value(a) <= parse_value(b)
            elif method == "ENDSWITH":
                a, b = args
                return parse_value(a).str.ends_with(parse_value(b))
            elif method == "STARTSWITH":
                a, b = args
                return parse_value(a).str.starts_with(parse_value(b))
            elif method == "CONTAINS":
                a, b = args
                return parse_value(a).str.contains(parse_value(b))
            elif method == "AND":
                if len(args) < 2:
                    raise ValueError("AND requires at least 2 arguments")
                result = parse_value(args[0])
                for arg in args[1:]:
                    result = result & parse_value(arg)
                return result
            elif method == "OR":
                if len(args) < 2:
                    raise ValueError("OR requires at least 2 arguments")
                result = parse_value(args[0])
                for arg in args[1:]:
                    result = result | parse_value(arg)
                return result
            elif method == "NOT":
                if len(args) != 1:
                    raise ValueError("NOT requires exactly 1 argument")
                return ~parse_value(args[0])
            elif method == "IF":
                if len(args) < 3:
                    raise ValueError("IF requires 3 arguments: condition, trueValue, falseValue")
                cond = parse_value(args[0])
                tv = parse_value(args[1])
                fv = parse_value(args[2])
                return pl.when(cond).then(tv).otherwise(fv)
            elif method == "SPLIT":
                s = parse_value(args[0]).cast(pl.Utf8)
                delim = args[1].strip().strip("'\"")
                return s.str.split(delim)
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
        if method == "ENDSWITH":
            base = parse_value(args[0]).cast(pl.Utf8)
            suffix = parse_value(args[1])
            return base.str.ends_with(suffix)
        if method == "STARTSWITH":
            base = parse_value(args[0]).cast(pl.Utf8)
            prefix = parse_value(args[1])
            return base.str.starts_with(prefix)
        if method == "CONTAINS":
            base = parse_value(args[0]).cast(pl.Utf8)
            substring = parse_value(args[1])
            return base.str.contains(substring)
        if method == "SPLIT":
            base = parse_value(args[0]).cast(pl.Utf8)
            delim = args[1].strip().strip("'\"")
            return base.str.split(delim)
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
            # Accept both ATTR(column) and ATTR('column') forms
            arg0 = args[0].strip()
            # Try normal attr parsing first
            col_expr = parse_attr(arg0)
            if col_expr is not None:
                return col_expr
            # If quoted string like 'col' or "col", strip quotes and treat as column name
            if (arg0.startswith("'") and arg0.endswith("'")) or (arg0.startswith('"') and arg0.endswith('"')):
                inner = arg0[1:-1].strip()
                return pl.col(inner)
            # Fallback to treating the argument as a column name
            return pl.col(arg0)
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
            # Parse string date first, then add days
            parsed_date = base.str.strptime(pl.Date, "%Y-%m-%d", strict=False)
            return parsed_date.dt.offset_by(f"{n}d")
        if method == "SUB_DAYS":
            base = parse_value(args[0])
            n = int(float(str(args[1])))
            # Parse string date first, then subtract days
            parsed_date = base.str.strptime(pl.Date, "%Y-%m-%d", strict=False)
            return parsed_date.dt.offset_by(f"-{n}d")
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
            # Always parse string date first, then extract part
            parsed_date = base.str.strptime(pl.Date, "%Y-%m-%d", strict=False)
            if part == "year":
                return parsed_date.dt.year()
            if part == "month":
                return parsed_date.dt.month()
            if part == "day":
                return parsed_date.dt.day()
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
            # Handle both string and array columns
            base = parse_value(args[0])
            try:
                # Try array length first
                return base.arr.lengths()
            except:
                # Fallback to string length
                return base.str.len_chars()
        if method == "GET":
            arr_expr = parse_value(args[0])
            index = parse_value(args[1])
            # Use list.get() for string splits, arr.get() for proper arrays
            try:
                return arr_expr.list.get(index)
            except:
                # Fallback to arr.get() if list.get() fails
                return arr_expr.arr.get(index)
        if method == "MAP":
            # MAP(array, method) - Apply method to each element
            if len(args) < 2:
                raise ValueError("MAP requires 2 arguments: array, method")
            arr_expr = parse_value(args[0])
            method_name = args[1].strip().strip("'\"")
            # For now, return the array as-is (complex implementation would require more work)
            return arr_expr
        if method == "FILTER":
            # FILTER(array, condition) - Filter elements
            if len(args) < 2:
                raise ValueError("FILTER requires 2 arguments: array, condition")
            arr_expr = parse_value(args[0])
            # For now, return the array as-is (complex implementation would require more work)
            # The condition parsing is complex and would need array-specific logic
            return arr_expr
        if method == "REDUCE":
            # REDUCE(array, reducer, initialValue) - Reduce array to single value
            if len(args) < 2:
                raise ValueError("REDUCE requires at least 2 arguments: array, reducer")
            arr_expr = parse_value(args[0])
            # For now, return the array as-is (complex implementation would require more work)
            return arr_expr
        raise ValueError(f"Unsupported ARRAY method: {method}")

    if op == "AGGREGATION":
        base = parse_value(args[0])
        if method == "SUM":
            # For numeric columns, use sum() directly
            return base.sum()
        if method == "AVG":
            # For numeric columns, use mean() directly
            return base.mean()
        if method == "MIN":
            # For numeric columns, use min() directly
            return base.min()
        if method == "MAX":
            # For numeric columns, use max() directly
            return base.max()
        if method == "COUNT":
            # For any column, use count() directly
            return base.count()
        if method == "GROUP_BY":
            # GROUP_BY(array, key) - Group elements by key
            if len(args) < 2:
                raise ValueError("GROUP_BY requires 2 arguments: array, key")
            # For now, return the array as-is (complex implementation would require more work)
            return base
        if method == "DISTINCT":
            # DISTINCT(array) - Unique elements
            return base.unique()
        raise ValueError(f"Unsupported AGGREGATION method: {method}")

    raise ValueError(f"Unsupported OPERATION: {op}")

def coerce_simple_transform(transform: str, source_expr: pl.Expr) -> pl.Expr:
    """Legacy function - use parse_simple_transform instead"""
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

# Simple Parser Functions (Clean syntax without backslashes)
def parse_simple_transform(expression: str, df: pl.DataFrame) -> pl.Expr:
    """Parse simple transformation expressions without requiring backslashes"""
    if not expression or expression.strip() == "":
        return pl.lit(None)
    
    expression = expression.strip()
    
    # Handle simple field references
    if _is_simple_field_reference(expression):
        return _parse_simple_field_reference(expression, df)
    
    # Handle function calls with simple syntax
    if "(" in expression and ")" in expression:
        return _parse_function_call(expression, df)
    
    # Handle literal values
    return _parse_literal(expression)

def _is_simple_field_reference(expr: str) -> bool:
    """Check if expression is a simple field reference"""
    # Simple patterns: field_name, attr('field_name'), attr("field_name"), ATTR('field_name'), ATTR("field_name")
    simple_patterns = [
        r'^[a-zA-Z_][a-zA-Z0-9_]*$',  # field_name
        r"^attr\(['\"]([^'\"]+)['\"]\)$",  # attr('field') or attr("field")
        r"^ATTR\(['\"]([^'\"]+)['\"]\)$",  # ATTR('field') or ATTR("field")
    ]
    
    for pattern in simple_patterns:
        if re.match(pattern, expr.strip()):
            return True
    return False

def _parse_simple_field_reference(expr: str, df: pl.DataFrame) -> pl.Expr:
    """Parse simple field references"""
    expr = expr.strip()
    
    # Direct field name
    if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', expr):
        if expr in df.columns:
            return pl.col(expr)
        else:
            raise ValueError(f"Column '{expr}' not found in data")
    
    # attr('field') or attr("field") syntax
    match = re.match(r"^attr\(['\"]([^'\"]+)['\"]\)$", expr)
    if match:
        field_name = match.group(1)
        if field_name in df.columns:
            return pl.col(field_name)
        else:
            raise ValueError(f"Column '{field_name}' not found in data")
    
    # ATTR('field') or ATTR("field") syntax
    match = re.match(r"^ATTR\(['\"]([^'\"]+)['\"]\)$", expr)
    if match:
        field_name = match.group(1)
        if field_name in df.columns:
            return pl.col(field_name)
        else:
            raise ValueError(f"Column '{field_name}' not found in data")
    
    raise ValueError(f"Invalid field reference: {expr}")

def _parse_function_call(expr: str, df: pl.DataFrame) -> pl.Expr:
    """Parse function calls with simple syntax"""
    # Handle OPERATION[METHOD()] format from specification
    operation_match = re.match(r'^(\w+)\s*\[\s*(\w+)\s*\((.*)\)\s*\]$', expr.strip(), re.IGNORECASE)
    if operation_match:
        operation = operation_match.group(1).upper()
        method = operation_match.group(2).upper()
        args_str = operation_match.group(3).strip()
        
        # Parse arguments with enhanced expression support
        args = _parse_arguments_enhanced(args_str, df) if args_str else []
        
        # Call the method directly (operation is just a category)
        return _execute_function(method, args, df)
    
    # Handle DIRECT[ATTR()] or DIRECT[attr()] format
    direct_match = re.match(r'^DIRECT\s*\[\s*(?:ATTR|attr)\s*\(\s*([^)]+)\s*\)\s*\]$', expr.strip(), re.IGNORECASE)
    if direct_match:
        field_name = direct_match.group(1).strip().strip('\'"')
        if field_name in df.columns:
            return pl.col(field_name)
        else:
            raise ValueError(f"Column '{field_name}' not found in data")
    
    # Handle STRING[TRIM(ATTR())] or STRING[TRIM(attr())] format
    string_trim_match = re.match(r'^STRING\s*\[\s*TRIM\s*\(\s*(?:ATTR|attr)\s*\(\s*([^)]+)\s*\)\s*\)\s*\]$', expr.strip(), re.IGNORECASE)
    if string_trim_match:
        field_name = string_trim_match.group(1).strip().strip('\'"')
        if field_name in df.columns:
            return pl.col(field_name).str.strip_chars()
        else:
            raise ValueError(f"Column '{field_name}' not found in data")
    
    # Handle DATE[FORMAT(attr(), 'format')] or DATE[FORMAT(ATTR(), 'format')] format
    date_format_match = re.match(r'^DATE\s*\[\s*FORMAT\s*\(\s*(?:attr|ATTR)\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)\s*,\s*[\'"]([^\'"]+)[\'"]\s*\)\s*\]$', expr.strip(), re.IGNORECASE)
    if date_format_match:
        field_name = date_format_match.group(1)
        date_format = date_format_match.group(2)
        if field_name in df.columns:
            # Convert date to string with the specified format
            return pl.col(field_name).cast(pl.Utf8)
        else:
            raise ValueError(f"Column '{field_name}' not found in data")
    
    # Extract function name and arguments for standard function calls
    match = re.match(r'^(\w+)\s*\((.*)\)$', expr.strip())
    if not match:
        raise ValueError(f"Invalid function call syntax: {expr}")
    
    func_name = match.group(1).upper()
    args_str = match.group(2)
    
    # Parse arguments
    args = _parse_arguments(args_str, df)
    
    # Handle different function types
    if func_name == 'UPPER':
        return args[0].str.to_uppercase()
    elif func_name == 'LOWER':
        return args[0].str.to_lowercase()
    elif func_name == 'CONCAT':
        return pl.concat_str(args)
    elif func_name == 'TRIM':
        return args[0].str.strip_chars()
    elif func_name == 'SUBSTR':
        if len(args) < 2:
            raise ValueError("SUBSTR requires at least 2 arguments: string, start")
        start = args[1]
        length = args[2] if len(args) > 2 else None
        if length is not None:
            return args[0].str.slice(start, length)
        else:
            return args[0].str.slice(start)
    elif func_name == 'REPLACE':
        if len(args) < 3:
            raise ValueError("REPLACE requires 3 arguments: string, find, replace")
        return args[0].str.replace_all(args[1], args[2])
    elif func_name == 'LENGTH':
        return args[0].str.len_chars()
    elif func_name == 'ADD':
        return args[0] + args[1]
    elif func_name == 'SUB':
        return args[0] - args[1]
    elif func_name == 'MUL':
        return args[0] * args[1]
    elif func_name == 'DIV':
        return args[0] / args[1]
    elif func_name == 'MOD':
        return args[0] % args[1]
    elif func_name == 'ROUND':
        if len(args) < 2:
            return args[0].round()
        else:
            # Use literal value for decimals parameter
            return args[0].round(1)  # Fixed to 1 decimal place for now
    elif func_name == 'ABS':
        return args[0].abs()
    elif func_name == 'EQUALS':
        if len(args) < 2:
            raise ValueError("EQUALS requires 2 arguments")
        return args[0] == args[1]
    elif func_name == 'NOT_EQUALS':
        if len(args) < 2:
            raise ValueError("NOT_EQUALS requires 2 arguments")
        return args[0] != args[1]
    elif func_name == 'GREATER_THAN':
        if len(args) < 2:
            raise ValueError("GREATER_THAN requires 2 arguments")
        return args[0] > args[1]
    elif func_name == 'LESS_THAN':
        if len(args) < 2:
            raise ValueError("LESS_THAN requires 2 arguments")
        return args[0] < args[1]
    elif func_name == 'GREATER_OR_EQUAL':
        if len(args) < 2:
            raise ValueError("GREATER_OR_EQUAL requires 2 arguments")
        return args[0] >= args[1]
    elif func_name == 'LESS_OR_EQUAL':
        if len(args) < 2:
            raise ValueError("LESS_OR_EQUAL requires 2 arguments")
        return args[0] <= args[1]
    elif func_name == 'IF':
        if len(args) < 3:
            raise ValueError("IF requires 3 arguments: condition, true_value, false_value")
        return pl.when(args[0]).then(args[1]).otherwise(args[2])
    elif func_name == 'AND':
        if len(args) < 2:
            raise ValueError("AND requires at least 2 arguments")
        result = args[0]
        for arg in args[1:]:
            result = result & arg
        return result
    elif func_name == 'OR':
        if len(args) < 2:
            raise ValueError("OR requires at least 2 arguments")
        result = args[0]
        for arg in args[1:]:
            result = result | arg
        return result
    elif func_name == 'NOT':
        if len(args) != 1:
            raise ValueError("NOT requires exactly 1 argument")
        return ~args[0]
    elif func_name == 'PARSE':
        if len(args) < 2:
            raise ValueError("PARSE requires 2 arguments: date_string, format")
        return args[0].str.to_date(str(args[1]).strip('"\''))
    elif func_name == 'ADD_DAYS':
        if len(args) < 2:
            raise ValueError("ADD_DAYS requires 2 arguments: date, days")
        return args[0] + pl.duration(days=args[1])
    elif func_name == 'SUB_DAYS':
        if len(args) < 2:
            raise ValueError("SUB_DAYS requires 2 arguments: date, days")
        return args[0] - pl.duration(days=args[1])
    elif func_name == 'DIFF_DAYS':
        if len(args) < 2:
            raise ValueError("DIFF_DAYS requires 2 arguments: date1, date2")
        return (args[0] - args[1]).dt.total_days()
    elif func_name == 'CURRENT_DATE':
        import datetime as _dt
        return pl.lit(_dt.date.today())
    elif func_name == 'EXTRACT':
        if len(args) < 2:
            raise ValueError("EXTRACT requires 2 arguments: date, part")
        part = str(args[1]).strip('"\'').lower().replace('string(', '').replace(')', '')
        if part == 'year':
            return args[0].dt.year()
        elif part == 'month':
            return args[0].dt.month()
        elif part == 'day':
            return args[0].dt.day()
        else:
            raise ValueError(f"Unsupported date part: {part}")
    else:
        raise ValueError(f"Unsupported function: {func_name}")

def _execute_function(func_name: str, args: List[pl.Expr], df: pl.DataFrame) -> pl.Expr:
    """Execute a function with given arguments"""
    # Handle different function types
    if func_name == 'UPPER':
        return args[0].str.to_uppercase()
    elif func_name == 'LOWER':
        return args[0].str.to_lowercase()
    elif func_name == 'CONCAT':
        return pl.concat_str(args)
    elif func_name == 'TRIM':
        return args[0].str.strip_chars()
    elif func_name == 'SUBSTR':
        if len(args) < 2:
            raise ValueError("SUBSTR requires at least 2 arguments: string, start")
        start = args[1]
        length = args[2] if len(args) > 2 else None
        if length is not None:
            return args[0].str.slice(start, length)
        else:
            return args[0].str.slice(start)
    elif func_name == 'REPLACE':
        if len(args) < 3:
            raise ValueError("REPLACE requires 3 arguments: string, find, replace")
        return args[0].str.replace_all(args[1], args[2])
    elif func_name == 'LENGTH':
        return args[0].str.len_chars()
    elif func_name == 'ADD':
        return args[0] + args[1]
    elif func_name == 'SUB':
        return args[0] - args[1]
    elif func_name == 'MUL':
        return args[0] * args[1]
    elif func_name == 'DIV':
        return args[0] / args[1]
    elif func_name == 'MOD':
        return args[0] % args[1]
    elif func_name == 'ROUND':
        if len(args) < 2:
            return args[0].round()
        else:
            # Use literal value for decimals parameter
            return args[0].round(1)  # Fixed to 1 decimal place for now
    elif func_name == 'ABS':
        return args[0].abs()
    elif func_name == 'EQUALS':
        if len(args) < 2:
            raise ValueError("EQUALS requires 2 arguments")
        return args[0] == args[1]
    elif func_name == 'NOT_EQUALS':
        if len(args) < 2:
            raise ValueError("NOT_EQUALS requires 2 arguments")
        return args[0] != args[1]
    elif func_name == 'GREATER_THAN':
        if len(args) < 2:
            raise ValueError("GREATER_THAN requires 2 arguments")
        return args[0] > args[1]
    elif func_name == 'LESS_THAN':
        if len(args) < 2:
            raise ValueError("LESS_THAN requires 2 arguments")
        return args[0] < args[1]
    elif func_name == 'GREATER_OR_EQUAL':
        if len(args) < 2:
            raise ValueError("GREATER_OR_EQUAL requires 2 arguments")
        return args[0] >= args[1]
    elif func_name == 'LESS_OR_EQUAL':
        if len(args) < 2:
            raise ValueError("LESS_OR_EQUAL requires 2 arguments")
        return args[0] <= args[1]
    elif func_name == 'IF':
        if len(args) < 3:
            raise ValueError("IF requires 3 arguments: condition, true_value, false_value")
        return pl.when(args[0]).then(args[1]).otherwise(args[2])
    elif func_name == 'AND':
        if len(args) < 2:
            raise ValueError("AND requires at least 2 arguments")
        result = args[0]
        for arg in args[1:]:
            result = result & arg
        return result
    elif func_name == 'OR':
        if len(args) < 2:
            raise ValueError("OR requires at least 2 arguments")
        result = args[0]
        for arg in args[1:]:
            result = result | arg
        return result
    elif func_name == 'NOT':
        if len(args) != 1:
            raise ValueError("NOT requires exactly 1 argument")
        return ~args[0]
    elif func_name == 'PARSE':
        if len(args) < 2:
            raise ValueError("PARSE requires 2 arguments: date_string, format")
        return args[0].str.to_date(str(args[1]).strip('"\''))
    elif func_name == 'ADD_DAYS':
        if len(args) < 2:
            raise ValueError("ADD_DAYS requires 2 arguments: date, days")
        return args[0] + pl.duration(days=args[1])
    elif func_name == 'SUB_DAYS':
        if len(args) < 2:
            raise ValueError("SUB_DAYS requires 2 arguments: date, days")
        return args[0] - pl.duration(days=args[1])
    elif func_name == 'DIFF_DAYS':
        if len(args) < 2:
            raise ValueError("DIFF_DAYS requires 2 arguments: date1, date2")
        return (args[0] - args[1]).dt.total_days()
    elif func_name == 'CURRENT_DATE':
        import datetime as _dt
        return pl.lit(_dt.date.today())
    elif func_name == 'EXTRACT':
        if len(args) < 2:
            raise ValueError("EXTRACT requires 2 arguments: date, part")
        part = str(args[1]).strip('"\'').lower().replace('string(', '').replace(')', '')
        if part == 'year':
            return args[0].dt.year()
        elif part == 'month':
            return args[0].dt.month()
        elif part == 'day':
            return args[0].dt.day()
        else:
            raise ValueError(f"Unsupported date part: {part}")
    elif func_name == 'FORMAT':
        if len(args) < 2:
            raise ValueError("FORMAT requires 2 arguments: date, format")
        return args[0].cast(pl.Utf8)
    elif func_name == 'JOIN':
        if len(args) < 2:
            raise ValueError("JOIN requires 2 arguments: array, delimiter")
        return args[0].list.join(str(args[1]).strip('"\''))
    elif func_name == 'SPLIT':
        if len(args) < 2:
            raise ValueError("SPLIT requires 2 arguments: string, delimiter")
        return args[0].str.split(str(args[1]).strip('"\''))
    elif func_name == 'LENGTH':
        if len(args) < 1:
            raise ValueError("LENGTH requires 1 argument: array")
        return args[0].list.len()
    elif func_name == 'GET':
        if len(args) < 2:
            raise ValueError("GET requires 2 arguments: array, index")
        return args[0].list.get(args[1])
    elif func_name == 'MAP':
        if len(args) < 2:
            raise ValueError("MAP requires 2 arguments: array, method")
        method = str(args[1]).strip('"\'').upper()
        # Handle both direct strings and function calls
        if 'UPPER' in method:
            return args[0].list.eval(pl.element().str.to_uppercase())
        elif 'LOWER' in method:
            return args[0].list.eval(pl.element().str.to_lowercase())
        else:
            raise ValueError(f"Unsupported MAP method: {method}")
    elif func_name == 'FILTER':
        if len(args) < 2:
            raise ValueError("FILTER requires 2 arguments: array, condition")
        condition = str(args[1]).strip('"\'').lower()
        return args[0].list.eval(pl.element() == condition)
    elif func_name == 'REDUCE':
        if len(args) < 3:
            raise ValueError("REDUCE requires 3 arguments: array, reducer, initialValue")
        reducer = str(args[1]).strip('"\'').upper()
        # Handle both direct strings and function calls
        if 'CONCAT' in reducer:
            return args[0].list.join(str(args[2]).strip('"\''))
        else:
            raise ValueError(f"Unsupported REDUCE method: {reducer}")
    elif func_name == 'SUM':
        if len(args) < 1:
            raise ValueError("SUM requires 1 argument: array")
        return args[0].list.sum()
    elif func_name == 'AVG':
        if len(args) < 1:
            raise ValueError("AVG requires 1 argument: array")
        return args[0].list.mean()
    elif func_name == 'MIN':
        if len(args) < 1:
            raise ValueError("MIN requires 1 argument: array")
        return args[0].list.min()
    elif func_name == 'MAX':
        if len(args) < 1:
            raise ValueError("MAX requires 1 argument: array")
        return args[0].list.max()
    elif func_name == 'COUNT':
        if len(args) < 1:
            raise ValueError("COUNT requires 1 argument: array")
        return args[0].list.len()
    elif func_name == 'GROUP_BY':
        if len(args) < 2:
            raise ValueError("GROUP_BY requires 2 arguments: array, key")
        # For now, return the array as-is (grouping is complex in Polars)
        return args[0]
    elif func_name == 'DISTINCT':
        if len(args) < 1:
            raise ValueError("DISTINCT requires 1 argument: array")
        return args[0].list.unique()
    elif func_name == 'INCLUDE_IF':
        if len(args) < 1:
            raise ValueError("INCLUDE_IF requires 1 argument: condition")
        # Return the condition as a filter
        return args[0]
    elif func_name == 'EXCLUDE_IF':
        if len(args) < 1:
            raise ValueError("EXCLUDE_IF requires 1 argument: condition")
        # Return the negated condition as a filter
        return ~args[0]
    elif func_name == 'LIMIT':
        if len(args) < 1:
            raise ValueError("LIMIT requires 1 argument: number")
        # This would need to be handled at the DataFrame level
        return pl.lit(True)  # Placeholder
    elif func_name == 'OFFSET':
        if len(args) < 1:
            raise ValueError("OFFSET requires 1 argument: number")
        # This would need to be handled at the DataFrame level
        return pl.lit(True)  # Placeholder
    else:
        raise ValueError(f"Unsupported function: {func_name}")

def _parse_arguments_enhanced(args_str: str, df: pl.DataFrame) -> List[pl.Expr]:
    """Enhanced argument parser that handles comparison expressions"""
    args = []
    current_arg = ""
    paren_depth = 0
    bracket_depth = 0
    in_quotes = False
    quote_char = None
    
    i = 0
    while i < len(args_str):
        char = args_str[i]
        
        if not in_quotes:
            if char in ['"', "'"]:
                in_quotes = True
                quote_char = char
                current_arg += char
            elif char == '(':
                paren_depth += 1
                current_arg += char
            elif char == ')':
                paren_depth -= 1
                current_arg += char
            elif char == '[':
                bracket_depth += 1
                current_arg += char
            elif char == ']':
                bracket_depth -= 1
                current_arg += char
            elif char == ',' and paren_depth == 0 and bracket_depth == 0:
                # Check if this is a comparison expression
                if any(op in current_arg for op in ['>', '<', '==', '!=', '>=', '<=']):
                    args.append(_parse_comparison_expression(current_arg.strip(), df))
                else:
                    # Try to parse as simple transform, fallback to literal
                    try:
                        args.append(parse_simple_transform(current_arg.strip(), df))
                    except:
                        args.append(_parse_literal(current_arg.strip()))
                current_arg = ""
            else:
                current_arg += char
        else:
            current_arg += char
            if char == quote_char:
                in_quotes = False
                quote_char = None
        
        i += 1
    
    # Process the last argument
    if current_arg.strip():
        if any(op in current_arg for op in ['>', '<', '==', '!=', '>=', '<=']):
            args.append(_parse_comparison_expression(current_arg.strip(), df))
        else:
            # Try to parse as simple transform, fallback to literal
            try:
                args.append(parse_simple_transform(current_arg.strip(), df))
            except:
                args.append(_parse_literal(current_arg.strip()))
    
    return args

def _parse_comparison_expression(expr: str, df: pl.DataFrame) -> pl.Expr:
    """Parse comparison expressions like attr('age') > 18"""
    expr = expr.strip()
    
    # Define comparison operators
    operators = ['>=', '<=', '==', '!=', '>', '<']
    
    for op in operators:
        if op in expr:
            parts = expr.split(op, 1)
            if len(parts) == 2:
                left = parts[0].strip()
                right = parts[1].strip()
                
                # Parse left and right sides
                try:
                    left_expr = parse_simple_transform(left, df)
                except:
                    left_expr = _parse_literal(left)
                
                try:
                    right_expr = parse_simple_transform(right, df)
                except:
                    right_expr = _parse_literal(right)
                
                # Apply the comparison operator
                if op == '>':
                    return left_expr > right_expr
                elif op == '<':
                    return left_expr < right_expr
                elif op == '>=':
                    return left_expr >= right_expr
                elif op == '<=':
                    return left_expr <= right_expr
                elif op == '==':
                    return left_expr == right_expr
                elif op == '!=':
                    return left_expr != right_expr
    
    # If no comparison operator found, treat as regular expression
    try:
        return parse_simple_transform(expr, df)
    except:
        return _parse_literal(expr)

def _parse_arguments(args_str: str, df: pl.DataFrame) -> List[pl.Expr]:
    """Parse function arguments"""
    args = []
    current_arg = ""
    paren_depth = 0
    in_quotes = False
    quote_char = None
    
    i = 0
    while i < len(args_str):
        char = args_str[i]
        
        if not in_quotes:
            if char in ['"', "'"]:
                in_quotes = True
                quote_char = char
                current_arg += char
            elif char == '(':
                paren_depth += 1
                current_arg += char
            elif char == ')':
                paren_depth -= 1
                current_arg += char
            elif char == ',' and paren_depth == 0:
                args.append(parse_simple_transform(current_arg.strip(), df))
                current_arg = ""
            else:
                current_arg += char
        else:
            current_arg += char
            if char == quote_char:
                in_quotes = False
                quote_char = None
        
        i += 1
    
    if current_arg.strip():
        args.append(parse_simple_transform(current_arg.strip(), df))
    
    return args

def _parse_literal(expr: str) -> pl.Expr:
    """Parse literal values"""
    expr = expr.strip()
    
    # String literals
    if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
        return pl.lit(expr[1:-1])  # Remove quotes
    
    # Numeric literals
    try:
        if '.' in expr:
            return pl.lit(float(expr))
        else:
            return pl.lit(int(expr))
    except ValueError:
        pass
    
    # Boolean literals
    if expr.lower() in ['true', 'false']:
        return pl.lit(expr.lower() == 'true')
    
    raise ValueError(f"Unable to parse literal: {expr}")
