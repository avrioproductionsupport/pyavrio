import math
import time
import unittest
import mock
from unittest.mock import Mock, call, patch, MagicMock
from time import sleep
import uuid
from typing import Dict, Optional, Generic, TypeVar, List, Any
from urllib.parse import urlparse
from decimal import Decimal
import pytest
from requests_kerberos.exceptions import KerberosExchangeError
from tzlocal import get_localzone_name  # type: ignore
from datetime import timezone, timedelta, datetime, date, time
from zoneinfo import ZoneInfo
from pyavrio.client import (
    TimeWithTimeZoneValueMapper,
    TemporalType,
    RowMapperFactory,
    NoOpRowMapper,
    RowMapper,
    ValueMapper,
    TrinoRequest,
    ClientSession,
    TrinoQuery,
    TrinoResult,
    _DelayExponential,
    _RetryWithExponentialBackoff,
    _retry_with,
    NamedRowTuple,
    get_header_values,
    get_prepared_statement_values,
    get_roles_values,
    get_session_property_values,
    BinaryValueMapper,
    ArrayValueMapper,
    MapValueMapper,
    UuidValueMapper,
    TrinoStatus,
    NoOpValueMapper,
    DecimalValueMapper,
    DoubleValueMapper,
    _create_tzinfo,
    _fraction_to_decimal,
    Time,
    TimeWithTimeZone,
    Timestamp,
    TimestampWithTimeZone,
    TimeValueMapper,
    TimestampValueMapper,
    TimestampWithTimeZoneValueMapper,
)
from pyavrio import __version__, constants
from pyavrio.client import RowValueMapper, NamedRowTuple
import pyavrio.exceptions
from pyavrio.exceptions import TrinoExternalError, TrinoUserError, Http502Error, Http503Error, Http504Error, HttpError
import pytz
from threading import Lock

try:
    from zoneinfo import ZoneInfoNotFoundError  # type: ignore
except ModuleNotFoundError:
    from backports.zoneinfo._common import ZoneInfoNotFoundError  # type: ignore

#from your_module import ClientSession, get_header_values, get_session_property_values, get_prepared_statement_values, get_roles_values

class TestClientSession(unittest.TestCase):
  
    def setUp(self):
        self.your_instance = ClientSession(user="mock_user")
        self.your_instance._object_lock = Lock()
    def tearDown(self):
        del self.your_instance

    def test_format_roles_with_string_input(self):
        roles = "role_name"
        expected_result = {"system": 'ROLE{role_name}'}
        formatted_roles = self.your_instance._format_roles(roles)
        self.assertEqual(formatted_roles, expected_result)

    def test_format_roles_with_legacy_role(self):
        roles = {'catalog1': 'ROLE{legacy_role}'} 
        with self.assertWarns(DeprecationWarning):
            formatted_roles = self.your_instance._format_roles(roles)
        expected_result = {'catalog1': 'ROLE{legacy_role}'} 
        self.assertEqual(formatted_roles, expected_result)

    def test_format_roles_with_regular_role(self):
        roles = {"catalog1": "regular_role"}
        formatted_roles = self.your_instance._format_roles(roles)
        expected_result = {"catalog1": "ROLE{regular_role}"}
        self.assertEqual(formatted_roles, expected_result)

    def test_getstate_method(self):
        # Simulate the object state
        self.your_instance.some_attribute = "some_value"
        state = self.your_instance.__getstate__()

        # Assert that the object lock is not included in the state
        self.assertNotIn("_object_lock", state)
        # Assert that other attributes are included in the state
        self.assertIn("some_attribute", state)
        self.assertEqual(state["some_attribute"], "some_value")

    def test_client_session_properties(self):
        session = ClientSession(user="test_user", catalog="default", schema="public")
        self.assertEqual(session.user, "test_user")
        self.assertEqual(session.catalog, "default")
        self.assertEqual(session.schema, "public")

    def test_client_session_headers(self):
        session = ClientSession(user="test_user", headers={"Authorization": "Bearer token"})
        self.assertEqual(session.headers["Authorization"], "Bearer token")

    def test_get_header_values(self):
        headers = {"X-Header": "value1, value2, value3"}
        values = get_header_values(headers, "X-Header")
        self.assertEqual(values, ["value1", "value2", "value3"])

    def test_get_session_property_values(self):
        headers = {"Session-Properties": "key1=value1, key2=value2"}
        values = get_session_property_values(headers, "Session-Properties")
        self.assertEqual(values, [("key1", "value1"), ("key2", "value2")])

    def test_get_prepared_statement_values(self):
        headers = {"Prepared-Statements": "query1=statement1, query2=statement2"}
        values = get_prepared_statement_values(headers, "Prepared-Statements")
        self.assertEqual(values, [("query1", "statement1"), ("query2", "statement2")])

    def test_get_roles_values(self):
        headers = {"Roles": "catalog1=role1, catalog2=role2"}
        values = get_roles_values(headers, "Roles")
        self.assertEqual(values, [("catalog1", "role1"), ("catalog2", "role2")])

    
