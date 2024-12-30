import pytest
from sql_metadata import Parser
from pyavrio.query_parser import QueryParser

class TestQueryParser:
    
    # Tests for parse_query method
    @pytest.mark.parametrize(
        "query, platform, expected_result", [
            ("", None, False),  # Empty query
            ("select 1", None, True),  # Valid query in COMPATIBILITY_QUERIES
            ("select 2", None, True),  # Valid query in COMPATIBILITY_QUERIES
            ("select 3", None, True),  # Valid query in COMPATIBILITY_QUERIES
            ("select * from table", None, False),  # Query that doesn't match compatibility
            ("alter table table_name", None, True),  # Valid alter query
            ("update table_name set col = 1", None, False),  # Invalid query
            ("select 1", "data_products", True),  # Valid query with platform
        ]
    )
    def test_parse_query(self, query, platform, expected_result):
        result = QueryParser.parse_query(query, platform)
        assert result == expected_result
    
    # Tests for remove_schema_from_query method
    @pytest.mark.parametrize(
        "query, platform, expected_query", [
            ("select * from schema.table", "data_products", "select * from table"),  # Schema should be removed
            ("select * from table", "data_products", "select * from table"),  # No schema to remove
            ("select * from schema.table", "other_platform", "select * from schema.table"),  # Platform doesn't match
            ("select * from schema1.table1, schema2.table2", "data_products", "select * from table1, table2"),  # Multiple tables with schemas
            ("select * from schema1.table1, schema2.table2", "other_platform", "select * from schema1.table1, schema2.table2"),  # Platform doesn't match
        ]
    )
    def test_remove_schema_from_query(self, query, platform, expected_query):
        result = QueryParser.remove_schema_from_query(query, platform)
        assert result == expected_query
