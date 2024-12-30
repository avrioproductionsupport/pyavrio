import pytest
from pyavrio.constants import (
    DEFAULT_PORT,
    DEFAULT_TLS_PORT,
    DEFAULT_SOURCE,
    DEFAULT_CATALOG,
    DEFAULT_SCHEMA,
    DEFAULT_AUTH,
    DEFAULT_MAX_ATTEMPTS,
    DEFAULT_REQUEST_TIMEOUT,
    HTTP,
    HTTPS,
    URL_STATEMENT_PATH,
    CLIENT_NAME,
    HEADER_CATALOG,
    HEADER_SCHEMA,
    HEADER_SOURCE,
    HEADER_USER,
    HEADER_CLIENT_INFO,
    HEADER_CLIENT_TAGS,
    HEADER_EXTRA_CREDENTIAL,
    HEADER_TIMEZONE,
    HEADER_SESSION,
    HEADER_SET_SESSION,
    HEADER_CLEAR_SESSION,
    HEADER_ROLE,
    HEADER_SET_ROLE,
    HEADER_STARTED_TRANSACTION,
    HEADER_TRANSACTION,
    HEADER_PREPARED_STATEMENT,
    HEADER_ADDED_PREPARE,
    HEADER_DEALLOCATED_PREPARE,
    HEADER_SET_SCHEMA,
    HEADER_SET_CATALOG,
    HEADER_CLIENT_CAPABILITIES,
    LENGTH_TYPES,
    PRECISION_TYPES,
    SCALE_TYPES,
    AVRIO_METADATA_ENDPOINT,
)

def test_constants():
    # Check default constants
    assert DEFAULT_PORT == 8080
    assert DEFAULT_TLS_PORT == 443
    assert DEFAULT_SOURCE == "trino-python-client"
    assert DEFAULT_CATALOG is None
    assert DEFAULT_SCHEMA is None
    assert DEFAULT_AUTH is None
    assert DEFAULT_MAX_ATTEMPTS == 3
    assert DEFAULT_REQUEST_TIMEOUT == 30.0

    # Check HTTP/HTTPS
    assert HTTP == "http"
    assert HTTPS == "https"

    # Check URLs and endpoints
    assert URL_STATEMENT_PATH == "/v1/statement"
    assert AVRIO_METADATA_ENDPOINT == "/core/python/metadata/"

    # Check client info
    assert CLIENT_NAME == "Trino Python Client"

    # Check headers
    assert HEADER_CATALOG == "X-Trino-Catalog"
    assert HEADER_SCHEMA == "X-Trino-Schema"
    assert HEADER_SOURCE == "X-Trino-Source"
    assert HEADER_USER == "X-Trino-User"
    assert HEADER_CLIENT_INFO == "X-Trino-Client-Info"
    assert HEADER_CLIENT_TAGS == "X-Trino-Client-Tags"
    assert HEADER_EXTRA_CREDENTIAL == "X-Trino-Extra-Credential"
    assert HEADER_TIMEZONE == "X-Trino-Time-Zone"

    # Check session headers
    assert HEADER_SESSION == "X-Trino-Session"
    assert HEADER_SET_SESSION == "X-Trino-Set-Session"
    assert HEADER_CLEAR_SESSION == "X-Trino-Clear-Session"

    # Check role headers
    assert HEADER_ROLE == "X-Trino-Role"
    assert HEADER_SET_ROLE == "X-Trino-Set-Role"

    # Check transaction headers
    assert HEADER_STARTED_TRANSACTION == "X-Trino-Started-Transaction-Id"
    assert HEADER_TRANSACTION == "X-Trino-Transaction-Id"

    # Check prepared statement headers
    assert HEADER_PREPARED_STATEMENT == "X-Trino-Prepared-Statement"
    assert HEADER_ADDED_PREPARE == "X-Trino-Added-Prepare"
    assert HEADER_DEALLOCATED_PREPARE == "X-Trino-Deallocated-Prepare"

    # Check catalog/schema headers
    assert HEADER_SET_SCHEMA == "X-Trino-Set-Schema"
    assert HEADER_SET_CATALOG == "X-Trino-Set-Catalog"

    # Check client capabilities
    assert HEADER_CLIENT_CAPABILITIES == "X-Trino-Client-Capabilities"

    # Check types
    assert LENGTH_TYPES == ["char", "varchar"]
    assert PRECISION_TYPES == ["time", "time with time zone", "timestamp", "timestamp with time zone", "decimal"]
    assert SCALE_TYPES == ["decimal"]