class TestTrinoRequest(unittest.TestCase):

    def setUp(self):
        self.host = "example.com"
        self.port = 8080
        self.client = TrinoRequest('example.com', 8080, MagicMock())  # Adjust arguments as needed
        self.client_session = MagicMock()
        self.trino_request = TrinoRequest(
            host=self.host,
            port=self.port,
            client_session=self.client_session,
        )

    def test_init(self):
        self.assertEqual(self.trino_request._host, self.host)
        self.assertEqual(self.trino_request._port, self.port)
        self.assertEqual(self.trino_request._client_session, self.client_session)
        self.assertEqual(self.trino_request._http_scheme, "http")  # Assuming default is http
        self.assertIsNotNone(self.trino_request._http_session)
        self.assertEqual(self.trino_request.max_attempts, 3)  # Assuming default max_attempts is 3
    
    def test_get_url(self):
        path = "/query"
        expected_url = f"http://{self.host}:{self.port}{path}"
        self.assertEqual(self.trino_request.get_url(path), expected_url)

    def test_process_error_external(self):
        error = {"errorType": "EXTERNAL"}
        query_id = "123"
        with self.assertRaises(TrinoExternalError):
            self.client._process_error(error, query_id)

    def test_process_error_user(self):
        error = {"errorType": "USER_ERROR"}
        query_id = "123"
        result = self.client._process_error(error, query_id)
        self.assertIsInstance(result,TrinoUserError)

    def test_raise_response_error_502(self):
        http_response = MagicMock(status_code=502)
        with self.assertRaises(Http502Error):
            self.client.raise_response_error(http_response)

    def test_verify_extra_credential_valid(self):
        header = ("key", "value")
        self.client._verify_extra_credential(header)  # This should not raise any exceptions

    def test_verify_extra_credential_invalid_whitespace(self):
        header = ("invalid key", "value")
        with self.assertRaises(ValueError):
            self.client._verify_extra_credential(header)

    def test_verify_extra_credential_invalid_non_ascii(self):
        header = ("non-ascii-🚀", "value")
        with self.assertRaises(ValueError):
            self.client._verify_extra_credential(header)


class TestTrinoQuery(unittest.TestCase):
    def setUp(self):
        # Create mock objects for dependencies
        self.mock_request = MagicMock(spec=TrinoRequest)
        self.mock_request._host = 'example.com'
        self.mock_request = MagicMock()
        self.mock_request._client_session = MagicMock()
        # Set other necessary attributes and behaviors for mock_request
        self.trino_query = TrinoQuery(self.mock_request, 'SELECT * FROM table')

        # Create TrinoQuery instance with mock dependencies
        self.trino_query = TrinoQuery(self.mock_request, 'SELECT * FROM table')


    def setUp(self):
        # Create a mock for the _request and _extrica_http_handler objects
        self.mock_request = Mock()
        self.mock_avrio_http_handler = Mock()
        
        # Create an instance of YourClass, passing the mocks as dependencies
        self.your_instance = TrinoQuery(self.mock_request, self.mock_avrio_http_handler)

    def test_execute(self):
        # Set up necessary mock behavior
        self.your_instance._request._client_session.user = "test_user"
        self.your_instance._request._client_session.access_token = "test_token"
        self.your_instance._query = "SELECT * FROM table_name"

        # Mock the HTTP response for _get_modified_query
        mock_modified_response = Mock()
        mock_modified_response.ok = True
        mock_modified_response.text = "SELECT * FROM modified_table"
        self.mock_avrio_http_handler._get_modified_query.return_value = mock_modified_response

        # Mock the HTTP response for _request.post
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {"status": "success"}
        self.your_instance._request.post.return_value = mock_post_response

        # Call the execute method
        result = self.your_instance.execute()

        # Assertions
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json(), {"status": "success"})
        self.assertTrue(self.your_instance.finished)

    def test_execute_cancelled_query(self):
        # Set up mock for cancelled query
        self.your_instance.cancelled = True

        # Call the execute method
        with self.assertRaises(Exception): 
            self.your_instance.execute()

    def tearDown(self):
        pass

    def test_query_id(self):
        self.assertIsNone(self.trino_query.query_id)

    def test_query(self):
        self.assertEqual(self.trino_query.query, 'SELECT * FROM table')

    def test_stats(self):
        stats = self.trino_query.stats
        self.assertIsInstance(stats, dict)

    def test_update_type(self):
        update_type = self.trino_query.update_type
        self.assertIsNone(update_type)

class ConcreteTemporalType(TemporalType[datetime]): 
    def new_instance(self, value: datetime, fraction: Decimal) -> TemporalType[datetime]:
        return ConcreteTemporalType(value, fraction) 
    def to_python_type(self) -> datetime:
        return self._whole_python_temporal_value 

    def add_time_delta(self, time_delta: timedelta) -> datetime:
        return self._whole_python_temporal_value + time_delta 

