import unittest
from unittest.mock import MagicMock, patch, Mock, TestCase, mock
from pyavrio.dbapi import (
    Connection,
    Cursor,
    TimeBoundLRUCache,
    DBAPITypeObject,
    Binary,
    Date,
    Time,
    Timestamp,
    Decimal,
    IsolationLevel,
    DescribeOutput,
    ColumnDescription,
    pyavrio,
    STRING, BINARY, NUMBER, DATETIME
)
from datetime import datetime, timedelta, timezone, time, date
from zoneinfo import ZoneInfo
from decimal import Decimal
from time import sleep
from collections import OrderedDict
from threading import Thread

class TestTrinoDBAPIModule(unittest.TestCase):

    def test_connection_creation(self):
        with patch('pyavrio.dbapi.pyavrio.client.ClientSession') as mock_client_session:
            # Mocking auth parameter to have a token attribute
            mock_auth = MagicMock()
            mock_auth.token = 'mock_token_value'
            connection = Connection(
                host='example.com',
                port=8080,
                auth=mock_auth
                
            )
            self.assertIsInstance(connection, Connection)

            # Update the expected call with the correct parameter values
            mock_client_session.assert_called_with(
                user=None,
                catalog=None,  # Update to match actual behavior
                schema=None,  # Update to match actual behavior
                source='trino-python-client',
                properties=None,
                headers=None,
                transaction_id='NONE',  # Update to match actual behavior
                extra_credential=None,
                client_tags=None,
                roles=None,
                timezone=None,
                platform=None,
                access_token='mock_token_value'  # Ensure the correct token value is passed
            )

    @patch('pyavrio.dbapi.time')
    def test_cache_expiry(self, mock_time):
        # Test cache expiration
        mock_time.return_value = 0
        cache = TimeBoundLRUCache(capacity=2, ttl_seconds=1)
        cache.put('key1', 'value1')
        cache.put('key2', 'value2')
        mock_time.return_value = 2
        self.assertIsNone(cache.get('key1'))
        self.assertEqual(cache.get('key2'), None)

    def test_data_types(self):
        # Test data type conversions
        self.assertEqual(Binary('hello'), b'hello')
        self.assertIsInstance(Date(2024, 4, 1), Date)
        self.assertIsInstance(Time(12, 30, 0), Time)
        self.assertIsInstance(Timestamp(2024, 4, 1, 12, 30), Timestamp)
        self.assertIsInstance(Decimal('10.5'), Decimal)

    def test_dbapi_type_object(self):
        # Test DBAPITypeObject equality
        string_type = DBAPITypeObject('VARCHAR', 'CHAR')
        self.assertEqual(string_type, 'varchar')
        self.assertNotEqual(string_type, 'int')

    def test_describe_output(self):
        # Test DescribeOutput named tuple creation
        row_data = ['name', 'catalog', 'schema', 'table', 'type', 10, True]
        describe_output = DescribeOutput.from_row(row_data)
        self.assertEqual(describe_output.name, 'name')
        self.assertEqual(describe_output.catalog, 'catalog')
        self.assertEqual(describe_output.schema, 'schema')
        self.assertEqual(describe_output.table, 'table')
        self.assertEqual(describe_output.type, 'type')
        self.assertEqual(describe_output.type_size, 10)
        self.assertTrue(describe_output.aliased)

    def test_column_description(self):
        # Test ColumnDescription named tuple creation
        column_data = {
            'name': 'column_name',
            'type': 'int',
            'typeSignature': {'rawType': 'INTEGER', 'arguments': [{'value': 10}]},
        }
        column_desc = ColumnDescription.from_column(column_data)
        self.assertEqual(column_desc.name, 'column_name')
        self.assertEqual(column_desc.type_code, 'int')
        self.assertIsNone(column_desc.display_size)
        self.assertEqual(column_desc.internal_size, None)
        self.assertIsNone(column_desc.precision)
        self.assertIsNone(column_desc.scale)
        self.assertFalse(column_desc.null_ok)

