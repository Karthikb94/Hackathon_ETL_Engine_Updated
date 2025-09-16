# ETL Engine Transformation Logic Guide

## 📋 **Overview**

This comprehensive guide explains how to structure and send transformation logic to the ETL Engine API. The engine supports multiple transformation formats and provides powerful data manipulation capabilities.

## 🚀 **API Request Structure**

### **Base Request Format**
```json
{
  "source_file_path": "storage/input/your_file.parquet",
  "source_schema": { ... },
  "target_schema": { ... },
  "transformation_mapping": { ... }
}
```

### **Required Fields**
- `source_file_path`: Path to the Parquet file (ONLY .parquet files allowed)
- `source_schema`: Schema defining the source data structure
- `target_schema`: Schema defining the target data structure  
- `transformation_mapping`: Rules defining how to transform data

---

## 📊 **Schema Definitions**

### **Source Schema Structure**
```json
{
  "role": "source",
  "fileType": "csv|json|xml|fixedwidth",
  "schemaId": "schm-csv-1001",
  "schemaName": "customer_csv_v1",
  "attributes": {
    "column_name": {
      "name": "column_name",
      "dataType": "string|integer|float|boolean|date",
      "column_no": 1,
      "start_position": 0,
      "width": 20
    }
  }
}
```

### **Target Schema Structure**
```json
{
  "role": "target", 
  "fileType": "json|csv|xml|fixedwidth",
  "schemaId": "schm-json-2001",
  "schemaName": "customer_json_v1",
  "attributes": {
    "column_name": {
      "name": "column_name",
      "dataType": "string|integer|float|boolean|date",
      "column_no": 1,
      "start_position": 0,
      "width": 20
    }
  }
}
```

### **Schema Field Types**
- **`fileType`**: Original source format (csv, json, xml, fixedwidth) - NOT the current file format
- **`dataType`**: Data type for the column (string, integer, float, boolean, date)
- **`column_no`**: Column position (for CSV/JSON)
- **`start_position`**: Starting position (for Fixed-Width)
- **`width`**: Column width (for Fixed-Width)

---

## 🔧 **Transformation Mapping Formats**

### **Format 1: Rules-Based (Recommended)**
```json
{
  "mappingId": "d98f31c3-7973-4049-a719-a9359bdbfdef",
  "mappingName": "customer_transformation",
  "createdAt": "2025-09-11T07:32:22.113Z",
  "sourceSchemaId": "schm-csv-1001",
  "targetSchemaId": "schm-json-2001",
  "rules": [
    {
      "id": "rule_1",
      "trns": "DIRECT[ATTR('first_name')]",
      "affected_source": ["first_name"],
      "affected_target": "full_name"
    }
  ]
}
```

### **Format 2: Legacy Mappings (Deprecated)**
```json
{
  "mappings": {
    "column_name": "transformation_expression"
  }
}
```

---

## 🎯 **Transformation Expression Syntax**

### **Supported Syntax Formats**

#### **1. Direct Field Reference**
```
DIRECT[ATTR('column_name')]
DIRECT[attr('column_name')]
```

#### **2. Simple Function Calls**
```
STRING[UPPER(attr('column_name'))]
MATH[ADD(attr('col1'), attr('col2'))]
DATE[FORMAT(attr('date_col'), 'YYYY-MM-DD')]
```

#### **3. Complex Nested Operations**
```
LOGICAL[IF(attr('age') > 18, 'Adult', 'Minor')]
MATH[ADD(MATH[ADD(attr('salary'), attr('bonus'))], attr('commission'))]
```

#### **4. OPERATION[METHOD()] Format (Specification Compliant)**
```
MATH[ADD(attr('price'), 100)]
STRING[CONCAT(attr('first_name'), ' ', attr('last_name'))]
LOGICAL[AND(attr('age') > 18, attr('status') == 'Active')]
```

---

## 📚 **Complete Operation Reference**

### **MATH Operations (7/7)**
| Operation | Syntax | Description | Multi-Column |
|-----------|--------|-------------|--------------|
| ADD | `MATH[ADD(attr('col1'), attr('col2'))]` | Addition | ✅ 2 columns |
| SUB | `MATH[SUB(attr('total'), attr('discount'))]` | Subtraction | ✅ 2 columns |
| MUL | `MATH[MUL(attr('price'), attr('quantity'))]` | Multiplication | ✅ 2 columns |
| DIV | `MATH[DIV(attr('total'), attr('count'))]` | Division | ✅ 2 columns |
| MOD | `MATH[MOD(attr('number'), 10)]` | Modulo | ❌ 2 columns |
| ROUND | `MATH[ROUND(attr('price'), 2)]` | Round to decimals | ❌ 1 column |
| ABS | `MATH[ABS(attr('number'))]` | Absolute value | ❌ 1 column |