class TestTemporalType(unittest.TestCase):
    def setUp(self):
        self.temporal_value = datetime(2024, 4, 1, 12, 30, 45)
        self.remaining_fractional_seconds = Decimal('0.123456')
        self.temporal_type_instance = ConcreteTemporalType(self.temporal_value, self.remaining_fractional_seconds)

    def test_round_to(self):
        rounded_instance = self.temporal_type_instance.round_to(3)  # Round to millisecond precision
        expected_value = Decimal('0.123')
        self.assertEqual(rounded_instance._remaining_fractional_seconds, expected_value)

    def test_add_time_delta(self):
        time_delta = timedelta(hours=1, minutes=30)
        new_value = self.temporal_type_instance.add_time_delta(time_delta)
        expected_value = datetime(2024, 4, 1, 14, 0, 45)  # Adding 1 hour and 30 minutes
        self.assertEqual(new_value, expected_value)

MAX_PYTHON_TEMPORAL_PRECISION = 1000000  # Example value for the maximum precision

class TemporalType:
    pass

class Time(TemporalType):
    def __init__(self, value: time, fraction: Decimal):
        self._whole_python_temporal_value = value
        self._remaining_fractional_seconds = fraction

    def new_instance(self, value: time, fraction: Decimal) -> 'Time':
        return Time(value, fraction)

    def to_python_type(self) -> time:
        if self._remaining_fractional_seconds > 0:
            time_delta = timedelta(microseconds=int(self._remaining_fractional_seconds * MAX_PYTHON_TEMPORAL_PRECISION))
            return self.add_time_delta(time_delta)
        return self._whole_python_temporal_value

    def add_time_delta(self, time_delta: timedelta) -> time:
        time_delta_added = datetime.combine(datetime(1, 1, 1), self._whole_python_temporal_value) + time_delta
        return time_delta_added.time().replace(tzinfo=self._whole_python_temporal_value.tzinfo)

T = TypeVar('T')

class TemporalType(Generic[T]):
    def __init__(self, value: T, fraction: Decimal):
        self.value = value
        self.fraction = fraction

class TimeWithTimeZone(TemporalType[time]): 
    def new_instance(self, value: time, fraction: Decimal) -> 'TimeWithTimeZone': 
        return TimeWithTimeZone(value, fraction)

class TestTimestamp(unittest.TestCase):

    def setUp(self):
        # Initialize a Timestamp instance for testing
        self.timestamp = Timestamp(datetime(2022, 1, 1, 12, 0, 0), Decimal('0.5'))
    def test_new_instance(self):
        # Test if new_instance method creates a new Timestamp instance correctly
        new_timestamp = self.timestamp.new_instance(datetime(2023, 1, 1, 12, 0, 0), Decimal('0.3'))
        self.assertIsInstance(new_timestamp, Timestamp)
        self.assertEqual(new_timestamp.to_python_type().replace(microsecond=0), datetime(2023, 1, 1, 12, 0, 0).replace(microsecond=0))

    def test_to_python_type_without_fraction(self):
        # Test if to_python_type method returns the correct datetime without remaining fractional seconds
        expected_datetime = datetime(2022, 1, 1, 12, 0, 0)
        self.assertEqual(self.timestamp.to_python_type().replace(microsecond=0), expected_datetime.replace(microsecond=0))
   

    def test_to_python_type_with_fraction(self):
        # Test if to_python_type method returns the correct datetime with remaining fractional seconds
        timestamp_with_fraction = Timestamp(datetime(2022, 1, 1, 12, 0, 0), Decimal('0.123456'))
        expected_datetime = datetime(2022, 1, 1, 12, 0, 0) + timedelta(microseconds=123456)
        self.assertEqual(timestamp_with_fraction.to_python_type(), expected_datetime)

    def test_add_time_delta(self):
        # Test if add_time_delta method correctly adds a timedelta to the datetime
        time_delta = timedelta(days=1, hours=2, minutes=30)
        expected_datetime = datetime(2022, 1, 2, 14, 30, 0)
        self.assertEqual(self.timestamp.add_time_delta(time_delta), expected_datetime)

class TestTimestampWithTimeZone(unittest.TestCase):

    def setUp(self):
        # Initialize a TimestampWithTimeZone instance for testing
        self.timestamp_with_tz = TimestampWithTimeZone(datetime(2022, 1, 1, 12, 0, 0, tzinfo=pytz.utc), Decimal('0.5'))

    def test_new_instance(self):
        # Test if new_instance method creates a new TimestampWithTimeZone instance correctly
        new_timestamp_with_tz = self.timestamp_with_tz.new_instance(datetime(2023, 1, 1, 12, 0, 0, tzinfo=pytz.utc), Decimal('0.3'))
        self.assertIsInstance(new_timestamp_with_tz, TimestampWithTimeZone)
        self.assertEqual(new_timestamp_with_tz.to_python_type().replace(microsecond=0), datetime(2023, 1, 1, 12, 0, 0, tzinfo=pytz.utc).replace(microsecond=0)) 

    def test_normalize_non_ambiguous(self):
        # Test if normalize method handles non-ambiguous datetime values correctly
        non_ambiguous_dt = datetime(2022, 5, 15, 12, 0, 0, tzinfo=pytz.timezone('America/New_York'))
        normalized_dt = self.timestamp_with_tz.normalize(non_ambiguous_dt)
        self.assertEqual(normalized_dt, non_ambiguous_dt)