class TestConnection(unittest.TestCase):
    
    def setUp(self):
        self.connection = Connection('localhost')
        
    
       
    def tearDown(self):
        self.connection.close()


class ConnectionMock:
    def __init__(self):
        self._create_request = Mock(return_value=Mock())

class TestCursor(unittest.TestCase):

    def setUp(self):
        # Mocking a connection object for testing purposes
        self.mock_connection = ConnectionMock()
        self.cursor = Cursor(self.mock_connection, "SELECT * FROM table")

    def test_connection_is_set_correctly(self):
        self.assertEqual(self.cursor.connection, self.mock_connection)

    def test_description_returns_expected_values(self):
        # Mocking a query object for testing purposes
        mock_query = Mock()
        mock_query.columns = [
            ("column1", "VARCHAR"),
            ("column2", "INTEGER"),
            ("column3", "TIMESTAMP"),
        ]
        self.cursor._query = mock_query

        expected_description = [
            ("column1", STRING),
            ("column2", NUMBER),
            ("column3", DATETIME),
        ]
        self.assertEqual(self.cursor.description, expected_description)

    def setUp(self):
        # Create a mock instance of the class containing the execute method
        self.mock_instance = MagicMock()
        self.mock_instance.connection._use_legacy_prepared_statements.return_value = False
        self.mock_instance._execute_immediate_statement = MagicMock()
        self.mock_instance._execute_prepared_statement = MagicMock()
        self.mock_instance._deallocate_prepared_statement = MagicMock()
        self.mock_instance._query = MagicMock()
        self.mock_instance._query.execute = MagicMock(return_value=iter([1, 2, 3]))  # Mock query execution
        self.mock_instance._generate_unique_statement_name = MagicMock(return_value="stmt_1")

    @patch("pyavrio.client.TrinoQuery")  # Mock TrinoQuery for non-prepared statements
    def test_execute_without_params(self, MockTrinoQuery):
        # Test when params is None
        mock_request = MagicMock()
        self.mock_instance._request = mock_request
        self.mock_instance._legacy_primitive_types = False

        operation = "SELECT * FROM test_table"
        MockTrinoQuery.return_value = self.mock_instance._query

        result = self.mock_instance.execute(operation)

        # Assertions for TrinoQuery initialization
        MockTrinoQuery.assert_called_once_with(mock_request, query=operation, legacy_primitive_types=False)

        # Assertions for query execution
        self.assertEqual(list(result), [1, 2, 3])
        self.mock_instance._query.execute.assert_called_once()

    def test_execute_with_params_legacy(self):
        # Test with params and legacy prepared statements
        self.mock_instance.connection._use_legacy_prepared_statements.return_value = True

        operation = "SELECT * FROM test_table WHERE id = ?"
        params = [1]

        result = self.mock_instance.execute(operation, params)

        # Assertions for statement preparation and execution
        self.mock_instance._prepare_statement.assert_called_once_with(operation, "stmt_1")
        self.mock_instance._execute_prepared_statement.assert_called_once_with("stmt_1", params)
        self.mock_instance._deallocate_prepared_statement.assert_called_once_with("stmt_1")
        self.assertEqual(list(result), [1, 2, 3])

    def test_execute_with_invalid_params(self):
        # Test with invalid params type (should raise AssertionError)
        operation = "SELECT * FROM test_table WHERE id = ?"
        params = {"id": 1}  # Invalid type (dict)

        with self.assertRaises(AssertionError) as context:
            self.mock_instance.execute(operation, params)

        self.assertIn("params must be a list or tuple containing the query parameter values", str(context.exception))

    def test_execute_with_params_non_legacy(self):
        # Test with params and non-legacy prepared statements
        self.mock_instance.connection._use_legacy_prepared_statements.return_value = False

        operation = "SELECT * FROM test_table WHERE id = ?"
        params = [1]

        result = self.mock_instance.execute(operation, params)

        # Assertions for immediate statement execution
        self.mock_instance._execute_immediate_statement.assert_called_once_with(operation, params)
        self.mock_instance._query.execute.assert_called_once()
        self.assertEqual(list(result), [1, 2, 3])

