
class AvrioEndpoints:
    # Base endpoints
    IAM_SIGNIN = "/iam/security/signin"
    MODIFIED_QUERY = "/query-engine/dataDiscovery/getModifiedQuery/v2"
    
    # Dataset endpoints
    DATASETS_BASE = "/core/datasets/{email}"
    DATASETS_DOMAIN = "/core/datasets/{email}/domains/{domain}"
    DATASETS_SUBDOMAIN = "/core/datasets/{email}/domains/{domain}/subDomains/{subdomain}"
    DATASETS_COLUMNS = "/core/datasets/{dataproduct}/{email}/columns"
    
    # Python specific endpoints
    PYTHON_SCHEMAS = "/core/python/schemas/{email}"
    PYTHON_TABLES = "/core/python/tables/{email}"

    # Data sources endpoints
    JDBC_DATASOURCES = "/core/datasource/jdbcDatasources/list/{email}"
    JDBC_SCHEMAS = "/core/datasource/{datasource}/jdbcSchemas/{email}"
    JDBC_TABLES = "/core/datasource/jdbcTables/{catalog}/{schema}/{email}"
    DATASOURCE_COLUMNS = "/access/datasourcePrivilege/getAllColumnsByTableId/{email}/{catalog}/{schema}/{table}"
    
    
   