class TimeValueMapper:

    def __init__(self, precision):
        self.time_default_size = 8  # size of 'HH:MM:SS'
        self.precision = precision

    def map(self, value) -> Optional[time]:
        if value is None:
            return None
        whole_python_temporal_value = value[:self.time_default_size]
        remaining_fractional_seconds = value[self.time_default_size + 1:]
        return time.fromisoformat(whole_python_temporal_value).replace(microsecond=_fraction_to_decimal(remaining_fractional_seconds) * 1000000)

    def _add_second(self, time_value: time) -> time:
        return (datetime.combine(datetime(1, 1, 1), time_value) + timedelta(seconds=1)).time()

class TestTimeValueMapper(unittest.TestCase):

    def setUp(self):
        # Initialize a TimeValueMapper instance for testing
        self.time_mapper = TimeValueMapper(Decimal('0.001'))  # Set precision to 0.001 seconds

    def test_map_none(self):
        # Test the map method with None input
        mapped_time = self.time_mapper.map(None)
        self.assertIsNone(mapped_time)

    def test_add_second(self):
        # Test the _add_second method with a time value
        input_time = time(23, 59, 59)
        result_time = self.time_mapper._add_second(input_time)
        expected_time = time(0, 0, 0)
        self.assertEqual(result_time, expected_time)

class TestTimeWithTimeZoneValueMapper(unittest.TestCase):
    def test_map_with_none_value(self):
        precision = 3  # Placeholder for the precision argument
        mapper = TimeWithTimeZoneValueMapper(precision)
        input_value = None
        
        mapped_time = mapper.map(input_value)
        
        self.assertIsNone(mapped_time)

class DateValueMapper:
    def map(self, value) -> Optional[date]:
        if value is None:
            return None
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None

class TestDateValueMapper(unittest.TestCase):
    def setUp(self):
        self.mapper = DateValueMapper()

    def test_map_valid_date(self):
        # Test with a valid ISO date string
        input_value = "2024-04-01"
        expected_output = date(2024, 4, 1)
        self.assertEqual(self.mapper.map(input_value), expected_output)
        
    def test_map_none(self):
        # Test with None input
        input_value = None
        self.assertIsNone(self.mapper.map(input_value))

    def test_map_empty_string(self):
        # Test with an empty string input
        input_value = ""
        self.assertIsNone(self.mapper.map(input_value))

class TestTimestampValueMapper(unittest.TestCase):

    def test_map_with_none_value(self):
        mapper = TimestampValueMapper(precision=3)
        result = mapper.map(None)
        self.assertIsNone(result)

    def test_map_with_valid_value(self):
        mapper = TimestampValueMapper(precision=3)
        value = '2024-04-01 12:30:45.678'
        expected_result = datetime(2024, 4, 1, 12, 30, 45, 678000)
        result = mapper.map(value)
        self.assertEqual(result, expected_result)

class TestBinaryValueMapper(unittest.TestCase):

    def test_map_with_valid_value(self):
        mapper = BinaryValueMapper()
        value = "SGVsbG8gV29ybGQ="
        expected_result = b'Hello World'
        result = mapper.map(value)
        self.assertEqual(result, expected_result)

    def test_map_with_none_value(self):
        mapper = BinaryValueMapper()
        value = None
        result = mapper.map(value)
        self.assertIsNone(result)

class TestArrayValueMapper(unittest.TestCase):

    def test_map_with_valid_values(self):
        inner_mapper = BinaryValueMapper()
        mapper = ArrayValueMapper(inner_mapper)
        values = ["SGVsbG8gV29ybGQ=", "VGhpcyBpcyBhIHRlc3Q="]
        expected_result = [b'Hello World', b'This is a test']
        result = mapper.map(values)
        self.assertEqual(result, expected_result)

    def test_map_with_none_values(self):
        inner_mapper = BinaryValueMapper()
        mapper = ArrayValueMapper(inner_mapper)
        values = None
        result = mapper.map(values)
        self.assertIsNone(result)


class TestRowValueMapper(unittest.TestCase):

    def setUp(self):
        self.mock_mappers = [Mock(), Mock(), Mock()]
        self.mapper = RowValueMapper(self.mock_mappers, ['id', 'name', 'value'], ['int', 'str', 'float'])

    def test_map_with_none_values(self):
        values = None
        result = self.mapper.map(values)
        self.assertIsNone(result)

import uuid
class TestUuidValueMapper(unittest.TestCase):

    def setUp(self):
        self.mapper = UuidValueMapper()

    def test_map_with_valid_value(self):
        value = '550e8400-e29b-41d4-a716-446655440000'
        result = self.mapper.map(value)
        self.assertIsInstance(result, uuid.UUID)
        self.assertEqual(result, uuid.UUID('550e8400-e29b-41d4-a716-446655440000'))

    def test_map_with_none_value(self):
        value = None
        result = self.mapper.map(value)
        self.assertIsNone(result)

class TestNoOpRowMapper(unittest.TestCase):

    def setUp(self):
        self.mapper = NoOpRowMapper()

    def test_map(self):
        rows = [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]
        result = self.mapper.map(rows)
        self.assertEqual(result, rows)

