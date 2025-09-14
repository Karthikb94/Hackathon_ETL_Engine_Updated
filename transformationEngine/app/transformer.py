import polars as pl
import re
import traceback
from typing import Any, Dict, List, Optional, Union, Tuple
from .exceptions import MappingError, TransformError
from .utils import coerce_simple_transform, parse_boolean_expr, parse_simple_transform

class TransformationNode:
    """Represents a node in the transformation parsing tree"""
    def __init__(self, operation: str, operands: List[Any], precedence: int = 0):
        self.operation = operation
        self.operands = operands
        self.precedence = precedence
        self.dependencies = []
        self.execution_order = 0
        
    def add_dependency(self, node: 'TransformationNode'):
        """Add a dependency to this node"""
        if node not in self.dependencies:
            self.dependencies.append(node)
    
    def __repr__(self):
        return f"TransformationNode({self.operation}, {len(self.operands)} operands, precedence={self.precedence})"

class AdvancedTransformer:
    """Advanced transformation engine with parsing tree execution"""
    
    # Operation precedence (higher number = higher precedence)
    PRECEDENCE = {
        'ATTR': 100,
        'LIT': 100,
        'DIRECT': 90,
        'MATH': 80,
        'STRING': 70,
        'DATE': 60,
        'LOGICAL': 50,
        'BOOLEAN': 40,
        'ARRAY': 30,
        'FILTER': 20,
        'FILTERS': 20
    }
    
    def __init__(self):
        self.nodes = []
        self.execution_plan = []
    
    def parse_expression(self, expression: str, df: pl.DataFrame) -> pl.Expr:
        """Parse and execute a transformation expression using parsing tree"""
        try:
            # Clean up expression
            if expression.strip().lower().startswith("trns:"):
                expression = expression[5:].strip()
            
            # Use the existing parser for now, but with enhanced error handling
            return self._parse_with_fallback(expression, df)
            
        except Exception as e:
            raise TransformError(f"Failed to parse expression '{expression}': {e}") from e
    
    def _parse_with_fallback(self, expression: str, df: pl.DataFrame) -> pl.Expr:
        """Parse expression with fallback strategies (no backslash support)"""
        try:
            # Try simple parser first (handles new formats like DIRECT[ATTR()])
            return parse_simple_transform(expression, df)
        except Exception:
            try:
                # Try advanced parsing
                return self._parse_advanced(expression, df)
            except Exception:
                # Last resort: try to handle it as a simple field reference
                return self._handle_simple_field_reference(expression, df)
    
    def _handle_simple_field_reference(self, expression: str, df: pl.DataFrame) -> pl.Expr:
        """Handle simple field references as last resort"""
        expression = expression.strip()
        
        # Remove quotes if present
        if expression.startswith('"') and expression.endswith('"'):
            expression = expression[1:-1]
        elif expression.startswith("'") and expression.endswith("'"):
            expression = expression[1:-1]
        
        # Check if it's a column name
        if expression in df.columns:
            return pl.col(expression)
        
        raise TransformError(f"Unable to parse expression: {expression}")
    
    def _parse_advanced(self, expression: str, df: pl.DataFrame) -> pl.Expr:
        """Advanced parsing with dependency resolution"""
        self.nodes = []
        self.execution_plan = []
        
        # Parse the expression into nodes
        root_node = self._parse_recursive(expression, df)
        
        # Build dependency graph
        self._build_dependency_graph()
        
        # Create execution plan
        self._create_execution_plan()
        
        # Execute the plan
        return self._execute_plan(df)
    
    def _parse_recursive(self, expr: str, df: pl.DataFrame) -> TransformationNode:
        """Recursively parse expression components"""
        expr = expr.strip()
        
        # Handle nested expressions with brackets
        if '[' in expr and ']' in expr:
            return self._parse_bracketed_expression(expr, df)
        
        # Handle function calls with parentheses
        if '(' in expr and ')' in expr:
            return self._parse_function_call(expr, df)
        
        # Handle simple references
        return self._parse_simple_reference(expr, df)
    
    def _parse_bracketed_expression(self, expr: str, df: pl.DataFrame) -> TransformationNode:
        """Parse expressions like STRING[CONCAT(...)]"""
        bracket_start = expr.find('[')
        bracket_end = expr.rfind(']')
        
        if bracket_start == -1 or bracket_end == -1:
            raise TransformError(f"Malformed bracketed expression: {expr}")
        
        operation = expr[:bracket_start].strip().upper()
        content = expr[bracket_start + 1:bracket_end].strip()
        
        # Parse the content inside brackets
        inner_node = self._parse_function_call(content, df)
        
        # Create node for the main operation
        precedence = self.PRECEDENCE.get(operation, 0)
        node = TransformationNode(operation, [inner_node], precedence)
        
        self.nodes.append(node)
        return node
    
    def _parse_function_call(self, expr: str, df: pl.DataFrame) -> TransformationNode:
        """Parse function calls like CONCAT(attr('a'), ' ', attr('b'))"""
        paren_start = expr.find('(')
        paren_end = expr.rfind(')')
        
        if paren_start == -1 or paren_end == -1:
            raise TransformError(f"Malformed function call: {expr}")
        
        function_name = expr[:paren_start].strip().upper()
        args_str = expr[paren_start + 1:paren_end].strip()
        
        # Parse arguments
        args = self._parse_arguments(args_str, df)
        
        # Create node for the function
        precedence = self.PRECEDENCE.get(function_name, 0)
        node = TransformationNode(function_name, args, precedence)
        
        self.nodes.append(node)
        return node
    
    def _parse_arguments(self, args_str: str, df: pl.DataFrame) -> List[TransformationNode]:
        """Parse comma-separated arguments"""
        if not args_str.strip():
            return []
        
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
                if char in ('"', "'"):
                    in_quotes = True
                    quote_char = char
                elif char == '(':
                    paren_depth += 1
                elif char == ')':
                    paren_depth -= 1
                elif char == '[':
                    bracket_depth += 1
                elif char == ']':
                    bracket_depth -= 1
                elif char == ',' and paren_depth == 0 and bracket_depth == 0:
                    # Found argument separator
                    if current_arg.strip():
                        args.append(self._parse_recursive(current_arg.strip(), df))
                    current_arg = ""
                    i += 1
                    continue
            else:
                if char == quote_char and (i == 0 or args_str[i-1] != '\\'):
                    in_quotes = False
                    quote_char = None
            
            current_arg += char
            i += 1
        
        # Add the last argument
        if current_arg.strip():
            args.append(self._parse_recursive(current_arg.strip(), df))
        
        return args
    
    def _parse_simple_reference(self, expr: str, df: pl.DataFrame) -> TransformationNode:
        """Parse simple references like attr('column') or literals"""
        expr = expr.strip()
        
        # Handle attr('column') references
        attr_match = re.match(r"attr\(\s*['\"](.+?)['\"]\s*\)", expr, re.IGNORECASE)
        if attr_match:
            column_name = attr_match.group(1)
            if column_name not in df.columns:
                raise TransformError(f"Column '{column_name}' not found in data")
            node = TransformationNode('ATTR', [column_name], self.PRECEDENCE['ATTR'])
            self.nodes.append(node)
            return node
        
        # Handle ATTR(column) format
        attr_match = re.match(r"ATTR\(\s*([^)]+)\s*\)", expr, re.IGNORECASE)
        if attr_match:
            column_name = attr_match.group(1).strip()
            if column_name not in df.columns:
                raise TransformError(f"Column '{column_name}' not found in data")
            node = TransformationNode('ATTR', [column_name], self.PRECEDENCE['ATTR'])
            self.nodes.append(node)
            return node
        
        # Handle literals
        if expr.startswith('"') and expr.endswith('"'):
            value = expr[1:-1]
            node = TransformationNode('LIT', [value], self.PRECEDENCE['LIT'])
            self.nodes.append(node)
            return node
        
        if expr.startswith("'") and expr.endswith("'"):
            value = expr[1:-1]
            node = TransformationNode('LIT', [value], self.PRECEDENCE['LIT'])
            self.nodes.append(node)
            return node
        
        # Handle numeric literals
        try:
            if '.' in expr:
                value = float(expr)
            else:
                value = int(expr)
            node = TransformationNode('LIT', [value], self.PRECEDENCE['LIT'])
            self.nodes.append(node)
            return node
        except ValueError:
            pass
        
        # Handle boolean literals
        if expr.lower() in ('true', 'false'):
            value = expr.lower() == 'true'
            node = TransformationNode('LIT', [value], self.PRECEDENCE['LIT'])
            self.nodes.append(node)
            return node
        
        # Default: treat as column reference
        if expr in df.columns:
            node = TransformationNode('ATTR', [expr], self.PRECEDENCE['ATTR'])
            self.nodes.append(node)
            return node
        
        raise TransformError(f"Unable to parse expression: {expr}")
    
    def _build_dependency_graph(self):
        """Build dependency graph based on node relationships"""
        for node in self.nodes:
            for operand in node.operands:
                if isinstance(operand, TransformationNode):
                    node.add_dependency(operand)
    
    def _create_execution_plan(self):
        """Create execution plan using topological sort"""
        # Calculate in-degrees
        in_degree = {node: 0 for node in self.nodes}
        for node in self.nodes:
            for dep in node.dependencies:
                in_degree[node] += 1
        
        # Topological sort
        queue = [node for node in self.nodes if in_degree[node] == 0]
        execution_order = 0
        
        while queue:
            current = queue.pop(0)
            current.execution_order = execution_order
            execution_order += 1
            self.execution_plan.append(current)
            
            # Update dependencies
            for node in self.nodes:
                if current in node.dependencies:
                    in_degree[node] -= 1
                    if in_degree[node] == 0:
                        queue.append(node)
        
        # Check for circular dependencies
        if len(self.execution_plan) != len(self.nodes):
            raise TransformError("Circular dependency detected in transformation expression")
    
    def _execute_plan(self, df: pl.DataFrame) -> pl.Expr:
        """Execute the transformation plan"""
        node_results = {}
        
        for node in self.execution_plan:
            result = self._execute_node(node, df, node_results)
            node_results[node] = result
        
        # Return the result of the last node (root)
        return node_results[self.execution_plan[-1]]
    
    def _execute_node(self, node: TransformationNode, df: pl.DataFrame, node_results: Dict) -> pl.Expr:
        """Execute a single transformation node"""
        operation = node.operation.upper()
        
        # Get operand results
        operands = []
        for operand in node.operands:
            if isinstance(operand, TransformationNode):
                operands.append(node_results[operand])
            else:
                operands.append(operand)
        
        # Execute based on operation type
        if operation == 'ATTR':
            return pl.col(operands[0])
        
        elif operation == 'LIT':
            return pl.lit(operands[0])
        
        elif operation == 'DIRECT':
            return operands[0]
        
        elif operation == 'STRING':
            return self._execute_string_operation(operands)
        
        elif operation == 'MATH':
            return self._execute_math_operation(operands)
        
        elif operation == 'LOGICAL':
            return self._execute_logical_operation(operands)
        
        elif operation == 'DATE':
            return self._execute_date_operation(operands)
        
        elif operation == 'BOOLEAN':
            return self._execute_boolean_operation(operands)
        
        elif operation == 'ARRAY':
            return self._execute_array_operation(operands)
        
        elif operation == 'FILTER' or operation == 'FILTERS':
            return self._execute_filter_operation(operands)
        
        else:
            # Handle direct function calls
            return self._execute_function_call(operation, operands)
    
    def _execute_string_operation(self, operands: List) -> pl.Expr:
        """Execute string operations"""
        if not operands:
            raise TransformError("String operations require operands")
        
        # First operand should be the function name
        function = operands[0].operation if hasattr(operands[0], 'operation') else str(operands[0])
        args = operands[1:] if len(operands) > 1 else []
        
        if function == 'CONCAT':
            if not args:
                raise TransformError("CONCAT requires at least 1 argument")
            return pl.concat_str(args)
        elif function == 'UPPER':
            if not args:
                raise TransformError("UPPER requires 1 argument")
            return args[0].str.to_uppercase()
        elif function == 'LOWER':
            if not args:
                raise TransformError("LOWER requires 1 argument")
            return args[0].str.to_lowercase()
        elif function == 'TRIM':
            if not args:
                raise TransformError("TRIM requires 1 argument")
            return args[0].str.strip_chars()
        elif function == 'LENGTH':
            if not args:
                raise TransformError("LENGTH requires 1 argument")
            return args[0].str.len_chars()
        elif function == 'REPLACE':
            if len(args) < 3:
                raise TransformError("REPLACE requires 3 arguments: string, find, replace")
            return args[0].str.replace_all(args[1], args[2], literal=True)
        elif function == 'SUBSTR':
            if len(args) < 2:
                raise TransformError("SUBSTR requires at least 2 arguments: string, start")
            start = args[1]
            length = args[2] if len(args) > 2 else None
            if length is None:
                return args[0].str.slice(start)
            return args[0].str.slice(start, length)
        elif function == 'ENDSWITH':
            if len(args) < 2:
                raise TransformError("ENDSWITH requires 2 arguments: string, suffix")
            return args[0].str.ends_with(args[1])
        elif function == 'STARTSWITH':
            if len(args) < 2:
                raise TransformError("STARTSWITH requires 2 arguments: string, prefix")
            return args[0].str.starts_with(args[1])
        elif function == 'CONTAINS':
            if len(args) < 2:
                raise TransformError("CONTAINS requires 2 arguments: string, substring")
            return args[0].str.contains(args[1])
        elif function == 'REGEX_MATCH':
            if len(args) < 2:
                raise TransformError("REGEX_MATCH requires 2 arguments: string, pattern")
            return args[0].str.contains(args[1], literal=False)
        else:
            raise TransformError(f"Unknown string function: {function}")
    
    def _execute_math_operation(self, operands: List) -> pl.Expr:
        """Execute math operations"""
        if not operands:
            raise TransformError("Math operations require operands")
        
        function = operands[0].operation if hasattr(operands[0], 'operation') else str(operands[0])
        args = operands[1:] if len(operands) > 1 else []
        
        if function == 'ADD':
            if len(args) < 2:
                raise TransformError("ADD requires 2 arguments")
            return args[0] + args[1]
        elif function == 'SUB':
            if len(args) < 2:
                raise TransformError("SUB requires 2 arguments")
            return args[0] - args[1]
        elif function == 'MUL':
            if len(args) < 2:
                raise TransformError("MUL requires 2 arguments")
            return args[0] * args[1]
        elif function == 'DIV':
            if len(args) < 2:
                raise TransformError("DIV requires 2 arguments")
            return args[0] / args[1]
        elif function == 'MOD':
            if len(args) < 2:
                raise TransformError("MOD requires 2 arguments")
            return args[0] % args[1]
        elif function == 'ROUND':
            if len(args) < 2:
                raise TransformError("ROUND requires 2 arguments: value, precision")
            return args[0].round(int(args[1]))
        elif function == 'ABS':
            if not args:
                raise TransformError("ABS requires 1 argument")
            return args[0].abs()
        else:
            raise TransformError(f"Unknown math function: {function}")
    
    def _execute_logical_operation(self, operands: List) -> pl.Expr:
        """Execute logical operations"""
        if not operands:
            raise TransformError("Logical operations require operands")
        
        function = operands[0].operation if hasattr(operands[0], 'operation') else str(operands[0])
        args = operands[1:] if len(operands) > 1 else []
        
        if function == 'IF':
            if len(args) < 3:
                raise TransformError("IF requires 3 arguments: condition, true_value, false_value")
            return pl.when(args[0]).then(args[1]).otherwise(args[2])
        elif function == 'AND':
            if len(args) < 2:
                raise TransformError("AND requires at least 2 arguments")
            result = args[0]
            for arg in args[1:]:
                result = result & arg
            return result
        elif function == 'OR':
            if len(args) < 2:
                raise TransformError("OR requires at least 2 arguments")
            result = args[0]
            for arg in args[1:]:
                result = result | arg
            return result
        elif function == 'NOT':
            if not args:
                raise TransformError("NOT requires 1 argument")
            return ~args[0]
        else:
            raise TransformError(f"Unknown logical function: {function}")
    
    def _execute_date_operation(self, operands: List) -> pl.Expr:
        """Execute date operations"""
        if not operands:
            raise TransformError("Date operations require operands")
        
        function = operands[0].operation if hasattr(operands[0], 'operation') else str(operands[0])
        args = operands[1:] if len(operands) > 1 else []
        
        if function == 'FORMAT':
            if len(args) < 2:
                raise TransformError("FORMAT requires 2 arguments: date, format")
            return args[0].dt.strftime(args[1])
        elif function == 'PARSE':
            if len(args) < 2:
                raise TransformError("PARSE requires 2 arguments: date_string, format")
            return args[0].str.strptime(pl.Date, args[1], strict=False)
        elif function == 'ADD_DAYS':
            if len(args) < 2:
                raise TransformError("ADD_DAYS requires 2 arguments: date, days")
            return args[0].dt.offset_by(f"{int(args[1])}d")
        elif function == 'SUB_DAYS':
            if len(args) < 2:
                raise TransformError("SUB_DAYS requires 2 arguments: date, days")
            return args[0].dt.offset_by(f"-{int(args[1])}d")
        elif function == 'EXTRACT':
            if len(args) < 2:
                raise TransformError("EXTRACT requires 2 arguments: date, part")
            part = args[1].lower()
            if part == 'year':
                return args[0].dt.year()
            elif part == 'month':
                return args[0].dt.month()
            elif part == 'day':
                return args[0].dt.day()
            else:
                raise TransformError(f"Unknown date part: {part}")
        else:
            raise TransformError(f"Unknown date function: {function}")
    
    def _execute_boolean_operation(self, operands: List) -> pl.Expr:
        """Execute boolean operations"""
        if not operands:
            raise TransformError("Boolean operations require operands")
        
        function = operands[0].operation if hasattr(operands[0], 'operation') else str(operands[0])
        args = operands[1:] if len(operands) > 1 else []
        
        if function == 'EQ' or function == 'EQUALS':
            if len(args) < 2:
                raise TransformError("EQ requires 2 arguments")
            return args[0] == args[1]
        elif function == 'NE' or function == 'NOT_EQUALS':
            if len(args) < 2:
                raise TransformError("NE requires 2 arguments")
            return args[0] != args[1]
        elif function == 'GT' or function == 'GREATER_THAN':
            if len(args) < 2:
                raise TransformError("GT requires 2 arguments")
            return args[0] > args[1]
        elif function == 'LT' or function == 'LESS_THAN':
            if len(args) < 2:
                raise TransformError("LT requires 2 arguments")
            return args[0] < args[1]
        elif function == 'GTE' or function == 'GREATER_OR_EQUAL':
            if len(args) < 2:
                raise TransformError("GTE requires 2 arguments")
            return args[0] >= args[1]
        elif function == 'LTE' or function == 'LESS_OR_EQUAL':
            if len(args) < 2:
                raise TransformError("LTE requires 2 arguments")
            return args[0] <= args[1]
        else:
            raise TransformError(f"Unknown boolean function: {function}")
    
    def _execute_array_operation(self, operands: List) -> pl.Expr:
        """Execute array operations"""
        if not operands:
            raise TransformError("Array operations require operands")
        
        function = operands[0].operation if hasattr(operands[0], 'operation') else str(operands[0])
        args = operands[1:] if len(operands) > 1 else []
        
        if function == 'JOIN':
            if len(args) < 2:
                raise TransformError("JOIN requires 2 arguments: array, delimiter")
            return args[0].str.join(args[1])
        elif function == 'SPLIT':
            if len(args) < 2:
                raise TransformError("SPLIT requires 2 arguments: string, delimiter")
            return args[0].str.split(args[1])
        elif function == 'LENGTH':
            if not args:
                raise TransformError("LENGTH requires 1 argument")
            return args[0].arr.lengths()
        else:
            raise TransformError(f"Unknown array function: {function}")
    
    def _execute_filter_operation(self, operands: List) -> pl.Expr:
        """Execute filter operations"""
        if not operands:
            raise TransformError("Filter operations require operands")
        
        function = operands[0].operation if hasattr(operands[0], 'operation') else str(operands[0])
        args = operands[1:] if len(operands) > 1 else []
        
        if function == 'INCLUDE_IF':
            if not args:
                raise TransformError("INCLUDE_IF requires 1 argument")
            return args[0]
        elif function == 'EXCLUDE_IF':
            if not args:
                raise TransformError("EXCLUDE_IF requires 1 argument")
            return ~args[0]
        elif function == 'LIMIT':
            if not args:
                raise TransformError("LIMIT requires 1 argument")
            return args[0]
        elif function == 'OFFSET':
            if not args:
                raise TransformError("OFFSET requires 1 argument")
            return args[0]
        else:
            raise TransformError(f"Unknown filter function: {function}")
    
    def _execute_function_call(self, function: str, operands: List) -> pl.Expr:
        """Execute direct function calls"""
        if function == 'CONCAT':
            if not operands:
                raise TransformError("CONCAT requires at least 1 argument")
            return pl.concat_str(operands)
        elif function == 'UPPER':
            if not operands:
                raise TransformError("UPPER requires 1 argument")
            return operands[0].str.to_uppercase()
        elif function == 'LOWER':
            if not operands:
                raise TransformError("LOWER requires 1 argument")
            return operands[0].str.to_lowercase()
        elif function == 'TRIM':
            if not operands:
                raise TransformError("TRIM requires 1 argument")
            return operands[0].str.strip_chars()
        elif function == 'ENDSWITH':
            if len(operands) < 2:
                raise TransformError("ENDSWITH requires 2 arguments: string, suffix")
            return operands[0].str.ends_with(operands[1])
        elif function == 'STARTSWITH':
            if len(operands) < 2:
                raise TransformError("STARTSWITH requires 2 arguments: string, prefix")
            return operands[0].str.starts_with(operands[1])
        elif function == 'CONTAINS':
            if len(operands) < 2:
                raise TransformError("CONTAINS requires 2 arguments: string, substring")
            return operands[0].str.contains(operands[1])
        else:
            raise TransformError(f"Unknown function: {function}")