### **STRING Operations (7/7)**
| Operation | Syntax | Description | Multi-Column |
|-----------|--------|-------------|--------------|
| CONCAT | `STRING[CONCAT(attr('col1'), ' ', attr('col2'))]` | Concatenate | ✅ Unlimited |
| UPPER | `STRING[UPPER(attr('name'))]` | Uppercase | ❌ 1 column |
| LOWER | `STRING[LOWER(attr('name'))]` | Lowercase | ❌ 1 column |
| TRIM | `STRING[TRIM(attr('text'))]` | Trim whitespace | ❌ 1 column |
| SUBSTR | `STRING[SUBSTR(attr('text'), 0, 5)]` | Substring | ❌ 1 column |
| REPLACE | `STRING[REPLACE(attr('text'), 'old', 'new')]` | Replace text | ❌ 1 column |
| LENGTH | `STRING[LENGTH(attr('text'))]` | String length | ❌ 1 column |

### **LOGICAL Operations (4/4)**
| Operation | Syntax | Description | Multi-Column |
|-----------|--------|-------------|--------------|
| IF | `LOGICAL[IF(condition, 'true_value', 'false_value')]` | Conditional | ✅ Unlimited |
| AND | `LOGICAL[AND(cond1, cond2, cond3)]` | Logical AND | ✅ Unlimited |
| OR | `LOGICAL[OR(cond1, cond2, cond3)]` | Logical OR | ✅ Unlimited |
| NOT | `LOGICAL[NOT(condition)]` | Logical NOT | ❌ 1 column |

### **BOOLEAN Operations (6/6)**
| Operation | Syntax | Description | Multi-Column |
|-----------|--------|-------------|--------------|
| EQUALS | `BOOLEAN[EQUALS(attr('col1'), attr('col2'))]` | Equality | ✅ 2 columns |
| NOT_EQUALS | `BOOLEAN[NOT_EQUALS(attr('col1'), attr('col2'))]` | Inequality | ✅ 2 columns |
| GREATER_THAN | `BOOLEAN[GREATER_THAN(attr('age'), 18)]` | Greater than | ✅ 2 columns |
| LESS_THAN | `BOOLEAN[LESS_THAN(attr('age'), 65)]` | Less than | ✅ 2 columns |
| GREATER_OR_EQUAL | `BOOLEAN[GREATER_OR_EQUAL(attr('score'), 80)]` | Greater or equal | ✅ 2 columns |
| LESS_OR_EQUAL | `BOOLEAN[LESS_OR_EQUAL(attr('price'), 100)]` | Less or equal | ✅ 2 columns |

### **DATE Operations (7/7)**
| Operation | Syntax | Description | Multi-Column |
|-----------|--------|-------------|--------------|
| FORMAT | `DATE[FORMAT(attr('date_col'), 'YYYY-MM-DD')]` | Format date | ❌ 1 column |
| PARSE | `DATE[PARSE(attr('date_str'), 'YYYY-MM-DD')]` | Parse date | ❌ 1 column |
| ADD_DAYS | `DATE[ADD_DAYS(attr('date'), 30)]` | Add days | ❌ 1 column |
| SUB_DAYS | `DATE[SUB_DAYS(attr('date'), 7)]` | Subtract days | ❌ 1 column |
| DIFF_DAYS | `DATE[DIFF_DAYS(attr('end_date'), attr('start_date'))]` | Days difference | ✅ 2 columns |
| CURRENT_DATE | `DATE[CURRENT_DATE()]` | Current date | ❌ 0 columns |
| EXTRACT | `DATE[EXTRACT(attr('date'), 'year')]` | Extract part | ❌ 1 column |

### **ARRAY Operations (7/7)**
| Operation | Syntax | Description | Multi-Column |
|-----------|--------|-------------|--------------|
| JOIN | `ARRAY[JOIN(attr('tags'), ',')]` | Join array | ❌ 1 array |
| SPLIT | `ARRAY[SPLIT(attr('text'), ',')]` | Split string | ❌ 1 column |
| LENGTH | `ARRAY[LENGTH(attr('array_col'))]` | Array length | ❌ 1 array |
| GET | `ARRAY[GET(attr('array_col'), 0)]` | Get element | ❌ 1 array |
| MAP | `ARRAY[MAP(attr('array_col'), 'UPPER')]` | Map function | ❌ 1 array |
| FILTER | `ARRAY[FILTER(attr('array_col'), 'value')]` | Filter array | ❌ 1 array |
| REDUCE | `ARRAY[REDUCE(attr('array_col'), 'SUM', 0)]` | Reduce array | ❌ 1 array |