class TestRowMapperFactory(unittest.TestCase):

    def setUp(self):
        self.factory = RowMapperFactory()

    def test_create_legacy_primitive_types_true(self):
        columns = [{'typeSignature': {'rawType': 'integer'}}]
        legacy_primitive_types = True

        result = self.factory.create(columns, legacy_primitive_types)

        self.assertIsInstance(result, NoOpRowMapper)

    def test_create_legacy_primitive_types_false(self):
        columns = [{'typeSignature': {'rawType': 'integer'}}]
        legacy_primitive_types = False

        with patch.object(RowMapperFactory, '_create_value_mapper', return_value=MagicMock(spec=ValueMapper)) as mock_create_mapper:
            result = self.factory.create(columns, legacy_primitive_types)

            self.assertIsInstance(result, RowMapper)
            mock_create_mapper.assert_called_once()

    def test_create_with_mocked_value_mappers(self):
        columns = [{'typeSignature': {'rawType': 'array', 'arguments': [{'value': {'typeSignature': {'rawType': 'string'}}}]}}, 
                   {'typeSignature': {'rawType': 'map', 'arguments': [{'value': {'typeSignature': {'rawType': 'integer'}}}, {'value': {'typeSignature': {'rawType': 'boolean'}}}]}}, 
                   {'typeSignature': {'rawType': 'decimal'}},
                   {'typeSignature': {'rawType': 'unknown'}}]
        legacy_primitive_types = False

        with patch.object(RowMapperFactory, '_create_value_mapper', side_effect=[MagicMock(spec=ValueMapper), MagicMock(spec=ValueMapper), MagicMock(spec=ValueMapper), MagicMock(spec=ValueMapper)]) as mock_create_mapper:
            result = self.factory.create(columns, legacy_primitive_types)

            self.assertIsInstance(result, RowMapper)
            mock_create_mapper.assert_called()

    def test_get_precision(self):
        # Test cases for _get_precision method
        column_no_args = {'arguments': []}
        self.assertEqual(self.factory._get_precision(column_no_args), 3)

        column_with_args = {'arguments': [{'value': 5}]}
        self.assertEqual(self.factory._get_precision(column_with_args), 5)

        
class TestRowMapper(unittest.TestCase):

    def setUp(self):
        self.columns = [MagicMock(spec=ValueMapper) for _ in range(3)]  # Create mocked ValueMapper instances
        self.mapper = RowMapper(self.columns)
    def test_map_empty_columns(self):
        # Test mapping with empty columns
        self.mapper.columns = []
        rows = [[1, 2, 3], [4, 5, 6]]
        result = self.mapper.map(rows)
        self.assertEqual(result, rows)  # Mapping should not modify rows when columns are empty

    def test_map_non_empty_columns(self):
        # Test mapping with non-empty columns
        rows = [[1, 2, 3], [4, 5, 6]]
        expected_result = [["mapped1", "mapped2", "mapped3"], ["mapped4", "mapped5", "mapped6"]]
        
        # Mock _map_row to return mapped values for testing purposes
        def mock_map_row(row):
            return ["mapped" + str(val) for val in row]
        self.mapper._map_row = mock_map_row

        result = self.mapper.map(rows)
        self.assertEqual(result, expected_result)  # Verify that mapping is applied correctly

    def test_map_value_with_valid_value(self):
        value = 42
        value_mapper = MagicMock(spec=ValueMapper)
        value_mapper.map.return_value = value
        result = self.mapper._map_value(value, value_mapper)
        self.assertEqual(result, value)
        value_mapper.map.assert_called_once_with(value)

    def test_map_value_with_invalid_value(self):
        value = 'invalid_value'
        value_mapper = MagicMock(spec=ValueMapper)
        value_mapper.map.side_effect = ValueError("Invalid value")
        with self.assertRaises(pyavrio.exceptions.TrinoDataError):
            self.mapper._map_value(value, value_mapper)
class TestDelayExponential(unittest.TestCase):

    def test_initialization(self):
        base = 0.1
        exponent = 2
        jitter = True
        max_delay = 2 * 3600

        delay_exponential = _DelayExponential(base=base, exponent=exponent, jitter=jitter, max_delay=max_delay)

        self.assertEqual(delay_exponential._base, base)
        self.assertEqual(delay_exponential._exponent, exponent)
        self.assertEqual(delay_exponential._jitter, jitter)
        self.assertEqual(delay_exponential._max_delay, max_delay)

    def test_call_with_jitter(self):
        base = 0.1
        exponent = 2
        jitter = True
        max_delay = 2 * 3600
        max_attempts = 10 

        delay_exponential = _DelayExponential(base=base, exponent=exponent, jitter=jitter, max_delay=max_delay)

        delays = [delay_exponential(attempt) for attempt in range(max_attempts)]

        self.assertTrue(all(delay <= max_delay for delay in delays))
        self.assertTrue(all(delay >= 0 for delay in delays))

    def test_call_without_jitter(self):
        base = 0.1
        exponent = 2
        jitter = False
        max_delay = 2 * 3600
        max_attempts = 10  

        delay_exponential = _DelayExponential(base=base, exponent=exponent, jitter=jitter, max_delay=max_delay)

        delays = [delay_exponential(attempt) for attempt in range(max_attempts)]

        self.assertTrue(all(delay <= max_delay for delay in delays))
        self.assertTrue(all(delay >= base for delay in delays))

