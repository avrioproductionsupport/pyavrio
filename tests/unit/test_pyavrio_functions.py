import unittest
from unittest.mock import MagicMock, patch
from pyavrio.pyavrio_functions import PyAvrioFunctions

class TestPyAvrioFunctions(unittest.TestCase):

    def setUp(self):
        # Mock the SQLAlchemy engine for testing purposes
        self.engine = MagicMock()

    def test_get_catalog_names(self):
        # Mock the engine.dialect.get_catalog_names method
        self.engine.dialect.get_catalog_names = MagicMock(return_value=['catalog1', 'catalog2'])
        catalogs = PyAvrioFunctions.get_catalog_names(self.engine)
        self.assertEqual(catalogs, ['catalog1', 'catalog2'])

    def test_get_schema_names(self):
        # Mock the engine.dialect.get_schema_names method
        self.engine.dialect.get_schema_names = MagicMock(return_value=['schema1', 'schema2'])
        schemas = PyAvrioFunctions.get_schema_names(self.engine)
        self.assertEqual(schemas, ['schema1', 'schema2'])

    def test_get_table_names(self):
        # Mock the engine.dialect.get_table_names method
        self.engine.dialect.get_table_names = MagicMock(return_value=['table1', 'table2'])
        tables = PyAvrioFunctions.get_table_names(self.engine)
        self.assertEqual(tables, ['table1', 'table2'])

    def test_get_table_columns(self):
        # Mock the engine.dialect.get_columns method
        self.engine.dialect.get_columns = MagicMock(return_value=[('column1', 'type1'), ('column2', 'type2')])
        columns = PyAvrioFunctions.get_table_columns(self.engine, schema='schema1', table_name='table1')
        self.assertEqual(columns, [('column1', 'type1'), ('column2', 'type2')])

    def test_execute_sql_query(self):
        # Mock the connection.execute method
        mock_result = MagicMock()
        mock_result.fetchall = MagicMock(return_value=[(1, 'John'), (2, 'Doe')])
        self.engine.connect.return_value.__enter__.return_value.execute.return_value = mock_result

        result = PyAvrioFunctions.execute_sql_query(self.engine, 'SELECT * FROM users')
        self.assertEqual(result.fetchall(), [(1, 'John'), (2, 'Doe')])

    

if __name__ == '__main__':
    unittest.main()

