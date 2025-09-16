# ETL Engine Transformation Quick Reference

## 🚀 **API Request Structure**
```json
{
  "source_file_path": "storage/input/file.parquet",
  "source_schema": { "role": "source", "fileType": "csv", "attributes": {...} },
  "target_schema": { "role": "target", "fileType": "json", "attributes": {...} },
  "transformation_mapping": { "rules": [...] }
}
```

## 📝 **Rule Structure**
```json
{
  "id": "rule_1",
  "trns": "OPERATION[METHOD(attr('column'), 'literal')]",
  "affected_source": ["column1", "column2"],
  "affected_target": "target_column"
}
```

## 🎯 **Most Common Patterns**

### **String Operations**
```javascript
// Concatenate with space
STRING[CONCAT(attr('first_name'), ' ', attr('last_name'))]

// Uppercase
STRING[UPPER(attr('name'))]

// Lowercase  
STRING[LOWER(attr('name'))]

// Trim whitespace
STRING[TRIM(attr('text'))]

// Substring (start, length)
STRING[SUBSTR(attr('text'), 0, 5)]

// Replace text
STRING[REPLACE(attr('text'), 'old', 'new')]

// String length
STRING[LENGTH(attr('text'))]
```

### **Math Operations**
```javascript
// Addition
MATH[ADD(attr('price'), attr('tax'))]

// Subtraction
MATH[SUB(attr('total'), attr('discount'))]

// Multiplication
MATH[MUL(attr('price'), attr('quantity'))]

// Division
MATH[DIV(attr('total'), attr('count'))]

// Modulo
MATH[MOD(attr('number'), 10)]

// Round to 2 decimals
MATH[ROUND(attr('price'), 2)]

// Absolute value
MATH[ABS(attr('number'))]
```

### **Logical Operations**
```javascript
// Simple IF
LOGICAL[IF(attr('age') > 18, 'Adult', 'Minor')]

// Multiple conditions with AND
LOGICAL[AND(attr('age') > 18, attr('status') == 'Active')]

// Multiple conditions with OR
LOGICAL[OR(attr('status') == 'Premium', attr('status') == 'VIP')]

// Negation
LOGICAL[NOT(attr('inactive') == true)]

// Nested IF
LOGICAL[IF(attr('age') >= 65, 'Senior', LOGICAL[IF(attr('age') >= 18, 'Adult', 'Minor')])]
```

### **Boolean Comparisons**
```javascript
// Equality
BOOLEAN[EQUALS(attr('email'), attr('verified_email'))]

// Inequality
BOOLEAN[NOT_EQUALS(attr('old_value'), attr('new_value'))]

// Greater than
BOOLEAN[GREATER_THAN(attr('salary'), 50000)]

// Less than
BOOLEAN[LESS_THAN(attr('age'), 65)]

// Greater or equal
BOOLEAN[GREATER_OR_EQUAL(attr('score'), 80)]

// Less or equal
BOOLEAN[LESS_OR_EQUAL(attr('price'), 100)]
```

### **Date Operations**
```javascript
// Format date
DATE[FORMAT(attr('date_col'), 'YYYY-MM-DD')]

// Parse date string
DATE[PARSE(attr('date_str'), 'YYYY-MM-DD')]

// Add days
DATE[ADD_DAYS(attr('start_date'), 30)]

// Subtract days
DATE[SUB_DAYS(attr('end_date'), 7)]

// Days difference
DATE[DIFF_DAYS(attr('end_date'), attr('start_date'))]

// Current date
DATE[CURRENT_DATE()]

// Extract year
DATE[EXTRACT(attr('date'), 'year')]
```

### **Array Operations**
```javascript
// Join array with delimiter
ARRAY[JOIN(attr('tags'), ', ')]

// Split string into array
ARRAY[SPLIT(attr('text'), ',')]

// Array length
ARRAY[LENGTH(attr('array_col'))]

// Get element at index
ARRAY[GET(attr('array_col'), 0)]

// Map function over array
ARRAY[MAP(attr('tags'), 'UPPER')]

// Filter array
ARRAY[FILTER(attr('scores'), '>80')]

// Reduce array
ARRAY[REDUCE(attr('numbers'), 'SUM', 0)]
```