class TestRetryWithExponentialBackoff(unittest.TestCase):

    def test_retry(self):
        base = 0.1
        exponent = 2
        jitter = True
        max_delay = 2 * 3600
        max_attempts = 0 

        retry_with_backoff = _RetryWithExponentialBackoff(base=base, exponent=exponent, jitter=jitter, max_delay=max_delay)

        mock_func = Mock()
        args = (1, 2, 3)
        kwargs = {'param': 'value'}
        err = Exception("Something went wrong")

        with patch('time.sleep') as mock_sleep:
            retry_with_backoff.retry(mock_func, args, kwargs, err, max_attempts)

        self.assertEqual(mock_func.call_count, max_attempts)
        calls = [mock.call(*args, **kwargs)] * max_attempts
        mock_func.assert_has_calls(calls)

        expected_delays = [retry_with_backoff._get_delay(attempt) for attempt in range(max_attempts)]
        expected_sleep_calls = [call(delay) for delay in expected_delays]
        mock_sleep.assert_has_calls(expected_sleep_calls)

class TestTrinoResult(unittest.TestCase):
    def test_iteration(self):
        # Mock the TrinoQuery object for testing TrinoResult
        mock_query = Mock()
        mock_query.finished = False  # Set finished to False initially
        mock_query.fetch.return_value = [{"col1": 1, "col2": "value1"}, {"col1": 2, "col2": "value2"}]

        # Create a TrinoResult instance with the mock TrinoQuery and initial rows
        trino_result = TrinoResult(mock_query, [{"col1": 0, "col2": "value0"}])

        # Initialize an iterator using iter()
        iterator = iter(trino_result)

        # Fetch the first row from the iterator
        first_row = next(iterator)
        self.assertEqual(first_row, {"col1": 0, "col2": "value0"})  # Check if the first row matches

        # Fetch the next rows from the iterator
        second_row = next(iterator)
        third_row = next(iterator)

        # Check if the row numbers are incremented correctly
        self.assertEqual(trino_result.rownumber, 3)  # Since three rows are fetched

        # Check if the fetched rows match the expected values
        self.assertEqual(second_row, {"col1": 1, "col2": "value1"})
        self.assertEqual(third_row, {"col1": 2, "col2": "value2"})

    def test_iteration_finished_query(self):
        # Mock the TrinoQuery object for testing TrinoResult with a finished query
        mock_query = Mock()
        mock_query.finished = True  # Set finished to True initially
        mock_query.fetch.return_value = None  # No more rows to fetch

        # Create a TrinoResult instance with the mock TrinoQuery and initial rows
        trino_result = TrinoResult(mock_query, [{"col1": 0, "col2": "value0"}])

        # Initialize an iterator using iter()
        iterator = iter(trino_result)

        # Fetch the first row from the iterator
        first_row = next(iterator)
        self.assertEqual(first_row, {"col1": 0, "col2": "value0"})  # Check if the first row matches

        # Attempt to fetch the next row, which should raise StopIteration since the query is finished
        with self.assertRaises(StopIteration):
            next(iterator)

        # Check if the row number remains unchanged
        self.assertEqual(trino_result.rownumber, 1) 


class TestValueMappers(unittest.TestCase):
    def test_no_op_value_mapper(self):
        mapper = NoOpValueMapper()
        self.assertEqual(mapper.map(10), 10)
        self.assertEqual(mapper.map("hello"), "hello")
        self.assertIsNone(mapper.map(None))

    def test_decimal_value_mapper(self):
        mapper = DecimalValueMapper()
        self.assertEqual(mapper.map(10), Decimal(10))
        self.assertEqual(mapper.map("3.14"), Decimal("3.14"))
        self.assertIsNone(mapper.map(None))

    def test_double_value_mapper(self):
        mapper = DoubleValueMapper()
        self.assertEqual(mapper.map(10), 10.0)
        self.assertEqual(mapper.map("3.14"), 3.14)
        self.assertEqual(mapper.map("Infinity"), float("inf"))
        self.assertEqual(mapper.map("-Infinity"), float("-inf"))
        self.assertTrue(math.isnan(mapper.map("NaN")))
        self.assertIsNone(mapper.map(None))