class TestCursor(unittest.TestCase):
    def setUp(self):
        # Mock the Connection class and create a mock connection object
        self.mock_connection = MagicMock(spec=Connection)
        self.cursor = Cursor(self.mock_connection, MagicMock())

    def test_execute(self):
        # Mock the behavior of the execute method
        with patch.object(self.cursor._query, 'execute'):
            self.cursor._iterator = iter([[1, 'foo'], [2, 'bar']])
            self.cursor.execute("SELECT * FROM table")
            result = self.cursor.fetchone()
            self.assertEqual(result, [1, 'foo'])

    def test_executemany(self):
        # Mock the behavior of the execute method
        with patch.object(self.cursor._query, 'execute'):
            self.cursor._iterator = iter([[1], [2]])
            self.cursor.executemany("INSERT INTO table VALUES (?)", [[1], [2]])
            result = self.cursor.fetchall()
            self.assertEqual(result, [[1], [2]])

    def test_fetchone(self):
        # Mock the iterator to return a sequence of results
        self.cursor._iterator = iter([[1], [2], [3]])

        # Fetch one row at a time and check if the results are as expected
        result1 = self.cursor.fetchone()
        result2 = self.cursor.fetchone()
        result3 = self.cursor.fetchone()
        result4 = self.cursor.fetchone()

        self.assertEqual(result1, [1])
        self.assertEqual(result2, [2])
        self.assertEqual(result3, [3])
        self.assertIsNone(result4)  # No more rows available

    def test_fetchmany(self):
        # Mock the iterator to return a sequence of results
        self.cursor._iterator = iter([[1], [2], [3]])

        # Fetch multiple rows and check if the results are as expected
        result1 = self.cursor.fetchmany(2)
        result2 = self.cursor.fetchmany(2)
        result3 = self.cursor.fetchmany(2)

        self.assertEqual(result1, [[1], [2]])
        self.assertEqual(result2, [[3]])
        self.assertEqual(result3, [])

    def test_fetchall(self):
        # Mock the iterator to return a sequence of results
        self.cursor._iterator = iter([[1], [2], [3]])

        # Fetch all rows and check if the results are as expected
        result = self.cursor.fetchall()
        self.assertEqual(result, [[1], [2], [3]])

    def test_describe(self):
        # Mock the behavior of the describe method
        with patch.object(self.cursor._query, 'execute', return_value=[["col1", "INTEGER"], ["col2", "VARCHAR"]]):
            result = self.cursor.describe("SELECT * FROM table")
            self.assertEqual(result, [["col1", "INTEGER"], ["col2", "VARCHAR"]])
class TestTimeBoundLRUCache(unittest.TestCase):
    def test_cache_put_get(self):
        cache = TimeBoundLRUCache(2, 1)  # Capacity 2, TTL 1 second

        # Insert items into the cache
        cache.put(1, 'a')
        cache.put(2, 'b')

        # Access the items immediately after insertion
        self.assertEqual(cache.get(1), 'a')
        self.assertEqual(cache.get(2), 'b')

        # Wait for TTL to expire
        sleep(1)

        # Access the items after TTL expiration
        self.assertIsNone(cache.get(1))
        self.assertIsNone(cache.get(2))

    def test_cache_eviction(self):
        cache = TimeBoundLRUCache(2, 1)  # Capacity 2, TTL 1 second

        # Insert items into the cache
        cache.put(1, 'a')
        cache.put(2, 'b')

        # Access an item to trigger LRU eviction
        cache.get(1)

        # Insert a new item, forcing eviction due to capacity
        cache.put(3, 'c')

        # Check that the evicted item is no longer in the cache
        self.assertIsNone(cache.get(2))

    def test_cache_concurrency(self):
        cache = TimeBoundLRUCache(2, 1)  # Capacity 2, TTL 1 second

        # Helper function to access cache concurrently
        def concurrent_access(key, expected_value):
            sleep(0.5)  # Ensure some delay for TTL to expire
            value = cache.get(key)
            self.assertEqual(value, expected_value)

        # Insert items into the cache
        cache.put(1, 'a')
        cache.put(2, 'b')

        # Concurrently access items to test thread safety
        thread1 = Thread(target=concurrent_access, args=(1, 'a'))
        thread2 = Thread(target=concurrent_access, args=(2, 'b'))
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()