### **Aggregation Operations**
```javascript
// Sum array
AGGREGATION[SUM(attr('sales_array'))]

// Average array
AGGREGATION[AVG(attr('scores'))]

// Minimum value
AGGREGATION[MIN(attr('prices'))]

// Maximum value
AGGREGATION[MAX(attr('scores'))]

// Count elements
AGGREGATION[COUNT(attr('items'))]

// Unique values
AGGREGATION[DISTINCT(attr('categories'))]

// Group by
AGGREGATION[GROUP_BY(attr('sales'), 'region')]
```

## 🔧 **Comparison Operators**
```javascript
>   // Greater than
<   // Less than
>=  // Greater or equal
<=  // Less or equal
==  // Equal to
!=  // Not equal to
```

## 📊 **Literal Values**
```javascript
"Hello World"    // String
'Hello World'    // String (single quotes)
123              // Integer
123.45           // Float
true             // Boolean
false            // Boolean
```

## 🎯 **Common Use Cases**

### **Full Name Creation**
```javascript
STRING[CONCAT(attr('first_name'), ' ', attr('last_name'))]
```

### **Age Category**
```javascript
LOGICAL[IF(attr('age') >= 65, 'Senior', LOGICAL[IF(attr('age') >= 18, 'Adult', 'Minor')])]
```

### **Salary with Bonus**
```javascript
MATH[ADD(attr('base_salary'), attr('bonus'))]
```

### **Conditional Salary**
```javascript
LOGICAL[IF(LOGICAL[AND(attr('performance') > 8, attr('tenure') > 2)], MATH[ADD(attr('salary'), MATH[MUL(attr('salary'), 0.2)])], attr('salary'))]
```

### **Active Senior Check**
```javascript
LOGICAL[AND(attr('age') >= 65, attr('status') == 'Active')]
```

### **Email Validation**
```javascript
BOOLEAN[EQUALS(attr('email'), attr('verified_email'))]
```

### **High Earner Check**
```javascript
BOOLEAN[GREATER_THAN(attr('salary'), 100000)]
```

### **Tenure Calculation**
```javascript
DATE[DIFF_DAYS(attr('end_date'), attr('start_date'))]
```

### **Tags as String**
```javascript
ARRAY[JOIN(attr('tags'), ', ')]
```

## ⚠️ **Common Mistakes**

### **❌ Wrong Quotes**
```javascript
attr("column_name")  // Wrong - double quotes
attr(column_name)    // Wrong - no quotes
```

### **✅ Correct Quotes**
```javascript
attr('column_name')  // Correct - single quotes
ATTR('column_name')  // Also correct - uppercase
```

### **❌ Wrong Boolean**
```javascript
attr('verified') == True     // Wrong - wrong case
attr('verified') == "true"   // Wrong - string instead of boolean
```

### **✅ Correct Boolean**
```javascript
attr('verified') == true     // Correct - lowercase boolean
```

### **❌ Missing Brackets**
```javascript
MATH[ADD(attr('a'), MATH[ADD(attr('b'), attr('c'))]  // Missing closing bracket
```

### **✅ Correct Brackets**
```javascript
MATH[ADD(attr('a'), MATH[ADD(attr('b'), attr('c')))]  // All brackets closed
```

## 🚀 **Multi-Column Support**

### **Functions Supporting Multiple Columns (22/48)**
- `STRING[CONCAT]` - Unlimited columns
- `MATH[ADD/SUB/MUL/DIV]` - 2 columns each
- `LOGICAL[AND/OR/IF]` - Unlimited conditions
- `BOOLEAN[*]` - All support 2-column comparisons
- `DATE[DIFF_DAYS]` - 2 columns
- `ARRAY[JOIN/REDUCE]` - 1 array column
- `AGGREGATION[SUM/AVG/MIN/MAX/COUNT/DISTINCT]` - 1 array column

### **Chaining for More Columns**
```javascript
// Add 3 columns
MATH[ADD(MATH[ADD(attr('a'), attr('b')), attr('c'))]

// Multiple AND conditions
LOGICAL[AND(cond1, LOGICAL[AND(cond2, cond3)])]
```

## 📋 **Complete Example**
```json
{
  "id": "employee_summary",
  "trns": "STRING[CONCAT('Employee: ', attr('first_name'), ' ', attr('last_name'), ' (', LOGICAL[IF(attr('age') >= 65, 'Senior', 'Regular'), ')')]",
  "affected_source": ["first_name", "last_name", "age"],
  "affected_target": "employee_summary"
}
```

This quick reference covers 90% of common transformation needs!