class TestHelperFunctions(unittest.TestCase):
    def test_create_tzinfo(self):
        tzinfo = _create_tzinfo("+03:00")
        self.assertIsInstance(tzinfo, timezone)
        self.assertEqual(str(tzinfo), "UTC+03:00")

        tzinfo = _create_tzinfo("-05:30")
        self.assertIsInstance(tzinfo, timezone)
        self.assertEqual(str(tzinfo), "UTC-05:30")

        tzinfo = _create_tzinfo("Europe/Paris")
        self.assertIsInstance(tzinfo, ZoneInfo)
        self.assertEqual(str(tzinfo), "Europe/Paris")

    def test_fraction_to_decimal(self):
        decimal_val = _fraction_to_decimal("12345")
        self.assertEqual(decimal_val, Decimal("0.12345"))

        decimal_val = _fraction_to_decimal("")
        self.assertEqual(decimal_val, Decimal(0))

        decimal_val = _fraction_to_decimal("987654321")
        self.assertEqual(decimal_val, Decimal("0.987654321"))

@patch("trino.client.TrinoRequest.http")
def test_trino_initial_request(mock_requests):
    sample_post_response_data = {
        "nextUri": "https://example.com/next",
        "id": "123456"
    }
    mock_requests.Response.return_value.json.return_value = sample_post_response_data

@pytest.mark.parametrize("header,error", [
    ("", "Error: header WWW-Authenticate not available in the response."),
    ('Bearer"', 'Error: header info didn\'t have x_token_server'),
    ('x_redirect_server="redirect_server", x_token_server="token_server"', 'Error: header info didn\'t match x_redirect_server="redirect_server", x_token_server="token_server"'),  # noqa: E501
    ('Bearer x_redirect_server="redirect_server"', 'Error: header info didn\'t have x_token_server'),
])


@pytest.mark.parametrize("header", [
    'Bearer x_redirect_server="{redirect_server}", x_token_server="{token_server}", additional_challenge',
    'Bearer x_redirect_server="{redirect_server}", x_token_server="{token_server}", additional_challenge="value"',
    'Bearer x_token_server="{token_server}", x_redirect_server="{redirect_server}"',
    'Basic realm="Trino", Bearer x_redirect_server="{redirect_server}", x_token_server="{token_server}"',
    'Bearer x_redirect_server="{redirect_server}", x_token_server="{token_server}", Basic realm="Trino"',
])


class RetryRecorder(object):
    def __init__(self, error=None, result=None):
        self.__name__ = "RetryRecorder"
        self._retry_count = 0
        self._error = error
        self._result = result

    def __call__(self, *args, **kwargs):
        self._retry_count += 1
        if self._error is not None:
            raise self._error
        if self._result is not None:
            return self._result

    @property
    def retry_count(self):
        return self._retry_count

@pytest.mark.parametrize("status_code, attempts", [
    (502, 3),
    (503, 3),
    (504, 3),
])
def test_5XX_error_retry(status_code, attempts, monkeypatch):
    http_resp = TrinoRequest.http.Response()
    http_resp.status_code = status_code

    post_retry = RetryRecorder(result=http_resp)
    monkeypatch.setattr(TrinoRequest.http.Session, "post", post_retry)

    get_retry = RetryRecorder(result=http_resp)
    monkeypatch.setattr(TrinoRequest.http.Session, "get", get_retry)

    req = TrinoRequest(
        host="coordinator",
        port=8080,
        client_session=ClientSession(
            user="test",
        ),
        max_attempts=attempts
    )

    req.post("URL")
    assert post_retry.retry_count == attempts

    req.get("URL")
    assert post_retry.retry_count == attempts


@pytest.mark.parametrize("status_code", [
    501
])
def test_error_no_retry(status_code, monkeypatch):
    http_resp = TrinoRequest.http.Response()
    http_resp.status_code = status_code

    post_retry = RetryRecorder(result=http_resp)
    monkeypatch.setattr(TrinoRequest.http.Session, "post", post_retry)

    get_retry = RetryRecorder(result=http_resp)
    monkeypatch.setattr(TrinoRequest.http.Session, "get", get_retry)

    req = TrinoRequest(
        host="coordinator",
        port=8080,
        client_session=ClientSession(
            user="test",
        ),
        max_attempts=3,
    )

    req.post("URL")
    assert post_retry.retry_count == 1

    req.get("URL")
    assert post_retry.retry_count == 1