# Removed old mapping functions - only using rules format now

def apply_transformations_from_rules(df: pl.DataFrame, rules: List[Dict], error_handler=None) -> pl.DataFrame:
    """
    Apply transformations to a DataFrame using rules format directly.
    
    Args:
        df: Input Polars DataFrame
        rules: List of rule dictionaries with id, trns, affected_source, affected_target
        error_handler: Optional error handler for detailed error tracking
        
    Returns:
        Transformed Polars DataFrame
    """
    if not rules:
        raise TransformError("Rules list cannot be empty")
    
    # Build expressions for each rule using advanced parser
    select_exprs = []
    
    for rule_index, rule in enumerate(rules):
        try:
            expr = _build_expr_for_rule(df, rule)
            
            # Skip None expressions (filter operations)
            if expr is None:
                continue
                
            target = rule.get('affected_target', f"field_{rule.get('id', 'unknown')}")
            select_exprs.append(expr.alias(target))
            
        except Exception as e:
            if error_handler:
                error_handler.add_error(
                    error_type="TRANSFORMATION_RULE_ERROR",
                    error_message=str(e),
                    line_number=rule_index + 1,
                    column_name=rule.get('affected_target'),
                    transformation_rule=rule,
                    stack_trace=traceback.format_exc()
                )
            raise TransformError(f"Failed to build expression for rule {rule.get('id', rule_index + 1)}: {e}") from e
    
    # Apply transformations
    try:
        # Apply any filters first
        df2 = df
        for rule_index, rule in enumerate(rules):
            if rule.get('trns', '').startswith(('FILTER[', 'FILTERS[')):
                try:
                    df2 = _apply_filter_from_rule(df2, rule)
                except Exception as e:
                    if error_handler:
                        error_handler.add_error(
                            error_type="FILTER_RULE_ERROR",
                            error_message=str(e),
                            line_number=rule_index + 1,
                            column_name=rule.get('affected_target'),
                            transformation_rule=rule,
                            stack_trace=traceback.format_exc()
                        )
                    raise TransformError(f"Failed to apply filter rule {rule.get('id', rule_index + 1)}: {e}") from e
        
        # Apply all transformations
        out = df2.select(select_exprs)
        return out
        
    except Exception as e:
        if error_handler:
            error_handler.add_error(
                error_type="TRANSFORMATION_EXECUTION_ERROR",
                error_message=str(e),
                line_number=None,
                column_name=None,
                transformation_rule=None,
                stack_trace=traceback.format_exc()
            )
        raise TransformError(f"Failed to apply transformations: {e}") from e

