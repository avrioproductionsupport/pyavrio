import pytest
from sqlalchemy import exc
from pyavrio.sqlalchemy.util import _url

class TestUrlFunction:
    def test_required_parameters(self):
        """
        Test that the function works with only the required parameters.
        """
        url = _url(
            host="localhost"
        )
        # Check the key components of the URL
        assert "pyavrio://localhost:8080/" in url
        assert "?source=pyavrio-sqlalchemy" in url
        assert "&platform=data_products" in url

    def test_with_all_optional_parameters(self):
        """
        Test the function with all optional parameters.
        """
        url = _url(
            host="localhost",
            port=8888,
            user="test_user",
            password="test_pass",
            catalog="my_catalog",
            schema="my_schema",
            source="custom_source",
            session_properties={"key1": "value1"},
            http_headers={"header1": "value1", "header2": 123},
            extra_credential=[("user1", "password1")],
            client_tags=["tag1", "tag2"],
            legacy_primitive_types=True,
            legacy_prepared_statements=False,
            access_token="my_access_token",
            cert="cert_path",
            key="key_path",
            verify=False,
            roles={"role1": "admin"},
            platform="my_platform"
        )
        # Check if the URL contains expected components
        assert "pyavrio://test_user:test_pass@localhost:8888/my_catalog/my_schema" in url
        assert "?source=custom_source" in url
        assert "&session_properties=%7B%22key1%22%3A+%22value1%22%7D" in url
        assert "&http_headers=%7B%22header1%22%3A+%22value1%22%2C+%22header2%22%3A+123%7D" in url
        assert "&extra_credential=%5B%5B%22user1%22%2C+%22password1%22%5D%5D" in url
        assert "&client_tags=%5B%22tag1%22%2C+%22tag2%22%5D" in url
        assert "&legacy_primitive_types=true" in url
        assert "&legacy_prepared_statements=false" in url
        assert "&access_token=my_access_token" in url
        assert "&cert=cert_path" in url
        assert "&key=key_path" in url
        assert "&verify=false" in url
        assert "&roles=%7B%22role1%22%3A+%22admin%22%7D" in url
        assert "&platform=my_platform" in url

    def test_special_characters_in_user_and_password(self):
        """
        Test that special characters in user and password are encoded correctly.
        """
        url = _url(
            host="localhost",
            user="user@name",
            password="pa:ss/word"
        )
        # Check that special characters are encoded correctly
        assert "pyavrio://user%40name:pa%3Ass%2Fword@localhost:8080/" in url
        assert "?source=pyavrio-sqlalchemy" in url
        assert "&platform=data_products" in url

    def test_no_schema_or_catalog(self):
        """
        Test that the function works without catalog or schema.
        """
        url = _url(
            host="localhost",
            user="test_user",
            password="test_pass"
        )
        # Check if it falls back correctly
        assert "pyavrio://test_user:test_pass@localhost:8080/" in url
        assert "?source=pyavrio-sqlalchemy" in url
        assert "&platform=data_products" in url

    def test_default_source_and_platform(self):
        """
        Test that the default source and platform values are used when not specified.
        """
        url = _url(
            host="localhost"
        )
        # Check if the default source and platform are included
        assert "?source=pyavrio-sqlalchemy" in url
        assert "&platform=data_products" in url

    def test_custom_port(self):
        """
        Test that the function works with a custom port.
        """
        url = _url(
            host="localhost",
            port=5432
        )
        # Check if the custom port is applied
        assert "pyavrio://localhost:5432/" in url
        assert "?source=pyavrio-sqlalchemy" in url
        assert "&platform=data_products" in url