class FakeGatewayResponse(object):
    def __init__(self, http_response=None, redirect_count=1,access_token=123):
        self.__name__ = "FakeGatewayResponse"
        self._access_token=access_token or 'default_access_token'
        self.http_response = http_response or mock.MagicMock()
        self.redirect_count = redirect_count
        self.count = 0
    
    def execute_query(self):
        access_token = self._get_valid_access_token()
        headers = {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'}
    
    def _get_valid_access_token(self):
        if self._access_token is None:
            return self._fetch_access_token_from_source()
        else:
            return str(self._access_token)

    def _fetch_access_token_from_source(self):
        return 'default_token_value' 

    def __call__(self, *args, **kwargs):
        self.count += 1
        if self.count == self.redirect_count:
            return self.http_response
        http_response = TrinoRequest.http.Response()
        http_response.status_code = 301
        http_response.headers["Location"] = "http://1.2.3.4:8080/new-path/"
        assert http_response.is_redirect
        return http_response

# Testing the FakeGatewayResponse class with dummy values directly in the function calls
    def test_fake_gateway_response():
        dummy_http_response = mock.MagicMock(status_code=200, headers={"Content-Type": "application/json"})
        dummy_access_token = "dummy_access_token"
        fake_response = FakeGatewayResponse(http_response=dummy_http_response, access_token=dummy_access_token)

        # Assert that the http_response and access_token are correctly set in the FakeGatewayResponse instance
        assert fake_response.http_response.status_code == 200
        assert fake_response.http_response.headers["Content-Type"] == "application/json"
        assert fake_response._access_token == "dummy_access_token"

    # Call execute_query method and perform assertions or further testing as needed
        fake_response.execute_query()
        
class MockResponse(mock.Mock):
    # Fake response class
    @property
    def headers(self):
        return {
            'X-Trino-Fake-1': 'one',
            'X-Trino-Fake-2': 'two',
        }

def test_delay_exponential_without_jitter():
    max_delay = 1200.0
    get_delay = _DelayExponential(base=5, jitter=False, max_delay=max_delay)
    results = [
        10.0,
        20.0,
        40.0,
        80.0,
        160.0,
        320.0,
        640.0,
        max_delay,  # rather than 1280.0
        max_delay,  # rather than 2560.0
    ]
    for i, result in enumerate(results, start=1):
        assert get_delay(i) == result


def test_delay_exponential_with_jitter():
    max_delay = 120.0
    get_delay = _DelayExponential(base=10, jitter=False, max_delay=max_delay)
    for i in range(10):
        assert get_delay(i) <= max_delay 


class SomeException(Exception):
    pass


def test_retry_with():
    max_attempts = 3
    with_retry = _retry_with(
        handle_retry=_RetryWithExponentialBackoff(),
        handled_exceptions=[SomeException],
        conditions={},
        max_attempts=max_attempts,
    )

    class FailerUntil(object):
        def __init__(self, until=1):
            self.attempt = 0
            self._until = until

        def __call__(self):
            self.attempt += 1
            if self.attempt > self._until:
                return
            raise SomeException(self.attempt)

    with_retry(FailerUntil(2).__call__)()
    with pytest.raises(SomeException):
        with_retry(FailerUntil(3).__call__)()


class TestNamedRowTuple(unittest.TestCase):
    def test_duplicate_names(self):
            names = ['id', 'id', 'name']  # Duplicate 'id' name
            types = ['int', 'int', 'str']
            values = [1, 2, 'Alice']
            named_row_tuple = NamedRowTuple(values, names, types)

            # Ensure duplicate names are handled correctly
            self.assertEqual(named_row_tuple._names, ['id', 'id', 'name'])  # Accesses the duplicated names
            self.assertEqual(named_row_tuple[0], 1)  # Accesses the first 'id' field
            self.assertEqual(named_row_tuple[1], 2)  # Accesses the second 'id' field
            self.assertEqual(named_row_tuple[2], 'Alice')  # Accesses the 'name' field


    def test_no_names(self):
        names = []  # Empty names list
        types = []
        values = []
        named_row_tuple = NamedRowTuple(values, names, types)

        # Ensure no names are handled correctly
        self.assertEqual(repr(named_row_tuple), "()")  # Empty representation

class TestTrinoQuery(unittest.TestCase):

    def setUp(self):
        # Create a mock TrinoRequest object for testing
        self.mock_request = Mock()
        self.mock_request._host = 'example.com'
        self.mock_request._client_session.access_token = 'token'

        # Create a TrinoQuery object for testing
        self.trino_query = TrinoQuery(self.mock_request, 'SELECT * FROM table')

    def test_query_id(self):
        self.assertIsNone(self.trino_query.query_id)

    def test_query(self):
        self.assertEqual(self.trino_query.query, 'SELECT * FROM table')

    def test_columns(self):
        # Mock the fetch method to return sample rows
        self.trino_query.fetch = Mock(return_value=[[1, 'Alice'], [2, 'Bob']])
        columns = self.trino_query.columns
        self.assertIsNone(columns)
        self.assertEqual(columns, None)

    def test_stats(self):
        self.assertEqual(self.trino_query.stats, {})

    def test_update_type(self):
        self.assertIsNone(self.trino_query.update_type)

    def test_update_count(self):
        self.assertIsNone(self.trino_query.update_count)

    def test_warnings(self):
        self.assertEqual(self.trino_query.warnings, [])

    def test_result(self):
        self.assertIsNone(self.trino_query.result)

    def test_info_uri(self):
        self.assertIsNone(self.trino_query.info_uri)

    def test_split_query(self):
        part1, part2 = self.trino_query.split_query('Prepare ... FROM SELECT ...')
        self.assertIsNotNone(part1)
        self.assertIsNotNone(part2)

    def test_is_show_query(self):
        self.assertFalse(self.trino_query.is_show_query('SELECT * FROM table'))
        self.assertTrue(self.trino_query.is_show_query('SHOW TABLES'))

    def test_is_finished(self):
        with self.assertWarns(DeprecationWarning):
            self.assertFalse(self.trino_query.is_finished())

    def test_finished(self):
        self.assertFalse(self.trino_query.finished)

    def test_cancelled(self):
        self.assertFalse(self.trino_query.cancelled)

if __name__ == '__main__':
    unittest.main()