def _build_expr_for_rule(df: pl.DataFrame, rule: Dict[str, Any]) -> Optional[pl.Expr]:
    """Build a Polars expression for a single rule using advanced parser"""
    target = rule.get("affected_target")
    source_columns = rule.get("affected_source", [])
    transform = rule.get("trns", "")
    
    # Processing transformation rule
    
    # Ensure source_columns is a list
    if source_columns is None:
        source_columns = []
    
    # Check if source columns exist
    missing_columns = [col for col in source_columns if col not in df.columns]
    
    if missing_columns:
        raise MappingError(f"Source column(s) {missing_columns} not found for rule {rule.get('id', 'unknown')}.")
    
    if transform:
        try:
            # Use advanced transformer for complex expressions
            transformer = AdvancedTransformer()
            return transformer.parse_expression(transform, df)
        except Exception as e:
            raise TransformError(f"Failed to apply transform for rule '{rule.get('id', 'unknown')}': {e}") from e
    else:
        # If no transform, use the first source column
        if source_columns:
            return pl.col(source_columns[0])
        else:
            raise MappingError(f"Rule {rule.get('id', 'unknown')} requires either trns or affected_source.")

def _apply_filter_from_rule(df: pl.DataFrame, rule: Dict[str, Any]) -> pl.DataFrame:
    """Apply a single filter rule to the DataFrame"""
    transform = str(rule.get("trns", "")).strip()
    
    try:
        transformer = AdvancedTransformer()
        expr = transformer.parse_expression(transform, df)
        
        # Check if it's a filter operation
        if rule.get("trns", "").upper().startswith(("FILTER[", "FILTERS[")):
            # Apply the filter
            return df.filter(expr)
        else:
            return df
    except Exception as e:
        raise TransformError(f"Failed to apply FILTER transform for rule {rule.get('id', 'unknown')}: {e}") from e

# Removed old apply_transformations function - only using rules format now