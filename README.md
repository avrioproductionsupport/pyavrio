# PyAvrio Library for Avrio Product

PyAvrio allows you to query and transform data in [Avrio](https://avriodata.ai/) (Data To AI) platform directly without having to download the data locally. This library provides seamless access to the Avrio platform, allowing users to execute SQL queries and retrieve metadata such as catalog names, schema names, table names, and column information.

## Getting Started

### Installation
You can install PyAvrio via pip:

```bash
pip install pyavrio
```

### Usage
To start using PyAvrio, you first need to import the PyAvrioFunctions module:

```python
from pyavrio import PyAvrioFunctions
```

### Connecting to Avrio
To connect to the Avrio platform, use the avrio_engine method:

```python
from pyavrio import PyAvrioFunctions

# Define connection parameters
user_email = "your_email@example.com"
password = "your_password"
host = "host"
port = 1234 
catalog = "your_catalog"
platform = "data_sources"  # Platform should be either "data_products" or "data_sources"

# Establish connection to Avrio
engine = PyAvrioFunctions.avrio_engine(f"pyavrio://{user_email}:{password}@{host}:{port}/{catalog}?platform={platform}")

```

### Using SQL
You can execute SQL queries using the execute_sql_query method:

```python
sql_query = """
    SELECT column1, column2 FROM table_name LIMIT 10
"""

result = PyAvrioFunctions.execute_sql_query(engine, sql_query)
```
Replace sql_query with your desired SQL query string.

### Querying Data
```python
import pandas as pd

# Execute query and store result in DataFrame
df = pd.DataFrame(result, columns=['column1', 'column2'])
print(df.head())

# Perform DataFrame operations
# Example: Filter DataFrame
filtered_df = df[df['column1'] > 100]
print(filtered_df.head())
```
### DataFrame Aggregation
```python
# Example: Aggregating DataFrame
aggregated_df = df.groupby('column1').agg({'column2': 'sum'}).reset_index()
print(aggregated_df.head())
```

### DataFrame Join
```python
sql_query2 = """
    SELECT column3, column4 FROM second_table LIMIT 10
"""
result2 = PyAvrioFunctions.execute_sql_query(engine, sql_query2)
df2 = pd.DataFrame(result2, columns=['column3', 'column4'])

# Join DataFrames
joined_df = df.merge(df2, on='common_column')
print(joined_df.head())
```

### Available Methods
PyAvrio provides the following methods for interacting with the Avrio platform:

- avrio_engine: Connects to the Avrio platform.
- execute_sql_query: Executes SQL queries.
- get_catalog_names: Retrieves catalog names. (Requires platform=data_products for data products or platform=data_sources for data sources). For data products, catalog name represents the domain name, and schema name represents the subdomain name. For data sources, it is similar to Trino catalog and schema.
- get_schema_names: Retrieves schema names. (Requires platform=data_products for data products or platform=data_sources for data sources)
- get_table_names: Retrieves table names. (Requires platform=data_products for data products or platform=data_sources for data sources)
- get_table_columns: Retrieves column information for a specified table. (Requires platform=data_products for data products or platform=data_sources for data sources)

```python
# Retrieve catalog names
catalogs = PyAvrioFunctions.get_catalog_names(engine)
print("Catalogs:", catalogs)

# Retrieve schema names
schemas = PyAvrioFunctions.get_schema_names(engine)
print("Schemas:", schemas)

# Retrieve table names
tables = PyAvrioFunctions.get_table_names(engine, schema='schema_name')
print("Tables:", tables)

# Retrieve columns information for a table
columns_info = PyAvrioFunctions.get_table_columns(engine, schema='schema_name', table_name='table_name')
print("Columns Information:", columns_info)
```
### Supported Operations

DML operations are only supported for Data Sources and not for Data Products, while DDL operations are supported by both Data Sources and Data Products in PyAvrio.

### Example of DML Query
```python
# Example of executing a DML query
dml_query = """
    INSERT INTO table_name (column1, column2) VALUES (value1, value2)
"""

result = PyAvrioFunctions.execute_sql_query(engine, dml_query)
print(result)  

```