class TestCursor(unittest.TestCase):
    def setUp(self):
        # Create a mock Connection object with a token attribute
        self.mock_connection = Mock(spec=Connection, token='example_token')
        self.request = Mock()
        self.cursor = Cursor(self.mock_connection, self.request)
        self.mock_iterator = Mock()

        # Create a Cursor object with the mock objects
        self.cursor = Cursor(self.mock_connection, Mock())
        self.cursor._iterator = self.mock_iterator
    def test_connection_type(self):
        self.assertIsInstance(self.cursor.connection, Connection)

    def test_info_uri(self):
        # Mock _query to have an info_uri attribute
        self.cursor._query = Mock(info_uri='http://example.com')
        self.assertEqual(self.cursor.info_uri, 'http://example.com')

    def test_update_type(self):
        # Mock _query to have an update_type attribute
        self.cursor._query = Mock(update_type='UPDATE')
        self.assertEqual(self.cursor.update_type, 'UPDATE')
    def test_init_with_valid_connection(self):
        # Create a mock Connection object
        mock_connection = Mock(spec=Connection)
        request = Mock()

        # Initialize Cursor with the mock Connection
        cursor = Cursor(mock_connection, request)

        # Check that the connection attribute is set correctly
        self.assertEqual(cursor._connection, mock_connection)

        # Check that the request attribute is set correctly
        self.assertEqual(cursor._request, request)

        # Check default values of other attributes
        self.assertEqual(cursor.arraysize, 1)
        self.assertIsNone(cursor._iterator)
        self.assertIsNone(cursor._query)
        self.assertFalse(cursor._legacy_primitive_types)

    def test_init_with_invalid_connection(self):
        # Create a mock object that is not an instance of Connection
        invalid_connection = Mock()

        # Attempt to initialize Cursor with the invalid connection
        with self.assertRaises(ValueError) as context:
            Cursor(invalid_connection, Mock())

        # Check that the ValueError is raised with the correct message
        self.assertIn("connection must be a Connection object", str(context.exception))
        
    def test_iter_property(self):
        # Call the __iter__ method using the property
        iterator = self.cursor.__iter__()

        # Check that the returned iterator is the same as the mock iterator
        self.assertEqual(iterator, self.mock_iterator)

    def test_connection_property(self):
        # Call the connection property to get the connection object
        connection = self.cursor.connection

        # Check that the returned connection object is the same as the mock connection
        self.assertEqual(connection, self.mock_connection)


class TestCursorFetchOne(TestCase):
    def test_fetchone_returns_row(self):
        # Mock the Connection class
        mock_connection = mock.MagicMock(spec=Connection)
        mock_cursor = Cursor(connection=mock_connection, request=None)
        
        # Mock the _iterator attribute of the Cursor class
        mock_cursor._iterator = iter([['value1', 'value2']])

        # Call the fetchone method
        result = mock_cursor.fetchone()

        # Check if fetchone returns the correct row
        self.assertEqual(result, ['value1', 'value2'])

    def test_fetchone_returns_none(self):
        # Mock the Connection class
        mock_connection = mock.MagicMock(spec=Connection)
        mock_cursor = Cursor(connection=mock_connection, request=None)
        
        # Mock the _iterator attribute of the Cursor class
        mock_cursor._iterator = iter([])  # Empty iterator to simulate no more data

        # Call the fetchone method
        result = mock_cursor.fetchone()

        # Check if fetchone returns None when no more data is available
        self.assertIsNone(result)

mock_connection = Mock(spec=Connection)
mock_request = Mock()