### **AGGREGATION Operations (7/7)**
| Operation | Syntax | Description | Multi-Column |
|-----------|--------|-------------|--------------|
| SUM | `AGGREGATION[SUM(attr('array_col'))]` | Sum values | ❌ 1 array |
| AVG | `AGGREGATION[AVG(attr('array_col'))]` | Average values | ❌ 1 array |
| MIN | `AGGREGATION[MIN(attr('array_col'))]` | Minimum value | ❌ 1 array |
| MAX | `AGGREGATION[MAX(attr('array_col'))]` | Maximum value | ❌ 1 array |
| COUNT | `AGGREGATION[COUNT(attr('array_col'))]` | Count elements | ❌ 1 array |
| GROUP_BY | `AGGREGATION[GROUP_BY(attr('array_col'), 'key')]` | Group by key | ❌ 1 array |
| DISTINCT | `AGGREGATION[DISTINCT(attr('array_col'))]` | Unique values | ❌ 1 array |

### **FILTERS Operations (4/4)**
| Operation | Syntax | Description | Multi-Column |
|-----------|--------|-------------|--------------|
| INCLUDE_IF | `FILTERS[INCLUDE_IF(condition)]` | Include rows | ❌ 1 condition |
| EXCLUDE_IF | `FILTERS[EXCLUDE_IF(condition)]` | Exclude rows | ❌ 1 condition |
| LIMIT | `FILTERS[LIMIT(100)]` | Limit rows | ❌ 0 columns |
| OFFSET | `FILTERS[OFFSET(50)]` | Skip rows | ❌ 0 columns |

---

## 💡 **Advanced Examples**

### **Example 1: Complex String Concatenation**
```json
{
  "id": "full_name_rule",
  "trns": "STRING[CONCAT(attr('first_name'), ' ', attr('last_name'), ' (', attr('status'), ')')]",
  "affected_source": ["first_name", "last_name", "status"],
  "affected_target": "full_name"
}
```

### **Example 2: Conditional Salary Calculation**
```json
{
  "id": "salary_rule",
  "trns": "LOGICAL[IF(LOGICAL[AND(attr('age') > 25, attr('status') == 'Active')], MATH[ADD(attr('salary'), attr('bonus'))], attr('salary'))]",
  "affected_source": ["age", "status", "salary", "bonus"],
  "affected_target": "final_salary"
}
```

### **Example 3: Date Processing**
```json
{
  "id": "tenure_rule",
  "trns": "DATE[DIFF_DAYS(attr('end_date'), attr('start_date'))]",
  "affected_source": ["end_date", "start_date"],
  "affected_target": "tenure_days"
}
```

### **Example 4: Nested Logical Operations**
```json
{
  "id": "eligibility_rule",
  "trns": "LOGICAL[IF(LOGICAL[AND(attr('age') >= 18, attr('verified') == true, attr('status') == 'Active')], 'Eligible', 'Not Eligible')]",
  "affected_source": ["age", "verified", "status"],
  "affected_target": "eligibility"
}
```

---

## 🔍 **Comparison Operators**

### **Supported Operators**
- `>` - Greater than
- `<` - Less than
- `>=` - Greater than or equal
- `<=` - Less than or equal
- `==` - Equal to
- `!=` - Not equal to

### **Usage in Conditions**
```
attr('age') > 18
attr('status') == 'Active'
attr('price') >= 100.50
attr('verified') == true
attr('count') != 0
```

---

## 📝 **Literal Values**

### **String Literals**
```
"Hello World"
'Hello World'
```

### **Numeric Literals**
```
123          # Integer
123.45       # Float
```

### **Boolean Literals**
```
true
false
```

### **Date Literals**
```
"2024-01-15"
"2024-01-15 10:30:00"
```

---

## ⚠️ **Common Pitfalls & Best Practices**

### **1. JSON Escaping**
❌ **Wrong:**
```json
"trns": "STRING[CONCAT(attr(\"first_name\"), \" \", attr(\"last_name\"))]"
```

✅ **Correct:**
```json
"trns": "STRING[CONCAT(attr('first_name'), ' ', attr('last_name'))]"
```

### **2. Column References**
❌ **Wrong:**
```
attr(first_name)     # Missing quotes
attr("first_name")   # Wrong quotes
```

✅ **Correct:**
```
attr('first_name')   # Single quotes
ATTR('first_name')   # Uppercase also works
```

### **3. Nested Operations**
❌ **Wrong:**
```
MATH[ADD(attr('a'), MATH[ADD(attr('b'), attr('c'))]  # Missing closing bracket
```

✅ **Correct:**
```
MATH[ADD(attr('a'), MATH[ADD(attr('b'), attr('c')))]
```

### **4. Boolean Comparisons**
❌ **Wrong:**
```
attr('verified') == True    # Wrong case
attr('verified') == "true"  # String instead of boolean
```