class TestYourClass(unittest.TestCase):
    def setUp(self):
        # Create a mock object for _query
        self.mock_query = Mock()
        
        self.mock_query.columns = [{'name': 'column1'}, {'name': 'column2'}]
        self.mock_query.update_count = 10
        self.mock_query.stats = {'execution_time': 100}
        self.mock_query.query_id = '12345'
        self.mock_query.query = 'SELECT * FROM table'
        self.mock_query.warnings = ['Warning 1', 'Warning 2']
        

        # Create an instance of YourClass with the mock query
        self.your_class_instance = Cursor(connection=mock_connection, request=mock_request)
        self.your_class_instance._query = self.mock_query

    def test_rowcount(self):
        expected_rowcount = 10
        self.assertEqual(self.your_class_instance.rowcount, expected_rowcount)

    def test_stats(self):
        expected_stats = {'execution_time': 100}
        self.assertEqual(self.your_class_instance.stats, expected_stats)

    def test_query_id(self):
        expected_query_id = '12345'
        self.assertEqual(self.your_class_instance.query_id, expected_query_id)

    def test_query(self):
        expected_query = 'SELECT * FROM table'
        self.assertEqual(self.your_class_instance.query, expected_query)

    def test_warnings(self):
        expected_warnings = ['Warning 1', 'Warning 2']
        self.assertEqual(self.your_class_instance.warnings, expected_warnings)

    def test_setinputsizes_raises_error(self):
        with self.assertRaises(pyavrio.exceptions.NotSupportedError):
            self.your_class_instance.setinputsizes(sizes=[1, 2])

    def test_setoutputsize_raises_error(self):
        with self.assertRaises(pyavrio.exceptions.NotSupportedError):
            self.your_class_instance.setoutputsize(size=10, column='column1')

class TestFormatPreparedParam(unittest.TestCase):
    def setUp(self):
        self.your_class_instance = Cursor(connection=mock_connection, request=mock_request)

    def test_format_none(self):
        self.assertEqual(self.your_class_instance._format_prepared_param(None), "NULL")

    def test_format_bool(self):
        self.assertEqual(self.your_class_instance._format_prepared_param(True), "true")
        self.assertEqual(self.your_class_instance._format_prepared_param(False), "false")

    def test_format_int(self):
        self.assertEqual(self.your_class_instance._format_prepared_param(123), "123")

    def test_format_float(self):
        self.assertEqual(self.your_class_instance._format_prepared_param(123.45), "DOUBLE '123.45'")
        self.assertEqual(self.your_class_instance._format_prepared_param(float('inf')), "infinity()")
        self.assertEqual(self.your_class_instance._format_prepared_param(float('-inf')), "-infinity()")
        self.assertEqual(self.your_class_instance._format_prepared_param(float('nan')), "nan()")

    def test_format_str(self):
        self.assertEqual(self.your_class_instance._format_prepared_param("Hello"), "'Hello'")
        self.assertEqual(self.your_class_instance._format_prepared_param("It's a test"), "'It''s a test'")

    def test_format_datetime(self):
        dt = datetime(2022, 1, 1, 12, 0, 0)
        self.assertEqual(self.your_class_instance._format_prepared_param(dt), "TIMESTAMP '2022-01-01 12:00:00.000000'")