✅ **Correct:**
```
attr('verified') == true    # Lowercase boolean
```

---

## 🚀 **Complete Example Request**

```json
{
  "source_file_path": "storage/input/customers.parquet",
  "source_schema": {
    "role": "source",
    "fileType": "csv",
    "schemaId": "schm-csv-1001",
    "schemaName": "customer_csv_v1",
    "attributes": {
      "first_name": {
        "name": "first_name",
        "dataType": "string",
        "column_no": 1
      },
      "last_name": {
        "name": "last_name", 
        "dataType": "string",
        "column_no": 2
      },
      "age": {
        "name": "age",
        "dataType": "integer",
        "column_no": 3
      },
      "salary": {
        "name": "salary",
        "dataType": "float",
        "column_no": 4
      },
      "status": {
        "name": "status",
        "dataType": "string",
        "column_no": 5
      }
    }
  },
  "target_schema": {
    "role": "target",
    "fileType": "json",
    "schemaId": "schm-json-2001", 
    "schemaName": "customer_json_v1",
    "attributes": {
      "full_name": {
        "name": "full_name",
        "dataType": "string"
      },
      "age_group": {
        "name": "age_group",
        "dataType": "string"
      },
      "salary_plus_bonus": {
        "name": "salary_plus_bonus",
        "dataType": "float"
      },
      "is_senior": {
        "name": "is_senior",
        "dataType": "boolean"
      }
    }
  },
  "transformation_mapping": {
    "mappingId": "d98f31c3-7973-4049-a719-a9359bdbfdef",
    "mappingName": "customer_transformation",
    "createdAt": "2025-09-11T07:32:22.113Z",
    "sourceSchemaId": "schm-csv-1001",
    "targetSchemaId": "schm-json-2001",
    "rules": [
      {
        "id": "rule_1",
        "trns": "STRING[CONCAT(attr('first_name'), ' ', attr('last_name'))]",
        "affected_source": ["first_name", "last_name"],
        "affected_target": "full_name"
      },
      {
        "id": "rule_2", 
        "trns": "LOGICAL[IF(attr('age') >= 65, 'Senior', LOGICAL[IF(attr('age') >= 18, 'Adult', 'Minor')])]",
        "affected_source": ["age"],
        "affected_target": "age_group"
      },
      {
        "id": "rule_3",
        "trns": "MATH[ADD(attr('salary'), MATH[MUL(attr('salary'), 0.1)])]",
        "affected_source": ["salary"],
        "affected_target": "salary_plus_bonus"
      },
      {
        "id": "rule_4",
        "trns": "LOGICAL[AND(attr('age') >= 65, attr('status') == 'Active')]",
        "affected_source": ["age", "status"],
        "affected_target": "is_senior"
      }
    ]
  }
}
```

---

## 📊 **Multi-Column Support Summary**

| Category | Multi-Column Functions | Single-Column Functions | Total |
|----------|----------------------|------------------------|-------|
| STRING | 1/7 (14%) | 6/7 (86%) | 7 |
| MATH | 4/7 (57%) | 3/7 (43%) | 7 |
| LOGICAL | 3/4 (75%) | 1/4 (25%) | 4 |
| BOOLEAN | 6/6 (100%) | 0/6 (0%) | 6 |
| DATE | 1/7 (14%) | 6/7 (86%) | 7 |
| ARRAY | 2/7 (29%) | 5/7 (71%) | 7 |
| AGGREGATION | 5/7 (71%) | 2/7 (29%) | 7 |
| FILTERS | 0/4 (0%) | 4/4 (100%) | 4 |
| **TOTAL** | **22/48 (46%)** | **26/48 (54%)** | **48** |

---

## 🎯 **Quick Reference**

### **Most Flexible Operations**
- `STRING[CONCAT]` - Unlimited columns
- `LOGICAL[AND/OR]` - Unlimited conditions  
- `LOGICAL[IF]` - Complex nested conditions
- `BOOLEAN[*]` - All support 2-column comparisons

### **Chaining Operations**
```
MATH[ADD(MATH[ADD(attr('a'), attr('b')), attr('c'))]
LOGICAL[IF(LOGICAL[AND(cond1, cond2)], value1, value2)]
```

### **Common Patterns**
- **Full Name**: `STRING[CONCAT(attr('first'), ' ', attr('last'))]`
- **Age Group**: `LOGICAL[IF(attr('age') >= 65, 'Senior', 'Adult')]`
- **Salary with Bonus**: `MATH[ADD(attr('salary'), attr('bonus'))]`
- **Active Senior**: `LOGICAL[AND(attr('age') >= 65, attr('status') == 'Active')]`

This guide provides everything you need to effectively use the ETL Engine's transformation capabilities!