class TestFormatPreparedParam(unittest.TestCase):

    def setUp(self):
       
        self.obj = Cursor(connection=mock_connection, request=mock_request)
       
    def test_format_none_param(self):
        param = None
        self.assertEqual(self.obj._format_prepared_param(param), "NULL")

    def test_format_bool_param_true(self):
        param = True
        self.assertEqual(self.obj._format_prepared_param(param), "true")

    def test_format_bool_param_false(self):
        param = False
        self.assertEqual(self.obj._format_prepared_param(param), "false")

    def test_format_int_param(self):
        param = 42
        self.assertEqual(self.obj._format_prepared_param(param), "42")

    def test_format_float_param_infinity(self):
        param = float("+inf")
        self.assertEqual(self.obj._format_prepared_param(param), "infinity()")

    def test_format_float_param_negative_infinity(self):
        param = float("-inf")
        self.assertEqual(self.obj._format_prepared_param(param), "-infinity()")

    def test_format_float_param_nan(self):
        param = float("nan")
        self.assertEqual(self.obj._format_prepared_param(param), "nan()")

    def test_format_float_param(self):
        param = 3.14
        self.assertEqual(self.obj._format_prepared_param(param), "DOUBLE '3.14'")

    def test_format_str_param(self):
        param = "Hello, world!"
        self.assertEqual(self.obj._format_prepared_param(param), "'Hello, world!'")

    def test_format_bytes_param(self):
        param = b"\x00\x01\x02"
        self.assertEqual(self.obj._format_prepared_param(param), "X'000102'")

    def test_format_datetime_param_no_tz(self):
        param = datetime(2024, 4, 16, 12, 30, 0)
        expected_result = "TIMESTAMP '2024-04-16 12:30:00.000000'"
        self.assertEqual(self.obj._format_prepared_param(param), expected_result)

    def test_format_datetime_param_with_tz_named(self):
        param = datetime(2024, 4, 16, 12, 30, 0, tzinfo=ZoneInfo("America/New_York"))
        expected_result = "TIMESTAMP '2024-04-16 12:30:00.000000 America/New_York'"
        self.assertEqual(self.obj._format_prepared_param(param), expected_result)

    def test_format_datetime_param_with_tz_offset(self):
        # Create a timezone with the desired offset (UTC+03:00)
        tz_offset = timedelta(hours=3)
        tz = timezone(tz_offset)

        # Create the datetime object with the timezone
        param = datetime(2024, 4, 16, 12, 30, 0, tzinfo=tz)

        # Define the expected result
        expected_result = "TIMESTAMP '2024-04-16 12:30:00.000000 UTC+03:00'"

        # Perform the assertion
        self.assertEqual(self.obj._format_prepared_param(param), expected_result)

    def test_format_time_param_no_tz(self):
        param = time(12, 30, 0)
        expected_result = "TIME '12:30:00.000000'"
        self.assertEqual(self.obj._format_prepared_param(param), expected_result)

    def test_format_time_param_with_tz_offset(self):
        # Create a timezone with the desired offset (UTC+03:00)
        tz_offset = timedelta(hours=3)
        tz = timezone(tz_offset)

        # Create the time object with the timezone
        param = time(12, 30, 0, tzinfo=tz)

        # Define the expected result
        expected_result =  "TIME '12:30:00.000000 +03:00'"
        # Perform the assertion
        self.assertEqual(self.obj._format_prepared_param(param), expected_result)

    def test_format_date_param(self):
        param = date(2024, 4, 16)
        expected_result = "DATE '2024-04-16'"
        self.assertEqual(self.obj._format_prepared_param(param), expected_result)

    def test_format_list_param(self):
        param = [1, 2, 3]
        expected_result = "ARRAY[1,2,3]"
        self.assertEqual(self.obj._format_prepared_param(param), expected_result)

    def test_format_tuple_param(self):
        param = (1, 2, 3)
        expected_result = "ROW(1,2,3)"
        self.assertEqual(self.obj._format_prepared_param(param), expected_result)

    def test_format_dict_param(self):
        param = {'key1': 'value1', 'key2': 'value2'}
        expected_result = "MAP(ARRAY['key1','key2'], ARRAY['value1','value2'])" 
        self.assertEqual(self.obj._format_prepared_param(param), expected_result)

    def test_format_uuid_param(self):
        import uuid
        param = uuid.UUID("12345678-1234-5678-1234-567812345678")
        expected_result = "UUID '12345678-1234-5678-1234-567812345678'"
        self.assertEqual(self.obj._format_prepared_param(param), expected_result)

    def test_format_decimal_param(self):
        param = Decimal("3.14159")
        expected_result = "DECIMAL '3.14159'"
        self.assertEqual(self.obj._format_prepared_param(param), expected_result)

    def test_format_bytes_param_binascii(self):
        param = b"\x00\x01\x02"
        expected_result = "X'000102'"
        self.assertEqual(self.obj._format_prepared_param(param), expected_result)

    def test_format_unsupported_param(self):
        param = complex(1, 2)
        with self.assertRaises(pyavrio.exceptions.NotSupportedError):
            self.obj._format_prepared_param(param)

